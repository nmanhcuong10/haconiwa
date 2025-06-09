"""
CRD Data Models for Haconiwa v1.0
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict
import re


class Metadata(BaseModel):
    """CRD Metadata"""
    name: str = Field(..., description="Resource name")


class AgentConfig(BaseModel):
    """Agent configuration embedded in desks"""
    name: str
    role: str
    model: str
    env: Optional[Dict[str, str]] = None


class DeskConfig(BaseModel):
    """Desk configuration"""
    id: str
    agent: Optional[AgentConfig] = None


class RoomConfig(BaseModel):
    """Room configuration"""
    id: str
    name: str
    desks: List[DeskConfig] = []


class FloorConfig(BaseModel):
    """Floor configuration"""
    level: int
    rooms: List[RoomConfig] = []


class BuildingConfig(BaseModel):
    """Building configuration"""
    id: str
    name: str
    floors: List[FloorConfig] = []


class GitRepoConfig(BaseModel):
    """Git repository configuration"""
    url: str
    defaultBranch: str = "main"
    auth: str = Field(..., description="Authentication method: ssh, https, token")
    
    @field_validator('auth')
    @classmethod
    def validate_auth(cls, v):
        if v not in ['ssh', 'https', 'token']:
            raise ValueError('auth must be ssh, https, or token')
        return v


class OrganizationConfig(BaseModel):
    """Organization configuration"""
    id: str
    name: str
    tasks: List[str] = []


class CompanyConfig(BaseModel):
    """Company configuration"""
    name: str
    grid: str = "8x4"
    basePath: str
    gitRepo: Optional[GitRepoConfig] = None
    organizations: List[OrganizationConfig] = []
    buildings: List[BuildingConfig] = []


class VillageConfig(BaseModel):
    """Village configuration"""
    id: str
    name: str
    companies: List[CompanyConfig] = []


class CityConfig(BaseModel):
    """City configuration"""
    id: str
    name: str
    villages: List[VillageConfig] = []


class NationConfig(BaseModel):
    """Nation configuration"""
    id: str
    name: str
    cities: List[CityConfig] = []


class SpaceSpec(BaseModel):
    """Space CRD specification"""
    nations: List[NationConfig] = Field(..., description="List of nations")
    
    @field_validator('nations')
    @classmethod
    def validate_nations(cls, v):
        if not v:
            raise ValueError('nations cannot be empty')
        return v


class SpaceCRD(BaseModel):
    """Space CRD - World/Company/Room/Desk hierarchy"""
    apiVersion: str = Field("haconiwa.dev/v1", description="API version")
    kind: str = Field("Space", description="Resource kind")
    metadata: Metadata
    spec: SpaceSpec


class AgentSpec(BaseModel):
    """Agent CRD specification"""
    role: str = Field(..., description="Agent role: pm or worker")
    model: str = Field(..., description="AI model to use")
    spaceRef: Optional[str] = Field(None, description="Reference to Space")
    systemPromptPath: Optional[str] = Field(None, description="Path to system prompt file")
    env: Optional[Dict[str, str]] = Field(None, description="Environment variables")
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v not in ['pm', 'worker']:
            raise ValueError("role must be 'pm' or 'worker'")
        return v


class AgentCRD(BaseModel):
    """Agent CRD - AI agent configuration"""
    apiVersion: str = Field("haconiwa.dev/v1", description="API version")
    kind: str = Field("Agent", description="Resource kind")
    metadata: Metadata
    spec: AgentSpec


class TaskSpec(BaseModel):
    """Task CRD specification"""
    branch: str = Field(..., description="Git branch name")
    worktree: bool = Field(True, description="Use git worktree")
    assignee: Optional[str] = Field(None, description="Assigned agent")
    spaceRef: Optional[str] = Field(None, description="Reference to Space")
    description: Optional[str] = Field(None, description="Task description")
    
    @field_validator('branch')
    @classmethod
    def validate_branch(cls, v):
        # Git branch name validation
        if not re.match(r'^[a-zA-Z0-9._/-]+$', v):
            raise ValueError('branch name contains invalid characters')
        return v


class TaskCRD(BaseModel):
    """Task CRD - Git worktree task"""
    apiVersion: str = Field("haconiwa.dev/v1", description="API version")
    kind: str = Field("Task", description="Resource kind")
    metadata: Metadata
    spec: TaskSpec


class PathScanSpec(BaseModel):
    """PathScan CRD specification"""
    include: List[str] = Field(..., description="Include patterns")
    exclude: List[str] = Field(default_factory=list, description="Exclude patterns")


class PathScanCRD(BaseModel):
    """PathScan CRD - File path scanning configuration"""
    apiVersion: str = Field("haconiwa.dev/v1", description="API version")
    kind: str = Field("PathScan", description="Resource kind")
    metadata: Metadata
    spec: PathScanSpec


class DatabaseSpec(BaseModel):
    """Database CRD specification"""
    dsn: str = Field(..., description="Database connection string")
    useSSL: bool = Field(False, description="Use SSL connection")


class DatabaseCRD(BaseModel):
    """Database CRD - Database connection configuration"""
    apiVersion: str = Field("haconiwa.dev/v1", description="API version")
    kind: str = Field("Database", description="Resource kind")
    metadata: Metadata
    spec: DatabaseSpec


class RolePolicy(BaseModel):
    """Role-specific policy"""
    allow: Dict[str, List[str]] = Field(default_factory=dict, description="Allowed commands")
    deny: Dict[str, List[str]] = Field(default_factory=dict, description="Denied commands")


class CommandPolicySpec(BaseModel):
    """CommandPolicy CRD specification"""
    global_commands: Dict[str, List[str]] = Field(
        default_factory=dict, 
        description="Global command whitelist",
        alias="global"
    )
    roles: Dict[str, RolePolicy] = Field(
        default_factory=dict, 
        description="Role-specific policies"
    )


class CommandPolicyCRD(BaseModel):
    """CommandPolicy CRD - Command execution policy"""
    apiVersion: str = Field("haconiwa.dev/v1", description="API version")
    kind: str = Field("CommandPolicy", description="Resource kind")
    metadata: Metadata
    spec: CommandPolicySpec
    
    model_config = ConfigDict(populate_by_name=True) 