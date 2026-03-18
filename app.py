import streamlit as st
import google.generativeai as genai
import PyPDF2

st.set_page_config(page_title="مساعد فرع رشيد", layout="wide")

# إعداد الربط
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("يرجى إضافة المفتاح في Secrets")
    st.stop()

# دالة قراءة الملف
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PyPDF2.PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

st.title("🤖 مساعد فرع رشيد")

with st.sidebar:
    st.header("إدارة الملفات")
    pdf_files = st.file_uploader("ارفع ملفات PDF", type="pdf", accept_multiple_files=True)

if pdf_files:
    # استخراج النص
    raw_text = get_pdf_text(pdf_files)
    
    user_question = st.chat_input("اسأل عن محتوى الملفات...")
    
    if user_question:
        with st.chat_message("user"):
            st.write(user_question)
            
        with st.chat_message("assistant"):
            try:
                # المحاولة باستخدام الاسم الأساسي للموديل
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(f"اجب بالعربية بناء على النص التالي:\n{raw_text}\nالسؤال: {user_question}")
                st.write(response.text)
            except Exception as e:
                st.error(f"حدث خطأ: {e}")
else:
    st.info("👈 يرجى رفع ملف PDF للبدء")
