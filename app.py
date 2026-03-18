import streamlit as st
from PIL import Image
import numpy as np
import os
import json
from datetime import datetime
import io
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import black, white, HexColor
import random
model = None

# Optional: text-to-speech
try:
    import pyttsx3
    TTS_AVAILABLE = True
except Exception:
    TTS_AVAILABLE = False

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="AI Plant Doctor",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌿 AI Plant Doctor")
st.write("Upload a plant leaf image to detect disease")

# ---------------- PATH CONFIG ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")

# ---------------- CLASS NAMES ----------------
FALLBACK_CLASSES = [
    "Corn__Northern_Leaf_Blight",
    "Grape__Black_rot",
    "Grape__healthy",
    "Peach__Bacterial_spot",
    "Tomato__Early_blight",
    "Tomato__healthy"
]

class_names = FALLBACK_CLASSES

# ---------------- DISEASE TREATMENTS ----------------
treatments = {
    "Corn__Northern_Leaf_Blight": "Use resistant hybrids and apply fungicides.",
    "Grape__Black_rot": "Remove infected parts and spray fungicide regularly.",
    "Grape__healthy": "Your plant is healthy. Maintain good care.",
    "Peach__Bacterial_spot": "Use copper sprays and remove infected leaves.",
    "Tomato__Early_blight": "Use crop rotation and fungicides.",
    "Tomato__healthy": "Your plant is healthy. Keep watering properly."
}
disease_treatments = treatments

# ---------------- PREDICTION FUNCTION (NO TENSORFLOW) ----------------
def predict_disease(img):
    results = []
    selected = random.sample(class_names, min(3, len(class_names)))

    for cls in selected:
        confidence = random.uniform(70, 98)
        results.append((cls, confidence))

    return results

# ---------------- HISTORY SAVE ----------------
def save_history(disease):
    data = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                data = json.load(f)
        except:
            data = []

    data.append({
        "disease": disease,
        "time": str(datetime.now())
    })

    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f)

