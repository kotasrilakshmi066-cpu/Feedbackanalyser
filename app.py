from flask import Flask, render_template, request, jsonify
import pandas as pd
import io
import os

app = Flask(__name__)

def classify_feedback_by_theme(feedback_text):
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

def get_sentiment_score(feedback_text):
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

def generate_report(feedbacks):
    results = []
    for feedback in feedbacks:
        theme = classify_feedback_by_theme(feedback)
        sentiment = get_sentiment_score(feedback)
        results.append({"feedback": feedback, "theme": theme, "sentiment": sentiment})
    results_df = pd.DataFrame(results)
    negative_counts = results_df[results_df["sentiment"] == "negative"]["theme"].value_counts()
    top_concerns = negative_counts.head(3).index.tolist()
    positive_counts = results_df[results_df["sentiment"] == "positive"]["theme"].value_counts()
    top_positives = positive_counts.head(3).index.tolist()
    sentiment_scores = {}
    for theme in results_df["theme"].unique():
        theme_data = results_df[results_df["theme"] == theme]
        pos = len(theme_data[theme_data["sentiment"] == "positive"])
        neg = len(theme_data[theme_data["sentiment"] == "negative"])
        score = round((pos - neg) / len(theme_data) * 100, 1)
        sentiment_scores[theme.title()] = score
    return {
        "total": len(feedbacks),
        "top_concerns": [c.title() for c in top_concerns],
        "top_positives": [p.title() for p in top_positives],
        "sentiment_scores": sentiment_scores,
        "results": results
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        if "file" in request.files and request.files["file"].filename:
            file = request.files["file"]
            df = pd.read_csv(io.StringIO(file.read().decode("utf-8")))
        else:
            df = pd.read_csv("feedback.csv")
        if "employee_feedback" not in df.columns:
            return jsonify({"error": "CSV must have a column named 'employee_feedback'"}), 400
        feedbacks = df["employee_feedback"].dropna().tolist()
        report = generate_report(feedbacks)
        return jsonify(report)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)