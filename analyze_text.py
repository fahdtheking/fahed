from transformers import pipeline
import re

def analyze_text(text):
    # Sentiment & tone analysis
    sentiment_analyzer = pipeline("sentiment-analysis")
    sentiment = sentiment_analyzer(text)[0]
    
    # Simple fraud keyword/pattern matching
    fraud_keywords = ["fake", "scam", "fraud", "suspicious", "unverified", "counterfeit"]
    keyword_hits = [kw for kw in fraud_keywords if re.search(rf"\\b{kw}\\b", text, re.IGNORECASE)]
    
    # Consistency check (placeholder: can be expanded)
    consistency = "consistent" if len(text.split()) > 20 else "too short"
    
    # Trust score logic (simple example)
    trust_score = 100
    if sentiment['label'] == 'NEGATIVE':
        trust_score -= 30
    if keyword_hits:
        trust_score -= 40
    if consistency != "consistent":
        trust_score -= 20
    trust_score = max(0, trust_score)
    
    # Decision
    if trust_score >= 70:
        decision = "approve"
    elif trust_score >= 40:
        decision = "flag for review"
    else:
        decision = "reject"
    
    return {
        "sentiment": sentiment,
        "fraud_keywords": keyword_hits,
        "consistency": consistency,
        "trust_score": trust_score,
        "decision": decision
    }
