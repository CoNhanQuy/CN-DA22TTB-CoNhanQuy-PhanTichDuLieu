%%writefile app.py
import streamlit as st
import pandas as pd
import datetime as dt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Universal Sales Analytics", layout="wide", page_icon="🕵️‍♀️")

# --- 1. CÁC HÀM XỬ LÝ (CORE FUNCTIONS) ---

def smart_map_columns(df):
    """Tự động nhận diện tên cột thông minh"""
    cols = df.columns
    mapping = {}
    keywords = {
        'date': ['date', 'time', 'ngay', 'thoi_gian', 'invoice_date', 'day'],
        'price': ['total sales', 'amount', 'total', 'money', 'tien', 'price', 'gia', 'doanh_thu', 'sales'],
        'quantity': ['qty', 'quantity', 'so_luong', 'sl', 'num', 'count', 'units sold', 'units'],
        'customer': ['retailer id', 'cust', 'customer', 'khach', 'member', 'user', 'id'],
        'product': ['product', 'desc', 'item', 'hang', 'ten', 'sku', 'stockcode'],
        'country': ['country', 'nation', 'quoc_gia', 'vung', 'region']
    }

    for key, search_terms in keywords.items():
        found = None
        for term in search_terms:
            for col in cols:
                if term.lower() in col.lower():
                    found = col
                    break
            if found: break
        mapping[key] = found
    return mapping

def standardize_data(df, col_map):
    """Bước 1: Đổi tên, làm sạch ký tự lạ ($,,) và ép kiểu"""
    # 1. Đổi tên cột
    rename_dict = {
        col_map['date']: 'Date',
        col_map['price']: 'Amount',
        col_map['quantity']: 'Quantity'
    }
    if col_map['customer']: rename_dict[col_map['customer']] = 'CustomerID'
    if col_map['product']: rename_dict[col_map['product']] = 'Product'
    if col_map['country']: rename_dict[col_map['country']] = 'Country'

    df_std = df.rename(columns=rename_dict).copy()

    # 2. Hàm làm sạch tiền tệ (Xóa $, , %)
    def clean_currency(x):
        if isinstance(x, str):
            return x.replace('$', '').replace(',', '').replace(' ', '').replace('%', '')
        return x

    # 3. Áp dụng làm sạch
    if 'Amount' in df_std.columns:
        df_std['Amount'] = df_std['Amount'].apply(clean_currency)
    if 'Quantity' in df_std.columns:
        df_std['Quantity'] = df_std['Quantity'].apply(clean_currency)

    # 4. Ép kiểu dữ liệu an toàn
    df_std['Date'] = pd.to_datetime(df_std['Date'], errors='coerce')
    df_std['Amount'] = pd.to_numeric(df_std['Amount'], errors='coerce').fillna(0)
    df_std['Quantity'] = pd.to_numeric(df_std['Quantity'], errors='coerce').fillna(0)

    # 5. Xử lý logic Doanh thu
    if df_std['Amount'].mean() < 1000 and df_std['Quantity'].mean() > 0:
        df_std['TotalSales'] = df_std['Amount'] * df_std['Quantity']
    else:
        df_std['TotalSales'] = df_std['Amount']

    return df_std

def clean_data(df_std):
    """Bước 2: Lọc bỏ nhiễu"""
    df_clean = df_std.copy()

    # Loại bỏ giá trị âm/bằng 0
    df_clean = df_clean[(df_clean['Amount'] > 0) & (df_clean['Quantity'] > 0)]

    # Loại bỏ Outliers (Top 1%)
    if not df_clean.empty:
        q99 = df_clean['TotalSales'].quantile(0.99)
        df_clean = df_clean[df_clean['TotalSales'] <= q99]

    # Thêm thông tin thời gian
    df_clean['Year'] = df_clean['Date'].dt.year
    df_clean['YYYYMM'] = df_clean['Date'].dt.strftime('%Y-%m')
    df_clean['Hour'] = df_clean['Date'].dt.hour
    df_clean['Weekday'] = df_clean['Date'].dt.day_name()

    return df_clean

