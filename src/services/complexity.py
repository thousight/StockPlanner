import re
import textstat

ACTION_KEYWORDS = [r"\bBUY\b", r"\bSELL\b", r"\bTRADE\b", r"\bINVEST\b"]

def evaluate_complexity(text: str) -> float:
    """
    Evaluates the complexity of a given text.
    
    Returns a score between 0 and 100, where higher means more complex.
    - P0: Action keywords (BUY, SELL, TRADE, INVEST) set complexity to 100.
    - P1: Flesch Reading Ease is used to calculate linguistic complexity.
    """
    if not text:
        return 0.0

    # P0: Check for action keywords (force interrupt)
    for keyword in ACTION_KEYWORDS:
        if re.search(keyword, text, re.IGNORECASE):
            return 100.0

    # P1: Linguistic metrics
    # flesch_reading_ease returns a score between 0 and 100. 
    # 90-100: Very Easy
    # 0-30: Very Confusing/Hard
    flesch_score = textstat.flesch_reading_ease(text)
    
    # Normalize: we want higher score for harder text
    # Map 100 -> 0 and 0 -> 100
    complexity_score = max(0.0, min(100.0, 100.0 - flesch_score))
    
    return complexity_score

def requires_interrupt(complexity_score: float, threshold: float = 50.0) -> bool:
    """
    Determines if a report requires human interrupt based on complexity score.
    """
    return complexity_score >= threshold
