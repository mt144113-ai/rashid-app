import streamlit as st
import requests
import PyPDF2
import json

# إعداد واجهة التطبيق
st.set_page_config(page_title="مساعد فرع رشيد الذكي", layout="wide")

st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    .stMarkdown, .stText, .stTitle, .stHeader, .stCaption { text-align: right; direction: rtl; }
    div[data-testid="stSidebar"] { direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 مساعد فرع رشيد الذكي")

# جلب المفتاح من Secrets
if "GOOGLE_API_KEY" in st.secrets:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("⚠️ يرجى إضافة المفتاح في Secrets")
    st.stop()

# دالة استخراج النص
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        try:
            pdf_reader = PyPDF2.PdfReader(pdf)
            for page in pdf_reader.pages:
                content = page.extract_text()
                if content: text += content
        except: continue
    return text

# القائمة الجانبية
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
                # نداء مباشر لرابط API المستقر v1 (بدون بيتا)
                url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
                
                payload = {
                    "contents": [{
                        "parts": [{"text": f"استخدم النص التالي للإجابة بالعربية فقط:\n{context_text}\n\nالسؤال: {question}"}]
                    }]
                }
                
                try:
                    response = requests.post(url, json=payload, timeout=30)
                    if response.status_code == 200:
                        result = response.json()
                        answer = result['candidates'][0]['content']['parts'][0]['text']
                        st.write(answer)
                    else:
                        st.error(f"خطأ من سيرفر جوجل (كود {response.status_code})")
                        st.info("تأكد أن مفتاح API صحيح ومفعل في Google AI Studio.")
                except Exception as e:
                    st.error(f"حدث خطأ في الاتصال: {e}")
else:
    st.info("👈 يرجى رفع ملف PDF للبدء.")
