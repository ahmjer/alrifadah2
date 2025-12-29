import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
import tempfile

# إعداد الصفحة - يجب أن يكون أول سطر
st.set_page_config(page_title="نظام التقييم", layout="wide")

# 1. تهيئة البيانات في الجلسة
if 'suppliers_data' not in st.session_state:
    st.session_state.suppliers_data = pd.DataFrame(columns=[
        "التاريخ", "اسم الموظف", "المورد", "الجودة", "الوقت", "السعر", "التواصل", "النتيجة النهائية"
    ])

# 2. دالة بناء ملف PDF (تدعم الإنجليزية لتجنب مشاكل الخطوط العربية حالياً)
def create_pdf(df, fig):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "Supplier Evaluation Report", ln=True, align='C')
    pdf.ln(10)
    
    # حفظ الرسم البياني كصورة وإضافته للـ PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
        fig.write_image(tmpfile.name)
        pdf.image(tmpfile.name, x=10, y=None, w=180)
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, "Summary Table:", ln=True)
    pdf.set_font("Arial", "", 10)
    
    for _, row in df.iterrows():
        line = f"Supplier: {row['المورد']} | Score: {row['النتيجة النهائية']:.1f}% | By: {row['اسم الموظف']}"
        pdf.cell(190, 8, line, border=1, ln=True)
    
    return pdf.output()

# 3. واجهة المستخدم
st.sidebar.title("🛠 التحكم")
menu = st.sidebar.radio("انتقل إلى:", ["إدخال بيانات", "عرض التقارير وتصدير PDF"])

if menu == "إدخال بيانات":
    st.header("📝 إدخال تقييم جديد")
    with st.form("input_form"):
        col1, col2 = st.columns(2)
        with col1:
            emp = st.text_input("اسم الموظف")
            sup = st.text_input("اسم المورد")
        with col2:
            q = st.number_input("الجودة (1-10)", 1, 10, 8)
            t = st.number_input("الوقت (1-10)", 1, 10, 7)
        
        if st.form_submit_button("حفظ التقييم"):
            if emp and sup:
                score = (q * 0.6 + t * 0.4) * 10
                new_data = {"التاريخ": str(datetime.now().date()), "اسم الموظف": emp, "المورد": sup, 
                            "الجودة": q, "الوقت": t, "النتيجة النهائية": score}
                st.session_state.suppliers_data = pd.concat([st.session_state.suppliers_data, pd.DataFrame([new_data])], ignore_index=True)
                st.success("تم الحفظ! انتقل الآن لصفحة التقارير للتصدير.")
            else:
                st.error("يرجى إدخال البيانات")

else:
    st.header("📊 التقارير والتصدير")
    df = st.session_state.suppliers_data
    
    if df.empty:
        st.warning("لا توجد بيانات حالياً. يرجى إضافة تقييم أولاً.")
    else:
        st.subheader("بيانات الموردين")
        st.dataframe(df, use_container_width=True)
        
        # الرسم البياني
        fig = px.bar(df, x="المورد", y="النتيجة النهائية", title="تحليل الأداء", color="النتيجة النهائية")
        st.plotly_chart(fig)
        
        st.divider()
        st.subheader("🖨 خيارات التصدير")
        
        # زر التصدير
        col_pdf, col_csv = st.columns(2)
        with col_pdf:
            if st.button("🔄 تجهيز ملف PDF"):
                with st.spinner("جاري إنشاء التقرير..."):
                    pdf_data = create_pdf(df, fig)
                    st.download_button(
                        label="📥 تحميل تقرير PDF الآن",
                        data=bytes(pdf_data),
                        file_name="Supplier_Report.pdf",
                        mime="application/pdf"
                    )