def calculate_rfm(df):
    """Tính toán RFM"""
    if 'CustomerID' not in df.columns: return None
    df_user = df.dropna(subset=['CustomerID'])
    if df_user.empty: return None

    snapshot_date = df_user['Date'].max() + dt.timedelta(days=1)
    rfm = df_user.groupby('CustomerID').agg({
        'Date': lambda x: (snapshot_date - x.max()).days,
        'Quantity': 'count',
        'TotalSales': 'sum'
    })
    rfm.rename(columns={'Date': 'Recency', 'Quantity': 'Frequency', 'TotalSales': 'Monetary'}, inplace=True)

    try:
        rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=['5','4','3','2','1'])
        rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=['1','2','3','4','5'])

        def segment(x):
            if int(x['R_Score']) >= 4 and int(x['F_Score']) >= 4: return 'Champions'
            elif int(x['F_Score']) >= 3: return 'Loyal'
            elif int(x['R_Score']) <= 2: return 'At Risk'
            else: return 'Regular'
        rfm['Segment'] = rfm.apply(segment, axis=1)
    except:
        return rfm
    return rfm

# --- 2. GIAO DIỆN STREAMLIT ---
st.title("📊 Ứng Dụng Phân Tích Dữ Liệu Doanh thu bán hàng")

# --- SIDEBAR ---
st.sidebar.header("1. Nhập liệu")
uploaded_file = st.sidebar.file_uploader("Tải file CSV", type=['csv'])

