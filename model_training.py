import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# 🟢 UPDATE THIS LINE: Add "data/" before the filename
try:
    df = pd.read_csv("data/features.csv") 
    
    # Split into features (X) and label (y)
    X = df.drop(columns=['label'])
    y = df['label']

    # Train the model
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)

    # Save the model to the main folder for app.py to find
    joblib.dump(model, "phishing_model.pkl")
    print("✅ SUCCESS: phishing_model.pkl has been created!")
    print("Now you can finally run: python app.py")

except Exception as e:
    print(f"❌ Error: {e}")