from flask import Flask, render_template, request
import joblib
import re

app = Flask(__name__)

# 1. LOAD THE MODEL
# Ensure 'phishing_model.pkl' is in your main project folder
try:
    model = joblib.load('phishing_model.pkl')
except:
    print("Warning: Model file not found. AI prediction will fail, but Hard Flags will still work.")

def extract_features(text):
    """Converts text into the 4 features the model expects."""
    text_lower = text.lower()
    length = len(text)
    
    # Feature 1: Has Links (check for common URL patterns)
    has_link = 1 if re.search(r'http|https|www|\.com|\.net|\.org', text_lower) else 0
    
    # Feature 2: Count of standard urgent keywords
    urgent_words = ['urgent', 'suspended', 'verify', 'bank', 'blocked', 'action', 'restricted']
    urgent_count = sum(1 for word in urgent_words if word in text_lower)
    
    # Feature 3: Capitalization Ratio (Detects 'shouting' text)
    caps_count = sum(1 for char in text if char.isupper())
    caps_ratio = caps_count / length if length > 0 else 0
    
    # Feature 4: Length (just the raw character count)
    return [length, has_link, urgent_count, caps_ratio]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        message = request.form['message']
        message_clean = message.lower()

        # --- STEP 1: HYBRID LAYER (Hard Flags for $5000/week, Winner, etc.) ---
        # This catches the scams that the AI model misses!
        scam_triggers = [
            'winner', 'won', 'gift card', 'prize', 'lottery', '$1000', 
            'work from home', '$5000', 'no experience', 'make money',
            'earn extra', 'fast cash', 'reply yes', 'investment', 'bitcoin'
        ]
        
        if any(trigger in message_clean for trigger in scam_triggers):
            return render_template('index.html', 
                                 prediction="🚨 Phishing/Scam Detected!", 
                                 message=message, color="red")

        # --- STEP 2: ALLOWLIST (Protects trusted sources from false alarms) ---
        trusted_sites = ['google.com', 'github.com', 'microsoft.com', 'apple.com', 'hospital', 'appointment']
        if any(site in message_clean for site in trusted_sites):
            return render_template('index.html', 
                                 prediction="✅ Verified Safe (Trusted Source)", 
                                 message=message, color="green")

        # --- STEP 3: AI PREDICTION ---
        try:
            features = extract_features(message)
            # Get probability: [Prob_Safe, Prob_Phishing]
            probabilities = model.predict_proba([features])[0]
            phishing_prob = probabilities[1] 

            # Threshold 0.45: Be moderately strict
            if phishing_prob >= 0.45:
                prediction = "🚨 Phishing Detected!"
                color = "red"
            else:
                prediction = "✅ This message looks safe."
                color = "green"
        except Exception as e:
            # Fallback if the AI fails
            prediction = "⚠️ Error in AI Analysis"
            color = "gray"

        return render_template('index.html', 
                             prediction=prediction, 
                             message=message, 
                             color=color)

if __name__ == '__main__':
    app.run(debug=True)