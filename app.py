from flask import Flask, render_template, request, jsonify
import joblib
import re

app = Flask(__name__)

# Load the brain (the model we just trained)
try:
    model = joblib.load("phishing_model.pkl")
    print("✅ Model loaded successfully!")
except:
    print("❌ Error: 'phishing_model.pkl' not found. Run model_training.py first!")

# This function must match your training logic EXACTLY
def extract_features(message):
    msg = str(message).lower()
    
    # Feature 1: Length of message
    length = len(msg)
    
    # Feature 2: Does it have a link?
    has_link = 1 if re.search(r"https?://|www\.", msg) else 0
    
    # Feature 3: Does it have "scammy" words?
    scam_words = ["verify", "urgent", "account", "otp", "bank", "win", "free"]
    has_urgent = 1 if any(word in msg for word in scam_words) else 0
    
    # Feature 4: Number of Capital letters
    num_caps = sum(1 for c in str(message) if c.isupper())
    
    return [length, has_link, has_urgent, num_caps]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        user_message = data.get('message', '')

        # 1. Transform the input text into the 4 numbers the model expects
        features = [extract_features(user_message)]

        # 2. Ask the model for the result
        prediction_code = model.predict(features)[0]

        # 3. Convert 1/0 to human-readable text
        result = "🚨 Phishing Detected!" if prediction_code == 1 else "✅ Message is Safe."
        
        return jsonify({'prediction': result})
    
    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({'prediction': "Error processing request."})

if __name__ == '__main__':
    app.run(debug=True)