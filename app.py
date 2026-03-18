import streamlit as st
from PIL import Image
from tensorflow.keras.preprocessing import image as kimage
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

# ---------------- UI / CSS STYLING (Aether-Flora Theme) ----------------
st.markdown("""
<style>
    /* 1. Animated Mesh Gradient Background */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #0a1f1c 0%, #040d0b 100%);
        background-attachment: fixed;
    }
    
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
    .prediction-box, .solution-box, .stChatMessage, .stTable { 
        background: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(20px) saturate(180%);
        border-radius: 24px !important; 
        padding: 25px; 
        color: #f0fff4;
        border: 1px solid rgba(167, 255, 131, 0.1);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
        margin-bottom: 25px; 
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
        padding: 10px 20px !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 800 !important;
        transition: 0.4s all;
        width: 100%;
    }

    .stButton button:hover {
        background: #a7ff83 !important;
        color: #020806 !important;
        box-shadow: 0 0 30px rgba(167, 255, 131, 0.6);
    }

    /* Hiding File Uploader Text per user request */
    [data-testid="stFileUploadDropzone"] div div span { display: none; }
    [data-testid="stFileUploadDropzone"] div div small { display: none; }
    
</style>
""", unsafe_allow_html=True)

# ---------------- PATH CONFIG ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")

# ---------------- CLASS NAMES ----------------
class_names = [
    "Apple___Apple_scab", "Apple___Black_rot", "Apple___Cedar_apple_rust", "Apple___healthy",
    "Blueberry___healthy", "Cherry___healthy", "Cherry___Powdery_mildew",
    "Corn___Cercospora_leaf_spot Gray_leaf_spot", "Corn___Common_rust", "Corn___Northern_Leaf_Blight", "Corn___healthy",
    "Grape___Black_rot", "Grape___Esca_(Black_Measles)", "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)", "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)", "Peach___Bacterial_spot", "Peach___healthy",
    "Pepper,_bell___Bacterial_spot", "Pepper,_bell___healthy", "Potato___Early_blight", "Potato___Late_blight", "Potato___healthy",
    "Raspberry___healthy", "Soybean___healthy", "Squash___Powdery_mildew", "Strawberry___Leaf_scorch", "Strawberry___healthy",
    "Tomato___Bacterial_spot", "Tomato___Early_blight", "Tomato___healthy", "Tomato___Late_blight", "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot", "Tomato___Spider_mites Two-spotted_spider_mite", "Tomato___Target_Spot",
    "Tomato___Tomato_mosaic_virus", "Tomato___Tomato_Yellow_Leaf_Curl_Virus"
]

# ---------------- DISEASE TREATMENTS ----------------
disease_treatments = {
    "Apple___Apple_scab": {"medicines": "Copper fungicide, Mancozeb", "treatment": "Spray early spring.", "suggestions": "Prune dense branches.", "nutrients": "Calcium"},
    "Apple___Black_rot": {"medicines": "Myclobutanil", "treatment": "Remove fruit mummies.", "suggestions": "Avoid overhead watering.", "nutrients": "Potassium"},
    "Corn___Northern_Leaf_Blight": {"medicines": "Azoxystrobin", "treatment": "Apply at tasseling.", "suggestions": "Rotate crops.", "nutrients": "Balanced NPK"},
    "Grape___Black_rot": {"medicines": "Myclobutanil, Captan", "treatment": "Remove mummified berries.", "suggestions": "Improve air circulation.", "nutrients": "Magnesium"},
    "Potato___Early_blight": {"medicines": "Chlorothalonil", "treatment": "Spray at first spot appearance.", "suggestions": "Remove infected leaves.", "nutrients": "Potassium"},
    "Tomato___Early_blight": {"medicines": "Mancozeb, Chlorothalonil", "treatment": "Spray every 14 days.", "suggestions": "Remove lower leaves.", "nutrients": "K and Mg"},
    "Tomato___healthy": {"medicines": "None", "treatment": "Maintain staking.", "suggestions": "Mulch soil.", "nutrients": "Balanced NPK"}
}

# ---------------- FUNCTIONS ----------------

def get_farmer_alert():
    current_month = datetime.now().month
    if current_month in [11, 12]:
        return {"title": "🍂 High Fungal Risk!", "message": "High humidity alert. Watch for Blights.", "type": "warning"}
    return None

