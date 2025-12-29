import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="نظام إدارة وتقييم الموردين", layout="wide")

# تهيئة مخزن البيانات (في الجلسة الحالية)
if 'suppliers_data' not in st.session_state:
    # بيانات تجريبية أولية
    st.session_state.suppliers_data = pd.DataFrame(columns=[
        "التاريخ", "اسم الموظف", "المورد", "الجودة", "الوقت", "السعر", "التواصل", "النتيجة النهائية"
    ])

# القائمة الجانبية للتنقل
st.sidebar.title("🗂 القائمة الرئيسية")
page = st.sidebar.radio("انتقل إلى:", ["لوحة التحكم (الإحصائيات)", "إدخال تقييم جديد", "تقارير الموظفين"])

# --- الصفحة الأولى: إدخال تقييم جديد ---
if page == "إدخال تقييم جديد":
    st.header("📝 نموذج تقييم مورد جديد")
    
    with st.form("evaluation_form"):
        col1, col2 = st.columns(2)
        with col1:
            employee_name = st.text_input("اسم الموظف القائم بالتقييم")
            supplier_name = st.text_input("اسم المورد")
        with col2:
            date_eval = st.date_input("تاريخ التقييم", datetime.now())
            
        st.markdown("---")
        st.write("⭐ **درجات التقييم (من 1 إلى 10):**")
        c1, c2, c3, c4 = st.columns(4)
        q = c1.slider("الجودة", 1, 10, 5)
        t = c2.slider("الالتزام بالوقت", 1, 10, 5)
        p = c3.slider("السعر", 1, 10, 5)
        s = c4.slider("التواصل", 1, 10, 5)
        
        submit = st.form_submit_button("حفظ التقييم")
        
        if submit:
            if employee_name and supplier_name:
                # حساب النتيجة (بافتراض أوزان متساوية أو ثابتة)
                final_score = (q * 0.4 + t * 0.3 + p * 0.2 + s * 0.1) * 10
                
                new_data = {
                    "التاريخ": date_eval,
                    "اسم الموظف": employee_name,
                    "المورد": supplier_name,
                    "الجودة": q,
                    "الوقت": t,
                    "السعر": p,
                    "التواصل": s,
                    "النتيجة النهائية": final_score
                }
                
                st.session_state.suppliers_data = pd.concat([st.session_state.suppliers_data, pd.DataFrame([new_data])], ignore_index=True)
                st.success(f"تم حفظ تقييم المورد '{supplier_name}' بنجاح!")
            else:
                st.error("يرجى إكمال اسم الموظف والمورد")

# --- الصفحة الثانية: لوحة التحكم ---
elif page == "لوحة التحكم (الإحصائيات)":
    st.header("📊 تحليل أداء الموردين العام")
    
    if st.session_state.suppliers_data.empty:
        st.info("لا توجد بيانات حالياً. قم بإضافة تقييمات من صفحة 'إدخال تقييم جديد'.")
    else:
        df = st.session_state.suppliers_data
        
        # ملخص سريع
        c1, c2, c3 = st.columns(3)
        c1.metric("عدد الموردين", df["المورد"].nunique())
        c2.metric("إجمالي التقييمات", len(df))
        c3.metric("متوسط الأداء العام", f"{df['النتيجة النهائية'].mean():.1f}%")

        # رسم بياني لأفضل الموردين
        fig = px.bar(df.groupby("المورد")["النتيجة النهائية"].mean().reset_index(), 
                     x="المورد", y="النتيجة النهائية", title="متوسط أداء الموردين",
                     color="النتيجة النهائية", color_continuous_scale="RdYlGn")
        st.plotly_chart(fig, use_container_width=True)

# --- الصفحة الثالثة: تقارير الموظفين ---
elif page == "تقارير الموظفين":
    st.header("📋 استخراج تقارير التقييم")
    
    if st.session_state.suppliers_data.empty:
        st.info("لا توجد بيانات لاستخراج التقارير.")
    else:
        df = st.session_state.suppliers_data
        
        # تصفية حسب الموظف
        employees = ["الكل"] + list(df["اسم الموظف"].unique())
        selected_emp = st.selectbox("اختر الموظف لعرض تقييماته:", employees)
        
        if selected_emp == "الكل":
            report_df = df
        else:
            report_df = df[df["اسم الموظف"] == selected_emp]
            
        st.write(f"### التقييمات التي أجراها: {selected_emp}")
        st.dataframe(report_df, use_container_width=True)
        
        # تصدير التقرير
        csv = report_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 تحميل التقرير (Excel/CSV)",
            data=csv,
            file_name=f"تقرير_تقييم_{selected_emp}_{datetime.now().date()}.csv",
            mime='text/csv',
        )

st.sidebar.markdown("---")
st.sidebar.info("ملاحظة: هذه البيانات تُحفظ في الجلسة الحالية. لتخزين دائم، يجب ربط التطبيق بقاعدة بيانات أو Google Sheets.")