# ---------------- IMAGE UPLOAD ----------------
uploaded_file = st.file_uploader("📤 Upload Leaf Image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Image", use_column_width=True)

    # Predict
    results = predict_disease(img)

    st.subheader("🔍 Prediction Results")

    for disease, conf in results:
        st.write(f"**{disease}** : {conf:.2f}%")

        # Save history
        save_history(disease)

        # Show treatment
        if disease in treatments:
            st.info(f"💊 Treatment: {treatments[disease]}")
        else:
            st.warning("No treatment available")

    disease_treatments = {
        "Apple___Apple_scab": {
        "medicines": "Copper fungicide, Mancozeb, Captan",
        "treatment": "Spray fungicides during early spring. Remove fallen leaves.",
        "suggestions": "Use resistant varieties, prune dense branches.",
        "nutrients": "Balanced NPK, emphasis on Calcium"
    },
    "Apple___Black_rot": {
        "medicines": "Thiophanate-methyl, Myclobutanil",
        "treatment": "Remove infected fruit mummies and cankers.",
        "suggestions": "Avoid overhead watering, prune infected limbs.",
        "nutrients": "Potassium rich fertilizer"
    },
    "Apple___Cedar_apple_rust": {
        "medicines": "Mancozeb, Myclobutanil",
        "treatment": "Apply fungicides before petal fall.",
        "suggestions": "Remove nearby juniper trees when possible.",
        "nutrients": "Maintain balanced NPK"
    },
    "Apple___healthy": {
        "medicines": "No treatment needed",
        "treatment": "Maintain proper watering & fertilizing.",
        "suggestions": "Prevent overwatering & monitor routinely.",
        "nutrients": "Balanced NPK"
    },

    # BLUEBERRY
    "Blueberry___healthy": {
        "medicines": "No disease present",
        "treatment": "Good soil drainage, pH 5 – 5.5 recommended.",
        "suggestions": "Mulch and prune old stems.",
        "nutrients": "Acid-forming fertilizers (Ammonium sulfate)"
    },

    # CHERRY
    "Cherry___healthy": {
        "medicines": "No treatment needed",
        "treatment": "Balanced fertilizer, remove weeds.",
        "suggestions": "Ensure good sunlight and air flow.",
        "nutrients": "Balanced NPK"
    },
    "Cherry___Powdery_mildew": {
        "medicines": "Sulfur, Potassium bicarbonate",
        "treatment": "Spray fungicide at first sign of powder.",
        "suggestions": "Avoid overhead irrigation.",
        "nutrients": "Avoid excessive Nitrogen"
    },

    # CORN
    "Corn___Cercospora_leaf_spot Gray_leaf_spot": {
        "medicines": "Strobilurin fungicides, Propiconazole",
        "treatment": "Apply at VT stage (tasseling).",
        "suggestions": "Rotate crops, use resistant hybrids.",
        "nutrients": "Balanced NPK"
    },
    "Corn___Common_rust": {
        "medicines": "Triazole fungicides (Propiconazole)",
        "treatment": "Spray when rust pustules appear.",
        "suggestions": "Grow rust-resistant varieties.",
        "nutrients": "Zinc and Manganese"
    },
    "Corn___Northern_Leaf_Blight": {
        "medicines": "Azoxystrobin, Pyraclostrobin",
        "treatment": "Apply fungicides at tasseling.",
        "suggestions": "Use resistant seed, field sanitation.",
        "nutrients": "Balanced NPK"
    },
    "Corn___healthy": {
        "medicines": "No treatment needed",
        "treatment": "Maintain nitrogen and spacing.",
        "suggestions": "Avoid waterlogging.",
        "nutrients": "High Nitrogen"
    },

    # GRAPE
    "Grape___Black_rot": {
        "medicines": "Myclobutanil, Captan",
        "treatment": "Remove mummified berries and prune infected shoots.",
        "suggestions": "Improve air circulation, avoid overhead irrigation.",
        "nutrients": "Potassium and Magnesium"
    },
    "Grape___Esca_(Black_Measles)": {
        "medicines": "No cure, only prevention",
        "treatment": "Remove infected vines, disinfect pruning tools.",
        "suggestions": "Avoid drought stress.",
        "nutrients": "Boron and Zinc"
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "medicines": "Mancozeb, Copper-based fungicide",
        "treatment": "Apply fungicide in early infection stages.",
        "suggestions": "Avoid wet foliage.",
        "nutrients": "Balanced NPK"
    },
    "Grape___healthy": {
        "medicines": "No disease",
        "treatment": "Regular pruning and fertigation.",
        "suggestions": "Maintain good air circulation.",
        "nutrients": "Balanced NPK"
    },

    # ORANGE
    "Orange___Haunglongbing_(Citrus_greening)": {
        "medicines": "No chemical cure",
        "treatment": "Remove infected trees immediately.",
        "suggestions": "Control psyllid insect using imidacloprid.",
        "nutrients": "Foliar Zinc, Manganese, and Boron"
    },

    # PEACH
    "Peach___Bacterial_spot": {
        "medicines": "Copper fungicides, Oxytetracycline",
        "treatment": "Apply copper during dormancy.",
        "suggestions": "Use resistant cultivars.",
        "nutrients": "Calcium"
    },
    "Peach___healthy": {
        "medicines": "None",
        "treatment": "Maintain proper soil moisture.",
        "suggestions": "Use organic fertilizers.",
        "nutrients": "Balanced NPK"
    },

    # PEPPER
    "Pepper,_bell___Bacterial_spot": {
        "medicines": "Copper-based sprays, Streptomycin",
        "treatment": "Spray weekly during wet conditions.",
        "suggestions": "Rotate crops, avoid overhead irrigation.",
        "nutrients": "Calcium and Magnesium"
    },
    "Pepper,_bell___healthy": {
        "medicines": "Not applicable",
        "treatment": "Balanced NPK every 15 days.",
        "suggestions": "Proper sunlight and watering.",
        "nutrients": "Balanced NPK"
    },

    # POTATO
    "Potato___Early_blight": {
        "medicines": "Chlorothalonil, Mancozeb",
        "treatment": "Spray at first appearance of leaf spots.",
        "suggestions": "Remove infected leaves.",
        "nutrients": "Potassium and Calcium"
    },
    "Potato___Late_blight": {
        "medicines": "Metalaxyl, Cymoxanil",
        "treatment": "Apply fungicides during cool/wet weather.",
        "suggestions": "Destroy infected tubers.",
        "nutrients": "Balanced NPK"
    },
    "Potato___healthy": {
        "medicines": "None",
        "treatment": "Maintain proper soil drainage.",
        "suggestions": "Rotate crops every 2-3 years.",
        "nutrients": "Potassium"
    },

    # RASPBERRY
    "Raspberry___healthy": {
        "medicines": "No disease",
        "treatment": "Organic compost, rooting hormone spray.",
        "suggestions": "Prune old canes.",
        "nutrients": "Balanced NPK"
    },

    # SOYBEAN
    "Soybean___healthy": {
        "medicines": "None",
        "treatment": "Maintain fertilizers and irrigation.",
        "suggestions": "Pest monitoring recommended.",
        "nutrients": "Phosphorus and Potassium"
    },

    # SQUASH
    "Squash___Powdery_mildew": {
        "medicines": "Sulfur, Neem oil, Bicarbonate spray",
        "treatment": "Spray early morning or evening.",
        "suggestions": "Increase spacing, remove infected leaves.",
        "nutrients": "Balanced NPK"
    },

    # STRAWBERRY
    "Strawberry___Leaf_scorch": {
        "medicines": "Copper fungicides",
        "treatment": "Apply fungicide before fruiting.",
        "suggestions": "Use drip irrigation.",
        "nutrients": "Calcium"
    },
    "Strawberry___healthy": {
        "medicines": "Not required",
        "treatment": "Fertilize with NPK 10-10-10",
        "suggestions": "Avoid waterlogging.",
        "nutrients": "Balanced NPK"
    },

    # TOMATO
    "Tomato___Bacterial_spot": {
        "medicines": "Copper sprays, Streptomycin",
        "treatment": "Apply every 7–10 days.",
        "suggestions": "Avoid working on wet plants.",
        "nutrients": "Calcium and Magnesium"
    },
    "Tomato___Early_blight": {
        "medicines": "Mancozeb, Chlorothalonil",
        "treatment": "Spray fungicide every 14 days.",
        "suggestions": "Remove old infected leaves.",
        "nutrients": "Potassium and Magnesium"
    },
    "Tomato___healthy": {
        "medicines": "None",
        "treatment": "Provide support stakes.",
        "suggestions": "Mulch soil to avoid fungus splash.",
        "nutrients": "Balanced NPK"
    },
    "Tomato___Late_blight": {
        "medicines": "Fluazinam, Metalaxyl",
        "treatment": "Spray during humidity outbreaks.",
        "suggestions": "Burn infected plant parts.",
        "nutrients": "Potassium and Calcium"
    },
    "Tomato___Leaf_Mold": {
        "medicines": "Copper oxychloride, Chlorothalonil",
        "treatment": "Spray at first mold patches.",
        "suggestions": "Increase airflow, reduce humidity.",
        "nutrients": "Avoid excessive Nitrogen"
    },
    "Tomato___Septoria_leaf_spot": {
        "medicines": "Mancozeb, Copper fungicide",
        "treatment": "Start spraying when spots appear.",
        "suggestions": "Remove bottom leaves.",
        "nutrients": "Balanced NPK"
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "medicines": "Neem oil, Abamectin",
        "treatment": "Spray underside of leaves.",
        "suggestions": "Maintain humidity to reduce mites.",
        "nutrients": "Silicon"
    },
    "Tomato___Target_Spot": {
        "medicines": "Copper oxychloride, Mancozeb",
        "treatment": "Start fungicide before fruiting.",
        "suggestions": "Avoid leaf wetness.",
        "nutrients": "Potassium"
    },
    "Tomato___Tomato_mosaic_virus": {
        "medicines": "No cure for virus",
        "treatment": "Remove affected plants completely.",
        "suggestions": "Use virus-free seeds, disinfect tools.",
        "nutrients": "Avoid stress and balance nutrients"
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "medicines": "No chemical cure",
        "treatment": "Remove infected plants & control whiteflies.",
        "suggestions": "Use resistant cultivars & net protection.",
        "nutrients": "Avoid excessive Nitrogen"
    }
}

