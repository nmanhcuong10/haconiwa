"""
CRD Applier for Haconiwa v1.0
"""

from typing import Union, List, Dict
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
        self.force_clone = False  # Default to False
    
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
        space_sessions = []  # Track space sessions for post-processing
        
        for crd in crds:
            try:
                result = self.apply(crd)
                results.append(result)
                
                # Track Space CRDs for later pane updates
                if isinstance(crd, SpaceCRD) and result:
                    # Extract session name from Space CRD
                    company = crd.spec.nations[0].cities[0].villages[0].companies[0]
                    space_sessions.append({
                        "session_name": company.name,
                        "space_ref": company.name
                    })
                    
            except Exception as e:
                logger.error(f"Failed to apply CRD {crd.metadata.name}: {e}")
                results.append(False)
        
        # IMPORTANT: Re-update task assignments for all spaces after all CRDs are applied
        # This fixes the timing issue where SpaceCRD is applied before TaskCRDs
        if space_sessions:
            logger.info("Re-updating task assignments after all CRDs are applied...")
            self._update_all_space_task_assignments(space_sessions)
        
        # Update agent pane directories for all spaces after all CRDs are applied
        self._update_all_agent_pane_directories(space_sessions)
        
        return results
    
    def _update_all_agent_pane_directories(self, space_sessions: List[Dict[str, str]]):
        """Update agent pane directories for all space sessions"""
        if not space_sessions:
            return
        
        try:
            logger.info("🎯 Using new log-file based agent assignment (TaskManager pattern matching disabled)")
            
            # Import SpaceManager to call the new log-based update method
            from ..space.manager import SpaceManager
            space_manager = SpaceManager()
            
            total_updated = 0
            
            for space_info in space_sessions:
                session_name = space_info["session_name"]
                space_ref = space_info["space_ref"]
                
                logger.info(f"🔄 Running log-based pane update for space: {space_ref}")
                
                # Use SpaceManager's new log-based update method
                updated_count = space_manager.update_all_panes_from_task_logs(session_name, space_ref)
                total_updated += updated_count
                
                if updated_count > 0:
                    logger.info(f"✅ Updated {updated_count} agent panes for space: {space_ref}")
                else:
                    logger.info(f"ℹ️ No task assignments found for space: {space_ref}")
                
            logger.info(f"🎉 Total agent panes updated across all spaces: {total_updated}")
                
        except Exception as e:
            logger.error(f"Failed to coordinate agent pane directories: {e}")
    
    def _update_all_space_task_assignments(self, space_sessions: List[Dict[str, str]]):
        """Re-update task assignments for all space sessions after all CRDs are applied"""
        try:
            from ..task.manager import TaskManager
            from ..space.manager import SpaceManager
            
            task_manager = TaskManager()
            
            for space_info in space_sessions:
                session_name = space_info["session_name"]
                space_ref = space_info["space_ref"]
                
                # Get all task assignments for this space
                task_assignments = {}
                for task_name, task_data in task_manager.tasks.items():
                    assignee = task_data["config"].get("assignee")
                    task_space_ref = task_data["config"].get("space_ref")
                    if assignee and task_space_ref == space_ref:
                        task_assignments[assignee] = {
                            "name": task_name,
                            "worktree_path": f"tasks/{task_name}",
                            "config": task_data["config"]
                        }
                
                logger.info(f"Re-updating task assignments for space {space_ref}: {len(task_assignments)} tasks")
                for assignee, task_info in task_assignments.items():
                    logger.info(f"  {assignee} → {task_info['name']}")
                
                # Find and update the SpaceManager instance for this session
                # We need to get the SpaceManager instance that created this session
                # For now, we'll create a new one and set the task assignments
                space_manager = SpaceManager()
                space_manager.set_task_assignments(task_assignments)
                
                # Store the updated task assignments in active_sessions if available
                if session_name in space_manager.active_sessions:
                    space_manager.active_sessions[session_name]["task_assignments"] = task_assignments
                    
        except Exception as e:
            logger.error(f"Failed to re-update task assignments: {e}")
    
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
                logger.info(f"Git repository specified: {git_config['url']} (will be handled by SpaceManager)")
            
            # IMPORTANT: Get TaskManager tasks and pass to SpaceManager for agent assignment
            from ..task.manager import TaskManager
            task_manager = TaskManager()
            
            # Pass task assignments to SpaceManager
            task_assignments = {}
            for task_name, task_data in task_manager.tasks.items():
                assignee = task_data["config"].get("assignee")
                space_ref = task_data["config"].get("space_ref")
                if assignee and space_ref == config['name']:
                    task_assignments[assignee] = {
                        "name": task_name,
                        "worktree_path": f"tasks/{task_name}",
                        "config": task_data["config"]
                    }
            
            logger.info(f"Passing {len(task_assignments)} task assignments to SpaceManager")
            for assignee, task_info in task_assignments.items():
                logger.info(f"  {assignee} → {task_info['name']}")
            
            # Set task assignments in SpaceManager
            space_manager.set_task_assignments(task_assignments)
            
            # Create space infrastructure (32-pane tmux session with task-centric structure)
            logger.info("Creating 32-pane tmux session with tasks/ directory structure...")
            
            # Pass force_clone flag to SpaceManager
            space_manager._force_clone = self.force_clone
            
            result = space_manager.create_multiroom_session(config)
            
            if result:
                logger.info(f"✅ Space CRD {crd.metadata.name} applied successfully")
                logger.info(f"   📁 Base path: {config['base_path']}")
                logger.info(f"   🖥️ Session: {config['name']} (32 panes)")
                logger.info(f"   🏢 Organizations: {len(config.get('organizations', []))}")
                logger.info(f"   🚪 Rooms: {len(config.get('rooms', []))}")
                logger.info(f"   🎯 Agent assignments: {len(task_assignments)}")
            else:
                logger.error(f"❌ Failed to apply Space CRD {crd.metadata.name}")
            
            return result
            
        except Exception as e:
            logger.error(f"Exception while applying Space CRD {crd.metadata.name}: {e}")
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
        task_manager = TaskManager()  # This will get the singleton instance
        
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