def mock_chatbot_response(prompt):
    prompt = prompt.lower()
    if "help" in prompt: return "I can help with crop care, disease management, and finding help centers."
    if "npk" in prompt: return "NPK stands for Nitrogen, Phosphorus, and Potassium. Essential for plant growth."
    return "I'm your AI Crop Assistant. Try asking about 'early blight' or 'fertilizers'!"

def predict_disease(img):
    # Mimicking a prediction result based on random selection for this version
    results = []
    selected = random.sample(class_names, 3)
    for cls in selected:
        confidence = random.uniform(75, 99)
        results.append({"class": cls, "confidence": confidence})
    return results

def save_history(record):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

def load_history():
    if not os.path.exists(HISTORY_FILE): return []
    with open(HISTORY_FILE, "r") as f:
        return [json.loads(line) for line in f if line.strip()]

def generate_pdf_report(disease, conf, image):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setFillColor(HexColor('#004d40'))
    c.rect(0, 750, 600, 100, fill=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, 780, "DIAGNOSIS REPORT")
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 720, f"Detected: {disease} ({conf:.2f}%)")
    c.save()
    buf.seek(0)
    return buf

# ---------------- UI LAYOUT ----------------

st.sidebar.title("🌲 Nexus Controls")
lang_choice = st.sidebar.selectbox("Language / ಭಾಷೆ", ("en","kn"))
txt = {
    "en": {"title": "AI Plant Doctor", "analyze": "Analyze Specimen", "medicines": "Prescription", "alert_title": "🚨 Farmer Alert"},
    "kn": {"title": "ಎಐ ಗಿಡ ವೈದ್ಯ", "analyze": "ವಿಶ್ಲೇಷಿಸಿ", "medicines": "ಔಷಧಿಗಳು", "alert_title": "🚨 ರೈತ ಎಚ್ಚರಿಕೆ"}
}[lang_choice]

alert = get_farmer_alert()
if alert:
    st.sidebar.warning(f"**{alert['title']}**\n\n{alert['message']}")

page = st.sidebar.radio("Navigate", ["Home", "Chatbot", "History", "About"])

if page == "Home":
    st.title(txt["title"])
    input_method = st.radio("Select Source", ["Camera", "Upload"], horizontal=True)
    
    image_obj = None
    if input_method == "Camera":
        cam = st.camera_input("Scan Leaf")
        if cam: image_obj = Image.open(cam).convert("RGB")
    else:
        up = st.file_uploader("📤 Upload Leaf Image", type=["jpg","jpeg","png"])
        if up: image_obj = Image.open(up).convert("RGB")

    if image_obj:
        st.image(image_obj, width=300)
        if st.button(txt["analyze"]):
            results = predict_disease(image_obj)
            top = results[0]
            
            # Save History
            save_history({"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "disease": top["class"], "confidence": top["confidence"]})
            
            # Display Result
            st.markdown(f"""
            <div class='primary-diagnosis-box'>
                <h2>{top['class']}</h2>
                <p>Accuracy Index: {top['confidence']:.2f}%</p>
            </div>
            """, unsafe_allow_html=True)
            
            info = disease_treatments.get(top["class"], {"medicines": "Check local store", "treatment": "N/A"})
            st.markdown(f"<div class='solution-box'><h4>{txt['medicines']}</h4>{info['medicines']}</div>", unsafe_allow_html=True)
            
            pdf = generate_pdf_report(top["class"], top["confidence"], image_obj)
            st.download_button("📥 Download Report", data=pdf, file_name="Report.pdf", mime="application/pdf")

elif page == "Chatbot":
    st.header("🤖 Botanical AI")
    prompt = st.chat_input("Ask me about plant health...")
    if prompt:
        with st.chat_message("user"): st.write(prompt)
        with st.chat_message("assistant"): st.write(mock_chatbot_response(prompt))

elif page == "History":
    st.header("📜 Scan Logs")
    data = load_history()
    if data: st.table(pd.DataFrame(data))
    else: st.info("No scan history found.")

else:
    st.header("About Nexus")
    st.write("Developed by: Rahul S. | AI-Driven Agricultural Analytics.")