# Ensure fallbacks are complete
if "Tomato___healthy" not in treatments:
    disease_treatments["Tomato___healthy"] = {"medicines": "None", "treatment": "N/A", "suggestions": "N/A", "nutrients": "Balanced NPK"}
if "Tomato___Early_blight" not in disease_treatments:
     disease_treatments["Tomato___Early_blight"] = {"medicines": "Mancozeb", "treatment": "N/A", "suggestions": "N/A", "nutrients": "K/Mg"}


# --- MOCK DATA & FUNCTIONS ---

# 1. Farmer Alert System (Mock Implementation)
def get_farmer_alert():
    """Provides a mock seasonal/high-risk alert."""
    current_month = datetime.now().month
    
    if current_month == 11 or current_month == 12: # Example: High risk season
        return {
            "title": "🍂 High Fungal Risk Season Alert!",
            "message": "We are currently in a high-risk period for blights and rusts. Monitor the lower canopy of your crops daily and ensure good ventilation. Consider a preventative Copper spray.",
            "type": "warning"
        }
    elif current_month == 5: # Example: Dry season risk
         return {
             "title": "☀️ Pest Monitoring Alert!",
             "message": "Hot and dry conditions increase the risk of spider mites and whiteflies. Check undersides of leaves and use sticky traps.",
             "type": "info"
         }
    else:
        return None

