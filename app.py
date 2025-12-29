import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# إعداد الصفحة
st.set_page_config(page_title="إدارة الموردين", layout="wide")

# دالة إنشاء PDF لمورد واحد
def create_single_report(row):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "Supplier Evaluation Ticket", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    # محتوى التقرير
    data = [
        ["Field", "Details"],
        ["Date", str(row['التاريخ'])],
        ["Supplier Name", str(row['المورد'])],
        ["Employee", str(row['الموظف'])],
        ["Quality Score", f"{row['الجودة']}/10"],
        ["Delivery Score", f"{row['الوقت']}/10"],
        ["Final Score", f"{row['النتيجة']}%"]
    ]
    
    for item in data:
        pdf.cell(50, 10, item[0], border=1)
        pdf.cell(100, 10, item[1], border=1)
        pdf.ln()
        
    return pdf.output()

# --- البيانات ---
if 'suppliers_data' not in st.session_state:
    st.session_state.suppliers_data = pd.DataFrame([
        {"التاريخ": "2023-10-25", "المورد": "شركة النور", "الموظف": "أحمد", "الجودة": 9, "الوقت": 8, "النتيجة": 85.0},
        {"التاريخ": "2023-10-26", "المورد": "مؤسسة الأمل", "الموظف": "سارة", "الجودة": 7, "الوقت": 9, "النتيجة": 80.0}
    ])

st.title("📋 لوحة تحكم الموردين")
st.markdown("---")

# عرض البيانات مع زر تحميل لكل صف
st.subheader("التقييمات المسجلة")

# العناوين (Header)
h_col1, h_col2, h_col3, h_col4, h_col5 = st.columns([1, 2, 1, 1, 1.5])
h_col1.write("**التاريخ**")
h_col2.write("**اسم المورد**")
h_col3.write("**النتيجة**")
h_col4.write("**بواسطة**")
h_col5.write("**الإجراء**")

st.markdown("---")

# عرض الصفوف
for index, row in st.session_state.suppliers_data.iterrows():
    col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 1, 1.5])
    
    col1.write(row['التاريخ'])
    col2.write(row['المورد'])
    col3.write(f"{row['النتيجة']}%")
    col4.write(row['الموظف'])
    
    # إنشاء PDF لكل صف عند الطلب
    pdf_bytes = create_single_report(row)
    col5.download_button(
        label=f"📄 تحميل PDF ({row['المورد']})",
        data=bytes(pdf_bytes),
        file_name=f"Report_{row['المورد']}.pdf",
        mime="application/pdf",
        key=f"btn_{index}" # مفتاح فريد لكل زر
    )

# --- نموذج الإضافة في الأسفل ---
st.markdown("---")
with st.expander("➕ إضافة تقييم جديد"):
    with st.form("new_eval"):
        c1, c2 = st.columns(2)
        sup = c1.text_input("اسم المورد")
        emp = c1.text_input("اسم الموظف")
        q = c2.slider("الجودة", 1, 10, 5)
        t = c2.slider("الوقت", 1, 10, 5)
        
        if st.form_submit_button("حفظ البيانات"):
            if sup and emp:
                res = (q * 0.5 + t * 0.5) * 10
                new_entry = {
                    "التاريخ": str(datetime.now().date()), 
                    "المورد": sup, 
                    "الموظف": emp, 
                    "الجودة": q, 
                    "الوقت": t, 
                    "النتيجة": res
                }
                st.session_state.suppliers_data = pd.concat([st.session_state.suppliers_data, pd.DataFrame([new_entry])], ignore_index=True)
                st.rerun()
