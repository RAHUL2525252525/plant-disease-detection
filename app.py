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

# Optional: Text-to-Speech
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

# ---------------- PATH CONFIG ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")

# ---------------- CLASS NAMES ----------------
FALLBACK_CLASSES = [
    "Corn__Northern_Leaf_Blight", "Grape__Black_rot", "Grape__healthy",
    "Peach__Bacterial_spot", "Tomato__Early_blight", "Tomato__healthy"
]
class_names = FALLBACK_CLASSES

# ---------------- DISEASE TREATMENTS (Full Dictionary) ----------------
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
    "Blueberry___healthy": {
        "medicines": "No disease present",
        "treatment": "Good soil drainage, pH 5 – 5.5 recommended.",
        "suggestions": "Mulch and prune old stems.",
        "nutrients": "Acid-forming fertilizers (Ammonium sulfate)"
    },
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
    "Orange___Haunglongbing_(Citrus_greening)": {
        "medicines": "No chemical cure",
        "treatment": "Remove infected trees immediately.",
        "suggestions": "Control psyllid insect using imidacloprid.",
        "nutrients": "Foliar Zinc, Manganese, and Boron"
    },
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
    "Raspberry___healthy": {
        "medicines": "No disease",
        "treatment": "Organic compost, rooting hormone spray.",
        "suggestions": "Prune old canes.",
        "nutrients": "Balanced NPK"
    },
    "Soybean___healthy": {
        "medicines": "None",
        "treatment": "Maintain fertilizers and irrigation.",
        "suggestions": "Pest monitoring recommended.",
        "nutrients": "Phosphorus and Potassium"
    },
    "Squash___Powdery_mildew": {
        "medicines": "Sulfur, Neem oil, Bicarbonate spray",
        "treatment": "Spray early morning or evening.",
        "suggestions": "Increase spacing, remove infected leaves.",
        "nutrients": "Balanced NPK"
    },
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

# ---------------- MOCK PREDICTION FUNCTION ----------------
def predict_disease(img, top_n=3):
    results = []
    selected = random.sample(class_names, min(top_n, len(class_names)))
    for cls in selected:
        confidence = random.uniform(70, 99)
        results.append({
            "class": cls,
            "confidence": confidence
        })
    return sorted(results, key=lambda x: x["confidence"], reverse=True)

# ---------------- HISTORY FUNCTIONS ----------------
def save_history(record: dict):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    items = []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    items.append(json.loads(line))
    except Exception:
        pass
    return items

def clear_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)

def history_to_df(items):
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
            "source": it.get("source", "unknown")
        })
    return pd.DataFrame(data)

# ---------------- PDF REPORT ----------------
def generate_pdf_report(current_diagnosis: str, confidence: float, record: dict, treatments: dict, image: Image.Image):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    y = height - 50

    GREEN_HEADER = HexColor('#004d40')
    c.setFillColor(GREEN_HEADER)
    c.rect(0, y + 10, width, 25, fill=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y + 15, "AI Plant Doctor - Diagnosis Report")

    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y - 30, f"Predicted Disease: {current_diagnosis} ({confidence:.2f}%)")
    c.setFont("Helvetica", 10)
    c.drawString(50, y - 50, f"Time of Diagnosis: {record['time']}")

    y -= 100

    # Treatment Info
    info = treatments.get(current_diagnosis, {})
    meds = info.get("medicines", "None")
    treatment = info.get("treatment", "No treatment info available.")
    suggestions = info.get("suggestions", "No suggestions available.")
    nutrients = info.get("nutrients", "Consult local expert.")

    # Image
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Input Image:")
    y -= 25

    img_w, img_h = 180, 180
    c.drawInlineImage(image, 50, y - img_h, width=img_w, height=img_h, preserveAspectRatio=True)
    y -= img_h + 30

    # Treatment Details
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Treatment Plan:")
    y -= 25
    c.setFont("Helvetica", 10)

    c.drawString(60, y, f"• Recommended Medicines: {meds}"); y -= 20
    c.drawString(60, y, "• Suggested Treatment:"); y -= 15
    for line in [treatment[i:i+90] for i in range(0, len(treatment), 90)]:
        c.drawString(70, y, line); y -= 15
    y -= 10
    c.drawString(60, y, "• Additional Suggestions:"); y -= 15
    for line in [suggestions[i:i+90] for i in range(0, len(suggestions), 90)]:
        c.drawString(70, y, line); y -= 15
    y -= 10
    c.drawString(60, y, f"• Key Nutrient Focus: {nutrients}")

    c.save()
    buf.seek(0)
    return buf

