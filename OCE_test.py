import streamlit as st
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt

# Định nghĩa các cột (giữ nguyên từ trước)
columns = [
    'Tháng', 'Năm', 'Mã ĐVKD', 'Tên ĐVKD',
    'Thu nhập lãi thuần tiền gửi', 'Thu nhập lãi thuần tiền vay', 'Thu nhập lãi thuần',
    'Thu nhập từ hoạt động dịch vụ', 'Chi phí hoạt động dịch vụ', 'Lãi/ lỗ thuần từ hoạt động dịch vụ',
    'Thu từ dịch vụ thanh toán', 'Thu từ dịch vụ ngân quỹ', 'Thu từ nghiệp vụ ủy thác và đại lý',
    'Thu từ kinh doanh và dịch vụ bảo hiểm', 'Thu DV khác',
    'Lãi/ lỗ thuần từ hoạt động kinh doanh ngoại hối',
    'Lãi/ lỗ thuần từ mua bán chứng khoán kinh doanh',
    'Lãi/ lỗ thuần từ mua bán chứng khoán đầu tư',
    'Thu nhập từ hoạt động khác', 'Chi phí hoạt động khác', 'Lãi/ lỗ thuần từ hoạt động khác',
    'Thu nhập từ góp vốn, mua cổ phần',
    'Chi phí hoạt động', 'Chi nộp thuế và các khoản phí, lệ phí (trừ thuế TNDN)',
    'Chi phí cho nhân viên', 'Chi cho hoạt động quản lý và công vụ', 'Chi về tài sản',
    'Chi phí khác', 'Chi phí BHTG',
    'Lợi nhuận thuần từ hoạt động kinh doanh trước chi phí dự phòng rủi ro',
    'Chi phí dự phòng rủi ro', 'Tổng lợi nhuận trước thuế', 'Chi phí thuế TNDN', 'Lợi nhuận sau thuế'
]

# Tải dữ liệu từ Excel (thay 'financial_data.xlsx' bằng tên file thực của bạn)
try:
    df = pd.read_excel(".\[FOXAI] Bài Test - Data Analytics Engineer.xlsx", sheet_name='Data')
except FileNotFoundError:
    st.error("File 'financial_data.xlsx' không tìm thấy. Vui lòng kiểm tra lại đường dẫn.")
    st.stop()

# Streamlit App
st.title('Phân tích Tài chính Ngân hàng - Nâng cao')

# Lọc dữ liệu
st.subheader('Lọc Dữ liệu')
selected_month = st.multiselect('Chọn Tháng', df['Tháng'].unique())
selected_year = st.multiselect('Chọn Năm', df['Năm'].unique())
selected_unit = st.multiselect('Chọn Tên ĐVKD', df['Tên ĐVKD'].unique())
st.subheader('Phân tích Cơ bản')
filtered_df = df
if selected_month:
    filtered_df = filtered_df[filtered_df['Tháng'].isin(selected_month)]
if selected_year:
    filtered_df = filtered_df[filtered_df['Năm'].isin(selected_year)]
if selected_unit:
    filtered_df = filtered_df[filtered_df['Tên ĐVKD'].isin(selected_unit)]

if not filtered_df.empty:
    total_profit_after_tax = filtered_df['Lợi nhuận sau thuế'].sum()
    avg_profit = filtered_df['Lợi nhuận sau thuế'].mean()
    st.write(f'Tổng lợi nhuận sau thuế: {total_profit_after_tax:.2f} triệu VND')
    st.write(f'Trung bình lợi nhuận sau thuế: {avg_profit:.2f} triệu VND')

    # Tỷ lệ thu nhập lãi / tổng thu nhập
    total_income = filtered_df['Thu nhập lãi thuần'] + filtered_df['Lãi/ lỗ thuần từ hoạt động dịch vụ'] + filtered_df['Lãi/ lỗ thuần từ hoạt động khác']
    interest_ratio = (filtered_df['Thu nhập lãi thuần'].sum() / total_income.sum()) * 100 if total_income.sum() != 0 else 0
    st.write(f'Tỷ lệ thu nhập lãi thuần / tổng thu nhập: {interest_ratio:.2f}%')

# Hiển thị bảng dữ liệu
st.subheader('Bảng Dữ liệu')
st.dataframe(df)



# Phân tích nâng cao
st.subheader('Phân tích Nâng cao')

if not filtered_df.empty:
    # 1. Cost-to-Income Ratio
    operating_income = filtered_df['Thu nhập lãi thuần'] + filtered_df['Lãi/ lỗ thuần từ hoạt động kinh doanh ngoại hối'] + filtered_df['Lãi/ lỗ thuần từ hoạt động dịch vụ'] + filtered_df['Thu nhập từ góp vốn, mua cổ phần'] + filtered_df['Lãi/ lỗ thuần từ hoạt động kinh doanh ngoại hối'] + filtered_df['Lãi/ lỗ thuần từ mua bán chứng khoán kinh doanh'] + filtered_df['Lãi/ lỗ thuần từ mua bán chứng khoán đầu tư ']
    filtered_df['CIR'] = filtered_df['Chi phí hoạt động'] / operating_income * 100
    st.write('Cost-to-Income Ratio (%):')
    st.dataframe(filtered_df[['Tháng', 'CIR']])

    # 2. Hồi quy OLS
    if len(filtered_df) > 2:  # Cần ít nhất 3 điểm để hồi quy đáng tin
        X = filtered_df[['Thu nhập lãi thuần', 'Chi phí hoạt động']]
        X = sm.add_constant(X)
        y = filtered_df['Lợi nhuận sau thuế']
        model = sm.OLS(y, X).fit()
        st.write('Hồi quy OLS Summary:')
        st.text(model.summary())
    else:
        st.write('Dữ liệu quá ít để hồi quy đáng tin. Sử dụng dữ liệu mẫu cho minh họa.')

    # 3. Tăng trưởng lợi nhuận
    filtered_df['Tăng trưởng lợi nhuận (%)'] = filtered_df['Lợi nhuận sau thuế'].pct_change() * 100
    st.write('Tăng trưởng lợi nhuận (%):')
    st.dataframe(filtered_df[['Tháng', 'Tăng trưởng lợi nhuận (%)']])

    # 4. Variance chi phí
    chi_phi_cols = ['Chi phí cho nhân viên', 'Chi cho hoạt động quản lý và công vụ', 'Chi về tài sản', 'Chi phí khác', 'Chi phí BHTG']
    chi_phi_var = filtered_df[chi_phi_cols].var().reset_index()
    chi_phi_var.columns = ['Chi phí', 'Variance']
    st.write('Variance của các chi phí:')
    st.dataframe(chi_phi_var)

# Biểu đồ nâng cao
st.subheader('Biểu đồ Nâng cao')
if not filtered_df.empty:
    # Biểu đồ CIR
    fig_cir, ax_cir = plt.subplots()
    filtered_df.plot(x='Tháng', y='CIR', kind='bar', ax=ax_cir)
    ax_cir.set_title('Cost-to-Income Ratio Theo Tháng')
    st.pyplot(fig_cir)

    # Biểu đồ variance chi phí
    fig_var, ax_var = plt.subplots()
    chi_phi_var.plot(x='Chi phí', y='Variance', kind='bar', ax=ax_var)
    ax_var.set_title('Variance Chi phí')
    st.pyplot(fig_var)
