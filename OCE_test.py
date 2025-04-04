import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Thiết lập trang
st.set_page_config(layout="wide", page_title="Dashboard Phân Tích Doanh Thu")

# Tạo CSS cho trang
st.markdown("""
<style>
.main-header {
    font-size: 28px;
    font-weight: bold;
    color: #1E3A8A;
    text-align: center;
    margin-bottom: 20px;
    padding: 10px;
    background-color: #F0F7FF;
    border-radius: 5px;
}
.sub-header {
    font-size: 20px;
    font-weight: bold;
    color: #1E3A8A;
    margin-top: 15px;
    margin-bottom: 10px;
}
.card {
    background-color: #F8FAFC;
    border-radius: 5px;
    padding: 15px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}
.metric-card {
    background-color: #EFF6FF;
    border-radius: 5px;
    padding: 10px;
    text-align: center;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}
.metric-value {
    font-size: 24px;
    font-weight: bold;
    color: #2563EB;
}
.metric-label {
    font-size: 14px;
    color: #475569;
}
</style>
""", unsafe_allow_html=True)

# Tiêu đề trang
st.markdown('<div class="main-header">DASHBOARD PHÂN TÍCH DOANH THU</div>', unsafe_allow_html=True)

# Đọc dữ liệu
@st.cache_data
def load_data():
    file_path = "OCR_test.xlsx"
    df = pd.read_excel(file_path, skiprows=0)
    
    df['Trước ưu đãi'] = pd.to_numeric(df['Trước ưu đãi'], errors='coerce')
    df['Sau ưu đãi'] = pd.to_numeric(df['Sau ưu đãi'], errors='coerce')
    df['% Ưu đãi'] = pd.to_numeric(df['% Ưu đãi'], errors='coerce')
    df['Số tháng học dự kiến'] = pd.to_numeric(df['Số tháng học dự kiến'], errors='coerce')
    
    df['Trước ưu đãi'] = df['Trước ưu đãi'].abs()
    df['Sau ưu đãi'] = df['Sau ưu đãi'].abs()
    df['Số tháng học dự kiến'] = df['Số tháng học dự kiến'].abs()
    
    df['Ngày thanh toán'] = pd.to_datetime(df['Ngày thanh toán'], errors='coerce')
    df['Tháng'] = df['Ngày thanh toán'].dt.to_period('M')
    df['Tháng_str'] = df['Tháng'].astype(str)
    
    return df

df = load_data()

# Các bộ lọc trong sidebar
st.sidebar.markdown("### Bộ lọc dữ liệu")

branch_container = st.sidebar.expander("Chi nhánh", expanded=True)
selected_branch = branch_container.selectbox(
    "Chọn chi nhánh:",
    options=["Tất cả"] + df['Chi nhánh'].unique().tolist(),
    index=0
)

program_container = st.sidebar.expander("Chương trình học", expanded=True)
selected_program = program_container.selectbox(
    "Chọn chương trình học:",
    options=["Tất cả"] + df['Chương trình học'].unique().tolist(),
    index=0
)

time_container = st.sidebar.expander("Thời gian", expanded=True)
min_date = df['Ngày thanh toán'].min().date() if not pd.isna(df['Ngày thanh toán'].min()) else datetime(2023, 1, 1).date()
max_date = df['Ngày thanh toán'].max().date() if not pd.isna(df['Ngày thanh toán'].max()) else datetime.now().date()

start_date = time_container.date_input("Từ ngày:", min_date, min_value=min_date, max_value=max_date)
end_date = time_container.date_input("Đến ngày:", max_date, min_value=min_date, max_value=max_date)

# Lọc dữ liệu dựa trên các bộ lọc đã chọn
filtered_df = df[
    (df['Ngày thanh toán'].dt.date >= start_date) &
    (df['Ngày thanh toán'].dt.date <= end_date)
]

if selected_branch != "Tất cả":
    filtered_df = filtered_df[filtered_df['Chi nhánh'] == selected_branch]

if selected_program != "Tất cả":
    filtered_df = filtered_df[filtered_df['Chương trình học'] == selected_program]

# Hiển thị dữ liệu gốc (nếu muốn)
if st.sidebar.checkbox("Hiển thị dữ liệu gốc"):
    st.subheader("Dữ liệu ban đầu")
    st.dataframe(filtered_df.head(50))

