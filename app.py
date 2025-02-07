from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import io
from PIL import Image
import numpy as np

app = Flask(__name__)
CORS(app)

def analyze_image(image_data):
  
    try:
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        img_array = np.array(image)
        
        metrics = {
            'noise_level': np.std(img_array),  
            'avg_brightness': np.mean(img_array),  
            'edge_density': np.gradient(img_array)[0].std(), 
        }
        
     
        suspicious_markers = 0
        confidence = 0.5  
        
        if metrics['noise_level'] > 50: 
            suspicious_markers += 1
            confidence += 0.1
            
        if metrics['edge_density'] < 10:  
            suspicious_markers += 1
            confidence += 0.1
            
        if abs(metrics['avg_brightness'] - 128) > 50: 
            suspicious_markers += 1
            confidence += 0.1
            
        is_deepfake = suspicious_markers >= 2
        
        return {
            "is_deepfake": is_deepfake,
            "confidence": round(confidence, 2),
            "message": "Image analyzed successfully",
            "details": {
                "noise_level": round(float(metrics['noise_level']), 2),
                "brightness": round(float(metrics['avg_brightness']), 2),
                "edge_density": round(float(metrics['edge_density']), 2),
                "suspicious_markers": suspicious_markers
            }
        }
        
    except Exception as e:
        return {
            "error": f"Image analysis failed: {str(e)}",
            "is_deepfake": None,
            "confidence": 0,
        }

@app.route('/')
def home():
    return "Fake News & Deepfake Detection API is running!"

@app.route('/detect_fake_news', methods=['POST'])
def detect_fake_news():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Missing text data"}), 400
    
    text = data["text"]
    
    result = {"text": text, "is_fake": False, "confidence": 0.85}
    return jsonify(result)

@app.route('/upload_image', methods=['POST'])
def upload_image():
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"error": "No image data received"}), 400
        
        image_data = data['image'].split(',')[1]
        
        result = analyze_image(image_data)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)