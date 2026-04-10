"""
Task Definitions & Graders for Email Triage Environment.

Tasks:
- Task 1 (Easy): Classify 5 simple emails
- Task 2 (Medium): Classify + prioritize 10 emails
- Task 3 (Hard): Handle 15 complex emails with full actions
"""

from typing import List, Callable, Dict, Any
from .models import Email, EmailCategory, Priority, ActionType


def create_email(
    id: str,
    sender: str,
    subject: str,
    body: str,
    timestamp: str,
    category: EmailCategory,
    priority: Priority,
    action: ActionType = None
) -> Email:
    """Helper to create an email with ground truth."""
    return Email(
        id=id,
        sender=sender,
        subject=subject,
        body=body,
        timestamp=timestamp,
        ground_truth_category=category,
        ground_truth_priority=priority,
        ground_truth_action=action
    )


# ============================================================================
# TASK 1: Easy - Classify 5 simple emails
# ============================================================================

TASK1_EMAILS = [
    create_email(
        id="email_001",
        sender="boss@company.com",
        subject="Q3 Report Review",
        body="Please review the attached Q3 report and provide your feedback by Friday. This is important for our board meeting.",
        timestamp="2024-01-15T09:00:00Z",
        category=EmailCategory.WORK,
        priority=Priority.HIGH
    ),
    create_email(
        id="email_002",
        sender="newsletter@techsite.com",
        subject="Weekly Tech Digest",
        body="Here's your weekly roundup of the latest tech news, gadget reviews, and industry insights. Click to read more.",
        timestamp="2024-01-15T08:30:00Z",
        category=EmailCategory.NEWSLETTER,
        priority=Priority.LOW
    ),
    create_email(
        id="email_003",
        sender="mom@family.net",
        subject="Dinner this Sunday?",
        body="Hi sweetie! Would you like to come over for dinner this Sunday? Dad is grilling steaks. Let me know!",
        timestamp="2024-01-15T10:15:00Z",
        category=EmailCategory.PERSONAL,
        priority=Priority.MEDIUM
    ),
    create_email(
        id="email_004",
        sender="prince@nigeria.spam",
        subject="YOU WON $1,000,000!!!",
        body="Congratulations! You have been selected to receive $1,000,000. Please send your bank details immediately.",
        timestamp="2024-01-15T07:00:00Z",
        category=EmailCategory.SPAM,
        priority=Priority.LOW
    ),
    create_email(
        id="email_005",
        sender="cto@company.com",
        subject="URGENT: Server Down",
        body="Our production server is down. Need all hands on deck immediately. Please join the emergency call.",
        timestamp="2024-01-15T11:00:00Z",
        category=EmailCategory.URGENT,
        priority=Priority.CRITICAL
    ),
]


def task1_grader(emails: List[Email]) -> float:
    """
    Grade Task 1: Classification accuracy.
    Score = correct classifications / total emails
    Returns score strictly between 0 and 1 (never exactly 0.0 or 1.0)
    """
    correct = 0
    for email in emails:
        if email.predicted_category == email.ground_truth_category:
            correct += 1
    
    if not emails:
        return 0.01  # Minimum score if no emails
    
    raw_score = correct / len(emails)
    # Ensure score is strictly between 0 and 1 (never exactly 0.0 or 1.0)
    # Map [0.0, 1.0] to (0.01, 0.99)
    return 0.01 + (raw_score * 0.98)


# ============================================================================
# TASK 2: Medium - Classify + Prioritize 10 emails
# ============================================================================

