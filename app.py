import streamlit as st
import google.generativeai as genai
import PyPDF2

# إعداد واجهة التطبيق
st.set_page_config(page_title="مساعد فرع رشيد الذكي", layout="wide")

# تصميم الواجهة العربية
st.markdown("""
    <style>
    .reportview-container { text-align: right; direction: rtl; }
    .stTextInput > div > div > input { text-align: right; direction: rtl; }
    </style>
    """, unsafe_allow_stdio=True)

st.title("🤖 مساعد فرع رشيد - نظام الاستعلام عن المستندات")
st.info("مرحباً بك! قم برفع ملفات PDF (لوائح، جداول، أو تعليمات) واسأل عنها.")

# جلب مفتاح API من إعدادات الأمان في Streamlit
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except:
    st.error("خطأ: لم يتم ضبط 'GOOGLE_API_KEY' في إعدادات Secrets.")
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
    if uploaded_files:
        st.success(f"تم تحميل {len(uploaded_files)} ملفات")

# منطقة المحادثة
if uploaded_files:
    # دمج نصوص كافة الملفات
    all_context = ""
    for f in uploaded_files:
        all_context += extract_text_from_pdf(f)

    user_question = st.chat_input("اسأل أي سؤال حول محتوى الملفات المرفوعة...")

    if user_question:
        with st.chat_message("user"):
            st.write(user_question)

        with st.chat_message("assistant"):
            with st.spinner("جاري تحليل البيانات..."):
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # بناء البرومبت الاحترافي
                prompt = f"""
                أنت مساعد ذكي مخصص لخدمة فريق عمل "فرع رشيد". 
                مهمتك هي الإجابة على أسئلة الموظفين بناءً على النص المرفق فقط.
                
                القواعد:
                1. استخدم اللغة العربية بأسلوب مهني وواضح.
                2. إذا كانت المعلومة غير موجودة في النص، قل بكل أدب: "عذراً، لم أجد إجابة لهذا السؤال في المستندات المرفوعة".
                3. كن دقيقاً جداً في الأرقام والمواعيد.
                
                النص المرجعي:
                {all_context}
                
                سؤال الموظف:
                {user_question}
                """
                
                try:
                    response = model.generate_content(prompt)
                    st.write(response.text)
                except Exception as e:
                    st.error("حدث خطأ أثناء الاتصال بالذكاء الاصطناعي.")
else:
    st.warning("👈 من فضلك ارفع ملف PDF واحد على الأقل من القائمة الجانبية للبدء.")
