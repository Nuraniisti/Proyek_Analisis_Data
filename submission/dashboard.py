import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set tema visualisasi
sns.set_theme(style="whitegrid")

# Load datasets
@st.cache_data
def load_data():
    customers = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/refs/heads/main/E-Commerce%20Public%20Dataset/customers_dataset.csv')
    order_items = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/refs/heads/main/E-Commerce%20Public%20Dataset/order_items_dataset.csv')
    order_payments = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/refs/heads/main/E-Commerce%20Public%20Dataset/order_payments_dataset.csv')
    order_reviews = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/refs/heads/main/E-Commerce%20Public%20Dataset/order_reviews_dataset.csv')
    orders = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/refs/heads/main/E-Commerce%20Public%20Dataset/orders_dataset.csv')
    product_category_name = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/refs/heads/main/E-Commerce%20Public%20Dataset/product_category_name_translation.csv')
    products = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/refs/heads/main/E-Commerce%20Public%20Dataset/products_dataset.csv')
    sellers = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/refs/heads/main/E-Commerce%20Public%20Dataset/sellers_dataset.csv')

    # Data Cleaning
    orders.dropna(inplace=True)
    order_reviews.dropna(inplace=True)
    products.dropna(inplace=True)
    
    # Merge product categories
    products = pd.merge(products, product_category_name, on='product_category_name', how='left')
    products.rename(columns={'product_category_name_english': 'product_category'}, inplace=True)

    # Merge datasets
    df = pd.merge(orders, customers, on='customer_id')
    df = df.merge(order_items, on='order_id')
    df = df.merge(order_payments, on='order_id')
    df = df.merge(products, on='product_id')
    df = df.merge(sellers, on='seller_id')

    # Tambahkan kolom waktu
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df['order_purchase_year'] = df['order_purchase_timestamp'].dt.year
    df['order_purchase_month'] = df['order_purchase_timestamp'].dt.month

    return df, customers, order_items, order_payments, orders

df, customers, order_items, order_payments, orders = load_data()

# Sidebar Navigasi
st.sidebar.title("📊 E-Commerce Dashboard")
menu = st.sidebar.radio("Pilih Analisis:", ["Home", "Penjualan", "Metode Pembayaran", "Produk Terlaris", "Customer Distribution"])

#HOME PAGE
if menu == "Home":
    st.title("📊 E-Commerce Dashboard")
    st.markdown("Dashboard ini menampilkan analisis data e-commerce berdasarkan transaksi pelanggan, metode pembayaran, dan produk yang paling laris.")

    # Menampilkan statistik
    st.subheader("Ringkasan Data")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Customers", customers["customer_unique_id"].nunique())
    col2.metric("Total Orders", orders["order_id"].nunique())
    col3.metric("Total Revenue", f"${order_payments['payment_value'].sum():,.2f}")

#ANALISIS PENJUALAN
elif menu == "Penjualan":
    st.title("Analisis Penjualan")
    
    # Trend Penjualan
    orders_trend = df.groupby(['order_purchase_year', 'order_purchase_month']).order_id.nunique().reset_index()
    orders_trend["period"] = orders_trend["order_purchase_month"].astype(str) + "/" + orders_trend["order_purchase_year"].astype(str)

    st.subheader("Tren Penjualan dari Tahun 2016-2018")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(orders_trend['period'], orders_trend['order_id'])
    plt.xticks(rotation=75)
    plt.xlabel("Bulan/Tahun")
    plt.ylabel("Jumlah Order")
    plt.title("Tren Order per Bulan")
    st.pyplot(fig)

#METODE PEMBAYARAN
elif menu == "Metode Pembayaran":
    st.title("Analisis Metode Pembayaran")
    
    # Distribusi Metode Pembayaran
    payment_counts = order_payments.groupby("payment_type")["order_id"].nunique().reset_index()

    st.subheader("Distribusi Metode Pembayaran")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.pie(payment_counts["order_id"], labels=payment_counts["payment_type"], autopct="%.0f%%", colors=sns.color_palette("pastel"))
    plt.title("Proporsi Metode Pembayaran")
    st.pyplot(fig)

#PRODUK TERLARIS
elif menu == "Produk Terlaris":
    st.title("Produk Terlaris")
    
    # Produk Terlaris
    top_categories = df.groupby("product_category")["order_item_id"].sum().reset_index()
    top_categories = top_categories.sort_values(by="order_item_id", ascending=False).head(10)

    st.subheader("10 Kategori Produk Terlaris")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(top_categories['product_category'], top_categories['order_item_id'])
    plt.xticks(rotation=75)
    plt.xlabel("Kategori Produk")
    plt.ylabel("Jumlah Terjual")
    plt.title("Produk Terlaris")
    st.pyplot(fig)

#DISTRIBUSI CUSTOMER
elif menu == "Customer Distribution":
    st.title("Distribusi Customer")
    
    # Distribusi Customer per Wilayah
    customer_state = df.groupby("customer_state")["customer_unique_id"].nunique().reset_index()
    customer_state = customer_state.sort_values(by="customer_unique_id", ascending=False)

    st.subheader("Jumlah Customer per Wilayah")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(customer_state['customer_state'], customer_state['customer_unique_id'])
    plt.xlabel("Wilayah")
    plt.ylabel("Jumlah Customer")
    plt.title("Distribusi Customer per Wilayah")
    st.pyplot(fig)