TASK2_EMAILS = TASK1_EMAILS + [
    create_email(
        id="email_006",
        sender="support@vendor.com",
        subject="Your support ticket #12345",
        body="Thank you for contacting us. We've received your ticket about the software bug. Our team will respond within 24 hours.",
        timestamp="2024-01-15T12:00:00Z",
        category=EmailCategory.SUPPORT,
        priority=Priority.MEDIUM
    ),
    create_email(
        id="email_007",
        sender="sales@softwareco.com",
        subject="Special offer: 50% off Enterprise Plan",
        body="For a limited time, get 50% off our Enterprise Plan. This offer expires in 48 hours. Don't miss out!",
        timestamp="2024-01-15T13:30:00Z",
        category=EmailCategory.SALES,
        priority=Priority.LOW
    ),
    create_email(
        id="email_008",
        sender="hr@company.com",
        subject="Updated PTO Policy",
        body="Please review the updated PTO policy attached. All employees must acknowledge receipt by end of week.",
        timestamp="2024-01-15T14:00:00Z",
        category=EmailCategory.INTERNAL,
        priority=Priority.MEDIUM
    ),
    create_email(
        id="email_009",
        sender="client@bigcorp.com",
        subject="Contract Renewal Discussion",
        body="We'd like to discuss renewing our contract. Can we schedule a call this week? Looking forward to continuing our partnership.",
        timestamp="2024-01-15T15:00:00Z",
        category=EmailCategory.WORK,
        priority=Priority.HIGH
    ),
    create_email(
        id="email_010",
        sender="friend@email.com",
        subject="Game night this Friday",
        body="Hey! We're having a game night this Friday at my place. Bring some snacks if you can make it!",
        timestamp="2024-01-15T16:00:00Z",
        category=EmailCategory.PERSONAL,
        priority=Priority.LOW
    ),
]


def task2_grader(emails: List[Email]) -> float:
    """
    Grade Task 2: Classification + Priority accuracy.
    Score = (correct classifications + correct priorities) / (2 * total emails)
    Returns score strictly between 0 and 1 (never exactly 0.0 or 1.0)
    """
    correct_category = 0
    correct_priority = 0
    
    for email in emails:
        if email.predicted_category == email.ground_truth_category:
            correct_category += 1
        if email.predicted_priority == email.ground_truth_priority:
            correct_priority += 1
    
    total_checks = len(emails) * 2
    
    if total_checks == 0:
        return 0.01  # Minimum score if no emails
    
    raw_score = (correct_category + correct_priority) / total_checks
    # Ensure score is strictly between 0 and 1 (never exactly 0.0 or 1.0)
    # Map [0.0, 1.0] to (0.01, 0.99)
    return 0.01 + (raw_score * 0.98)


# ============================================================================
# TASK 3: Hard - Handle 15 complex emails with full actions
# ============================================================================

TASK3_EMAILS = TASK2_EMAILS + [
    create_email(
        id="email_011",
        sender="security@bank.com",
        subject="Suspicious activity on your account",
        body="We detected unusual login attempts on your account. Please verify your recent transactions immediately.",
        timestamp="2024-01-15T17:00:00Z",
        category=EmailCategory.URGENT,
        priority=Priority.CRITICAL,
        action=ActionType.ESCALATE
    ),
    create_email(
        id="email_012",
        sender="promo@shopping.com",
        subject="Flash Sale: 80% OFF Everything!",
        body="Massive clearance sale starting now! 80% off all items. Limited stock available. Shop now!",
        timestamp="2024-01-15T18:00:00Z",
        category=EmailCategory.SPAM,
        priority=Priority.LOW,
        action=ActionType.ARCHIVE
    ),
    create_email(
        id="email_013",
        sender="ceo@company.com",
        subject="Strategic Planning Meeting",
        body="I'd like to schedule a strategic planning session for next quarter. Please review the attached documents before we meet.",
        timestamp="2024-01-15T19:00:00Z",
        category=EmailCategory.WORK,
        priority=Priority.HIGH,
        action=ActionType.DEFER
    ),
    create_email(
        id="email_014",
        sender="it@company.com",
        subject="Scheduled Maintenance Tonight",
        body="Systems will be down for maintenance tonight from 11 PM to 2 AM. Please save your work before then.",
        timestamp="2024-01-15T20:00:00Z",
        category=EmailCategory.INTERNAL,
        priority=Priority.MEDIUM,
        action=ActionType.ARCHIVE
    ),
    create_email(
        id="email_015",
        sender="angry.customer@email.com",
        subject="COMPLAINT: Terrible Service!!!",
        body="I am extremely dissatisfied with your service! I demand a full refund and an explanation. This is unacceptable!",
        timestamp="2024-01-15T21:00:00Z",
        category=EmailCategory.SUPPORT,
        priority=Priority.CRITICAL,
        action=ActionType.ESCALATE
    ),
]


