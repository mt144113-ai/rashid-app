import streamlit as st
import google.generativeai as genai
import PyPDF2

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="مساعد فرع رشيد الذكي", layout="wide")

# 2. تحسين واجهة المستخدم لتدعم اللغة العربية (RTL)
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    .stMarkdown, .stText, .stTitle, .stHeader, .stCaption { text-align: right; direction: rtl; }
    div[data-testid="stSidebar"] { direction: rtl; }
    .stChatInput { direction: ltr; } /* صندوق الكتابة يفضل لتر لسهولة الإدخال المختلط */
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 مساعد فرع رشيد - نظام الاستعلام")
st.info("مرحباً بك! قم برفع ملفات PDF (مثل ملفات الأصناف أو اللوائح) واسأل عنها.")

# 3. جلب مفتاح API من إعدادات Streamlit Secrets
try:
    if "GOOGLE_API_KEY" in st.secrets:
        GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=GOOGLE_API_KEY)
    else:
        st.error("⚠️ خطأ: لم يتم العثور على مفتاح GOOGLE_API_KEY. يرجى إضافته في Settings > Secrets")
        st.stop()
except Exception as e:
    st.error(f"❌ حدث خطأ في النظام: {e}")
    st.stop()

# 4. وظيفة استخراج النصوص من ملفات PDF
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
        st.error(f"حدث خطأ أثناء قراءة الملف {pdf_file.name}: {e}")
        return ""

# 5. القائمة الجانبية (Sidebar)
with st.sidebar:
    st.header("📁 إدارة ملفات فرع رشيد")
    uploaded_files = st.file_uploader("ارفع ملفاتك هنا (PDF)", type="pdf", accept_multiple_files=True)
    if uploaded_files:
        st.success(f"تم تحميل {len(uploaded_files)} ملف/ملفات")

# 6. منطقة المحادثة ومعالجة الأسئلة
if uploaded_files:
    # تجميع كل النصوص من الملفات المرفوعة
    with st.spinner("جاري قراءة الملفات..."):
        all_context = ""
        for f in uploaded_files:
            all_context += extract_text_from_pdf(f)

    # استقبال سؤال المستخدم
    user_question = st.chat_input("اسأل أي سؤال حول محتوى الملفات المرفوعة...")

    if user_question:
        # عرض سؤال المستخدم
        with st.chat_message("user"):
            st.write(user_question)

        # توليد الرد من الذكاء الاصطناعي
        with st.chat_message("assistant"):
            with st.spinner("جاري البحث في المستندات وصياغة الرد..."):
                try:
                    # تعديل اسم الموديل ليعمل بشكل صحيح
                    model = genai.GenerativeModel('models/gemini-1.5-flash')
                    
                    # صياغة التعليمات (Prompt)
                    full_prompt = f"""
                    أنت مساعد خبير لفرع صيدلية (فرع رشيد). 
                    أجب على السؤال التالي بناءً على المعلومات الموجودة في النص المرفق فقط.
                    إذا لم تجد الإجابة، قل بكل أدب أن المعلومة غير متوفرة في المستندات الحالية.
                    
                    النص المرجعي:
                    {all_context}
                    
                    السؤال:
                    {user_question}
                    """
                    
                    response = model.generate_content(full_prompt)
                    st.write(response.text)
                except Exception as e:
                    st.error(f"حدث خطأ أثناء الاتصال بالموديل: {e}")
else:
    st.warning("👈 يرجى رفع ملفات الـ PDF الخاصة بالفرع من القائمة الجانبية للبدء.")

# تذييل الصفحة
st.markdown("---")
st.caption("تطبيق مساعد فرع رشيد الذكي v1.1 - يعمل بواسطة Gemini AI")
