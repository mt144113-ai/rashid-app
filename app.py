import streamlit as st
import google.generativeai as genai
import PyPDF2

# 1. إعدادات الصفحة
st.set_page_config(page_title="مساعد فرع رشيد الذكي", layout="wide")

# 2. تنسيق الواجهة العربية
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    .stMarkdown, .stText, .stTitle, .stHeader, .stCaption { text-align: right; direction: rtl; }
    div[data-testid="stSidebar"] { direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 مساعد فرع رشيد - نظام الاستعلام")

# 3. الربط بـ API (تأكد من وجوده في Secrets)
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.error("⚠️ يرجى إضافة GOOGLE_API_KEY في إعدادات Secrets")
        st.stop()
except Exception as e:
    st.error(f"❌ خطأ في النظام: {e}")
    st.stop()

# 4. استخراج النص من الـ PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

# 5. القائمة الجانبية
with st.sidebar:
    st.header("📁 الملفات")
    uploaded_files = st.file_uploader("ارفع ملفات PDF هنا", type="pdf", accept_multiple_files=True)

# 6. المعالجة والرد
if uploaded_files:
    with st.spinner("جاري معالجة الملفات الكبيرة..."):
        all_context = ""
        for f in uploaded_files:
            all_context += extract_text_from_pdf(f)

    user_question = st.chat_input("اسأل أي سؤال عن محتوى الملفات...")

    if user_question:
        with st.chat_message("user"):
            st.write(user_question)

        with st.chat_message("assistant"):
            try:
                # التعديل الهام هنا: استخدام اسم الموديل المحدث
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                
                prompt = f"أجب باللغة العربية بناءً على النص فقط:\nالنص:\n{all_context}\nالسؤال: {user_question}"
                response = model.generate_content(prompt)
                st.write(response.text)
            except Exception as e:
                st.error(f"حدث خطأ: {e}")
else:
    st.warning("👈 ارفع ملف PDF للبدء.")
