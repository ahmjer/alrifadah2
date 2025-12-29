import streamlit as st
import pandas as pd
import plotly.express as px

# إعدادات الصفحة
st.set_page_config(page_title="نظام تقييم الموردين", layout="wide")

st.title("📊 لوحة تقييم أداء الموردين")
st.markdown("---")

# القسم الأول: تحديد الأوزان النسبية (Weights)
st.sidebar.header("⚙️ إعدادات المعايير (الأوزان)")
w_quality = st.sidebar.slider("الجودة (%)", 0, 100, 40)
w_delivery = st.sidebar.slider("الالتزام بالوقت (%)", 0, 100, 30)
w_price = st.sidebar.slider("تنافسية السعر (%)", 0, 100, 20)
w_support = st.sidebar.slider("التواصل والدعم (%)", 0, 100, 10)

# التأكد من أن مجموع الأوزان 100%
total_weight = w_quality + w_delivery + w_price + w_support
if total_weight != 100:
    st.sidebar.error(f"تنبيه: مجموع الأوزان حالياً {total_weight}%، يجب أن يكون 100%")

# القسم الثاني: إدخال بيانات الموردين
st.subheader("📝 إدخال بيانات الموردين")
df_input = pd.DataFrame([
    {"المورد": "مورد أ", "الجودة (10/1)": 8, "الوقت (10/1)": 7, "السعر (10/1)": 9, "التواصل (10/1)": 8},
    {"المورد": "مورد ب", "الجودة (10/1)": 6, "الوقت (10/1)": 9, "السعر (10/1)": 7, "التواصل (10/1)": 6},
])

# جدول تفاعلي لتعديل البيانات
edited_df = st.data_editor(df_input, num_rows="dynamic", use_container_width=True)

# القسم الثالث: المعالجة والحسابات
if st.button("تحليل وتقييم الموردين"):
    # حساب النتيجة النهائية بناءً على الأوزان
    edited_df['النتيجة النهائية'] = (
        (edited_df['الجودة (10/1)'] * w_quality) +
        (edited_df['الوقت (10/1)'] * w_delivery) +
        (edited_df['السعر (10/1)'] * w_price) +
        (edited_df['التواصل (10/1)'] * w_support)
    ) / 10 # للتحويل لنسبة مئوية

    st.success("تم التحديث!")

    # عرض النتائج في أعمدة
    col1, col2 = st.columns([1, 1])

    with col1:
        st.write("### ترتيب الموردين")
        st.dataframe(edited_df.sort_values(by="النتيجة النهائية", ascending=False))

    with col2:
        st.write("### مقارنة الأداء")
        fig = px.bar(edited_df, x="المورد", y="النتيجة النهائية", 
                     color="النتيجة النهائية", color_continuous_scale="RdYlGn",
                     range_y=[0, 100])
        st.plotly_chart(fig, use_container_width=True)

    # رسم بياني راداري للمقارنة التفصيلية
    st.write("### التحليل التفصيلي (Radar Chart)")
    radar_df = edited_df.melt(id_vars="المورد", value_vars=['الجودة (10/1)', 'الوقت (10/1)', 'السعر (10/1)', 'التواصل (10/1)'])
    fig_radar = px.line_polar(radar_df, r="value", theta="variable", color="المورد", line_close=True)
    st.plotly_chart(fig_radar, use_container_width=True)
