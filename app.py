from flask import Flask, render_template, request
import joblib
import re

app = Flask(__name__)

# 1. LOAD THE MODEL
model = joblib.load('phishing_model.pkl')

def extract_features(text):
    text_lower = text.lower()
    length = len(text)
    has_link = 1 if re.search(r'http|https|www|\.com|\.net|\.org', text_lower) else 0
    
    # Check for urgency
    urgent_words = ['urgent', 'suspended', 'verify', 'bank', 'blocked', 'action', 'restricted']
    urgent_count = sum(1 for word in urgent_words if word in text_lower)
    
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

    # --- 1. HYBRID LAYER: SCAM TRIGGER WORDS ---
    scam_triggers = ['winner', 'won', 'gift card', 'claim', 'prize', 'lottery', '$1000']
    if any(trigger in message_clean for trigger in scam_triggers):
        return render_template('index.html', 
                             prediction="🚨 Phishing Detected (Scam Pattern)!", 
                             message=message, color="red")

    # --- 2. ALLOWLIST ---
    trusted = ['google.com', 'github.com', 'microsoft.com', 'apple.com']
    if any(site in message_clean for site in trusted):
        return render_template('index.html', 
                             prediction="✅ Verified Safe (Trusted Source)", 
                             message=message, color="green")

    # --- 3. AI PREDICTION ---
    features = extract_features(message)
    probabilities = model.predict_proba([features])[0]
    phishing_prob = probabilities[1] 

    # Balanced threshold for the demo
    threshold = 0.45 
    
    if phishing_prob >= threshold:
        prediction = "🚨 Phishing Detected!"
        color = "red"
    else:
        prediction = "✅ This message looks safe."
        color = "green"
        
    return render_template('index.html', prediction=prediction, message=message, color=color)

if __name__ == '__main__':
    app.run(debug=True)