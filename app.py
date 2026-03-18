import streamlit as st
import google.generativeai as genai
import PyPDF2

# إعداد واجهة التطبيق
st.set_page_config(page_title="مساعد فرع رشيد الذكي", layout="wide")

# تصميم الواجهة العربية (تصحيح الخطأ هنا)
st.markdown("""
    <style>
    .reportview-container { text-align: right; direction: rtl; }
    .stTextInput > div > div > input { text-align: right; direction: rtl; }
    div[st-html="true"] { text-align: right; direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 مساعد فرع رشيد - نظام الاستعلام")
st.info("مرحباً بك! قم برفع ملفات PDF واسأل عنها.")

# جلب مفتاح API من إعدادات الأمان في Streamlit
try:
    if "GOOGLE_API_KEY" in st.secrets:
        GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=GOOGLE_API_KEY)
    else:
        st.error("خطأ: لم يتم العثور على GOOGLE_API_KEY في Secrets.")
        st.stop()
except Exception as e:
    st.error(f"حدث خطأ في قراءة الإعدادات: {e}")
    st.stop()

# وظيفة استخراج النص
def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            content = page.extract_text()
            if content:
                text += content
        return text
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
        return ""

# القائمة الجانبية لرفع الملفات
with st.sidebar:
    st.header("📁 إدارة الملفات")
    uploaded_files = st.file_uploader("ارفع ملفات الفرع هنا", type="pdf", accept_multiple_files=True)

# منطقة المحادثة
if uploaded_files:
    all_context = ""
    for f in uploaded_files:
        all_context += extract_text_from_pdf(f)

    user_question = st.chat_input("اسأل أي سؤال حول محتوى الملفات المرفوعة...")

    if user_question:
        with st.chat_message("user"):
            st.write(user_question)

        with st.chat_message("assistant"):
            with st.spinner("جاري تحليل البيانات..."):
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"استخدم النص التالي للإجابة على السؤال باللغة العربية:\nالنص:\n{all_context}\nالسؤال: {user_question}"
                    response = model.generate_content(prompt)
                    st.write(response.text)
                except Exception as e:
                    st.error(f"حدث خطأ أثناء الاتصال بالذكاء الاصطناعي: {e}")
else:
    st.warning("👈 من فضلك ارفع ملف PDF واحد على الأقل من القائمة الجانبية للبدء.")
