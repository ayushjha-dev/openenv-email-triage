"""
Test graders to verify they return scores strictly between 0 and 1.
"""

from src.tasks import task1_grader, task2_grader, task3_grader, TASK1_EMAILS, TASK2_EMAILS, TASK3_EMAILS
from copy import deepcopy

def test_grader_boundaries():
    """Test all graders return scores in valid range (0, 1) - excluding 0.0 and 1.0"""
    
    print("Testing Task 1 Grader...")
    print("=" * 60)
    
    # Test with perfect score
    emails_perfect = deepcopy(TASK1_EMAILS)
    for email in emails_perfect:
        email.predicted_category = email.ground_truth_category
    score = task1_grader(emails_perfect)
    print(f"Perfect score: {score:.4f}")
    assert 0 < score < 1, f"Score {score} not in range (0, 1)"
    assert score != 0.0 and score != 1.0, f"Score {score} is a boundary value"
    
    # Test with zero score
    emails_zero = deepcopy(TASK1_EMAILS)
    # Don't set predicted_category (will be None, won't match)
    score = task1_grader(emails_zero)
    print(f"Zero score: {score:.4f}")
    assert 0 < score < 1, f"Score {score} not in range (0, 1)"
    assert score != 0.0 and score != 1.0, f"Score {score} is a boundary value"
    
    # Test with partial score
    emails_partial = deepcopy(TASK1_EMAILS)
    for i, email in enumerate(emails_partial):
        if i < 3:  # 3 out of 5 correct = 60%
            email.predicted_category = email.ground_truth_category
    score = task1_grader(emails_partial)
    print(f"Partial score (3/5): {score:.4f}")
    assert 0 < score < 1, f"Score {score} not in range (0, 1)"
    
    print("\n✅ Task 1 grader passed all tests\n")
    
    print("Testing Task 2 Grader...")
    print("=" * 60)
    
    # Test with perfect score
    emails_perfect = deepcopy(TASK2_EMAILS)
    for email in emails_perfect:
        email.predicted_category = email.ground_truth_category
        email.predicted_priority = email.ground_truth_priority
    score = task2_grader(emails_perfect)
    print(f"Perfect score: {score:.4f}")
    assert 0 < score < 1, f"Score {score} not in range (0, 1)"
    assert score != 0.0 and score != 1.0, f"Score {score} is a boundary value"
    
    # Test with zero score
    emails_zero = deepcopy(TASK2_EMAILS)
    score = task2_grader(emails_zero)
    print(f"Zero score: {score:.4f}")
    assert 0 < score < 1, f"Score {score} not in range (0, 1)"
    assert score != 0.0 and score != 1.0, f"Score {score} is a boundary value"
    
    # Test with partial score
    emails_partial = deepcopy(TASK2_EMAILS)
    for i, email in enumerate(emails_partial):
        if i < 5:  # Half correct
            email.predicted_category = email.ground_truth_category
            email.predicted_priority = email.ground_truth_priority
    score = task2_grader(emails_partial)
    print(f"Partial score (5/10): {score:.4f}")
    assert 0 < score < 1, f"Score {score} not in range (0, 1)"
    
    print("\n✅ Task 2 grader passed all tests\n")
    
    print("Testing Task 3 Grader...")
    print("=" * 60)
    
    # Test with perfect score
    emails_perfect = deepcopy(TASK3_EMAILS)
    for email in emails_perfect:
        email.predicted_category = email.ground_truth_category
        email.predicted_priority = email.ground_truth_priority
        # Set actions for emails with ground_truth_action
        if email.ground_truth_action:
            from src.models import ActionType
            if email.ground_truth_action == ActionType.ESCALATE:
                email.is_escalated = True
            elif email.ground_truth_action == ActionType.ARCHIVE:
                email.is_archived = True
            elif email.ground_truth_action == ActionType.DEFER:
                email.is_deferred = True
    score = task3_grader(emails_perfect)
    print(f"Perfect score: {score:.4f}")
    assert 0 < score < 1, f"Score {score} not in range (0, 1)"
    assert score != 0.0 and score != 1.0, f"Score {score} is a boundary value"
    
    # Test with zero score
    emails_zero = deepcopy(TASK3_EMAILS)
    score = task3_grader(emails_zero)
    print(f"Zero score: {score:.4f}")
    assert 0 < score < 1, f"Score {score} not in range (0, 1)"
    assert score != 0.0 and score != 1.0, f"Score {score} is a boundary value"
    
    # Test with partial score
    emails_partial = deepcopy(TASK3_EMAILS)
    for i, email in enumerate(emails_partial):
        if i < 8:  # About half
            email.predicted_category = email.ground_truth_category
            email.predicted_priority = email.ground_truth_priority
    score = task3_grader(emails_partial)
    print(f"Partial score (8/15): {score:.4f}")
    assert 0 < score < 1, f"Score {score} not in range (0, 1)"
    
    print("\n✅ Task 3 grader passed all tests\n")
    
    print("=" * 60)
    print("🎉 ALL GRADERS PASS - Scores are strictly between 0 and 1")
    print("=" * 60)

if __name__ == "__main__":
    test_grader_boundaries()