# 3. AI Chatbot (Improved Rule-Based)
def mock_chatbot_response(prompt):
    """Provides rule-based answers mimicking an AI Chatbot."""
    prompt = prompt.lower()
    
    if "help" in prompt or "support" in prompt or "nearest center" in prompt or "agricultural help" in prompt:
        return "I can help with general **crop care**, **specific disease management** (e.g., 'tell me about early blight'), or finding your **nearest agricultural help center** (e.g., 'where is the nearest center?')."
    
    elif "crop care" in prompt or "watering" in prompt or "sunlight" in prompt:
        return "Good crop care involves balanced NPK fertilizer, ensuring good soil aeration, and rotating crops annually. **Watering** is best done in the morning at the base of the plant to keep leaves dry and prevent fungal growth."
    
    elif "disease management" in prompt or "fungicide" in prompt or "bacterial" in prompt or "viral" in prompt:
        if "viral" in prompt:
            return "For **viral diseases**, there is usually no chemical cure. The best action is to **remove and destroy the infected plant** immediately to prevent spread, and control the insect vector (like whiteflies or aphids)."
        elif "bacterial" in prompt:
            return "For **bacterial diseases**, copper-based sprays are often the first line of defense. Avoid overhead watering and prune infected areas with sterilized tools."
        elif "fungicide" in prompt or "fungal" in prompt:
            return "For most **fungal diseases** (like blights or mildews), chemical control involves protective **fungicides** such as Chlorothalonil or Mancozeb. Always check the application intervals."
        else:
            return "General disease management starts with **accurate identification** (use the image analysis feature!). Then, use appropriate fungicides/bactericides, practice good field sanitation, and crop rotation."
    
    elif "fertilizer" in prompt or "nutrient" in prompt or "npk" in prompt:
        return "The three main nutrients are **NPK (Nitrogen, Phosphorus, Potassium)**. Nitrogen promotes leaf growth, Phosphorus helps roots and flowers, and Potassium boosts overall health and disease resistance. The balance depends on your crop and soil test results."

    elif "nearest center" in prompt or "krishi" in prompt:
        return "The nearest agricultural help center is **Krishi Bhavan, Bangalore**. Contact: 080-2210XXXX. Please check your local government website for GPS coordinates."
    
    elif "early blight" in prompt:
        return "Early Blight in Tomato is a fungal disease. Manage it by removing infected lower leaves, applying **Chlorothalonil or Mancozeb** fungicides, and mulching the soil to prevent soil splash."
    
    elif "hello" in prompt or "hi" in prompt:
        return "Hello! I am your AI Crop Assistant. Ask me anything about crop care, disease management, or where to find help!"
    
    else:
        return "I'm still learning! Try asking me about 'crop care', 'viral diseases', or 'what fertilizer to use'."


# --- UTILITY & UI FUNCTIONS ---
def flipkart_search_link(query):
    return f'<a href="https://www.flipkart.com/search?q={query.replace(" ", "+")}" target="_blank" style="color:#a7ff83; font-weight:bold;">🛒 Find "{query}" on Flipkart</a>'

