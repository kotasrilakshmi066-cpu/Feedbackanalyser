from flask import Flask, request, jsonify
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

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"/>
<title>FeedbackAnalyser</title>
<style>
body{background:#0d0f14;color:#e8eaf0;font-family:sans-serif;max-width:800px;margin:0 auto;padding:2rem}
h1{color:#6ee7b7}
button{background:#6ee7b7;color:#0d0f14;padding:0.8rem 2rem;border:none;border-radius:8px;font-size:1rem;cursor:pointer;margin-top:1rem;width:100%}
.card{background:#161920;border:1px solid #252830;border-radius:12px;padding:1.5rem;margin-top:1.5rem}
.pill{display:inline-block;padding:0.3rem 0.8rem;border-radius:999px;margin:0.3rem;font-size:0.85rem}
.red{background:rgba(248,113,113,0.15);color:#f87171;border:1px solid rgba(248,113,113,0.3)}
.green{background:rgba(110,231,183,0.12);color:#6ee7b7;border:1px solid rgba(110,231,183,0.3)}
#results{display:none}
</style>
</head>
<body>
<h1>FeedbackAnalyser</h1>
<p style="color:#6b7280">HR Employee Feedback Intelligence</p>
<div class="card">
<p>Upload a CSV with <code>employee_feedback</code> column, or click Analyse to use default data.</p>
<input type="file" id="csvFile" accept=".csv" style="color:#e8eaf0;margin-top:1rem"/>
<button onclick="analyse()">Analyse Feedback</button>
</div>
<div id="results">
<div class="card"><h2>Total Responses: <span id="total" style="color:#6ee7b7"></span></h2></div>
<div class="card"><h3>Top Concerns</h3><div id="concerns"></div></div>
<div class="card"><h3>Top Positives</h3><div id="positives"></div></div>
<div class="card"><h3>Sentiment Scores</h3><div id="scores"></div></div>
</div>
<script>
async function analyse(){
  const formData=new FormData();
  const file=document.getElementById('csvFile').files[0];
  if(file)formData.append('file',file);
  const res=await fetch('/analyze',{method:'POST',body:formData});
  const data=await res.json();
  if(data.error){alert(data.error);return;}
  document.getElementById('total').textContent=data.total;
  document.getElementById('concerns').innerHTML=data.top_concerns.map(c=>`<span class="pill red">${c}</span>`).join('');
  document.getElementById('positives').innerHTML=data.top_positives.map(p=>`<span class="pill green">${p}</span>`).join('');
  document.getElementById('scores').innerHTML=Object.entries(data.sentiment_scores).map(([t,s])=>`<p>${t}: <strong style="color:${s>=0?'#6ee7b7':'#f87171'}">${s}%</strong></p>`).join('');
  document.getElementById('results').style.display='block';
}
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return HTML

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