# Tính toán các chỉ số tổng quát
total_before = filtered_df['Trước ưu đãi'].sum()
total_after = filtered_df['Sau ưu đãi'].sum()
discount_amount = total_before - total_after
discount_percentage = (discount_amount / total_before * 100) if total_before > 0 else 0
total_students = filtered_df['Ngày thanh toán'].count()

# Tính toán chương trình học có nhiều học viên nhất
program_student_count = filtered_df.groupby('Chương trình học')['Ngày thanh toán'].count().reset_index()
program_student_count.columns = ['Chương trình học', 'Số học viên']
most_popular_program = program_student_count.loc[program_student_count['Số học viên'].idxmax()]
most_popular_program_name = most_popular_program['Chương trình học']
most_popular_program_students = most_popular_program['Số học viên']

# Hiển thị các thông số tổng quan
st.markdown('<div class="sub-header">TỔNG QUAN</div>', unsafe_allow_html=True)
metric_cols = st.columns(5)  # Tăng từ 4 lên 5 cột

with metric_cols[0]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_after:,.0f} VND</div>
        <div class="metric-label">Doanh thu sau ưu đãi</div>
    </div>
    """, unsafe_allow_html=True)

with metric_cols[1]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_before:,.0f} VND</div>
        <div class="metric-label">Doanh thu trước ưu đãi</div>
    </div>
    """, unsafe_allow_html=True)

with metric_cols[2]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{discount_percentage:.2f}%</div>
        <div class="metric-label">Tỷ lệ ưu đãi</div>
    </div>
    """, unsafe_allow_html=True)

with metric_cols[3]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_students}</div>
        <div class="metric-label">Số học viên</div>
    </div>
    """, unsafe_allow_html=True)