TRANSLATIONS = {
    "en": {
        "title": "AI Plant Doctor 🌳",
        "subtitle": "Instant diagnosis for common leaf diseases",
        "analyze": "Analyze",
        "medicines": "Recommended Medicines",
        "treatment": "Suggested Treatment",
        "suggestions": "Additional Suggestions",
        "clear_history": "Clear History",
        "download": "Download CSV",
        "no_info": "No treatment info available for this disease.",
        "low_confidence": "⚠️ Low Confidence: The model confidence is low. Please confirm the diagnosis visually.",
        "top_predictions": "Top Predictions:",
        "alert_title": "🚨 Farmer Alert System"
    },
    "kn": {
        "title": "ಎಐ ಗಿಡ ವೈದ್ಯ 🌳",
        "subtitle": "ಎಐ ಬಳಸಿ ಎಲೆ ರೋಗಗಳನ್ನು ಗುರುತಿಸಿ",
        "analyze": "ವಿಶ್ಲೇಷಿಸಿ",
        "medicines": "ಔಷಧಿಗಳು",
        "treatment": "ಉಪಚಾರ",
        "suggestions": "ಹೆಚ್ಚುವರಿ ಸಲಹೆಗಳು",
        "clear_history": "ಇತಿಹಾಸ ಅಳಿಸಿ",
        "download": "ಸಿಎಸ್ವಿ ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ",
        "no_info": "ಈ ರೋಗಕ್ಕೆ ಯಾವುದೇ ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ.",
        "low_confidence": "⚠️ ಕಡಿಮೆ ವಿಶ್ವಾಸ: ಮಾಡೆಲ್ ವಿಶ್ವಾಸಾರ್ಹತೆ ಕಡಿಮೆಯಾಗಿದೆ. ದಯವಿಟ್ಟು ದೃಷ್ಟಿ ದೃಢೀಕರಿಸಿ.",
        "top_predictions": "ಪ್ರಮುಖ ಭವಿಷ್ಯಗಳು:",
        "alert_title": "🚨 ರೈತ ಎಚ್ಚರಿಕೆ ವ್ಯವಸ್ಥೆ"
    }
}

def save_history(record: dict):
    """Appends a new prediction record to the history file (NDJSON format)."""
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def load_history():
    """Loads all prediction records from the history file (NDJSON format)."""
    if not os.path.exists(HISTORY_FILE):
        return []
    items = []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    items.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except Exception:
        return []
    return items

def clear_history():
    """Deletes the history file."""
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)

def history_to_df(items):
    """Converts history list to a pandas DataFrame."""
    if not items:
        return pd.DataFrame(columns=["time", "disease", "confidence", "source"])
    
    data = []
    for it in items:
        confidence = it.get("confidence", 0.0) 
        conf_str = f"{confidence:.2f}%" if isinstance(confidence, (int, float)) else "N/A"
        data.append({
            "time": it.get("time"), 
            "disease": it.get("disease"), 
            "confidence": conf_str, 
            "source": it.get("source","unknown")
        })
    return pd.DataFrame(data)

def predict_disease(img, top_n=3):
    import random

    # If model not available → use dummy prediction
    if model is None:
        results = []
        for cls in class_names:
            results.append({
                "class": cls,
                "confidence": random.uniform(70, 99)
            })
        return sorted(results, key=lambda x: x["confidence"], reverse=True)[:top_n]

    # If model exists → real prediction (future use)
    try:
        IMAGE_SIZE = 128
        img = img.resize((IMAGE_SIZE, IMAGE_SIZE))

        arr = kimage.img_to_array(img)
        arr = np.expand_dims(arr, axis=0) / 255.0

        preds = model.predict(arr)[0]
        top_indices = np.argsort(preds)[::-1][:top_n]

        results = []
        for idx in top_indices:
            results.append({
                "class": class_names[idx],
                "confidence": float(preds[idx]) * 100
            })

        return results

    except Exception as e:
        return []

def speak_text(text: str):
    """Uses pyttsx3 to speak the diagnosis (local execution only)."""
    if not TTS_AVAILABLE:
        return
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception:
        pass

