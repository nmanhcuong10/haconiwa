"""
Policy Engine for Haconiwa v1.0
"""

from typing import Dict, List, Any, Optional
import logging
from pathlib import Path

from .validator import CommandValidator, ValidationResult
from ..crd.models import CommandPolicyCRD

logger = logging.getLogger(__name__)


class PolicyViolationError(Exception):
    """Policy violation error"""
    pass


class PolicyEngine:
    """Policy engine for command validation and enforcement"""
    
    def __init__(self):
        self.active_policy = None
        self.validator = CommandValidator()
        self.policies = {}
        self.agent_roles = {}
    
    def load_policy(self, crd: CommandPolicyCRD) -> Dict[str, Any]:
        """Load policy from CommandPolicy CRD"""
        policy = {
            "name": crd.metadata.name,
            "global": crd.spec.global_commands,
            "roles": {}
        }
        
        # Convert CRD roles to internal format
        for role_name, role_policy in crd.spec.roles.items():
            policy["roles"][role_name] = {
                "allow": role_policy.allow,
                "deny": role_policy.deny
            }
        
        # Store policy
        self.policies[crd.metadata.name] = policy
        
        logger.info(f"Loaded policy: {crd.metadata.name}")
        return policy
    
    def set_active_policy(self, policy: Dict[str, Any]):
        """Set active policy"""
        self.active_policy = policy
        self.validator.set_policy(policy)
        logger.info(f"Set active policy: {policy.get('name', 'unknown')}")
    
    def get_active_policy(self) -> Optional[Dict[str, Any]]:
        """Get active policy"""
        return self.active_policy
    
    def test_command(self, agent_id: str, command: str) -> bool:
        """Test if command is allowed for agent"""
        # Get agent role
        role = self._get_agent_role(agent_id)
        
        # Validate command
        result = self.validator.validate_command(command, role)
        
        # Log validation result
        logger.info(f"Command validation - Agent: {agent_id}, Role: {role}, Command: {command}, Allowed: {result.allowed}, Reason: {result.reason}")
        
        return result.allowed
    
    def validate_command(self, agent_id: str, command: str) -> ValidationResult:
        """Validate command and return detailed result"""
        # Get agent role
        role = self._get_agent_role(agent_id)
        
        # Check for malicious commands
        if self.validator.is_malicious_command(command):
            return ValidationResult(
                allowed=False,
                reason="malicious command detected",
                command=command,
                role=role
            )
        
        # Validate command
        result = self.validator.validate_command(command, role)
        
        # Log validation result
        logger.info(f"Command validation - Agent: {agent_id}, Role: {role}, Command: {command}, Allowed: {result.allowed}, Reason: {result.reason}")
        
        return result
    
    def enforce_command(self, agent_id: str, command: str) -> bool:
        """Enforce command policy (raises exception if denied)"""
        result = self.validate_command(agent_id, command)
        
        if not result.allowed:
            raise PolicyViolationError(f"Command denied for agent {agent_id}: {result.reason}")
        
        return True
    
    def register_agent(self, agent_id: str, role: str):
        """Register agent with role"""
        if not self.validator.validate_role(role):
            valid_roles = list(self.active_policy.get("roles", {}).keys()) if self.active_policy else []
            raise ValueError(f"Invalid role '{role}'. Valid roles: {valid_roles}")
        
        self.agent_roles[agent_id] = role
        logger.info(f"Registered agent {agent_id} with role {role}")
    
    def unregister_agent(self, agent_id: str):
        """Unregister agent"""
        if agent_id in self.agent_roles:
            del self.agent_roles[agent_id]
            logger.info(f"Unregistered agent {agent_id}")
    
    def list_policies(self) -> List[Dict[str, Any]]:
        """List all loaded policies"""
        return [
            {
                "name": name,
                "type": "CommandPolicy",
                "active": name == self.active_policy.get("name") if self.active_policy else False
            }
            for name in self.policies.keys()
        ]
    
    def get_policy(self, name: str) -> Optional[Dict[str, Any]]:
        """Get policy by name"""
        return self.policies.get(name)
    
    def delete_policy(self, name: str) -> bool:
        """Delete policy"""
        if name in self.policies:
            del self.policies[name]
            
            # If this was the active policy, clear it
            if self.active_policy and self.active_policy.get("name") == name:
                self.active_policy = None
                self.validator.set_policy(None)
            
            logger.info(f"Deleted policy: {name}")
            return True
        return False
    
    def _get_agent_role(self, agent_id: str) -> str:
        """Get role for agent"""
        role = self.agent_roles.get(agent_id, "worker")  # Default to worker
        
        # If role not found and not in valid roles, try to infer from agent_id
        if role not in self.active_policy.get("roles", {}) if self.active_policy else {}:
            if "pm" in agent_id.lower():
                role = "pm"
            else:
                role = "worker"
        
        return role
    
    def _load_policies(self) -> List[Dict[str, Any]]:
        """Load policies from storage (placeholder for future implementation)"""
        return list(self.policies.values())
    
    def _notify_policy_update(self):
        """Notify about policy update (placeholder for future implementation)"""
        logger.info("Policy updated")
    
    def get_command_stats(self) -> Dict[str, Any]:
        """Get command validation statistics"""
        # Placeholder for future implementation
        return {
            "total_commands_validated": 0,
            "commands_allowed": 0,
            "commands_denied": 0,
            "malicious_commands_blocked": 0
        } 