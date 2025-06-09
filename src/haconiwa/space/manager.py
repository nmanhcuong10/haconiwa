"""
Space Manager for Haconiwa v1.0 - 32 Pane Support
"""

import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

from ..core.crd.models import SpaceCRD

logger = logging.getLogger(__name__)


class SpaceManagerError(Exception):
    """Space manager error"""
    pass


class SpaceManager:
    """Space manager with 32-pane and multi-room support"""
    
    def __init__(self):
        self.active_sessions = {}
    
    def create_multiroom_session(self, config: Dict[str, Any]) -> bool:
        """Create 32-pane multi-room tmux session"""
        try:
            session_name = config["name"]
            grid = config.get("grid", "8x4")
            base_path = Path(config.get("base_path", f"./{session_name}"))
            
            logger.info(f"Creating 32-pane session: {session_name}")
            
            # Create base directory
            base_path.mkdir(parents=True, exist_ok=True)
            
            # Generate desk mappings
            desk_mappings = self.generate_desk_mappings()
            
            # Create tmux session
            self._create_tmux_session(session_name)
            
            # Create 32 panes (8x4 layout)
            self._create_panes(session_name, 32)
            
            # Set up desk directories and pane titles
            for i, mapping in enumerate(desk_mappings):
                desk_dir = self._create_desk_directory(base_path, mapping)
                self._update_pane_directory(session_name, i, desk_dir)
                self._update_pane_title(session_name, i, mapping)
            
            # Store session info
            self.active_sessions[session_name] = {
                "config": config,
                "desk_mappings": desk_mappings,
                "pane_count": 32
            }
            
            logger.info(f"32-pane session created successfully: {session_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create session {config.get('name', 'unknown')}: {e}")
            return False
    
    def generate_desk_mappings(self) -> List[Dict[str, Any]]:
        """Generate 32-desk mappings (4 orgs × 4 roles × 2 rooms)"""
        mappings = []
        
        # Room-01 (desk-0100 to desk-0403)
        for org_id in range(1, 5):  # org-01 to org-04
            for role_id in range(4):  # pm, worker-a, worker-b, worker-c
                desk_id = f"desk-{org_id:02d}{role_id:02d}"
                role_name = "pm" if role_id == 0 else f"worker-{chr(ord('a') + role_id - 1)}"
                
                # Directory naming: 01pm, 01a, 01b, 01c
                if role_name == "pm":
                    dir_name = f"{org_id:02d}pm"
                else:
                    worker_suffix = role_name.split("-")[1]  # a, b, c
                    dir_name = f"{org_id:02d}{worker_suffix}"
                
                mappings.append({
                    "desk_id": desk_id,
                    "org_id": f"org-{org_id:02d}",
                    "role": role_name,
                    "room_id": "room-01",
                    "directory_name": dir_name,
                    "title": f"Org-{org_id:02d} {role_name.upper()} - Alpha Room"
                })
        
        # Room-02 (desk-1100 to desk-1403)
        for org_id in range(1, 5):  # org-01 to org-04
            for role_id in range(4):  # pm, worker-a, worker-b, worker-c
                desk_id = f"desk-1{org_id}{role_id:02d}"
                role_name = "pm" if role_id == 0 else f"worker-{chr(ord('a') + role_id - 1)}"
                
                # Directory naming: 11pm, 11a, 11b, 11c (1 + org_id + role)
                if role_name == "pm":
                    dir_name = f"1{org_id}pm"
                else:
                    worker_suffix = role_name.split("-")[1]  # a, b, c
                    dir_name = f"1{org_id}{worker_suffix}"
                
                mappings.append({
                    "desk_id": desk_id,
                    "org_id": f"org-{org_id:02d}",
                    "role": role_name,
                    "room_id": "room-02",
                    "directory_name": dir_name,
                    "title": f"Org-{org_id:02d} {role_name.upper()} - Beta Room"
                })
        
        return mappings
    
    def convert_crd_to_config(self, crd: SpaceCRD) -> Dict[str, Any]:
        """Convert Space CRD to internal configuration"""
        # Navigate through the CRD structure to get company config
        company = crd.spec.nations[0].cities[0].villages[0].companies[0]
        
        config = {
            "name": company.name,
            "grid": company.grid,
            "base_path": company.basePath,
            "git_repo": None,
            "organizations": [],
            "rooms": [
                {"id": "room-01", "name": "Alpha Room"},
                {"id": "room-02", "name": "Beta Room"}
            ]
        }
        
        # Add git repository config if specified
        if company.gitRepo:
            config["git_repo"] = {
                "url": company.gitRepo.url,
                "default_branch": company.gitRepo.defaultBranch,
                "auth": company.gitRepo.auth
            }
        
        # Add organizations
        for org in company.organizations:
            config["organizations"].append({
                "id": org.id,
                "name": org.name,
                "tasks": org.tasks
            })
        
        return config
    
    def _create_tmux_session(self, session_name: str):
        """Create tmux session"""
        cmd = ["tmux", "new-session", "-d", "-s", session_name]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise SpaceManagerError(f"Failed to create tmux session: {result.stderr}")
    
    def _create_panes(self, session_name: str, pane_count: int):
        """Create panes for 8x4 layout (32 panes)"""
        # Create 31 additional panes (first pane already exists)
        
        # Step 1: Create first row (8 panes) by splitting horizontally 7 times
        for i in range(7):
            cmd = ["tmux", "split-window", "-h", "-t", f"{session_name}:0"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.warning(f"Failed to create horizontal pane {i+1}: {result.stderr}")
        
        # Step 2: Create additional 3 rows (24 more panes)
        for row in range(1, 4):  # rows 1, 2, 3
            # Split the first pane of the first row vertically to create new row
            cmd = ["tmux", "split-window", "-v", "-t", f"{session_name}:0.0"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.warning(f"Failed to create row {row}: {result.stderr}")
            
            # Split the new row horizontally 7 times to create 8 panes in the row
            for col in range(7):
                cmd = ["tmux", "split-window", "-h", "-t", f"{session_name}:0.{row * 8}"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    logger.warning(f"Failed to create pane in row {row}, col {col}: {result.stderr}")
        
        # Step 3: Apply tiled layout for even distribution
        cmd = ["tmux", "select-layout", "-t", f"{session_name}:0", "tiled"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.warning(f"Failed to apply tiled layout: {result.stderr}")
        
        logger.info(f"Created {pane_count} panes in 8x4 layout for session {session_name}")
    
    def _create_desk_directory(self, base_path: Path, mapping: Dict[str, Any]) -> Path:
        """Create directory for desk"""
        org_id = mapping["org_id"]
        dir_name = mapping["directory_name"]
        
        desk_dir = base_path / org_id / dir_name
        desk_dir.mkdir(parents=True, exist_ok=True)
        
        return desk_dir
    
    def _update_pane_directory(self, session_name: str, pane_index: int, directory: Path):
        """Update pane working directory"""
        cmd = ["tmux", "send-keys", "-t", f"{session_name}:0.{pane_index}", f"cd {directory}", "Enter"]
        subprocess.run(cmd, capture_output=True, text=True)
    
    def _update_pane_title(self, session_name: str, pane_index: int, mapping: Dict[str, Any]):
        """Update pane title"""
        title = mapping["title"]
        cmd = ["tmux", "select-pane", "-t", f"{session_name}:0.{pane_index}", "-T", title]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    
    def create_room_layout(self, session_name: str, room_config: Dict[str, Any]) -> bool:
        """Create layout for specific room"""
        try:
            room_id = room_config["id"]
            desks = room_config.get("desks", [])
            
            logger.info(f"Creating room layout: {room_id} with {len(desks)} desks")
            
            # This is a simplified implementation
            # In a full implementation, this would handle room-specific layouts
            return True
            
        except Exception as e:
            logger.error(f"Failed to create room layout: {e}")
            return False
    
    def create_desk_directory(self, base_path: Path, desk_config: Dict[str, Any]) -> Path:
        """Create directory for individual desk"""
        org_id = desk_config["org_id"]
        role = desk_config["role"]
        room_id = desk_config.get("room_id", "room-01")
        
        # Determine directory name based on room
        if room_id == "room-02":
            # Room-02 uses 1X format
            org_num = org_id.split("-")[1]
            if role == "pm":
                dir_name = f"1{org_num}pm"
            else:
                worker_suffix = role.split("-")[1]
                dir_name = f"1{org_num}worker-{worker_suffix}"
        else:
            # Room-01 uses standard format
            org_num = org_id.split("-")[1]
            if role == "pm":
                dir_name = f"{org_num}pm"
            else:
                worker_suffix = role.split("-")[1]
                dir_name = f"{org_num}worker-{worker_suffix}"
        
        desk_dir = base_path / org_id / dir_name
        desk_dir.mkdir(parents=True, exist_ok=True)
        
        return desk_dir
    
    def extract_agent_config(self, desk_config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract agent configuration from desk config"""
        agent = desk_config.get("agent", {})
        return {
            "name": agent.get("name", ""),
            "role": agent.get("role", "worker"),
            "model": agent.get("model", "gpt-4o"),
            "env": agent.get("env", {}),
            "desk_id": desk_config["id"]
        }
    
    def update_pane_title(self, session_name: str, pane_index: int, config: Dict[str, Any]) -> bool:
        """Update tmux pane title"""
        title = config.get("title", f"Pane {pane_index}")
        cmd = ["tmux", "select-pane", "-t", f"{session_name}:0.{pane_index}", "-T", title]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    
    def create_task_worktree(self, task_config: Dict[str, Any]) -> bool:
        """Create Git worktree for task"""
        try:
            branch = task_config["branch"]
            base_path = task_config["base_path"]
            
            # Create worktree directory
            worktree_path = Path(base_path) / "worktrees" / branch
            
            cmd = ["git", "worktree", "add", str(worktree_path), branch]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=base_path)
            
            if result.returncode == 0:
                logger.info(f"Created worktree for branch {branch}")
                return True
            else:
                logger.error(f"Failed to create worktree: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to create task worktree: {e}")
            return False
    
    def switch_to_room(self, session_name: str, room_id: str) -> bool:
        """Switch to specific room"""
        try:
            # In a full implementation, this would switch between room layouts
            # For now, just select appropriate pane range
            
            if room_id == "room-01":
                # Select first pane (panes 0-15)
                cmd = ["tmux", "select-pane", "-t", f"{session_name}:0.0"]
            else:
                # Select pane 16 (panes 16-31)
                cmd = ["tmux", "select-pane", "-t", f"{session_name}:0.16"]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Failed to switch to room {room_id}: {e}")
            return False
    
    def calculate_layout(self, grid: str) -> Dict[str, Any]:
        """Calculate layout parameters"""
        if grid == "8x4":
            return {
                "columns": 8,
                "rows": 4,
                "total_panes": 32,
                "panes_per_room": 16
            }
        else:
            # Default fallback
            return {
                "columns": 4,
                "rows": 4,
                "total_panes": 16,
                "panes_per_room": 16
            }
    
    def distribute_organizations(self, organizations: List[Dict[str, Any]], room_count: int) -> List[Dict[str, Any]]:
        """Distribute organizations across rooms"""
        rooms = []
        for i in range(room_count):
            room_id = f"room-{i+1:02d}"
            room_name = ["Alpha Room", "Beta Room"][i] if i < 2 else f"Room {i+1}"
            
            rooms.append({
                "id": room_id,
                "name": room_name,
                "organizations": organizations.copy()  # All orgs in each room
            })
        
        return rooms
    
    def cleanup_session(self, session_name: str, purge_data: bool = False) -> bool:
        """Clean up tmux session and optionally data"""
        try:
            # Kill tmux session
            cmd = ["tmux", "kill-session", "-t", session_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Remove from active sessions
            if session_name in self.active_sessions:
                del self.active_sessions[session_name]
            
            logger.info(f"Cleaned up session: {session_name}")
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Failed to cleanup session {session_name}: {e}")
            return False
    
    def attach_to_room(self, session_name: str, room_id: str) -> bool:
        """Attach to specific room in session"""
        try:
            # Switch to room first
            self.switch_to_room(session_name, room_id)
            
            # Attach to session
            cmd = ["tmux", "attach-session", "-t", session_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Failed to attach to room {room_id}: {e}")
            return False
    
    def list_spaces(self) -> List[Dict[str, Any]]:
        """List all spaces"""
        return [
            {
                "name": name,
                "status": "active",
                "companies": 1,
                "rooms": len(info["config"].get("rooms", [])),
                "panes": info.get("pane_count", 0)
            }
            for name, info in self.active_sessions.items()
        ]
    
    def start_company(self, company_name: str) -> bool:
        """Start company session"""
        # This is a placeholder - would integrate with existing company logic
        return True
    
    def clone_repository(self, company_name: str) -> bool:
        """Clone repository for company"""
        # This is a placeholder - would integrate with Git operations
        return True 