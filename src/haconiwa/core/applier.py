"""
CRD Applier for Haconiwa v1.0
"""

from typing import Union, List
from pathlib import Path
import logging

from .crd.models import (
    SpaceCRD, AgentCRD, TaskCRD, PathScanCRD, DatabaseCRD, CommandPolicyCRD
)

logger = logging.getLogger(__name__)


class CRDApplierError(Exception):
    """CRD applier error"""
    pass


class CRDApplier:
    """CRD Applier - applies CRD objects to the system"""
    
    def __init__(self):
        self.applied_resources = {}
    
    def apply(self, crd: Union[SpaceCRD, AgentCRD, TaskCRD, PathScanCRD, DatabaseCRD, CommandPolicyCRD]) -> bool:
        """Apply CRD to the system"""
        try:
            if isinstance(crd, SpaceCRD):
                return self._apply_space_crd(crd)
            elif isinstance(crd, AgentCRD):
                return self._apply_agent_crd(crd)
            elif isinstance(crd, TaskCRD):
                return self._apply_task_crd(crd)
            elif isinstance(crd, PathScanCRD):
                return self._apply_pathscan_crd(crd)
            elif isinstance(crd, DatabaseCRD):
                return self._apply_database_crd(crd)
            elif isinstance(crd, CommandPolicyCRD):
                return self._apply_commandpolicy_crd(crd)
            else:
                raise CRDApplierError(f"Unknown CRD type: {type(crd)}")
        except Exception as e:
            logger.error(f"Failed to apply CRD {crd.metadata.name}: {e}")
            raise CRDApplierError(f"Failed to apply CRD {crd.metadata.name}: {e}")
    
    def apply_multiple(self, crds: List[Union[SpaceCRD, AgentCRD, TaskCRD, PathScanCRD, DatabaseCRD, CommandPolicyCRD]]) -> List[bool]:
        """Apply multiple CRDs to the system"""
        results = []
        for crd in crds:
            try:
                result = self.apply(crd)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to apply CRD {crd.metadata.name}: {e}")
                results.append(False)
        return results
    
    def _apply_space_crd(self, crd: SpaceCRD) -> bool:
        """Apply Space CRD"""
        logger.info(f"Applying Space CRD: {crd.metadata.name}")
        
        try:
            # Store CRD for later reference
            self.applied_resources[f"Space/{crd.metadata.name}"] = crd
            
            # Import space manager here to avoid circular import
            from ..space.manager import SpaceManager
            space_manager = SpaceManager()
            
            # Convert CRD to internal configuration
            config = space_manager.convert_crd_to_config(crd)
            logger.info(f"Converted CRD to config: {config['name']} with {len(config.get('organizations', []))} organizations")
            
            # Handle Git repository if specified
            if config.get("git_repo"):
                git_config = config["git_repo"]
                logger.info(f"Git repository specified: {git_config['url']}")
                
                # Check if repository needs to be cloned
                base_path = Path(config["base_path"])
                git_dir = base_path / ".git"
                
                if not git_dir.exists():
                    logger.info(f"Cloning repository to {base_path}")
                    success = self._clone_repository(git_config, base_path)
                    if not success:
                        logger.warning("Failed to clone repository, continuing without Git")
                else:
                    logger.info("Repository already exists, skipping clone")
            
            # Create space infrastructure (32-pane tmux session)
            logger.info("Creating 32-pane tmux session...")
            result = space_manager.create_multiroom_session(config)
            
            if result:
                logger.info(f"✅ Space CRD {crd.metadata.name} applied successfully")
                logger.info(f"   📁 Base path: {config['base_path']}")
                logger.info(f"   🖥️ Session: {config['name']} (32 panes)")
                logger.info(f"   🏢 Organizations: {len(config.get('organizations', []))}")
                logger.info(f"   🚪 Rooms: {len(config.get('rooms', []))}")
            else:
                logger.error(f"❌ Failed to apply Space CRD {crd.metadata.name}")
            
            return result
            
        except Exception as e:
            logger.error(f"Exception while applying Space CRD {crd.metadata.name}: {e}")
            return False
    
    def _clone_repository(self, git_config: dict, base_path: Path) -> bool:
        """Clone Git repository"""
        try:
            import subprocess
            
            # Create parent directory
            base_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare clone command
            url = git_config["url"]
            auth = git_config.get("auth", "https")
            
            cmd = ["git", "clone", url, str(base_path)]
            
            # Execute clone
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info(f"Successfully cloned repository from {url}")
                return True
            else:
                logger.error(f"Failed to clone repository: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Git clone operation timed out")
            return False
        except Exception as e:
            logger.error(f"Error during git clone: {e}")
            return False
    
    def _apply_agent_crd(self, crd: AgentCRD) -> bool:
        """Apply Agent CRD"""
        logger.info(f"Applying Agent CRD: {crd.metadata.name}")
        
        # Store CRD for later reference
        self.applied_resources[f"Agent/{crd.metadata.name}"] = crd
        
        # Import agent manager here to avoid circular import
        from ..agent.manager import AgentManager
        agent_manager = AgentManager()
        
        # Create agent configuration
        agent_config = {
            "name": crd.metadata.name,
            "role": crd.spec.role,
            "model": crd.spec.model,
            "space_ref": crd.spec.spaceRef,
            "system_prompt_path": crd.spec.systemPromptPath,
            "env": crd.spec.env or {}
        }
        
        # Apply agent configuration
        result = agent_manager.create_agent(agent_config)
        
        logger.info(f"Agent CRD {crd.metadata.name} applied successfully: {result}")
        return result
    
    def _apply_task_crd(self, crd: TaskCRD) -> bool:
        """Apply Task CRD"""
        logger.info(f"Applying Task CRD: {crd.metadata.name}")
        
        # Store CRD for later reference
        self.applied_resources[f"Task/{crd.metadata.name}"] = crd
        
        # Import task manager here to avoid circular import
        from ..task.manager import TaskManager
        task_manager = TaskManager()
        
        # Create task configuration
        task_config = {
            "name": crd.metadata.name,
            "branch": crd.spec.branch,
            "worktree": crd.spec.worktree,
            "assignee": crd.spec.assignee,
            "space_ref": crd.spec.spaceRef,
            "description": crd.spec.description
        }
        
        # Apply task configuration
        result = task_manager.create_task(task_config)
        
        logger.info(f"Task CRD {crd.metadata.name} applied successfully: {result}")
        return result
    
    def _apply_pathscan_crd(self, crd: PathScanCRD) -> bool:
        """Apply PathScan CRD"""
        logger.info(f"Applying PathScan CRD: {crd.metadata.name}")
        
        # Store CRD for later reference
        self.applied_resources[f"PathScan/{crd.metadata.name}"] = crd
        
        # Import path scanner here to avoid circular import
        from ..resource.path_scanner import PathScanner
        
        # Create scanner configuration
        scanner_config = {
            "name": crd.metadata.name,
            "include": crd.spec.include,
            "exclude": crd.spec.exclude
        }
        
        # Register scanner configuration
        PathScanner.register_config(crd.metadata.name, scanner_config)
        
        logger.info(f"PathScan CRD {crd.metadata.name} applied successfully")
        return True
    
    def _apply_database_crd(self, crd: DatabaseCRD) -> bool:
        """Apply Database CRD"""
        logger.info(f"Applying Database CRD: {crd.metadata.name}")
        
        # Store CRD for later reference
        self.applied_resources[f"Database/{crd.metadata.name}"] = crd
        
        # Import database manager here to avoid circular import
        from ..resource.db_fetcher import DatabaseManager
        
        # Create database configuration
        db_config = {
            "name": crd.metadata.name,
            "dsn": crd.spec.dsn,
            "use_ssl": crd.spec.useSSL
        }
        
        # Register database configuration
        DatabaseManager.register_config(crd.metadata.name, db_config)
        
        logger.info(f"Database CRD {crd.metadata.name} applied successfully")
        return True
    
    def _apply_commandpolicy_crd(self, crd: CommandPolicyCRD) -> bool:
        """Apply CommandPolicy CRD"""
        logger.info(f"Applying CommandPolicy CRD: {crd.metadata.name}")
        
        # Store CRD for later reference
        self.applied_resources[f"CommandPolicy/{crd.metadata.name}"] = crd
        
        # Import policy engine here to avoid circular import
        from .policy.engine import PolicyEngine
        policy_engine = PolicyEngine()
        
        # Load policy from CRD
        policy = policy_engine.load_policy(crd)
        
        # Set as active policy if it's the default
        if crd.metadata.name == "default-command-whitelist":
            policy_engine.set_active_policy(policy)
        
        logger.info(f"CommandPolicy CRD {crd.metadata.name} applied successfully")
        return True
    
    def get_applied_resources(self) -> dict:
        """Get list of applied resources"""
        return self.applied_resources.copy()
    
    def remove_resource(self, resource_type: str, name: str) -> bool:
        """Remove applied resource"""
        resource_key = f"{resource_type}/{name}"
        if resource_key in self.applied_resources:
            del self.applied_resources[resource_key]
            logger.info(f"Removed resource: {resource_key}")
            return True
        return False 