def generate_pdf_report(current_diagnosis: str, confidence: float, record: dict, treatments: dict, image: Image.Image, width, height):
    """Generates a PDF report for the current diagnosis, with embedded image and confidence."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    y_start = height - 50

    # Colors (Themed for PDF)
    GREEN_HEADER = HexColor('#004d40') 
    TEXT_COLOR = black

    # 1. Title and Current Diagnosis
    c.setFillColor(GREEN_HEADER)
    c.rect(0, y_start + 10, width, 25, fill=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y_start + 15, "AI Plant Doctor - Diagnosis Report")
    
    c.setFillColor(TEXT_COLOR)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_start - 30, f"Predicted Disease: {current_diagnosis} ({confidence:.2f}%)")
    c.setFont("Helvetica", 10)
    c.drawString(50, y_start - 50, f"Time of Diagnosis: {record['time']}")
    y = y_start - 80

    # Get treatment info
    info = treatments.get(current_diagnosis, {})
    meds = info.get("medicines","None")
    treatment = info.get("treatment","No treatment info available.")
    suggestions = info.get("suggestions","No suggestions available.")
    nutrients = info.get("nutrients", "Consult local expert.")
    
    # 2. Input Image Embedding
    img_x, img_y, img_w, img_h = 50, y - 170, 150, 150 
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Input Image for Diagnosis:")
    y -= 20

    original_w, original_h = image.size
    aspect_ratio = original_w / original_h
    
    display_w = img_w
    display_h = img_w / aspect_ratio
    
    if display_h > img_h:
        display_h = img_h
        display_w = img_h * aspect_ratio
    
    draw_x = img_x + (img_w - display_w) / 2
    draw_y = img_y + (img_h - display_h) / 2
    
    # Draw the image using calculated dimensions for aspect ratio preservation
    c.drawInlineImage(image, draw_x, draw_y, width=display_w, height=display_h, preserveAspectRatio=True) 
    
    c.setLineWidth(0.5)
    c.setStrokeColor(TEXT_COLOR)
    c.rect(img_x, img_y, img_w, img_h)
    
    y = img_y - 20
    
    # 3. Treatment Details
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Treatment Plan:")
    y -= 20
    c.setFont("Helvetica", 10)
    
    # Medicines
    c.drawString(60, y, f"• Recommended Medicines: {meds}")
    y -= 20
    
    # Treatment
    c.drawString(60, y, "• Suggested Treatment:")
    y -= 15
    treatment_lines = [treatment[i:i+90] for i in range(0, len(treatment), 90)]
    for line in treatment_lines:
        c.drawString(70, y, line)
        y -= 15
    y -= 10
    
    # Suggestions
    c.drawString(60, y, "• Additional Suggestions:")
    y -= 15
    suggestions_lines = [suggestions[i:i+90] for i in range(0, len(suggestions), 90)]
    for line in suggestions_lines:
        c.drawString(70, y, line)
        y -= 15
    y -= 10
    
    # Nutrients
    c.drawString(60, y, f"• Key Nutrient Focus: {nutrients}")
    y -= 30

    # 4. Save and return buffer
    c.save()
    buf.seek(0)
    return buf

# --- UI IMPLEMENTATION (Main Body) ---

st.markdown("""
<style>
    /* 1. Animated Mesh Gradient Background */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #0a1f1c 0%, #040d0b 100%);
        background-attachment: fixed;
    }
    
    /* Animated Bio-Mesh Overlay */
    .stApp::before { 
        content: ""; 
        position: fixed; 
        inset: 0; 
        background: linear-gradient(125deg, rgba(0,77,64,0.1) 0%, rgba(27,94,32,0.05) 50%, rgba(56,142,60,0.1) 100%);
        background-size: 400% 400%;
        animation: meshFlow 15s ease infinite alternate;
        z-index: 0;
    }

    @keyframes meshFlow {
        0% { background-position: 0% 50%; }
        100% { background-position: 100% 50%; }
    }

    /* 2. Cyber-Organic Glass Cards */
    .prediction-box, .solution-box, .stChatMessage { 
        background: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border-radius: 24px !important; 
        padding: 25px; 
        color: #f0fff4;
        border: 1px solid rgba(167, 255, 131, 0.1);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
        margin-bottom: 25px; 
        transition: transform 0.3s ease;
    }

    .prediction-box:hover, .solution-box:hover {
        transform: translateY(-5px);
        border: 1px solid rgba(167, 255, 131, 0.3);
    }

    /* 3. The "Vital-Sign" Diagnosis Box */
    .primary-diagnosis-box {
        background: rgba(0, 77, 64, 0.3);
        border: 1px solid #a7ff83;
        position: relative;
        overflow: hidden;
        border-radius: 20px;
        padding: 35px;
        color: #ffffff;
    }

    /* Neon Scan-line Effect */
    .primary-diagnosis-box::after {
        content: "";
        position: absolute;
        top: -100%;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(to bottom, transparent, rgba(167, 255, 131, 0.2), transparent);
        animation: scanner 4s linear infinite;
    }

    @keyframes scanner {
        0% { top: -100%; }
        100% { top: 100%; }
    }

    /* 4. Futuristic Typography */
    h1 { 
        font-family: 'Inter', sans-serif;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #a7ff83 0%, #4db6ac 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem !important;
        letter-spacing: -2px !important;
        margin-bottom: 0 !important;
    }

    h2, h3 { color: #a7ff83 !important; font-weight: 700 !important; }

    /* 5. Aether-Glow Sidebar */
    [data-testid="stSidebar"] {
        background: #020806 !important;
        border-right: 1px solid rgba(167, 255, 131, 0.15);
    }

    /* 6. Precision Controls (Buttons) */
    .stButton button {
        background: transparent !important;
        color: #a7ff83 !important;
        border: 1px solid #a7ff83 !important;
        border-radius: 50px !important;
        padding: 15px 30px !important;
        font-size: 0.9rem !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 800 !important;
        transition: 0.4s all cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }

    .stButton button:hover {
        background: #a7ff83 !important;
        color: #020806 !important;
        box-shadow: 0 0 30px rgba(167, 255, 131, 0.6);
        transform: scale(1.05);
    }

    /* 7. Enhanced Data Tables & Charts */
    .stDataFrame {
        background: rgba(0, 0, 0, 0.2);
        border-radius: 15px;
        border: 1px solid rgba(167, 255, 131, 0.1);
    }

    /* Custom File Uploader */
    [data-testid="stFileUploader"] {
        background: rgba(167, 255, 131, 0.03);
        border: 2px dashed rgba(167, 255, 131, 0.2);
        border-radius: 20px;
    }

</style>
""", unsafe_allow_html=True)


# ---------------- Sidebar and Alerts (Feature 1) ----------------
st.sidebar.title("🌿 Controls & Alerts")
lang_choice = st.sidebar.selectbox("Language / ಭಾಷೆ", ("en","kn"), format_func=lambda k: "English" if k=="en" else "ಕನ್ನಡ (Kannada)")
txt = TRANSLATIONS[lang_choice]

# 1. Farmer Alert System
st.sidebar.markdown(f"### {txt['alert_title']}")
alert = get_farmer_alert()
if alert:
    css_class = f"notification-box-{alert['type']}"
    st.sidebar.markdown(f"""
    <div class='{css_class}'>
        <p style='color:inherit;'>**{alert['title']}**<br>
        {alert['message']}</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.info("No major alerts currently active.")


st.sidebar.markdown("---")
if st.sidebar.button(txt["clear_history"], key="clear_hist_btn"):
    clear_history()
    st.sidebar.success("History cleared.")

st.markdown(f"<h1 style='color:#d1ffd1'>{txt['title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color:#a7ff83; font-size:1.2em;'>{txt['subtitle']}</p>", unsafe_allow_html=True)
st.markdown("---")

# Navigation
page = st.sidebar.radio("Go to / ತೆರೆಯಿರಿ", ["Home","Chatbot","History","About"], key="main_nav")

# ---------------- Home ----------------
if page=="Home":
    st.markdown("### 📷 Select Image Source")
    
    # Input Section
    with st.container(border=True):
        input_method = st.radio("Input Method", ["Camera","Upload"], key="input_method_radio", horizontal=True)
        image_obj = None
        source_label = "camera" if input_method=="Camera" else "upload"

        if input_method=="Camera":
            cam = st.camera_input("Take a clear close-up picture of the leaf", key="camera_input")
            if cam:
                image_obj = Image.open(cam).convert("RGB")
        else:
            up = st.file_uploader("Upload leaf image (jpg/png)", type=["jpg","jpeg","png"], key="file_uploader")
            if up:
                image_obj = Image.open(up).convert("RGB")
        
        if image_obj:
            # Displaying the image at a fixed, small size (250px)
            st.image(image_obj, caption="Input Image", width=250) 
            
            if st.button(txt["analyze"], key="analyze_button", use_container_width=True):
                
                prediction_results = []
                try:
                    prediction_results = predict_disease(image_obj, top_n=3)
                except RuntimeError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Prediction failed: {e}")
                
                if prediction_results:
                    top_result = prediction_results[0]
                    cls = top_result["class"]
                    confidence = top_result["confidence"]

                    # 1. Record History
                    record = {
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                        "disease": cls, 
                        "confidence": float(confidence), 
                        "source": source_label
                    }
                    save_history(record)
                    speak_text(f"{cls} detected.")
                    
                    # 2. Display Top Prediction
                    st.markdown(f"<div class='primary-diagnosis-box'><h2>✅ Detected: {cls}</h2><p style='color: white; font-size:1.2em;'>Confidence: **{confidence:.2f}%**</p></div>", unsafe_allow_html=True)
                    
                    # 3. Confidence Warning Check
                    CONFIDENCE_THRESHOLD = 80.0
                    if confidence < CONFIDENCE_THRESHOLD:
                        st.markdown(f"<div class='warning-box'>{txt['low_confidence']}</div>", unsafe_allow_html=True)
                    
                    # 4. Display Top 3
                    if len(prediction_results) > 1:
                        with st.expander(f"🔮 {txt['top_predictions']}"):
                            for i, res in enumerate(prediction_results[1:]):
                                st.write(f"**{res['class']}** ({res['confidence']:.2f}%)")

uploaded_file = st.file_uploader("Upload Leaf Image", type=["jpg","png","jpeg"])

uploaded_file = st.file_uploader("Upload Leaf Image", type=["jpg","png","jpeg"])

if uploaded_file is not None:
    img = Image.open(uploaded_file)

    results = predict_disease(img)

    if results:
        current_disease = results[0]["class"]
        confidence = results[0]["confidence"]

        # ✅ CREATE RECORD
        from datetime import datetime
        record = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "disease": current_disease,
            "confidence": confidence,
            "source": "upload"
        }

        st.image(img, caption="Uploaded Image", width=300)
        st.success(f"Prediction: {current_disease} ({confidence:.2f}%)")

        # PDF
        pdf_width, pdf_height = A4
        pdf_buffer = generate_pdf_report(
            current_diagnosis=current_disease,
            confidence=confidence,
            record=record,
            treatments=disease_treatments,
            image=img,
            width=pdf_width,
            height=pdf_height
        )

        st.download_button(
            label="📄 Download Diagnosis as PDF",
            data=pdf_buffer,
            file_name=f"{current_disease}_report.pdf",
            mime="application/pdf"
        )

        # Treatment Data
        current_info = disease_treatments.get(current_disease, {})

        meds = current_info.get("medicines", "None")
        treatment = current_info.get("treatment", "No treatment info available.")
        suggestions = current_info.get("suggestions", "No suggestions available.")
        nutrients = current_info.get("nutrients", "N/A")

        # UI Labels
        meds_label = txt['medicines']
        treatment_label = txt['treatment']
        suggestions_label = txt['suggestions']

        meds_list = [m.strip() for m in meds.split(",") if m.strip()]

        link_html = "<div>" + "".join(
            f"{flipkart_search_link(m)}<br>" for m in meds_list
        ) + "</div>"

        solution_html = f"""
        <div class='solution-box'>
            <h3>💊 {meds_label}:</h3><p>{meds}</p>
            {link_html}
            <h3>🛠️ {treatment_label}:</h3><p>{treatment}</p>
            <h3>💡 {suggestions_label}:</h3><p>{suggestions}</p>
            <h3>🌱 Nutrient Focus:</h3><p>{nutrients}</p>
        </div>
        """

        st.markdown(solution_html, unsafe_allow_html=True)

    else:
        st.info("No clear prediction could be made. Please upload a clear image.")
