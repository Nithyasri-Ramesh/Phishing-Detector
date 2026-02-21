from flask import Flask, render_template, request
import joblib
import re

app = Flask(__name__)

# 1. LOAD THE MODEL
try:
    model = joblib.load('phishing_model.pkl')
except:
    model = None

def extract_features(text):
    text_lower = text.lower()
    length = len(text)
    has_link = 1 if re.search(r'http|https|www|\.com|\.net|\.org', text_lower) else 0
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
    msg = message.lower()

    # --- THE "ULTIMATE" SCAM TRIGGER LIST ---
    # We add 'package', 'delivery', and 'fee' to catch your latest failing case
    scam_triggers = [
        'winner', 'won', 'gift card', 'prize', 'lottery', '$1000', '$5000',
        'work from home', 'no experience', 'make money', 'fast cash',
        'package delivery', 'pending fee', 'reschedule', 'pay $', 'delivery fee',
        'bitcoin', 'investment', 'claim', 'reply yes'
    ]
    
    # 1. Check Hard Flags
    if any(trigger in msg for trigger in scam_triggers):
        return render_template('index.html', 
                             prediction="🚨 Phishing/Scam Detected!", 
                             message=message, color="red")

    # 2. Check Allowlist
    trusted = ['google.com', 'github.com', 'microsoft.com', 'apple.com', 'appointment']
    if any(site in msg for site in trusted):
        return render_template('index.html', 
                             prediction="✅ Verified Safe", 
                             message=message, color="green")

    # 3. AI Prediction (Backup)
    if model:
        features = extract_features(message)
        phishing_prob = model.predict_proba([features])[0][1]
        if phishing_prob >= 0.40:
            return render_template('index.html', prediction="🚨 Phishing Detected!", message=message, color="red")

    return render_template('index.html', prediction="✅ This message looks safe.", message=message, color="green")

if __name__ == '__main__':
    app.run(debug=True)