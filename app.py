import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv
import pyttsx3
from fpdf import FPDF
from datetime import datetime

# Load env vars
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Voice Engine Setup
engine = pyttsx3.init()

# Streamlit Page Config
st.set_page_config(page_title="🤖 AI Customer Support Playbook", layout="wide")

# --- Custom CSS ---
st.markdown("""
    <style>
        .main-title {
            text-align: center;
            font-size: 48px;
            color: #00B8D4;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .sub-title {
            text-align: center;
            font-size: 20px;
            color: #607D8B;
            margin-bottom: 30px;
        }
        .section {
            background-color: #ffffff;
            padding: 25px;
            border-radius: 16px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
            margin-top: 20px;
        }
        .playbook-output {
            background-color: #f0f4f8;
            padding: 20px;
            border-left: 6px solid #00B8D4;
            border-radius: 10px;
            font-family: 'Segoe UI';
        }
        .sidebar-header {
            font-size: 24px;
            color: #00B8D4;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🤖 AI Customer Support Playbook Generator</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Craft professional, tone-matched support scripts instantly using Groq LLM</p>", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.markdown("<p class='sidebar-header'>🎯 Configure Your Playbook</p>", unsafe_allow_html=True)
product = st.sidebar.text_input("🛠️ Product/Service Name", placeholder="e.g., SmartHome App")
company = st.sidebar.text_input("🏢 Company Name", placeholder="e.g., HomeTech")
query_type = st.sidebar.selectbox(
    "📝 Customer Query Type",
    ["Late Delivery", "Billing Issues", "Technical Glitches", "Product Defect", "Refund Request", "Other"]
)
custom_query = st.sidebar.text_input("✍️ Custom Query (if 'Other')", placeholder="Describe the query")

tone = st.sidebar.selectbox(
    "🎙️ Preferred Tone",
    ["Friendly", "Formal", "Empathetic", "Apologetic", "Neutral"]
)

priority = st.sidebar.select_slider("🔥 Priority", options=["Low", "Medium", "High"], value="Medium")
voice_play = st.sidebar.checkbox("🔊 Read Out Loud", value=False)

generate_button = st.sidebar.button("🚀 Generate Playbook")

# Session memory for past results
if "history" not in st.session_state:
    st.session_state.history = []

# Generate Function
def generate_playbook(product, company, query, tone, priority):
    actual_query = custom_query if query_type == "Other" and custom_query else query_type
    company_name = company if company else "[Your Company]"

    prompt = f"""
    Strictly follow these inputs to generate a customer support playbook:
    - Product/Service: '{product}'
    - Company: '{company_name}'
    - Customer Query: '{actual_query}'
    - Tone: {tone.lower()}
    - Priority: {priority.lower()}
    
    Create a detailed playbook with these sections:
    1. **Greeting**: A warm, branded welcome specific to '{company_name}'.
    2. **Acknowledgment**: Recognize the '{actual_query}' issue in a {tone.lower()} tone.
    3. **Solution**: Provide a clear, product-specific resolution related to '{product}'.
    4. **Closing**: End with a positive {tone.lower()} message and CTA.
    5. **Escalation Guide**: Steps to escalate based on {priority.lower()} priority.
    6. Provide a 100-word advance settlement reply that is understandable and helpful for users about: {custom_query if custom_query else actual_query}.
    7. Your tone should be formal and respectful toward users.
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=16000,
            temperature=1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {e}"

# PDF Generator
def save_as_pdf(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for line in content.split("\n"):
        pdf.multi_cell(0, 10, txt=line, align='L')

    filename = f"playbook_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename

# --- Output Section ---
if generate_button and product:
    with st.spinner("Generating playbook..."):
        playbook = generate_playbook(product, company, query_type, tone, priority)
        st.session_state.history.append(playbook)

    if playbook:
        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.markdown("### 📘 Generated Playbook")
        st.markdown(f"<div class='playbook-output'>{playbook}</div>", unsafe_allow_html=True)

        # Voice
        if voice_play:
            engine.say(playbook)
            engine.runAndWait()

        # Download
        if st.button("📥 Download as PDF"):
            filepath = save_as_pdf(playbook)
            with open(filepath, "rb") as f:
                st.download_button(label="Click to Download", data=f, file_name=filepath, mime="application/pdf")

        st.markdown("</div>", unsafe_allow_html=True)

# --- Past Playbooks Tab ---
if st.toggle("🕘 Show Playbook History"):
    if st.session_state.history:
        for idx, past in enumerate(reversed(st.session_state.history)):
            st.markdown(f"#### 📜 Playbook #{len(st.session_state.history) - idx}")
            st.markdown(f"<div class='playbook-output'>{past}</div>", unsafe_allow_html=True)
    else:
        st.info("No history available yet.")

# --- Footer ---
st.markdown("---")
st.markdown("<center>⚡ Crafted with ❤️ using Groq & Streamlit | © 2025</center>", unsafe_allow_html=True)
