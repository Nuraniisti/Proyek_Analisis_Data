import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Konfigurasi umum
st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")
sns.set_theme(style="whitegrid")

# Load data
@st.cache_data
def load_data():
    customers = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/refs/heads/main/E-Commerce%20Public%20Dataset/customers_dataset.csv')
    order_items = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/refs/heads/main/E-Commerce%20Public%20Dataset/order_items_dataset.csv')
    order_payments = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/refs/heads/main/E-Commerce%20Public%20Dataset/order_payments_dataset.csv')
    order_reviews = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/refs/heads/main/E-Commerce%20Public%20Dataset/order_reviews_dataset.csv')
    orders = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/refs/heads/main/E-Commerce%20Public%20Dataset/orders_dataset.csv')
    products = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/refs/heads/main/E-Commerce%20Public%20Dataset/products_dataset.csv')
    product_category_name = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/refs/heads/main/E-Commerce%20Public%20Dataset/product_category_name_translation.csv')
    sellers = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/refs/heads/main/E-Commerce%20Public%20Dataset/sellers_dataset.csv')

    # Cleaning
    orders.dropna(inplace=True)
    order_reviews.dropna(inplace=True)
    products.dropna(inplace=True)

    # Merge categories
    products = pd.merge(products, product_category_name, on='product_category_name', how='left')
    products.rename(columns={'product_category_name_english': 'product_category'}, inplace=True)

    # Merge utama
    df = pd.merge(orders, customers, on='customer_id')
    df = df.merge(order_items, on='order_id')
    df = df.merge(order_payments, on='order_id')
    df = df.merge(products, on='product_id')
    df = df.merge(sellers, on='seller_id')

    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'], errors='coerce')
    df['order_purchase_year'] = df['order_purchase_timestamp'].dt.year
    df['order_purchase_month'] = df['order_purchase_timestamp'].dt.month
    df['period'] = df['order_purchase_timestamp'].dt.to_period('M').astype(str)

    return df, customers, orders, order_payments

df, customers, orders, order_payments = load_data()

# Sidebar
st.sidebar.title("📊 E-Commerce Dashboard")
menu = st.sidebar.radio("Pilih Analisis:", ["Home", "Distribusi Pelanggan", "Penjualan", "Metode Pembayaran", "Produk Terlaris"])

# Filter tanggal interaktif
min_date = pd.to_datetime(df['order_purchase_timestamp'].min())
max_date = pd.to_datetime(df['order_purchase_timestamp'].max())
date_range = st.sidebar.date_input("Tanggal Order", [min_date, max_date], min_value=min_date, max_value=max_date)

if isinstance(date_range, list) and len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    df_filtered = df[(df['order_purchase_timestamp'] >= start_date) & (df['order_purchase_timestamp'] <= end_date)]
else:
    st.sidebar.warning("Pilih Rentang Waktu")
    df_filtered = df.copy()

# HOME
if menu == "Home":
    st.title("📊 E-Commerce Dashboard")
    st.markdown("Selamat datang di dashboard analisis e-commerce. Gunakan menu di samping untuk melihat analisis spesifik.")
    st.subheader("Ringkasan Data")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Pelanggan", customers["customer_unique_id"].nunique())
    col2.metric("Total Order", orders["order_id"].nunique())
    col3.metric("Total Revenue", f"${order_payments['payment_value'].sum():,.2f}")

# DISTRIBUSI CUSTOMER
elif menu == "Distribusi Pelanggan":
    st.title("Distribusi Pelanggan per Wilayah")
    customer_state = df_filtered.groupby('customer_state')['customer_unique_id'].nunique().reset_index().sort_values(by='customer_unique_id', ascending=False)
    customer_state.columns = ['State', 'Jumlah Pelanggan']
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=customer_state, x='State', y='Jumlah Pelanggan', palette='Blues_r', ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)

# PENJUALAN
elif menu == "Penjualan":
    st.title("Analisis Penjualan")
    st.subheader("Jumlah Order per Bulan")
    trend = df_filtered.groupby(df_filtered['order_purchase_timestamp'].dt.to_period("M"))["order_id"].nunique().reset_index()
    trend.columns = ["Periode", "Jumlah Order"]
    trend["Periode"] = trend["Periode"].astype(str)
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.lineplot(data=trend, x="Periode", y="Jumlah Order", marker="o", color="teal", ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)

# METODE PEMBAYARAN
elif menu == "Metode Pembayaran":
    st.title("Analisis Metode Pembayaran")
    st.subheader("Distribusi Metode Pembayaran")
    payment_counts = order_payments.groupby("payment_type")["order_id"].nunique().reset_index()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.pie(payment_counts["order_id"], labels=payment_counts["payment_type"], autopct="%.0f%%", colors=sns.color_palette("pastel"))
    plt.title("Proporsi Metode Pembayaran")
    st.pyplot(fig)

# PRODUK TERLARIS
elif menu == "Produk Terlaris":
    st.title("Produk Terlaris")
    top_categories = df_filtered.groupby("product_category")["order_item_id"].sum().reset_index()
    top_categories = top_categories.sort_values(by="order_item_id", ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=top_categories, x='product_category', y='order_item_id', ax=ax)
    plt.xticks(rotation=45)
    plt.ylabel("Jumlah Terjual")
    st.pyplot(fig)