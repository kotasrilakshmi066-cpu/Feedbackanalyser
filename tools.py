import pandas as pd

def load_feedback(filepath="feedback.csv"):
    df = pd.read_csv(filepath)
    return df["employee_feedback"].tolist()

def classify_feedback_by_theme(feedback_text: str) -> str:
    feedback_lower = feedback_text.lower()
    if any(word in feedback_lower for word in ["balance", "flexible", "weekend", "hours", "overworked", "pressure"]):
        return "work-life balance"
    elif any(word in feedback_lower for word in ["manager", "leadership", "micromanage", "management", "senior"]):
        return "management"
    elif any(word in feedback_lower for word in ["salary", "pay", "compensation", "bonus", "underpaid"]):
        return "compensation"
    elif any(word in feedback_lower for word in ["growth", "promotion", "training", "skill", "promoted"]):
        return "growth"
    else:
        return "culture"

def get_sentiment_score(feedback_text: str) -> str:
    positive_words = ["excellent", "great", "supportive", "valued", "positive",
                     "competitive", "approachable", "enjoyable", "abundant", "well"]
    negative_words = ["toxic", "unfair", "opaque", "micromanage", "underpaid",
                     "overworked", "non-existent", "unrealistic", "never", "no clear"]
    
    text_lower = feedback_text.lower()
    pos = sum(1 for w in positive_words if w in text_lower)
    neg = sum(1 for w in negative_words if w in text_lower)
    
    if pos > neg:
        return "positive"
    elif neg > pos:
        return "negative"
    else:
        return "neutral"