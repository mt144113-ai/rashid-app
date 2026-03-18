import streamlit as st
import google.generativeai as genai
import PyPDF2

# إعدادات الصفحة
st.set_page_config(page_title="مساعد فرع رشيد", layout="wide")

# الربط بمفتاح جوجل
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("يرجى إضافة المفتاح في Secrets")
    st.stop()

# دالة قراءة الـ PDF
def extract_text(files):
    text = ""
    for f in files:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

st.title("🤖 مساعد فرع رشيد الذكي")

with st.sidebar:
    st.header("الملفات")
    uploaded_files = st.file_uploader("ارفع ملفات PDF هنا", type="pdf", accept_multiple_files=True)

if uploaded_files:
    # استخراج النص من الملفات
    context = extract_text(uploaded_files)
    
    question = st.chat_input("اسأل عن أي شيء في الملفات...")
    
    if question:
        with st.chat_message("user"):
            st.write(question)
            
        with st.chat_message("assistant"):
            try:
                # محاولة استخدام الاسم الأكثر استقراراً للموديل
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"أجب باللغة العربية بناءً على النص التالي فقط:\n{context}\nالسؤال: {question}"
                response = model.generate_content(prompt)
                
                st.write(response.text)
            except Exception as e:
                # إذا فشل، نحاول بالاسم البديل تلقائياً
                try:
                    model = genai.GenerativeModel('models/gemini-1.5-flash')
                    response = model.generate_content(prompt)
                    st.write(response.text)
                except:
                    st.error(f"حدث خطأ في الاتصال بموديل جوجل: {e}")
else:
    st.info("👈 من فضلك ارفع ملف PDF في القائمة الجانبية للبدء.")
