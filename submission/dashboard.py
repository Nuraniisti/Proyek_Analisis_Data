import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Title
st.title("E-Commerce Dashboard")
st.sidebar.header("Navigation")

# Load Data
@st.cache
def load_data():
    customers = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/refs/heads/main/E-Commerce%20Public%20Dataset/customers_dataset.csv')
    orders = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/refs/heads/main/E-Commerce%20Public%20Dataset/orders_dataset.csv')
    order_items = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/refs/heads/main/E-Commerce%20Public%20Dataset/order_items_dataset.csv')
    products = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/refs/heads/main/E-Commerce%20Public%20Dataset/products_dataset.csv')
    sellers = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/refs/heads/main/E-Commerce%20Public%20Dataset/sellers_dataset.csv')
    product_category_name = pd.read_csv('https://raw.githubusercontent.com/Nuraniisti/Proyek_Analisis_Data/refs/heads/main/E-Commerce%20Public%20Dataset/product_category_name_translation.csv')
    
    # Merge data
    products = pd.merge(products, product_category_name, on='product_category_name', how='left')
    products.rename(columns={'product_category_name_english': 'product_category'}, inplace=True)
    
    df = pd.merge(orders, customers, on='customer_id')
    df = pd.merge(df, order_items, on='order_id')
    df = pd.merge(df, products, on='product_id')
    df = pd.merge(df, sellers, on='seller_id')
    
    return df

df = load_data()

# Overview
st.header("Data Overview")
st.write(df.head())
st.write("Number of Rows: ", df.shape[0])
st.write("Number of Columns: ", df.shape[1])

# Unique Customers by State
st.subheader("Unique Customers by State")
customer_state = df[['customer_unique_id', 'customer_state']].groupby('customer_state').count().reset_index()
fig, ax = plt.subplots()
ax.bar(customer_state['customer_state'], customer_state['customer_unique_id'])
plt.xticks(rotation=45)
plt.xlabel("Customer State")
plt.ylabel("Unique Customers")
st.pyplot(fig)

# Number of Orders per Year
st.subheader("Number of Orders per Year")
df['order_purchase_year'] = pd.to_datetime(df['order_purchase_timestamp']).dt.year
orders_year = df.groupby('order_purchase_year')['order_id'].nunique().reset_index()
fig, ax = plt.subplots()
ax.bar(orders_year['order_purchase_year'], orders_year['order_id'])
plt.xlabel("Year")
plt.ylabel("Number of Orders")
st.pyplot(fig)

# Top Product Categories
st.subheader("Top 10 Product Categories")
top_categories = df.groupby('product_category')['order_item_id'].sum().sort_values(ascending=False).reset_index()
fig, ax = plt.subplots()
ax.bar(top_categories['product_category'][:10], top_categories['order_item_id'][:10])
plt.xticks(rotation=45)
plt.xlabel("Product Category")
plt.ylabel("Number of Items Sold")
st.pyplot(fig)