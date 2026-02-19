import pandas as pd

# This script creates a REAL small dataset since your current one is an HTML file
data = {
    'label': [0, 1, 0, 1, 0, 1, 0, 1],
    'message': [
        "Hey, are we still meeting for lunch?",
        "WINNER! You have won a 1000 gift card. Call now to claim.",
        "Can you send me the notes from today's class?",
        "URGENT: Your account is locked. Click here to verify: http://bit.ly/123",
        "Just checking in to see how you are doing.",
        "FREE entry into our weekly competition. Text WIN to 80085.",
        "I'll be there in 10 minutes.",
        "Bank Alert: Unusual activity detected. Please login at secure-verify.com"
    ]
}

df = pd.DataFrame(data)
df.to_csv("data/cleaned_dataset.csv", index=False)
print("✅ Success: Created a fresh, clean dataset from scratch!")
print("Now run: python feature_extraction.py")