def task3_grader(emails: List[Email]) -> float:
    """
    Grade Task 3: Full evaluation including classification, priority, and actions.
    Weighted scoring:
    - Classification: 40%
    - Priority: 30%
    - Correct action (for emails with ground_truth_action): 30%
    Returns score strictly between 0 and 1 (never exactly 0.0 or 1.0)
    """
    correct_category = 0
    correct_priority = 0
    correct_action = 0
    action_emails = 0
    
    for email in emails:
        if email.predicted_category == email.ground_truth_category:
            correct_category += 1
        if email.predicted_priority == email.ground_truth_priority:
            correct_priority += 1
        
        if email.ground_truth_action:
            action_emails += 1
            if email.ground_truth_action == ActionType.ESCALATE and email.is_escalated:
                correct_action += 1
            elif email.ground_truth_action == ActionType.ARCHIVE and email.is_archived:
                correct_action += 1
            elif email.ground_truth_action == ActionType.DEFER and email.is_deferred:
                correct_action += 1
    
    total_emails = len(emails)
    
    if total_emails == 0:
        return 0.01  # Minimum score if no emails
    
    category_score = correct_category / total_emails
    priority_score = correct_priority / total_emails
    action_score = correct_action / action_emails if action_emails > 0 else 0.5  # Neutral score if no actions
    
    # Weighted final score
    raw_score = (category_score * 0.4) + (priority_score * 0.3) + (action_score * 0.3)
    
    # Ensure score is strictly between 0 and 1 (never exactly 0.0 or 1.0)
    # Map [0.0, 1.0] to (0.01, 0.99)
    return 0.01 + (raw_score * 0.98)


# ============================================================================
# Task Registry
# ============================================================================

class Task:
    """Represents a task configuration."""
    def __init__(
        self,
        task_id: str,
        name: str,
        description: str,
        difficulty: str,
        emails: List[Email],
        grader: Callable[[List[Email]], float],
        max_steps: int = 100
    ):
        self.task_id = task_id
        self.name = name
        self.description = description
        self.difficulty = difficulty
        self.emails = emails
        self.grader = grader
        self.max_steps = max_steps
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "difficulty": self.difficulty,
            "email_count": len(self.emails),
            "max_steps": self.max_steps,
            "grader_enabled": self.grader is not None,
            "has_grader": self.grader is not None
        }


Task1 = Task(
    task_id="task1",
    name="Basic Email Classification",
    description="Classify 5 emails into the correct categories. Focus on identifying work, personal, spam, newsletter, and urgent emails.",
    difficulty="easy",
    emails=TASK1_EMAILS,
    grader=task1_grader,
    max_steps=50
)

Task2 = Task(
    task_id="task2",
    name="Classification and Prioritization",
    description="Classify 10 emails and assign appropriate priority levels (critical, high, medium, low) to each.",
    difficulty="medium",
    emails=TASK2_EMAILS,
    grader=task2_grader,
    max_steps=100
)

Task3 = Task(
    task_id="task3",
    name="Full Email Triage",
    description="Handle 15 complex emails: classify, prioritize, and decide whether to escalate, archive, or defer specific emails.",
    difficulty="hard",
    emails=TASK3_EMAILS,
    grader=task3_grader,
    max_steps=150
)

TASKS = {
    "task1": Task1,
    "task2": Task2,
    "task3": Task3,
}


def get_task(task_id: str) -> Task:
    """Get a task by ID."""
    if task_id not in TASKS:
        raise ValueError(f"Unknown task: {task_id}. Available: {list(TASKS.keys())}")
    return TASKS[task_id]


def list_tasks() -> List[Dict[str, Any]]:
    """List all available tasks."""
    return [task.to_dict() for task in TASKS.values()]
