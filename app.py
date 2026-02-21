from flask import Flask, render_template, request
import joblib
import re

app = Flask(__name__)

# 1. LOAD THE MODEL
# Ensure your 'phishing_model.pkl' is in your root folder
model = joblib.load('phishing_model.pkl')

def extract_features(text):
    """Converts text into the 4 features your model was trained on."""
    text_lower = text.lower()
    length = len(text)
    
    # Feature 2: Link detection
    has_link = 1 if re.search(r'http|https|www|\.com|\.net|\.org', text_lower) else 0
    
    # Feature 3: Urgent keywords
    urgent_words = ['urgent', 'suspended', 'verify', 'bank', 'blocked', 'action', 'restricted']
    urgent_count = sum(1 for word in urgent_words if word in text_lower)
    
    # Feature 4: Capitalization Ratio
    caps_count = sum(1 for char in text if char.isupper())
    caps_ratio = caps_count / length if length > 0 else 0
    
    return [length, has_link, urgent_count, caps_ratio]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    message = request.form['message']
    message_clean = message.lower()

    # --- 1. ALLOWLIST (Prevents False Positives) ---
    # If the message contains these, we immediately call it SAFE
    trusted_sources = ['google.com', 'microsoft.com', 'apple.com', 'github.com', 'linkedin.com']
    if any(site in message_clean for site in trusted_sources):
        return render_template('index.html', 
                             prediction="✅ Verified Safe (Trusted Source)", 
                             message=message, color="green")

    # --- 2. HARD FLAGS (Catches obvious scams) ---
    hard_flags = ['unauthorized login', 'account suspended', 'giveaway winner']
    if any(flag in message_clean for flag in hard_flags):
        return render_template('index.html', 
                             prediction="🚨 Phishing Detected (High Risk)!", 
                             message=message, color="red")

    # --- 3. AI PREDICTION WITH BALANCED THRESHOLD ---
    features = extract_features(message)
    probabilities = model.predict_proba([features])[0]
    phishing_prob = probabilities[1] 

    # We use 0.5 to balance precision (real messages) and recall (fake messages)
    threshold = 0.5 
    
    if phishing_prob >= threshold:
        prediction = "🚨 Phishing Detected!"
        color = "red"
    else:
        prediction = "✅ This message looks safe."
        color = "green"
        
    return render_template('index.html', prediction=prediction, message=message, color=color)

if __name__ == '__main__':
    app.run(debug=True)