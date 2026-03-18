import streamlit as st
import requests
import PyPDF2
import json
import time

st.set_page_config(page_title="مساعد فرع رشيد", layout="wide")

# جلب المفتاح
if "GOOGLE_API_KEY" in st.secrets:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("⚠️ يرجى إضافة المفتاح في Secrets")
    st.stop()

def get_text(files):
    text = ""
    for f in files:
        pdf = PyPDF2.PdfReader(f)
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

st.title("🤖 مساعد فرع رشيد الذكي")

with st.sidebar:
    files = st.file_uploader("ارفع ملفات PDF", type="pdf", accept_multiple_files=True)

if files:
    context = get_text(files)
    question = st.chat_input("اسأل عن أي شيء في الملفات...")

    if question:
        with st.chat_message("user"): st.write(question)
        with st.chat_message("assistant"):
            with st.spinner("جاري صياغة الرد..."):
                # استخدام رابط الإصدار المستقر v1
                url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
                payload = {
                    "contents": [{"parts": [{"text": f"النص المرجعي:\n{context}\n\nالسؤال: {question}\nأجب بالعربية بدقة."}]}]
                }
                
                response = requests.post(url, json=payload)
                
                if response.status_code == 200:
                    answer = response.json()['candidates'][0]['content']['parts'][0]['text']
                    st.write(answer)
                elif response.status_code == 429:
                    st.error("⚠️ وصلت للحد الأقصى من الطلبات المجانية حالياً. يرجى المحاولة مرة أخرى بعد دقيقة واحدة.")
                else:
                    st.error(f"خطأ: {response.status_code}")
