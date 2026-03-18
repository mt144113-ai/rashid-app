import streamlit as st
import google.generativeai as genai
import PyPDF2

# 1. إعداد الصفحة
st.set_page_config(page_title="مساعد فرع رشيد الذكي", layout="wide")

# 2. الربط بالمفتاح (Secrets)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("يرجى إضافة GOOGLE_API_KEY في Secrets")
    st.stop()

# 3. دالة استخراج النص
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PyPDF2.PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    return text

# 4. واجهة المستخدم
st.title("🤖 مساعد فرع رشيد الذكي")

with st.sidebar:
    st.header("إدارة الملفات")
    pdf_files = st.file_uploader("ارفع ملفات PDF هنا", type="pdf", accept_multiple_files=True)

if pdf_files:
    # استخراج النص من الملفات المرفوعة
    context_text = get_pdf_text(pdf_files)
    
    question = st.chat_input("اسأل عن أي شيء في الملفات...")
    
    if question:
        with st.chat_message("user"):
            st.write(question)
            
        with st.chat_message("assistant"):
            try:
                # هذا السطر هو مفتاح الحل: تحديد الإصدار المستقر v1
                model = genai.GenerativeModel(
                    model_name='gemini-1.5-flash'
                )
                
                # صياغة الطلب
                prompt = f"أجب باللغة العربية بناءً على النص المرفق فقط.\n\nالنص:\n{context_text}\n\nالسؤال: {question}"
                
                response = model.generate_content(prompt)
                st.write(response.text)
            except Exception as e:
                st.error(f"حدث خطأ في النظام: {e}")
else:
    st.info("👈 من فضلك ارفع ملف PDF في القائمة الجانبية (مثل ملف الجزاءات) للبدء.")
