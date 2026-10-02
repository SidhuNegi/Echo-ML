# 🚀 Echo-ML: Aspect-Based Sentiment Analysis

**Live Demo:** [Play with Echo-ML Here](https://echo-ml-ldaouvh4sbfwqdrgbnbvpu.streamlit.app/)

## 📌 Overview
Echo-ML is an intelligent web application designed to parse unstructured customer feedback and product reviews. It uses Generative AI to dynamically extract both the **Sentiment** (Positive/Negative/Neutral) and the **Core Aspect/Category** being discussed.

## 🛠️ Tech Stack
* **Language:** Python
* **Frontend:** Streamlit (Custom UI/CSS)
* **AI Engine:** Google Gemini API (`gemini-1.5-flash`)
* **Observability & Tracing:** LangSmith
* **Architecture:** Secure Cloud API key handling, dynamic JSON parsing, API rate-limiting

## 💡 Features
* **Real-time extraction:** Processes text and delivers structured JSON output instantly.
* **Aspect detection:** Dynamically understands context (e.g., separating "Battery" from "Camera").
* **Enterprise Tracing:** Fully integrated with LangSmith for live prompt monitoring, latency tracking, and error logging.
* **Bulk Processing Safe:** Built-in API rate limiting (11 RPM) for seamless and crash-free batch analysis via CSV uploads.
* **Bulletproof API Handling:** Employs Streamlit Secrets for cloud deployment and graceful fallback using `.env` for local testing.

## 🚀 Local Development Setup

Follow these steps to run Echo-ML on your local machine:

**Clone the repository and install dependencies:**
```bash
git clone [https://github.com/SidhuNegi/Echo-ML.git](https://github.com/SidhuNegi/Echo-ML.git)
cd Echo-ML
pip install -r requirements.txt```

2. Configure Environment Variables:
Create a .env file in the root directory and add your LangSmith and Gemini API keys:

Code snippet
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT="[https://api.smith.langchain.com](https://api.smith.langchain.com)"
LANGCHAIN_API_KEY="your_langsmith_key_here"
LANGCHAIN_PROJECT="Echo-ML"
GOOGLE_API_KEY="your_gemini_key_here"
3. Run the Application:

Bash
streamlit run app.py
🧠 Architecture Flow
Code snippet
graph TD
    A[Raw User Review] --> B(Preprocessing & Formatting)
    B --> C{Google Gemini API}
    
    C -->|Single Prompt| D[Sentiment Analysis]
    C -->|Dynamic Inference| E[Aspect Extraction]
    
    D --> F[🟢 Positive / 🔴 Negative / ⚪ Neutral]
    E --> G[Battery, Camera, Service, Fabric, etc.]
    
    F --> H(JSON Parsing)
    G --> H
    
    H --> I[🚀 Echo-ML Streamlit Dashboard]
    
    style C fill:#f9f,stroke:#333,stroke-width:2px
    style I fill:#bbf,stroke:#333,stroke-width:2px
