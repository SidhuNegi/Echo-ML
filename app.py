import os
import time
from dotenv import load_dotenv
import streamlit as st

# --- 1. ENVIRONMENT CONFIGURATION ---
# Load environment variables for local development
load_dotenv() 

# --- 2. PAGE INITIALIZATION ---
st.set_page_config(page_title="Echo-ML | AI Sentiment", page_icon="⚡", layout="centered")

# --- 3. CLOUD TRACING SETUP (LANGSMITH) ---
# Safely initialize LangSmith environment variables for Streamlit Cloud deployment
try:
    if "LANGCHAIN_API_KEY" in st.secrets:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
        os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]
        os.environ["LANGCHAIN_PROJECT"] = "Echo-ML"
except Exception:
    pass

# --- 4. APPLICATION DEPENDENCIES ---
import requests
import json
import pandas as pd
from langsmith import traceable

# --- 5. UI STYLING & CUSTOM CSS ---
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

# --- 6. APPLICATION HEADER ---
st.markdown('<div class="main-title">⚡ Echo-ML Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Intelligent Aspect-Based Sentiment Analysis</div>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555; margin-bottom: 30px;'>Enter any product review or customer feedback below, and AI will dynamically extract the <b>Sentiment</b> and the <b>Core Aspect/Category</b>.</p>", unsafe_allow_html=True)

# --- 7. SIDEBAR & CREDENTIAL MANAGEMENT ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/8636/8636883.png", width=80) 
    st.title("⚙️ Configuration")
    
    # Traceability Status Indicator
    if os.environ.get("LANGCHAIN_API_KEY"):
        st.success("✅ LangSmith Tracing Active")
        
    # API Key Authentication Logic
    try:
        API_KEY = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ Secure Cloud Key Connected")
    except:
        API_KEY = os.environ.get("GOOGLE_API_KEY", "")
        if not API_KEY:
            st.warning("Developer Mode Active")
            API_KEY = st.text_input("Enter Gemini API Key:", type="password", help="Required for local testing.")
    
    st.markdown("---")
    st.markdown("**About Echo-ML**")
    st.markdown("This tool uses Generative AI to parse unstructured customer feedback and extract precise sentiments along with the core aspect being discussed.")
    st.markdown("👨‍💻 *Developed by SIDDHARTH NEGI*")

# --- 8. CORE AI INFERENCE ENGINE ---
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

# --- 9. SINGLE REVIEW ANALYSIS UI ---
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
                # Render Professional Output Metrics
                st.markdown("### 📊 Extraction Results")
                
                col1, col2 = st.columns(2)
                
                sentiment = result.get('Sentiment', 'Neutral')
                category = result.get('Category', 'Unknown')
                
                # Dynamic visual indicators based on sentiment logic
                if sentiment.lower() == 'positive':
                    emo = "🟢"
                elif sentiment.lower() == 'negative':
                    emo = "🔴"
                else:
                    emo = "⚪"

                with col1:
                    st.metric(label="Detected Sentiment", value=f"{emo} {sentiment}")
                    
                with col2:
                    st.metric(label="Target Aspect", value=f"📌 {category}")
                
                # Expose raw JSON payload for developer reference
                with st.expander("Show Raw Developer Output (JSON)"):
                    st.json(result)

st.markdown("---")

# --- 10. BATCH PROCESSING & CSV UPLOAD MODULE ---
st.subheader("📁 Bulk Review Analysis (Upload CSV)")

# File Upload Widget
uploaded_file = st.file_uploader("Upload a CSV file containing reviews", type=["csv"])

if uploaded_file is not None:
    # Load dataset into Pandas DataFrame
    df = pd.read_csv(uploaded_file)
    
    st.write("✅ File Uploaded Successfully! Data Preview:")
    st.dataframe(df.head())
    
    st.markdown("### ⚙️ Process Reviews")
    # Target Column Selection for Analysis
    text_column = st.selectbox("Select the column containing the reviews:", df.columns)
    
    if st.button("Run Batch Analysis"):
        # Initialize UI Components for Progress Tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Initialize Data Structures for AI Results
        sentiments = []
        categories = []
        
        total_rows = len(df)
        
        # Iterate Through Dataset and Process Reviews
        for i, row in df.iterrows():
            review = str(row[text_column])
            
            try:
                # Execute AI Inference
                result = analyze_review_with_ai(review) 
                
                # Debug output for the first processed record
                if i == 0:
                    st.write(f"🔍 Debug (Row 1 Raw Output):", result)
                
                # Normalize keys and handle missing data safely
                senti = result.get('Sentiment', result.get('sentiment', 'Neutral'))
                cat = result.get('Category', result.get('category', 'General'))
                
                sentiments.append(senti)
                categories.append(cat)
                
            except Exception as e:
                # Exception handling to prevent batch failure
                sentiments.append(f"Error: {e}")
                categories.append(f"Error: {e}")
                
            # Update Progress Bar Dynamically
            progress_bar.progress((i + 1) / total_rows)
            status_text.text(f"Processed {i + 1} of {total_rows} reviews...")
            
            # --- API RATE LIMITING (11 RPM) ---
            # Implement delay to prevent API quota exhaustion (except for the last row)
            if i < total_rows - 1:
                time.sleep(5.5)  
            
        # Append Analysis Results to the Original DataFrame
        df['Sentiment'] = sentiments
        df['Category'] = categories
        
        st.success("✅ Batch Analysis Complete!")
        st.write("Here are your processed results:")
        st.dataframe(df)
