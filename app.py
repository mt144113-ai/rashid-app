import streamlit as st
import requests
import PyPDF2
import json

# 1. إعدادات الصفحة
st.set_page_config(page_title="مساعد فرع رشيد الذكي", layout="wide")

st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    .stMarkdown, .stText, .stTitle, .stHeader, .stCaption { text-align: right; direction: rtl; }
    div[data-testid="stSidebar"] { direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 مساعد فرع رشيد الذكي")

# 2. التأكد من وجود المفتاح
if "GOOGLE_API_KEY" in st.secrets:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("⚠️ يرجى إضافة GOOGLE_API_KEY في إعدادات Secrets")
    st.stop()

# 3. دالة استخراج النص
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PyPDF2.PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    return text

# 4. دالة الاتصال المباشر بجوجل (REST)
def ask_gemini_direct(prompt):
    # الرابط المباشر للإصدار المستقر
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"خطأ في الاتصال: {response.status_code} - {response.text}"

# 5. الواجهة والتشغيل
with st.sidebar:
    st.header("📁 الملفات")
    pdf_files = st.file_uploader("ارفع ملفات PDF هنا", type="pdf", accept_multiple_files=True)

if pdf_files:
    context_text = get_pdf_text(pdf_files)
    question = st.chat_input("اسأل عن أي شيء في الملفات...")

    if question:
        with st.chat_message("user"):
            st.write(question)
            
        with st.chat_message("assistant"):
            with st.spinner("جاري صياغة الرد..."):
                full_prompt = f"استخدم النص التالي للإجابة باللغة العربية فقط:\n{context_text}\nالسؤال: {question}"
                answer = ask_gemini_direct(full_prompt)
                st.write(answer)
else:
    st.info("👈 يرجى رفع ملف PDF (مثل لائحة الجزاءات) للبدء.")