with metric_cols[4]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{most_popular_program_name}</div>
        <div class="metric-label">Khóa học đông nhất ({most_popular_program_students} học viên)</div>
    </div>
    """, unsafe_allow_html=True)

# Chia bố cục cho biểu đồ
st.markdown('<div class="sub-header">PHÂN TÍCH DOANH THU</div>', unsafe_allow_html=True)

# Hàng 1: Xu hướng doanh thu theo thời gian và phân bố hình thức thanh toán
row1_col1, row1_col2 = st.columns([3, 1])

with row1_col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    revenue_by_month = filtered_df.groupby('Tháng_str').agg({
        'Trước ưu đãi': 'sum',
        'Sau ưu đãi': 'sum'
    }).reset_index()

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=revenue_by_month['Tháng_str'], y=revenue_by_month['Trước ưu đãi'], 
                            mode='lines+markers', name='Trước ưu đãi', line=dict(color='#64748b')))
    fig1.add_trace(go.Scatter(x=revenue_by_month['Tháng_str'], y=revenue_by_month['Sau ưu đãi'], 
                            mode='lines+markers', name='Sau ưu đãi', line=dict(color='#3b82f6')))
    fig1.update_layout(
        title='Xu hướng Doanh thu Theo Tháng',
        xaxis_title='Tháng',
        yaxis_title='Doanh thu (VND)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=40, b=20),
        height=300
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with row1_col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    payment_method_data = filtered_df.groupby('Hình thức thanh toán').agg({
        'Sau ưu đãi': 'sum'
    }).reset_index()
    fig3 = px.pie(
        payment_method_data, 
        names='Hình thức thanh toán', 
        values='Sau ưu đãi',
        title='Tỷ lệ Theo Hình thức Thanh toán',
        color_discrete_sequence=px.colors.sequential.Blues_r
    )
    fig3.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=300
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Hàng 2: Chi nhánh và chương trình học
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    revenue_by_branch = filtered_df.groupby('Chi nhánh').agg({
        'Trước ưu đãi': 'sum',
        'Sau ưu đãi': 'sum'
    }).reset_index()
    revenue_by_branch['Giá trị ưu đãi'] = revenue_by_branch['Trước ưu đãi'] - revenue_by_branch['Sau ưu đãi']
    revenue_by_branch = revenue_by_branch.sort_values('Sau ưu đãi')

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        y=revenue_by_branch['Chi nhánh'], 
        x=revenue_by_branch['Trước ưu đãi'],
        name='Trước ưu đãi', 
        orientation='h',
        marker_color='#cbd5e1'
    ))
    fig2.add_trace(go.Bar(
        y=revenue_by_branch['Chi nhánh'], 
        x=revenue_by_branch['Sau ưu đãi'],
        name='Sau ưu đãi', 
        orientation='h',
        marker_color='#2563eb'
    ))
    fig2.update_layout(
        title='Doanh thu Theo Chi Nhánh', 
        xaxis_title='Doanh thu (VND)',
        barmode='group',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=40, b=20),
        height=350
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with row2_col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    revenue_by_program = filtered_df.groupby('Chương trình học').agg({
        'Trước ưu đãi': 'sum',
        'Sau ưu đãi': 'sum'
    }).reset_index()
    revenue_by_program['Giá trị ưu đãi'] = revenue_by_program['Trước ưu đãi'] - revenue_by_program['Sau ưu đãi']
    revenue_by_program = revenue_by_program.sort_values('Sau ưu đãi')

    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        y=revenue_by_program['Chương trình học'], 
        x=revenue_by_program['Trước ưu đãi'],
        name='Trước ưu đãi', 
        orientation='h',
        marker_color='#cbd5e1'
    ))
    fig4.add_trace(go.Bar(
        y=revenue_by_program['Chương trình học'], 
        x=revenue_by_program['Sau ưu đãi'],
        name='Sau ưu đãi', 
        orientation='h',
        marker_color='#2563eb'
    ))
    fig4.update_layout(
        title='Doanh thu Theo Chương trình Học', 
        xaxis_title='Doanh thu (VND)',
        barmode='group',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=40, b=20),
        height=350
    )
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Hàng 3: Phân tích hiệu quả ưu đãi và doanh thu trung bình mỗi học viên
st.markdown('<div class="sub-header">PHÂN TÍCH HIỆU QUẢ KINH DOANH</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Hiệu quả ưu đãi", "Doanh thu trung bình / học viên"])

with tab1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    discount_analysis = filtered_df.groupby('Chương trình học').agg({
        'Trước ưu đãi': 'sum',
        'Sau ưu đãi': 'sum',
        'Ngày thanh toán': 'count'
    }).reset_index()
    discount_analysis['Giá trị ưu đãi'] = discount_analysis['Trước ưu đãi'] - discount_analysis['Sau ưu đãi']
    discount_analysis['% Ưu đãi thực tế'] = (discount_analysis['Giá trị ưu đãi'] / discount_analysis['Trước ưu đãi'] * 100).round(2)
    discount_analysis['Số học viên'] = discount_analysis['Ngày thanh toán']
    discount_analysis = discount_analysis.drop(columns=['Ngày thanh toán'])
    discount_analysis = discount_analysis.sort_values('% Ưu đãi thực tế', ascending=False)
    
    discount_analysis['Trước ưu đãi'] = discount_analysis['Trước ưu đãi'].apply(lambda x: f"{x:,.0f}")
    discount_analysis['Sau ưu đãi'] = discount_analysis['Sau ưu đãi'].apply(lambda x: f"{x:,.0f}")
    discount_analysis['Giá trị ưu đãi'] = discount_analysis['Giá trị ưu đãi'].apply(lambda x: f"{x:,.0f}")
    discount_analysis['% Ưu đãi thực tế'] = discount_analysis['% Ưu đãi thực tế'].apply(lambda x: f"{x:.2f}%")

    st.write(discount_analysis)
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    avg_revenue = filtered_df.groupby('Chương trình học').agg({
        'Sau ưu đãi': 'sum',
        'Ngày thanh toán': 'count'
    }).reset_index()
    avg_revenue['Doanh thu TB/học viên'] = (avg_revenue['Sau ưu đãi'] / avg_revenue['Ngày thanh toán']).round(0)
    avg_revenue = avg_revenue[['Chương trình học', 'Doanh thu TB/học viên', 'Ngày thanh toán']]
    avg_revenue.columns = ['Chương trình học', 'Doanh thu TB/học viên', 'Số học viên']
    avg_revenue = avg_revenue.sort_values('Doanh thu TB/học viên', ascending=False)

    fig6 = px.bar(
        avg_revenue, 
        x='Doanh thu TB/học viên', 
        y='Chương trình học', 
        orientation='h',
        text='Doanh thu TB/học viên', 
        color='Số học viên',
        color_continuous_scale='Blues',
        labels={'Doanh thu TB/học viên': 'Doanh thu TB/học viên (VND)'}
    )
    fig6.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    fig6.update_layout(height=400)
    st.plotly_chart(fig6, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Chân trang
st.markdown("""
<div style='text-align: center; color: #94a3b8; padding: 20px;'>
    © 2025 • Dashboard Phân Tích Doanh Thu
</div>
""", unsafe_allow_html=True)