"""
Data models for the Email Triage Environment.
Uses Pydantic for structure and validation.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class EmailCategory(str, Enum):
    """Email classification categories."""
    WORK = "work"
    PERSONAL = "personal"
    SPAM = "spam"
    NEWSLETTER = "newsletter"
    URGENT = "urgent"
    SUPPORT = "support"
    SALES = "sales"
    INTERNAL = "internal"


class Priority(str, Enum):
    """Email priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ActionType(str, Enum):
    """Available actions the agent can take."""
    CLASSIFY = "CLASSIFY"
    PRIORITIZE = "PRIORITIZE"
    REPLY_PLAN = "REPLY_PLAN"
    ESCALATE = "ESCALATE"
    ARCHIVE = "ARCHIVE"
    DEFER = "DEFER"
    DONE = "DONE"


class Email(BaseModel):
    """Represents an email in the inbox."""
    id: str = Field(..., description="Unique email identifier")
    sender: str = Field(..., description="Email sender address")
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Email body content")
    timestamp: str = Field(..., description="Email received timestamp")
    
    # Ground truth for grading
    ground_truth_category: Optional[EmailCategory] = Field(None, description="Correct category")
    ground_truth_priority: Optional[Priority] = Field(None, description="Correct priority")
    ground_truth_action: Optional[ActionType] = Field(None, description="Best action to take")
    
    # Agent's predictions
    predicted_category: Optional[EmailCategory] = Field(None, description="Agent's classification")
    predicted_priority: Optional[Priority] = Field(None, description="Agent's priority assignment")
    reply_plan: Optional[str] = Field(None, description="Agent's reply plan")
    
    # Status flags
    is_processed: bool = Field(default=False, description="Whether email has been processed")
    is_escalated: bool = Field(default=False, description="Whether email was escalated")
    is_archived: bool = Field(default=False, description="Whether email was archived")
    is_deferred: bool = Field(default=False, description="Whether email was deferred")


class Action(BaseModel):
    """An action taken by the agent."""
    action_type: ActionType = Field(..., description="Type of action")
    email_id: Optional[str] = Field(None, description="Target email ID")
    category: Optional[EmailCategory] = Field(None, description="Category for CLASSIFY action")
    priority: Optional[Priority] = Field(None, description="Priority for PRIORITIZE action")
    reply_plan: Optional[str] = Field(None, description="Reply plan for REPLY_PLAN action")
    reason: Optional[str] = Field(None, description="Reason for the action")


class Observation(BaseModel):
    """What the agent observes after an action."""
    emails: List[Email] = Field(default_factory=list, description="Current inbox state")
    processed_count: int = Field(default=0, description="Number of processed emails")
    total_count: int = Field(default=0, description="Total number of emails")
    current_task: str = Field(default="", description="Current task description")
    message: str = Field(default="", description="Feedback message")


class State(BaseModel):
    """Complete environment state."""
    task_id: str = Field(..., description="Current task identifier")
    observation: Observation = Field(..., description="Current observation")
    reward: float = Field(default=0.0, description="Accumulated reward")
    done: bool = Field(default=False, description="Whether episode is complete")
    info: Dict[str, Any] = Field(default_factory=dict, description="Additional information")


class StepRequest(BaseModel):
    """Request body for /step endpoint."""
    action: Action = Field(..., description="Action to execute")


class ResetRequest(BaseModel):
    """Request body for /reset endpoint."""
    task_id: str = Field(default="task1", description="Task to load")


class StepResponse(BaseModel):
    """Response from /step endpoint."""
    observation: Observation = Field(..., description="New observation")
    reward: float = Field(..., description="Reward for this step")
    done: bool = Field(..., description="Whether episode is complete")
    info: Dict[str, Any] = Field(default_factory=dict, description="Additional info")


class ResetResponse(BaseModel):
    """Response from /reset endpoint."""
    observation: Observation = Field(..., description="Initial observation")
    info: Dict[str, Any] = Field(default_factory=dict, description="Task info")
