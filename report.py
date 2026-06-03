import pandas as pd
from tools import classify_feedback_by_theme, get_sentiment_score

def generate_report(csv_path="feedback.csv"):
    df = pd.read_csv(csv_path)
    feedbacks = df["employee_feedback"].tolist()

    results = []
    for feedback in feedbacks:
        theme = classify_feedback_by_theme(feedback)
        sentiment = get_sentiment_score(feedback)
        results.append({
            "feedback": feedback,
            "theme": theme,
            "sentiment": sentiment
        })

    results_df = pd.DataFrame(results)

    # Count sentiments per theme
    theme_summary = results_df.groupby(["theme", "sentiment"]).size().unstack(fill_value=0)

    # Top 3 concerns (most negative themes)
    negative_counts = results_df[results_df["sentiment"] == "negative"]["theme"].value_counts()
    top_concerns = negative_counts.head(3).index.tolist()

    # Top 3 positives (most positive themes)
    positive_counts = results_df[results_df["sentiment"] == "positive"]["theme"].value_counts()
    top_positives = positive_counts.head(3).index.tolist()

    # Print Report
    print("\n" + "="*60)
    print("       HR FEEDBACK ANALYSIS REPORT")
    print("="*60)
    print(f"\n📊 Total Responses Analysed: {len(feedbacks)}")
    
    print("\n📁 THEME BREAKDOWN:")
    print(theme_summary.to_string())

    print("\n🔴 TOP 3 CONCERNS:")
    for i, concern in enumerate(top_concerns, 1):
        print(f"  {i}. {concern.title()}")

    print("\n🟢 TOP 3 POSITIVES:")
    for i, positive in enumerate(top_positives, 1):
        print(f"  {i}. {positive.title()}")

    print("\n💯 SENTIMENT SCORE PER THEME:")
    for theme in results_df["theme"].unique():
        theme_data = results_df[results_df["theme"] == theme]
        pos = len(theme_data[theme_data["sentiment"] == "positive"])
        neg = len(theme_data[theme_data["sentiment"] == "negative"])
        score = round((pos - neg) / len(theme_data) * 100, 1)
        print(f"  {theme.title()}: {score}% sentiment score")

    print("\n" + "="*60)
    return results_df
