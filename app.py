import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
import tempfile
import os

# إعداد الصفحة
st.set_page_config(page_title="نظام تقييم الموردين المتطور", layout="wide")

# تهيئة البيانات
if 'suppliers_data' not in st.session_state:
    st.session_state.suppliers_data = pd.DataFrame(columns=[
        "التاريخ", "اسم الموظف", "المورد", "الجودة", "الوقت", "السعر", "التواصل", "النتيجة النهائية"
    ])

# دالة إنشاء تقرير PDF
def generate_pdf(dataframe, plot_fig):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    
    # عنوان التقرير
    pdf.cell(190, 10, "Supplier Evaluation Report", ln=True, align='C')
    pdf.ln(10)
    
    # ملخص البيانات (جدول بسيط)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.ln(5)
    
    # تحويل الرسم البياني إلى صورة مؤقتة
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
        plot_fig.write_image(tmpfile.name)
        pdf.image(tmpfile.name, x=10, y=None, w=180)
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 10, "Summary Table:", ln=True)
    
    # إضافة البيانات كجدول
    pdf.set_font("Arial", "", 9)
    for index, row in dataframe.iterrows():
        text = f"Supplier: {row['المورد']} | Score: {row['النتيجة النهائية']:.1f}% | By: {row['اسم الموظف']}"
        pdf.cell(190, 8, text, border=1, ln=True)

    return pdf.output()

# --- واجهة التطبيق ---
st.title("🚀 نظام تقييم الموردين مع تصدير PDF")

tab1, tab2 = st.tabs(["➕ إدخال بيانات", "📊 التقارير والتصدير"])

with tab1:
    with st.form("eval_form"):
        col1, col2 = st.columns(2)
        with col1:
            emp_name = st.text_input("اسم الموظف")
            sup_name = st.text_input("اسم المورد")
        with col2:
            q = st.slider("الجودة", 1, 10, 8)
            t = st.slider("الوقت", 1, 10, 7)
        
        submitted = st.form_submit_button("حفظ التقييم")
        if submitted:
            score = (q*0.5 + t*0.5) * 10 # معادلة بسيطة
            new_row = {"التاريخ": str(datetime.now().date()), "اسم الموظف": emp_name, 
                       "المورد": sup_name, "الجودة": q, "الوقت": t, "النتيجة النهائية": score}
            st.session_state.suppliers_data = pd.concat([st.session_state.suppliers_data, pd.DataFrame([new_row])], ignore_index=True)
            st.success("تم الحفظ!")

with tab2:
    df = st.session_state.suppliers_data
    if not df.empty:
        st.write("### معاينة البيانات")
        st.dataframe(df)

        # إنشاء الرسم البياني
        fig = px.bar(df, x="المورد", y="النتيجة النهائية", color="المورد", title="مقارنة أداء الموردين")
        st.plotly_chart(fig)

        # زر تصدير PDF
        if st.button("📄 تجهيز تقرير PDF للتحميل"):
            try:
                pdf_bytes = generate_pdf(df, fig)
                st.download_button(
                    label="📥 تحميل التقرير الآن",
                    data=pdf_bytes,
                    file_name="Supplier_Report.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"حدث خطأ أثناء إنشاء PDF: {e}")
    else:
        st.info("لا توجد بيانات كافية لإصدار تقرير.")
