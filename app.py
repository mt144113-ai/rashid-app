import streamlit as st
import google.generativeai as genai
from google.generativeai.types import RequestOptions
import PyPDF2

# 1. إعدادات الصفحة
st.set_page_config(page_title="مساعد فرع رشيد الذكي", layout="wide")

# 2. الربط بالمفتاح (Secrets)
if "GOOGLE_API_KEY" in st.secrets:
    # تهيئة المكتبة مع فرض استخدام بروتوكول REST فقط
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"], transport='rest')
else:
    st.error("يرجى إضافة GOOGLE_API_KEY في إعدادات Secrets")
    st.stop()

# 3. دالة استخراج النص
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        try:
            pdf_reader = PyPDF2.PdfReader(pdf)
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
        except:
            continue
    return text

# 4. الواجهة
st.title("🤖 مساعد فرع رشيد الذكي")

with st.sidebar:
    st.header("الملفات")
    pdf_files = st.file_uploader("ارفع ملفات PDF هنا", type="pdf", accept_multiple_files=True)

if pdf_files:
    context_text = get_pdf_text(pdf_files)
    question = st.chat_input("اسأل عن أي شيء في الملفات...")

    if question:
        with st.chat_message("user"):
            st.write(question)
            
        with st.chat_message("assistant"):
            try:
                # السر هنا: إجبار الموديل على استخدام الإصدار v1 الصريح
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # استخدام خيارات طلب صريحة لتجاوز الإصدارات التجريبية
                response = model.generate_content(
                    f"استخدم النص التالي للإجابة باللغة العربية فقط:\n{context_text}\nالسؤال: {question}",
                    request_options=RequestOptions(api_version='v1')
                )
                
                st.write(response.text)
            except Exception as e:
                st.error(f"حدث خطأ في النظام: {e}")
                st.info("نصيحة: إذا استمر الخطأ، يرجى تجربة إنشاء مفتاح API جديد من Google AI Studio.")
else:
    st.info("👈 يرجى رفع ملف PDF (مثل لائحة الجزاءات) للبدء.")
