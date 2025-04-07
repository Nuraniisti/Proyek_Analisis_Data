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
    customers = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/main/E-Commerce%20Public%20Dataset/customers_dataset.csv')
    order_items = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/main/E-Commerce%20Public%20Dataset/order_items_dataset.csv')
    order_payments = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/main/E-Commerce%20Public%20Dataset/order_payments_dataset.csv')
    order_reviews = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/main/E-Commerce%20Public%20Dataset/order_reviews_dataset.csv')
    orders = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/main/E-Commerce%20Public%20Dataset/orders_dataset.csv')
    products = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/main/E-Commerce%20Public%20Dataset/products_dataset.csv')
    product_category_name = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/main/E-Commerce%20Public%20Dataset/product_category_name_translation.csv')
    sellers = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/main/E-Commerce%20Public%20Dataset/sellers_dataset.csv')

    # Cleaning
    orders.dropna(inplace=True)
    order_reviews.dropna(inplace=True)
    products.dropna(inplace=True)

    # Merge categories
    products = pd.merge(products, product_category_name, on='product_category_name', how='left')
    products.rename(columns={'product_category_name_english': 'product_category'}, inplace=True)

    # Preprocessing
    orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
    orders['order_purchase_year'] = orders['order_purchase_timestamp'].dt.year
    orders['order_purchase_month'] = orders['order_purchase_timestamp'].dt.month
    orders['order_purchase_date'] = orders['order_purchase_timestamp'].dt.date

    # Merge orders with other data
    df = pd.merge(orders, order_items, on="order_id")
    df = pd.merge(df, order_payments, on="order_id")
    df = pd.merge(df, customers[['customer_id', 'customer_unique_id', 'customer_state']], on="customer_id")
    
    return df, products

# Load & prepare data
df, products = load_data()

# Sidebar filter by date
min_date = df['order_purchase_timestamp'].min().date()
max_date = df['order_purchase_timestamp'].max().date()
start_date, end_date = st.sidebar.date_input("Pilih Rentang Tanggal", [min_date, max_date], min_value=min_date, max_value=max_date)

# Filter dataframe
df_filtered = df[(df['order_purchase_date'] >= start_date) & (df['order_purchase_date'] <= end_date)]

# METRICS
st.title("📦 E-Commerce Dashboard")
col1, col2 = st.columns(2)
col1.metric("Jumlah Pesanan", df_filtered['order_id'].nunique())
col2.metric("Jumlah Pelanggan", df_filtered['customer_unique_id'].nunique())

# ORDER STATUS DISTRIBUTION
st.subheader("Distribusi Status Pesanan")
status_counts = df_filtered['order_status'].value_counts()
status_percent = df_filtered['order_status'].value_counts(normalize=True) * 100
status_df = pd.DataFrame({'Jumlah': status_counts, 'Persentase (%)': status_percent.round(2)})
st.dataframe(status_df)

# CUSTOMER DISTRIBUTION
st.subheader("Distribusi Pelanggan per Wilayah")
customer_state = df_filtered.groupby('customer_state')['customer_unique_id'].nunique().reset_index()
customer_state = customer_state.sort_values(by='customer_unique_id', ascending=False)
customer_state.rename(columns={'customer_unique_id': 'jumlah_pelanggan'}, inplace=True)

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(data=customer_state, x='customer_state', y='jumlah_pelanggan', palette='Blues_r', ax=ax)
ax.set_title("Distribusi Pelanggan per Wilayah")
st.pyplot(fig)

# TREN ORDER BULANAN
st.subheader("Tren Jumlah Order per Bulan")
monthly_orders = df_filtered.groupby(['order_purchase_year', 'order_purchase_month'])['order_id'].nunique().reset_index()
monthly_orders['period'] = monthly_orders['order_purchase_month'].astype(str) + "/" + monthly_orders['order_purchase_year'].astype(str)
monthly_orders.rename(columns={'order_id': 'jumlah_order'}, inplace=True)
monthly_orders = monthly_orders.sort_values(by=['order_purchase_year', 'order_purchase_month'])

fig, ax = plt.subplots(figsize=(10, 6))
sns.lineplot(data=monthly_orders, x='period', y='jumlah_order', marker='o', color='teal', ax=ax)
plt.xticks(rotation=75)
st.pyplot(fig)

# METODE PEMBAYARAN
st.subheader("Distribusi Metode Pembayaran")
payment_method = df_filtered.groupby("payment_type").agg({"payment_value": "mean", "order_id": "nunique"}).reset_index()
payment_method.rename(columns={"order_id": "jumlah_order"}, inplace=True)

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=payment_method, x="payment_type", y="jumlah_order", palette="pastel", ax=ax)
ax.set_title("Distribusi Metode Pembayaran")
st.pyplot(fig)

# 10 KATEGORI PRODUK TERLARIS
st.subheader("10 Kategori Produk Terlaris")
product_sales = df_filtered.merge(products[['product_id', 'product_category']], on='product_id', how='left')

top_categories = product_sales.groupby('product_category')['order_item_id'].count().reset_index()
top_categories = top_categories.sort_values(by='order_item_id', ascending=False).head(10)

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(top_categories['product_category'], top_categories['order_item_id'], color='skyblue')
ax.set_title('10 Kategori Produk Terlaris')
ax.set_xlabel('Kategori Produk')
ax.set_ylabel('Jumlah Produk Terjual')
plt.xticks(rotation=75)
plt.tight_layout()
st.pyplot(fig)