if uploaded_file:
    # Đọc file (Hỗ trợ nhiều encoding)
    try: df_raw = pd.read_csv(uploaded_file, encoding='ISO-8859-1')
    except: df_raw = pd.read_csv(uploaded_file, encoding='utf-8')

    col_map = smart_map_columns(df_raw)

    # Mapping
    with st.sidebar.expander("⚙️ Cấu hình cột (Auto)", expanded=True):
        cols = list(df_raw.columns)
        def get_idx(key): return cols.index(col_map[key]) if col_map[key] in cols else 0

        final_map = {}
        final_map['date'] = st.selectbox("Ngày", cols, index=get_idx('date'))
        final_map['quantity'] = st.selectbox("Số lượng", cols, index=get_idx('quantity'))
        final_map['price'] = st.selectbox("Giá/Tiền", cols, index=get_idx('price'))
        final_map['customer'] = st.selectbox("Khách hàng", [None]+cols, index=cols.index(col_map['customer'])+1 if col_map['customer'] in cols else 0)
        final_map['product'] = st.selectbox("Sản phẩm", [None]+cols, index=cols.index(col_map['product'])+1 if col_map['product'] in cols else 0)
        final_map['country'] = None

    if st.sidebar.button("🚀 PHÂN TÍCH NGAY", type="primary"):
        # 1. Chuẩn hóa & Làm sạch
        df_std = standardize_data(df_raw, final_map)
        df_clean = clean_data(df_std)

        # TABS GIAO DIỆN
        tab1, tab2, tab3 = st.tabs(["1️⃣ Thống kê thô", "2️⃣ Xử lý & So sánh", "3️⃣ Phân tích sâu"])

        # TAB 1: RAW
        with tab1:
            st.subheader("Dữ liệu thô (Chưa lọc)")
            c1, c2 = st.columns(2)
            c1.metric("Số dòng", f"{df_std.shape[0]:,}")
            c2.metric("Số cột", f"{df_std.shape[1]}")
            st.dataframe(df_std.head())
            st.write("Thống kê mô tả (Raw):")
            st.dataframe(df_std.describe())

        # TAB 2: CLEANING (CÓ BẢNG SO SÁNH MỚI)
        with tab2:
            st.header("Hiệu quả làm sạch & So sánh Thống kê")

            # 1. Metrics cơ bản
            c1, c2, c3 = st.columns(3)
            diff = df_std.shape[0] - df_clean.shape[0]
            c1.metric("Số dòng (Sạch)", f"{df_clean.shape[0]:,}", delta=f"-{diff} dòng rác")
            c2.metric("Doanh thu (Sạch)", f"{df_clean['TotalSales'].sum():,.0f}")
            c3.metric("Giữ lại", f"{len(df_clean)/len(df_std)*100:.1f}%")

            st.markdown("---")

            # 2. BẢNG THỐNG KÊ SO SÁNH (MỚI)
            st.subheader("📋 Bảng so sánh chỉ số thống kê (Trước vs Sau)")

            # Tính toán describe cho 2 bản
            desc_raw = df_std[['Quantity', 'TotalSales']].describe()
            desc_clean = df_clean[['Quantity', 'TotalSales']].describe()

            # Gộp lại thành 1 bảng side-by-side
            comp_df = pd.concat([
                desc_raw['Quantity'].rename("SL (Trước)"),
                desc_clean['Quantity'].rename("SL (Sau)"),
                desc_raw['TotalSales'].rename("Tiền (Trước)"),
                desc_clean['TotalSales'].rename("Tiền (Sau)")
            ], axis=1)

            # Tô màu để dễ nhìn
            st.dataframe(comp_df.style.format("{:,.2f}").background_gradient(cmap="Blues", axis=1))
            st.caption("Ghi chú: Bảng trên giúp so sánh các chỉ số như Trung bình (mean), Độ lệch (std) và Cực đại (max) thay đổi thế nào sau khi loại bỏ nhiễu.")

            st.markdown("---")

            # 3. Biểu đồ Boxplot
            st.subheader("📊 Trực quan hóa so sánh (Boxplot)")
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                fig_box1 = go.Figure()
                fig_box1.add_trace(go.Box(y=df_std['TotalSales'], name='Trước (Raw)'))
                fig_box1.add_trace(go.Box(y=df_clean['TotalSales'], name='Sau (Clean)'))
                fig_box1.update_layout(title="Phân bố Doanh thu")
                st.plotly_chart(fig_box1, use_container_width=True)

            with col_v2:
                 fig_box2 = go.Figure()
                 fig_box2.add_trace(go.Box(y=df_std['Quantity'], name='Trước (Raw)'))
                 fig_box2.add_trace(go.Box(y=df_clean['Quantity'], name='Sau (Clean)'))
                 fig_box2.update_layout(title="Phân bố Số lượng")
                 st.plotly_chart(fig_box2, use_container_width=True)

        # TAB 3: ANALYSIS
        with tab3:
            st.header("Phân tích Chuyên sâu")

            # Xu hướng
            t1, t2 = st.columns(2)
            with t1:
                trend = df_clean.groupby('YYYYMM')['TotalSales'].sum().reset_index()
                fig = px.line(trend, x='YYYYMM', y='TotalSales', markers=True, title="Doanh thu theo Tháng")
                st.plotly_chart(fig, use_container_width=True)
            with t2:
                trend_h = df_clean.groupby('Hour')['TotalSales'].sum().reset_index()
                fig = px.bar(trend_h, x='Hour', y='TotalSales', title="Khung giờ vàng")
                st.plotly_chart(fig, use_container_width=True)

            # Top Sản phẩm
            if final_map['product']:
                st.subheader("Top Sản Phẩm")
                top = df_clean.groupby('Product')['TotalSales'].sum().nlargest(10).reset_index().sort_values('TotalSales')
                fig_p = px.bar(top, x='TotalSales', y='Product', orientation='h', title="Top 10 Sản phẩm", text_auto='.2s')
                fig_p.update_layout(margin=dict(l=150))
                st.plotly_chart(fig_p, use_container_width=True)

            # RFM
            if final_map['customer']:
                st.subheader("Phân nhóm Khách hàng (RFM)")
                rfm = calculate_rfm(df_clean)
                if rfm is not None and 'Segment' in rfm.columns:
                    cnt = rfm['Segment'].value_counts().reset_index()
                    cnt.columns = ['Segment', 'Count']
                    fig_pie = px.pie(cnt, values='Count', names='Segment')
                    st.plotly_chart(fig_pie)
                else:
                    st.info("Dữ liệu không đủ để chạy RFM")
else:
    st.info("👈 Hãy tải file CSV lên để bắt đầu.")