# ---------------- TTS ----------------
def speak_text(text: str):
    if not TTS_AVAILABLE:
        return
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception:
        pass

# ---------------- TRANSLATIONS ----------------
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
        "low_confidence": "⚠️ ಕಡಿಮೆ ವಿಶ್ವಾಸ: ಮಾಡೆಲ್ ವಿಶ್ವಾಸಾರ್ಹತೆ ಕಡಿಮೆಯಾಗಿದೆ. ದಯವಿಟ್ಟು ದೃಷ್ಟಿ ದೃಢೀಕರಿಸಿ.",
        "top_predictions": "ಪ್ರಮುಖ ಭವಿಷ್ಯಗಳು:",
        "alert_title": "🚨 ರೈತ ಎಚ್ಚರಿಕೆ ವ್ಯವಸ್ಥೆ"
    }
}

def flipkart_search_link(query):
    return f'<a href="https://www.flipkart.com/search?q={query.replace(" ", "+")}" target="_blank" style="color:#a7ff83; font-weight:bold;">🛒 Find "{query}" on Flipkart</a>'

# ---------------- MOCK FARMER ALERT ----------------
def get_farmer_alert():
    current_month = datetime.now().month
    if current_month in [11, 12]:
        return {"title": "🍂 High Fungal Risk Season Alert!", "message": "Monitor lower canopy and consider preventative Copper spray.", "type": "warning"}
    elif current_month == 5:
        return {"title": "☀️ Pest Monitoring Alert!", "message": "Hot dry conditions increase spider mites risk.", "type": "info"}
    return None

# ---------------- MOCK CHATBOT ----------------
def mock_chatbot_response(prompt):
    prompt = prompt.lower()
    if "help" in prompt or "support" in prompt:
        return "I can help with crop care, disease management, or finding nearest agricultural centers."
    elif "early blight" in prompt:
        return "Early Blight in Tomato: Remove infected leaves and spray Mancozeb or Chlorothalonil every 14 days."
    elif "hello" in prompt or "hi" in prompt:
        return "Hello! I'm your AI Crop Assistant. Ask me about diseases, fertilizers, or crop care!"
    else:
        return "I'm still learning! Try asking about 'early blight', 'fertilizer', or 'crop care'."

# 1. KINETIC BACKGROUND - Swaying Plants
st.markdown("""
    <video autoplay loop muted playsinline  style="
        position: fixed; right: 0; bottom: 0; min-width: 100%; min-height: 100%;
        z-index: -2; filter: brightness(0.2) contrast(1.1); object-fit: cover;">
        <source src="https://assets.mixkit.co/videos/preview/mixkit-slow-motion-video-of-leaves-in-a-branch-11440-large.mp4" type="video/mp4">
    </video>
""", unsafe_allow_html=True)

