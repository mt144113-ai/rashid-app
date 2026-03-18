import streamlit as st
import google.generativeai as genai
import PyPDF2

# 1. إعدادات الصفحة
st.set_page_config(page_title="مساعد فرع راشد الذكي", layout="wide")

# 2. الربط بالمفتاح من الـ Secrets
if "GOOGLE_API_KEY" in st.secrets:
    # إعداد المكتبة لاستخدام واجهة REST بدلاً من gRPC لحل مشكلة الـ 404
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"], transport='rest')
else:
    st.error("يرجى إضافة GOOGLE_API_KEY في إعدادات Secrets في Streamlit Cloud")
    st.stop()

# 3. دالة استخراج النص من الـ PDF
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        try:
            pdf_reader = PyPDF2.PdfReader(pdf)
            for page in pdf_reader.pages:
                content = page.extract_text()
                if content:
                    text += content
        except Exception as e:
            st.error(f"خطأ في قراءة الملف: {e}")
    return text

# 4. واجهة المستخدم
st.title("🤖 مساعد فرع رشيد الذكي")

with st.sidebar:
    st.header("إدارة الملفات")
    pdf_files = st.file_uploader("ارفع ملفات PDF (مثل لائحة الجزاءات)", type="pdf", accept_multiple_files=True)

if pdf_files:
    # استخراج النص
    with st.spinner("جاري معالجة المستندات..."):
        context_text = get_pdf_text(pdf_files)
    
    # منطقة الدردشة
    question = st.chat_input("اسأل عن أي شيء في الملفات...")
    
    if question:
        with st.chat_message("user"):
            st.write(question)
            
        with st.chat_message("assistant"):
            try:
                # محاولة استخدام الموديل المستقر
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"أجب باللغة العربية بناءً على النص التالي فقط:\n\n{context_text}\n\nالسؤال: {question}"
                
                response = model.generate_content(prompt)
                
                if response.text:
                    st.write(response.text)
                else:
                    st.warning("تعذر الحصول على رد، قد تكون هناك قيود على المحتوى.")
                    
            except Exception as e:
                st.error(f"حدث خطأ في النظام: {e}")
                st.info("نصيحة: تأكد من أن مفتاح API الخاص بك مأخوذ من Google AI Studio ومفعل.")
else:
    st.info("👈 من فضلك ارفع ملف PDF من القائمة الجانبية للبدء.")
