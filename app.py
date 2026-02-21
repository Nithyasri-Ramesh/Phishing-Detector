from flask import Flask, render_template, request
import joblib
import re

app = Flask(__name__)

# 1. LOAD THE MODEL
# Ensure your 'phishing_model.pkl' is in the same folder as this file
model = joblib.load('phishing_model.pkl')

def extract_features(text):
    """
    Converts raw text into the 4 numerical features your model expects.
    Make sure these match the order you used during training!
    """
    text_lower = text.lower()
    
    # Feature 1: Message Length
    length = len(text)
    
    # Feature 2: Has Links (Check for http, https, or .com/.net/.org)
    has_link = 1 if re.search(r'http|https|www|\.com|\.net|\.org', text_lower) else 0
    
    # Feature 3: Urgent Keywords Count
    # Add words that scammed you earlier to this list!
    urgent_words = ['urgent', 'suspended', 'verify', 'bank', 'blocked', 'action', 'restricted', 'login']
    urgent_count = sum(1 for word in urgent_words if word in text_lower)
    
    # Feature 4: Capitalization Ratio (Phishing often uses all caps)
    caps_count = sum(1 for char in text if char.isupper())
    caps_ratio = caps_count / length if length > 0 else 0
    
    return [length, has_link, urgent_count, caps_ratio]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        message = request.form['message']
        
        # --- MANUAL OVERRIDE (Safety Net) ---
        # If the message is obviously fake, we flag it even if the AI is unsure
        hard_flags = ['suspended', 'unauthorized access', 'account recovery']
        if any(flag in message.lower() for flag in hard_flags):
            return render_template('index.html', 
                                 prediction="🚨 Phishing Detected (High Risk)!", 
                                 message=message,
                                 color="red")

        # --- AI PREDICTION ---
        features = extract_features(message)
        
        # Get probabilities [Safe_Prob, Phishing_Prob]
        # This prevents the AI from being too "shy" about calling out a scam
        probabilities = model.predict_proba([features])[0]
        phishing_probability = probabilities[1] 

        # Sensitivity Threshold: 0.3 means if it's 30% sure, it flags it!
        threshold = 0.3 
        
        if phishing_probability >= threshold:
            prediction = "🚨 Phishing Detected!"
            color = "red"
        else:
            prediction = "✅ This message looks safe."
            color = "green"
            
        return render_template('index.html', 
                             prediction=prediction, 
                             message=message, 
                             color=color)

if __name__ == '__main__':
    app.run(debug=True)