# 2. THE SLIDING DASHBOARD & BUTTON CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;900&display=swap');
    
    .stApp { background: transparent; font-family: 'Inter', sans-serif; }

    /* --- 1. THE SWIPE BUTTON (System Toggle) --- */
    /* This button stays fixed at the top right */
    .stButton > button {
        position: fixed !important;
        top: 20px !important;
        right: 20px !important;
        width: 180px !important;
        height: 50px !important;
        z-index: 1000 !important;
        background: rgba(167, 255, 131, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(167, 255, 131, 0.5) !important;
        color: #a7ff83 !important;
        border-radius: 100px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: 0.4s all ease;
    }

    .stButton > button:hover {
        background: #a7ff83 !important;
        color: #000 !important;
        box-shadow: 0 0 30px rgba(167, 255, 131, 0.4);
    }

    /* --- 2. THE CONTROL DASHBOARD (SIDEBAR REPLACEMENT) --- */
    section[data-testid="stSidebar"] {
        background: rgba(0, 0, 0, 0.85) !important;
        backdrop-filter: blur(40px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.5s cubic-bezier(0.77, 0, 0.175, 1) !important;
    }

    /* --- 3. MICRO-UI FOR DASHBOARD --- */
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] p {
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        letter-spacing: 1px;
        color: #a7ff83 !important;
        text-transform: uppercase;
        opacity: 0.8;
    }

    .stAlert {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(167, 255, 131, 0.2) !important;
        border-radius: 8px !important;
        font-size: 0.8rem !important;
    }

    /* --- 4. MAIN CONTENT AREA --- */
    h1 {
        font-weight: 900 !important;
        font-size: clamp(3rem, 10vw, 6rem) !important;
        letter-spacing: -4px !important;
        color: #ffffff;
        line-height: 0.9 !important;
        filter: drop-shadow(0 20px 40px rgba(0,0,0,0.5));
    }

    .prediction-box, .solution-box {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(30px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 30px !important;
        padding: 40px !important;
        box-shadow: 0 40px 80px rgba(0,0,0,0.4);
    }

    /* Hide standard UI clutter */
    #MainMenu, footer, header {visibility: hidden;}
    .block-container { padding-top: 5rem !important; }

</style>
""", unsafe_allow_html=True)

# 3. IMPLEMENTATION
# This acts as the "Toggle" button for the dashboard
if st.button("⚙️ SYSTEM COMMAND"):
    st.sidebar.markdown("### 🛠️ DASHBOARD CONTROLS")
    # Add your alerts and controls here
    st.sidebar.warning("ALERT: High Humidity Detected")
    st.sidebar.selectbox("Language Select", ["English", "Kannada", "Hindi"])
    st.sidebar.slider("Scan Sensitivity", 0, 100, 85)-------
st.sidebar.title("🌿 Controls & Alerts")
lang_choice = st.sidebar.selectbox("Language / ಭಾಷೆ", ("en", "kn"), 
                                   format_func=lambda k: "English" if k=="en" else "ಕನ್ನಡ (Kannada)")
txt = TRANSLATIONS[lang_choice]

st.sidebar.markdown(f"### {txt['alert_title']}")
alert = get_farmer_alert()
if alert:
    st.sidebar.warning(f"**{alert['title']}**\n\n{alert['message']}")
else:
    st.sidebar.info("No major alerts currently active.")

if st.sidebar.button(txt["clear_history"], key="clear_hist_btn"):
    clear_history()
    st.sidebar.success("History cleared.")

# ---------------- MAIN TITLE ----------------
st.markdown(f"<h1>{txt['title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color:#a7ff83; font-size:1.2em;'>{txt['subtitle']}</p>", unsafe_allow_html=True)
st.markdown("---")

# ---------------- NAVIGATION ----------------
page = st.sidebar.radio("Go to / ತೆರೆಯಿರಿ", ["Home", "Chatbot", "History", "About"], key="main_nav")

# ---------------- HOME PAGE ----------------
if page == "Home":
    st.markdown("### 📷 Select Image Source")
    
    input_method = st.radio("Input Method", ["Camera", "Upload"], horizontal=True)
    image_obj = None

    if input_method == "Camera":
        cam = st.camera_input("Take a clear close-up picture of the leaf")
        if cam:
            image_obj = Image.open(cam).convert("RGB")
    else:
        up = st.file_uploader("Upload leaf image (jpg/png)", type=["jpg", "jpeg", "png"])
        if up:
            image_obj = Image.open(up).convert("RGB")

    if image_obj:
        st.image(image_obj, caption="Uploaded Leaf Image", use_column_width=True)

        if st.button(txt["analyze"], use_container_width=True):
            with st.spinner("Analyzing..."):
                prediction_results = predict_disease(image_obj, top_n=3)
                top_result = prediction_results[0]
                cls = top_result["class"]
                confidence = top_result["confidence"]

                # Save History
                record = {
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "disease": cls,
                    "confidence": float(confidence),
                    "source": "camera" if input_method == "Camera" else "upload"
                }
                save_history(record)
                speak_text(f"{cls} detected.")

                # Display Result
                st.markdown(
                    f"<div class='primary-diagnosis-box'>"
                    f"<h2>✅ Detected: {cls}</h2>"
                    f"<p style='color:white; font-size:1.3em;'>Confidence: <strong>{confidence:.2f}%</strong></p>"
                    f"</div>", unsafe_allow_html=True
                )

                if confidence < 80:
                    st.warning(txt["low_confidence"])

                # Top Predictions
                if len(prediction_results) > 1:
                    with st.expander(txt["top_predictions"]):
                        for res in prediction_results[1:]:
                            st.write(f"**{res['class']}** — {res['confidence']:.2f}%")

                # PDF Download
                pdf_buffer = generate_pdf_report(cls, confidence, record, disease_treatments, image_obj)
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_buffer,
                    file_name="plant_disease_report.pdf",
                    mime="application/pdf"
                )

                # Treatment Display
                if cls in disease_treatments:
                    info = disease_treatments[cls]
                    meds_list = [m.strip() for m in info["medicines"].split(",") if m.strip().lower() not in ["none", "no cure"]]

                    solution_html = f"""
                    <div class='solution-box'>
                        <h3>💊 {txt['medicines']}:</h3><p>{info['medicines']}</p>
                        {"".join(f"{flipkart_search_link(m)}<br>" for m in meds_list)}
                        <h3>🛠️ {txt['treatment']}:</h3><p>{info['treatment']}</p>
                        <h3>💡 {txt['suggestions']}:</h3><p>{info['suggestions']}</p>
                        <h3>🌱 Nutrient Focus:</h3><p>{info['nutrients']}</p>
                    </div>
                    """
                    st.markdown(solution_html, unsafe_allow_html=True)
                else:
                    st.info("No detailed treatment information available for this disease.")

# ---------------- CHATBOT PAGE ----------------
elif page == "Chatbot":
    st.markdown("## 🤖 AI Crop Assistant Chatbot")
    st.markdown("Ask me anything about crop care, fertilizers, or disease management.")

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🧑‍🌾" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])

    prompt = st.chat_input("How can I treat my tomato's early blight?")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍🌾"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            response = mock_chatbot_response(prompt)
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

# ---------------- HISTORY PAGE ----------------
elif page == "History":
    st.markdown("## 📜 Prediction History")
    history_data = load_history()
    df = history_to_df(history_data)

    if df.empty:
        st.info("No prediction history yet. Start analyzing images on the Home page!")
    else:
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name='plant_doctor_history.csv',
            mime='text/csv'
        )

# ---------------- ABOUT PAGE ----------------
elif page == "About":
    st.markdown("## ℹ️ About AI Plant Doctor")
    st.markdown("""
    This application helps farmers and gardeners quickly identify plant leaf diseases using AI.

    **Built with:**
    - Streamlit (UI)
    - ReportLab (PDF Generation)
    - Mock AI Model (Ready for real TensorFlow/Keras model)

    **Disclaimer:** This tool is for informational purposes only. Always consult local agricultural experts for final diagnosis and treatment.
    """)

else:
    st.warning("Invalid page selection.")
