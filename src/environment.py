"""
Email Triage Environment Logic.
Core functions: reset(), step(action), state()
"""

from typing import Tuple, Dict, Any, List, Optional
from copy import deepcopy

from .models import (
    Email, EmailCategory, Priority, ActionType, Action,
    Observation, State
)


# Reward configuration
REWARDS = {
    "CLASSIFY_CORRECT": 0.02,
    "CLASSIFY_INCORRECT": -0.01,
    "PRIORITIZE_CORRECT": 0.02,
    "PRIORITIZE_INCORRECT": -0.01,
    "ESCALATE_CORRECT": 0.01,
    "ESCALATE_INCORRECT": -0.02,
    "ARCHIVE_CORRECT": 0.01,
    "ARCHIVE_INCORRECT": -0.02,
    "DEFER_CORRECT": 0.01,
    "DEFER_INCORRECT": -0.01,
    "REPLY_PLAN": 0.01,
    "INVALID_ACTION": -0.05,
    "DONE_BASE": 0.0,
}


class EmailTriageEnv:
    """
    Email Triage Environment.
    
    The agent interacts with a simulated inbox and performs actions like:
    - CLASSIFY: Assign category to email
    - PRIORITIZE: Assign priority level
    - REPLY_PLAN: Create a reply plan
    - ESCALATE: Escalate email to supervisor
    - ARCHIVE: Archive the email
    - DEFER: Defer processing for later
    - DONE: Signal completion
    """
    
    def __init__(self):
        self.emails: List[Email] = []
        self.task_id: str = ""
        self.task_description: str = ""
        self.accumulated_reward: float = 0.0
        self.done: bool = False
        self.step_count: int = 0
        self.max_steps: int = 100
        self.grader = None
    
    def reset(self, task_id: str, emails: List[Email], task_description: str = "", 
              grader=None, max_steps: int = 100) -> Observation:
        """
        Reset the environment with a new task.
        
        Args:
            task_id: Identifier for the task
            emails: List of emails to process
            task_description: Human-readable task description
            grader: Optional grader function for final scoring
            max_steps: Maximum allowed steps
            
        Returns:
            Initial observation
        """
        self.emails = deepcopy(emails)
        self.task_id = task_id
        self.task_description = task_description
        self.accumulated_reward = 0.0
        self.done = False
        self.step_count = 0
        self.max_steps = max_steps
        self.grader = grader
        
        return self._get_observation("Environment reset. Process the emails in your inbox.")
    
    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        """
        Execute an action in the environment.
        
        Args:
            action: The action to execute
            
        Returns:
            Tuple of (observation, reward, done, info)
        """
        if self.done:
            return (
                self._get_observation("Episode already complete."),
                0.0,
                True,
                {"error": "Episode already complete"}
            )
        
        self.step_count += 1
        reward = 0.0
        message = ""
        info: Dict[str, Any] = {"action": action.action_type.value}
        
        # Handle DONE action
        if action.action_type == ActionType.DONE:
            self.done = True
            final_score = self._calculate_final_score()
            reward = final_score
            self.accumulated_reward += reward
            message = f"Task complete. Final score: {final_score:.2f}"
            info["final_score"] = final_score
            return (
                self._get_observation(message),
                reward,
                True,
                info
            )
        
        # Validate email_id for email-specific actions
        if action.action_type != ActionType.DONE:
            email = self._find_email(action.email_id)
            if email is None:
                reward = REWARDS["INVALID_ACTION"]
                self.accumulated_reward += reward
                message = f"Invalid email ID: {action.email_id}"
                info["error"] = message
                return (
                    self._get_observation(message),
                    reward,
                    False,
                    info
                )
        
        # Execute action
        if action.action_type == ActionType.CLASSIFY:
            reward, message = self._handle_classify(email, action)
        elif action.action_type == ActionType.PRIORITIZE:
            reward, message = self._handle_prioritize(email, action)
        elif action.action_type == ActionType.REPLY_PLAN:
            reward, message = self._handle_reply_plan(email, action)
        elif action.action_type == ActionType.ESCALATE:
            reward, message = self._handle_escalate(email)
        elif action.action_type == ActionType.ARCHIVE:
            reward, message = self._handle_archive(email)
        elif action.action_type == ActionType.DEFER:
            reward, message = self._handle_defer(email)
        else:
            reward = REWARDS["INVALID_ACTION"]
            message = f"Unknown action type: {action.action_type}"
        
        self.accumulated_reward += reward
        info["step_reward"] = reward
        info["accumulated_reward"] = self.accumulated_reward
        
        # Check if max steps reached
        if self.step_count >= self.max_steps:
            self.done = True
            final_score = self._calculate_final_score()
            info["final_score"] = final_score
            message += f" Max steps reached. Final score: {final_score:.2f}"
            info["max_steps_reached"] = True
        
        return (
            self._get_observation(message),
            reward,
            self.done,
            info
        )
    
    def state(self) -> State:
        """
        Get the current environment state.
        
        Returns:
            Current state including observation, reward, and done status
        """
        return State(
            task_id=self.task_id,
            observation=self._get_observation("Current state"),
            reward=self.accumulated_reward,
            done=self.done,
            info={
                "step_count": self.step_count,
                "max_steps": self.max_steps,
                "processed_emails": sum(1 for e in self.emails if e.is_processed)
            }
        )
    
    def _get_observation(self, message: str) -> Observation:
        """Generate current observation."""
        # Only show unprocessed emails to agent (hide ground truth)
        visible_emails = []
        for email in self.emails:
            visible_email = Email(
                id=email.id,
                sender=email.sender,
                subject=email.subject,
                body=email.body,
                timestamp=email.timestamp,
                predicted_category=email.predicted_category,
                predicted_priority=email.predicted_priority,
                reply_plan=email.reply_plan,
                is_processed=email.is_processed,
                is_escalated=email.is_escalated,
                is_archived=email.is_archived,
                is_deferred=email.is_deferred,
            )
            visible_emails.append(visible_email)
        
        return Observation(
            emails=visible_emails,
            processed_count=sum(1 for e in self.emails if e.is_processed),
            total_count=len(self.emails),
            current_task=self.task_description,
            message=message
        )
    
    def _find_email(self, email_id: Optional[str]) -> Optional[Email]:
        """Find email by ID."""
        if email_id is None:
            return None
        for email in self.emails:
            if email.id == email_id:
                return email
        return None
    
    def _handle_classify(self, email: Email, action: Action) -> Tuple[float, str]:
        """Handle CLASSIFY action."""
        if action.category is None:
            return REWARDS["INVALID_ACTION"], "CLASSIFY requires a category"
        
        email.predicted_category = action.category
        
        if email.ground_truth_category and action.category == email.ground_truth_category:
            return REWARDS["CLASSIFY_CORRECT"], f"Correct! Email {email.id} classified as {action.category.value}"
        elif email.ground_truth_category:
            return REWARDS["CLASSIFY_INCORRECT"], f"Email {email.id} classified as {action.category.value}"
        else:
            return REWARDS["CLASSIFY_CORRECT"], f"Email {email.id} classified as {action.category.value}"
    
    def _handle_prioritize(self, email: Email, action: Action) -> Tuple[float, str]:
        """Handle PRIORITIZE action."""
        if action.priority is None:
            return REWARDS["INVALID_ACTION"], "PRIORITIZE requires a priority level"
        
        email.predicted_priority = action.priority
        
        if email.ground_truth_priority and action.priority == email.ground_truth_priority:
            return REWARDS["PRIORITIZE_CORRECT"], f"Correct! Email {email.id} prioritized as {action.priority.value}"
        elif email.ground_truth_priority:
            return REWARDS["PRIORITIZE_INCORRECT"], f"Email {email.id} prioritized as {action.priority.value}"
        else:
            return REWARDS["PRIORITIZE_CORRECT"], f"Email {email.id} prioritized as {action.priority.value}"
    
    def _handle_reply_plan(self, email: Email, action: Action) -> Tuple[float, str]:
        """Handle REPLY_PLAN action."""
        if not action.reply_plan:
            return REWARDS["INVALID_ACTION"], "REPLY_PLAN requires a reply plan"
        
        email.reply_plan = action.reply_plan
        return REWARDS["REPLY_PLAN"], f"Reply plan created for email {email.id}"
    
    def _handle_escalate(self, email: Email) -> Tuple[float, str]:
        """Handle ESCALATE action."""
        email.is_escalated = True
        email.is_processed = True
        
        if email.ground_truth_action == ActionType.ESCALATE:
            return REWARDS["ESCALATE_CORRECT"], f"Correct! Email {email.id} escalated"
        elif email.ground_truth_action:
            return REWARDS["ESCALATE_INCORRECT"], f"Email {email.id} escalated (may not be optimal)"
        else:
            return REWARDS["ESCALATE_CORRECT"], f"Email {email.id} escalated"
    
    def _handle_archive(self, email: Email) -> Tuple[float, str]:
        """Handle ARCHIVE action."""
        email.is_archived = True
        email.is_processed = True
        
        if email.ground_truth_action == ActionType.ARCHIVE:
            return REWARDS["ARCHIVE_CORRECT"], f"Correct! Email {email.id} archived"
        elif email.ground_truth_action:
            return REWARDS["ARCHIVE_INCORRECT"], f"Email {email.id} archived (may not be optimal)"
        else:
            return REWARDS["ARCHIVE_CORRECT"], f"Email {email.id} archived"
    
    def _handle_defer(self, email: Email) -> Tuple[float, str]:
        """Handle DEFER action."""
        email.is_deferred = True
        email.is_processed = True
        
        if email.ground_truth_action == ActionType.DEFER:
            return REWARDS["DEFER_CORRECT"], f"Email {email.id} deferred"
        elif email.ground_truth_action:
            return REWARDS["DEFER_INCORRECT"], f"Email {email.id} deferred (may not be optimal)"
        else:
            return REWARDS["DEFER_CORRECT"], f"Email {email.id} deferred"
    
    def _calculate_final_score(self) -> float:
        """
        Calculate final score based on agent's performance.
        Score = correct_predictions / total_emails
        """
        if self.grader:
            return self.grader(self.emails)
        
        # Default grading logic
        total_checks = 0
        correct_checks = 0
        
        for email in self.emails:
            # Check classification
            if email.ground_truth_category:
                total_checks += 1
                if email.predicted_category == email.ground_truth_category:
                    correct_checks += 1
            
            # Check priority
            if email.ground_truth_priority:
                total_checks += 1
                if email.predicted_priority == email.ground_truth_priority:
                    correct_checks += 1
            
            # Check action taken
            if email.ground_truth_action:
                total_checks += 1
                if email.ground_truth_action == ActionType.ESCALATE and email.is_escalated:
                    correct_checks += 1
                elif email.ground_truth_action == ActionType.ARCHIVE and email.is_archived:
                    correct_checks += 1
                elif email.ground_truth_action == ActionType.DEFER and email.is_deferred:
                    correct_checks += 1
        
        if total_checks == 0:
            return 0.99
        
        raw_score = correct_checks / total_checks
        return min(max(raw_score, 0.01), 0.99)
