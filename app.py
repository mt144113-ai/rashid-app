import os
os.environ["GOOGLE_API_USE_MTLS_ENDPOINT"] = "never" # حل مشكلة الاتصال في بعض السيرفرات

import streamlit as st
import google.generativeai as genai
import PyPDF2

# إعداد الصفحة
st.set_page_config(page_title="مساعد فرع راشد الذكي", layout="wide")

# الربط بالمفتاح
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("يرجى إضافة المفتاح في Secrets")
    st.stop()

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PyPDF2.PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    return text

st.title("🤖 مساعد فرع رشيد الذكي")

with st.sidebar:
    st.header("إدارة الملفات")
    pdf_files = st.file_uploader("ارفع ملفات PDF هنا", type="pdf", accept_multiple_files=True)

if pdf_files:
    context_text = get_pdf_text(pdf_files)
    
    question = st.chat_input("اسأل عن أي شيء في الملفات...")
    
    if question:
        with st.chat_message("user"):
            st.write(question)
            
        with st.chat_message("assistant"):
            try:
                # محاولة مناداة الموديل بالاسم المختصر والأكثر استقراراً
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # استخدام أسلوب توليد المحتوى المباشر
                response = model.generate_content(
                    f"أجب باللغة العربية بناءً على النص التالي فقط:\n{context_text}\nالسؤال: {question}"
                )
                st.write(response.text)
            except Exception as e:
                # إذا فشل، نحاول بالاسم الكامل كخطة بديلة
                try:
                    model = genai.GenerativeModel('models/gemini-1.5-flash')
                    response = model.generate_content(f"اجب بالعربية:\n{context_text}\nالسؤال: {question}")
                    st.write(response.text)
                except:
                    st.error(f"حدث خطأ في الاتصال بموديل جوجل: {e}")
else:
    st.info("👈 من فضلك ارفع ملف PDF للبدء.")
