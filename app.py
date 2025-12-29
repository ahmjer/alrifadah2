import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. يجب أن يكون هذا أول أمر في الكود
st.set_page_config(page_title="نظام تقييم الموردين", layout="wide")

# 2. تهيئة مخزن البيانات
if 'suppliers_data' not in st.session_state:
    st.session_state.suppliers_data = pd.DataFrame(columns=[
        "التاريخ", "اسم الموظف", "المورد", "الجودة", "الوقت", "السعر", "التواصل", "النتيجة النهائية"
    ])

# 3. القائمة الجانبية
st.sidebar.title("القائمة الرئيسية")
page = st.sidebar.selectbox("اختر الصفحة:", ["إدخال تقييم جديد", "لوحة التحكم والتقارير"])

# --- الصفحة الأولى: إدخال تقييم جديد ---
if page == "إدخال تقييم جديد":
    st.header("📝 نموذج تقييم مورد جديد")
    
    with st.form("eval_form"):
        col1, col2 = st.columns(2)
        with col1:
            emp_name = st.text_input("اسم الموظف")
            sup_name = st.text_input("اسم المورد")
        with col2:
            eval_date = st.date_input("تاريخ التقييم", datetime.now())
        
        st.write("---")
        st.write("⭐ درجات التقييم (من 1 إلى 10)")
        c1, c2, c3, c4 = st.columns(4)
        q = c1.number_input("الجودة", 1, 10, 5)
        t = c2.number_input("الوقت", 1, 10, 5)
        p = c3.number_input("السعر", 1, 10, 5)
        s = c4.number_input("التواصل", 1, 10, 5)
        
        submitted = st.form_submit_button("حفظ التقييم")
        
        if submitted:
            if emp_name and sup_name:
                score = (q*0.4 + t*0.3 + p*0.2 + s*0.1) * 10
                new_row = {
                    "التاريخ": str(eval_date), "اسم الموظف": emp_name, 
                    "المورد": sup_name, "الجودة": q, "الوقت": t, 
                    "السعر": p, "التواصل": s, "النتيجة النهائية": score
                }
                st.session_state.suppliers_data = pd.concat([st.session_state.suppliers_data, pd.DataFrame([new_row])], ignore_index=True)
                st.success("تم الحفظ بنجاح!")
            else:
                st.warning("يرجى ملء جميع الحقول")

# --- الصفحة الثانية: التقارير ---
else:
    st.header("📊 التقارير والإحصائيات")
    df = st.session_state.suppliers_data
    
    if df.empty:
        st.info("لا توجد بيانات حالياً.")
    else:
        # فلترة حسب الموظف
        all_emps = ["الكل"] + list(df["اسم الموظف"].unique())
        selected_emp = st.selectbox("عرض تقارير موظف معين:", all_emps)
        
        filtered_df = df if selected_emp == "الكل" else df[df["اسم الموظف"] == selected_emp]
        
        st.dataframe(filtered_df, use_container_width=True)
        
        # رسم بياني بسيط
        fig = px.bar(filtered_df, x="المورد", y="النتيجة النهائية", color="المورد", title="أداء الموردين")
        st.plotly_chart(fig)
        
        # زر التحميل
        csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل التقرير CSV", csv, "report.csv", "text/csv")
