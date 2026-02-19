import pandas as pd
import re

def extract_features(message):
    msg = str(message).lower()
    length = len(msg)
    has_link = 1 if re.search(r"https?://|www\.", msg) else 0
    scam_words = ["verify", "urgent", "account", "otp", "bank", "win", "free"]
    has_urgent = 1 if any(word in msg for word in scam_words) else 0
    num_caps = sum(1 for c in str(message) if c.isupper())
    return pd.Series([length, has_link, has_urgent, num_caps])

try:
    df = pd.read_csv("data/cleaned_dataset.csv")
    cols = ['length', 'has_link', 'has_urgent', 'num_caps']
    df[cols] = df['message'].apply(extract_features)
    
    # Drop the text message before saving for ML
    df.drop(columns=['message']).to_csv("data/features.csv", index=False)
    print("✅ Success: features.csv created in 'data' folder.")
except Exception as e:
    print(f"❌ Error: {e}. Did you run data_cleaning.py first?")