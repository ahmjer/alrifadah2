import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
import tempfile

# إعداد الصفحة
st.set_page_config(page_title="نظام التقييم الاحترافي", layout="wide")

# --- دالة إنشاء الـ PDF ---
def create_pdf(df, fig):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 20)
        pdf.cell(190, 20, "Supplier Evaluation Report", ln=True, align='C')
        
        # تحويل الرسم البياني لصورة
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            fig.write_image(tmpfile.name)
            pdf.image(tmpfile.name, x=10, y=40, w=180)
        
        pdf.ln(110) # مسافة بعد الصورة
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, f"Report Generated on: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
        pdf.ln(5)
        
        # جدول البيانات
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(60, 10, "Supplier", border=1, fill=True)
        pdf.cell(60, 10, "Employee", border=1, fill=True)
        pdf.cell(70, 10, "Final Score", border=1, fill=True)
        pdf.ln()
        
        pdf.set_font("Arial", "", 10)
        for _, row in df.iterrows():
            pdf.cell(60, 10, str(row['المورد']), border=1)
            pdf.cell(60, 10, str(row['اسم الموظف']), border=1)
            pdf.cell(70, 10, f"{row['النتيجة النهائية']:.1f}%", border=1)
            pdf.ln()
            
        return pdf.output()
    except Exception as e:
        return str(e)

# --- تهيئة البيانات (مع بيانات تجريبية لضمان ظهور الزر) ---
if 'suppliers_data' not in st.session_state or st.session_state.suppliers_data.empty:
    st.session_state.suppliers_data = pd.DataFrame([
        {"التاريخ": "2023-10-01", "اسم الموظف": "Admin", "المورد": "Example Supplier A", "الجودة": 9, "الوقت": 8, "النتيجة النهائية": 85.0},
        {"التاريخ": "2023-10-02", "اسم الموظف": "Admin", "المورد": "Example Supplier B", "الجودة": 7, "الوقت": 6, "النتيجة النهائية": 65.0}
    ])

st.title("📊 نظام تقييم الموردين الذكي")

# القائمة الجانبية
st.sidebar.header("لوحة التحكم")
if st.sidebar.button("🗑 مسح كافة البيانات"):
    st.session_state.suppliers_data = pd.DataFrame(columns=["التاريخ", "اسم الموظف", "المورد", "الجودة", "الوقت", "النتيجة النهائية"])
    st.rerun()

# تقسيم الشاشة
col_input, col_report = st.columns([1, 2])

with col_input:
    st.subheader("📝 إدخال جديد")
    with st.form("my_form"):
        emp = st.text_input("اسم الموظف")
        sup = st.text_input("اسم المورد")
        q_val = st.slider("درجة الجودة", 1, 10, 5)
        t_val = st.slider("درجة الوقت", 1, 10, 5)
        
        if st.form_submit_button("حفظ"):
            if emp and sup:
                score = (q_val * 0.5 + t_val * 0.5) * 10
                new_row = {"التاريخ": str(datetime.now().date()), "اسم الموظف": emp, "المورد": sup, "الجودة": q_val, "الوقت": t_val, "النتيجة النهائية": score}
                st.session_state.suppliers_data = pd.concat([st.session_state.suppliers_data, pd.DataFrame([new_row])], ignore_index=True)
                st.success("تم الحفظ!")
                st.rerun()

with col_report:
    st.subheader("📈 التقرير الحالي")
    df = st.session_state.suppliers_data
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        # الرسم البياني
        fig = px.bar(df, x="المورد", y="النتيجة النهائية", color="المورد", title="أداء الموردين")
        st.plotly_chart(fig, use_container_width=True)
        
        # منطقة التصدير
        st.markdown("---")
        st.write("### ⬇️ تصدير التقرير")
        
        if st.button("🚀 إنشاء ملف PDF"):
            with st.spinner("جاري التحضير..."):
                pdf_result = create_pdf(df, fig)
                if isinstance(pdf_result, str):
                    st.error(f"خطأ تقني: {pdf_result}")
                else:
                    st.download_button(
                        label="✅ اضغط هنا لتحميل PDF",
                        data=bytes(pdf_result),
                        file_name="Supplier_Report.pdf",
                        mime="application/pdf"
                    )
    else:
        st.info("لا توجد بيانات حالياً.")
