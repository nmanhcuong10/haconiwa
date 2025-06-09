"""
Command Validator for Haconiwa v1.0
"""

import re
import shlex
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Command validation result"""
    allowed: bool
    reason: str
    command: str
    role: str


class CommandValidator:
    """Command validator with policy enforcement"""
    
    def __init__(self):
        self.active_policy = None
    
    def set_policy(self, policy: Dict[str, Any]):
        """Set active policy"""
        self.active_policy = policy
    
    def validate_command(self, command: str, role: str) -> ValidationResult:
        """Validate command against policy"""
        if not self.active_policy:
            return ValidationResult(
                allowed=False,
                reason="No active policy",
                command=command,
                role=role
            )
        
        # Parse command components
        components = self.parse_command(command)
        base_command = components["base"]
        subcommand = components["subcommand"]
        
        # Check role-specific deny first (highest priority)
        if self._is_role_denied(base_command, subcommand, role):
            return ValidationResult(
                allowed=False,
                reason="role-specific deny",
                command=command,
                role=role
            )
        
        # Check role-specific allow (second priority)
        if self._is_role_allowed(base_command, subcommand, role):
            return ValidationResult(
                allowed=True,
                reason="role-specific allow",
                command=command,
                role=role
            )
        
        # Check global allow (third priority)
        if self._is_global_allowed(base_command, subcommand):
            return ValidationResult(
                allowed=True,
                reason="global allow",
                command=command,
                role=role
            )
        
        # Default deny
        return ValidationResult(
            allowed=False,
            reason="not in global whitelist",
            command=command,
            role=role
        )
    
    def parse_command(self, command: str) -> Dict[str, Any]:
        """Parse command into components"""
        try:
            # Split command into tokens
            tokens = shlex.split(command)
            if not tokens:
                return {"base": "", "subcommand": "", "args": []}
            
            base = tokens[0]
            
            # Handle haconiwa namespace commands (e.g., "haconiwa space.start")
            if base == "haconiwa" and len(tokens) > 1:
                subcommand = tokens[1]
                args = tokens[2:] if len(tokens) > 2 else []
            else:
                subcommand = tokens[1] if len(tokens) > 1 else ""
                args = tokens[2:] if len(tokens) > 2 else []
            
            return {
                "base": base,
                "subcommand": subcommand,
                "args": args,
                "original": command
            }
        except Exception as e:
            logger.warning(f"Failed to parse command '{command}': {e}")
            return {"base": "", "subcommand": "", "args": [], "original": command}
    
    def _is_role_denied(self, base_command: str, subcommand: str, role: str) -> bool:
        """Check if command is explicitly denied for role"""
        if not self.active_policy or "roles" not in self.active_policy:
            return False
        
        role_policy = self.active_policy["roles"].get(role, {})
        deny_policy = role_policy.get("deny", {})
        
        if base_command in deny_policy:
            denied_subcommands = deny_policy[base_command]
            # If subcommand is in deny list, it's denied
            return subcommand in denied_subcommands
        
        return False
    
    def _is_role_allowed(self, base_command: str, subcommand: str, role: str) -> bool:
        """Check if command is explicitly allowed for role"""
        if not self.active_policy or "roles" not in self.active_policy:
            return False
        
        role_policy = self.active_policy["roles"].get(role, {})
        allow_policy = role_policy.get("allow", {})
        
        if base_command in allow_policy:
            allowed_subcommands = allow_policy[base_command]
            # If subcommand is in allow list, it's allowed
            return subcommand in allowed_subcommands
        
        return False
    
    def _is_global_allowed(self, base_command: str, subcommand: str) -> bool:
        """Check if command is globally allowed"""
        if not self.active_policy or "global" not in self.active_policy:
            return False
        
        global_policy = self.active_policy["global"]
        
        if base_command in global_policy:
            allowed_subcommands = global_policy[base_command]
            # If no subcommand specified or subcommand is in allow list
            return not subcommand or subcommand in allowed_subcommands
        
        return False
    
    def is_malicious_command(self, command: str) -> bool:
        """Detect potentially malicious commands"""
        malicious_patterns = [
            r'rm\s+-rf\s+/',
            r'sudo\s+rm\s+-rf\s+/',
            r'\|\s*bash',
            r'\|\s*sh',
            r';\s*rm\s+-rf',
            r'&&\s*rm\s+-rf',
            r'curl.*\|\s*bash',
            r'wget.*\|\s*sh',
            r'--privileged.*chroot'
        ]
        
        for pattern in malicious_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return True
        
        return False
    
    def validate_role(self, role: str) -> bool:
        """Validate if role exists in policy"""
        if not self.active_policy or "roles" not in self.active_policy:
            return False
        
        return role in self.active_policy["roles"] 