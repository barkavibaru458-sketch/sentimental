import streamlit as st
import pandas as pd
import json
from textblob import TextBlob
import PyPDF2

st.set_page_config(page_title="Word-Level Sentiment", layout="centered")

st.title("📋 Word-Level Sentiment")

# ---------- Sentiment Function ----------
def analyze_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        return "Positive"
    elif polarity < -0.1:
        return "Negative"
    else:
        return "Neutral"

# ---------- File Readers ----------
def read_json(file):
    data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError("JSON must be a dictionary")
    return list(data.values())

def read_csv(file):
    df = pd.read_csv(file)
    if "review" not in df.columns:
        raise ValueError("CSV must contain 'review' column")
    return df["review"].astype(str).tolist()

def read_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return [line.strip() for line in text.split("\n") if line.strip()]

# ---------- Upload ----------
uploaded_file = st.file_uploader(
    "Upload JSON / CSV / PDF",
    type=["json", "csv", "pdf"]
)

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".json"):
            reviews = read_json(uploaded_file)
        elif uploaded_file.name.endswith(".csv"):
            reviews = read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".pdf"):
            reviews = read_pdf(uploaded_file)
        else:
            st.error("Unsupported file type")
            st.stop()

        sentiments = []
        pos = neg = neu = 0

        for r in reviews:
            s = analyze_sentiment(r)
            sentiments.append(s)
            if s == "Positive":
                pos += 1
            elif s == "Negative":
                neg += 1
            else:
                neu += 1

        # ---------- Table like screenshot ----------
        df = pd.DataFrame({
            "review": reviews,
            "sentiment": sentiments
        })

        st.dataframe(df, use_container_width=True)

        # ---------- Sentiment Summary ----------
        st.subheader("📊 Sentiment Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Positive", pos)
        col2.metric("Negative", neg)
        col3.metric("Neutral", neu)

        # ---------- Overall Sentiment ----------
        st.subheader("🌟 Overall Sentiment")
        if pos > neg:
            st.success("Overall Sentiment: POSITIVE 😊")
        elif neg > pos:
            st.error("Overall Sentiment: NEGATIVE 😞")
        else:
            st.info("Overall Sentiment: NEUTRAL 😐")

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("👆 Upload a file to begin analysis")
