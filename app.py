try:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]
    os.environ["LANGCHAIN_PROJECT"] = "Echo-ML"
except:
    pass
    
from langsmith import traceable
import streamlit as st
import requests
import json

# --- 1. PRO PAGE CONFIGURATION ---
st.set_page_config(page_title="Echo-ML | AI Sentiment", page_icon="⚡", layout="centered")

# --- 2. CUSTOM CSS FOR PREMIUM LOOK ---
st.markdown("""
    <style>
    .main-title {
        font-size: 38px;
        font-weight: 800;
        color: #1E88E5;
        text-align: center;
        margin-bottom: -10px;
    }
    .sub-title {
        font-size: 18px;
        color: #666666;
        text-align: center;
        margin-bottom: 20px;
    }
    .stTextArea textarea {
        border-radius: 10px;
        border: 1px solid #1E88E5;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        background-color: #1E88E5;
        color: white;
    }
    .stButton>button:hover {
        background-color: #1565C0;
        border-color: #1565C0;
    }
    .result-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f8f9fa;
        border-left: 5px solid #1E88E5;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. HEADER SECTION ---
st.markdown('<div class="main-title">⚡ Echo-ML Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Intelligent Aspect-Based Sentiment Analysis</div>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555; margin-bottom: 30px;'>Enter any product review or customer feedback below, and AI will dynamically extract the <b>Sentiment</b> and the <b>Core Aspect/Category</b>.</p>", unsafe_allow_html=True)

# --- 4. SECURE API HANDLING (SIDEBAR) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/8636/8636883.png", width=80) 
    st.title("⚙️ Configuration")
    
    try:
        API_KEY = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ Secure Cloud Key Connected")
    except:
        API_KEY = ""
        st.warning("Developer Mode Active")
        API_KEY = st.text_input("Enter Gemini API Key:", type="password", help="Required for local testing.")
    
    st.markdown("---")
    st.markdown("**About Echo-ML**")
    st.markdown("This tool uses Generative AI to parse unstructured customer feedback and extract precise sentiments along with the core aspect being discussed.")
    st.markdown("👨‍💻 *Developed by Sidhu*")

# --- 5. CORE AI LOGIC ---
@traceable(name="Echo-ML-Core-Engine")
def analyze_review_with_ai(review_text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={API_KEY}"
    
    prompt = f"""
    Act as a precise AI data extraction tool. Analyze this customer feedback/review:
    "{review_text}"
    
    Return EXACTLY a JSON format with two keys:
    1. "Sentiment": (Strictly one of: Positive, Negative, Neutral)
    2. "Category": (The main aspect discussed, e.g., "Battery Life", "Customer Support", "Delivery". Max 2 words)
    
    Example output: {{"Sentiment": "Positive", "Category": "Screen Quality"}}
    """
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload)
        response_data = response.json()
        
        if "error" in response_data:
            return {"error": response_data['error']['message']}
            
        result_text = response_data['candidates'][0]['content']['parts'][0]['text']
        result_text = result_text.strip().replace("```json", "").replace("```", "")
        data = json.loads(result_text)
        
        return {"Sentiment": data.get("Sentiment", "Neutral"), "Category": data.get("Category", "Unknown")}
    except Exception as e:
        return {"error": str(e)}

# --- 6. CLEAN USER INTERFACE ---
st.markdown("### 📝 Enter Customer Feedback")
user_review = st.text_area("", height=130, placeholder="E.g., The camera quality is fantastic, especially in low light, but the battery drains too fast.")

if st.button("🚀 Run Analysis"):
    if not API_KEY:
        st.error("🚨 Missing API Key! Please enter it in the sidebar.")
    elif len(user_review.strip()) < 5:
        st.warning("⚠️ Please enter meaningful feedback to analyze.")
    else:
        with st.spinner("🧠 AI is processing the text..."):
            result = analyze_review_with_ai(user_review)
            
            if "error" in result:
                st.error(f"API Error: {result['error']}")
            else:
                # Professional Output Metrics
                st.markdown("### 📊 Extraction Results")
                
                col1, col2 = st.columns(2)
                
                sentiment = result['Sentiment']
                
                # Dynamic coloring based on sentiment
                if sentiment.lower() == 'positive':
                    emo = "🟢"
                elif sentiment.lower() == 'negative':
                    emo = "🔴"
                else:
                    emo = "⚪"

                with col1:
                    st.metric(label="Detected Sentiment", value=f"{emo} {sentiment}")
                    
                with col2:
                    st.metric(label="Target Aspect", value=f"📌 {result['Category']}")
                
                # Displaying raw JSON for technical recruiters
                with st.expander("Show Raw Developer Output (JSON)"):
                    st.json(result)
