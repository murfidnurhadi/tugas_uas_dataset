import streamlit as st
import plotly.express as px
import pandas as pd
import gdown

# Daftar URL Google Drive
file_urls = {
    "sellers": "https://drive.google.com/uc?id=1-5DduW0uWk4NfcXxL3FjnuuxCZEHWSoL",
    "products": "https://drive.google.com/uc?id=1CNR0MuaZU77tMeucFcDBcFNx0dQQ6Ouk",
    "product_category": "https://drive.google.com/uc?id=1CaUQEkqmBM_QuMbIfbxq-9dQsPv235to",
    "orders": "https://drive.google.com/uc?id=1nxEALRdWBAz-lFgVlVnC2UthLPvtlA_y",
    "order_reviews": "https://drive.google.com/uc?id=1ym5Xjq_a82D-dH195oImEaiQ5IxJB8Ot",
    "order_payments": "https://drive.google.com/uc?id=1io5sO6SzpHNTY-YqllDS8KNN0n6PwTqk",
    "order_items": "https://drive.google.com/uc?id=1XKcA-hNGB9YCbDNAAdBQxvDL3IcoQrXY",
    "geolocation": "https://drive.google.com/uc?id=1WhheFic-yVYvpMeccK30NebIhtfGIdUu",
    "customers": "https://drive.google.com/uc?id=1VAOSa_sNZV4-MJHEEvmgR2mpDoopK45q"
}

# Fungsi untuk mendownload CSV dari Google Drive
@st.cache_data
def load_csv(url):
    try:
        return pd.read_csv(url)
    except Exception as e:
        st.error(f"Error membaca dataset dari {url}: {e}")
        return None

# Memuat dataset dari Google Drive
st.title("Dashboard Analisis Data dari Google Drive")

# Pilihan Dataset
dataset_option = st.sidebar.selectbox(
    "Pilih Dataset",
    list(file_urls.keys())
)

# Load dataset yang dipilih
df = load_csv(file_urls[dataset_option])

if df is not None:
    st.write(f"### Dataset: {dataset_option}")
    st.write(df.head())  # Menampilkan 5 data teratas


# Sidebar
with st.sidebar:
    st.image("https://raw.githubusercontent.com/murfidnurhadi/tugas_uas_dataset/main/Images/logo-unikom.jpg", width=260)
    st.markdown("""
    **Kelompok 4**  
    **Anggota:**  
    - 10123034 - Irpan Agun Triyadi  
    - 10123029 - Raihan Rajwa Ali Makmur  
    - 10123032 - Berry Rizkya Fauzy  
    - 10123033 - Zaki Rahmat Nugroho  
    - 10123036 - Naufal Putra Firmansyah  
    - 10123037 - Vadya Aditya Syahputra  
    """)
    st.markdown("---")
    st.markdown("## 🗓️ Filter Penjulan")  
    year_selected = st.sidebar.selectbox("Pilih Tahun", merged_df['year'].unique() if not merged_df.empty else [None])

    st.header("🔍 Filter Lokasi")
    kota_terpilih = st.sidebar.selectbox("Pilih Kota:", ["Semua"] + sorted(geolocation_df["geolocation_city"].unique()))

st.title("📊 Dashboard Analisis E-Commerce")
st.markdown("---")

st.subheader("📝 Produk Paling Banyak Terjual")
product_sales = merged_df[merged_df['year'] == year_selected].groupby('product_category_name_english').agg({'order_item_id': 'count'}).reset_index()
product_sales = product_sales.sort_values(by='order_item_id', ascending=False).head(10)
fig_produk = px.bar(product_sales, 
                    x='order_item_id', 
                    y='product_category_name_english', 
                    orientation='h',
                    labels={'order_item_id': 'Jumlah Terjual', 'product_category_name_english': 'Kategori Produk'},
                    title="Top Produk Terlaris",
                    hover_data={'order_item_id': True})
fig_produk.update_layout(yaxis=dict(categoryorder='total ascending'))
st.plotly_chart(fig_produk, use_container_width=True)
st.markdown("---")


# Analisis Penjualan Bulanan
st.subheader("📈 Tren Penjualan Bulanan")
monthly_sales = merged_df[merged_df['year'] == year_selected].groupby(['month']).agg({'order_item_id': 'count'}).reset_index()
fig_bulanan = px.line(monthly_sales, 
                      x='month', 
                      y='order_item_id', 
                      markers=True,
                      labels={'month': 'Bulan', 'order_item_id': 'Jumlah Penjualan'},
                      title="Penjualan Bulanan")
st.plotly_chart(fig_bulanan, use_container_width=True)
st.markdown("---")

# Analisis Kota dengan Pesanan Terbanyak
st.subheader("🏙️ Kota Wilayah dengan Pesanan Terbanyak")
city_orders = city_df.groupby('customer_city').agg({'order_id': 'count'}).reset_index()
city_orders = city_orders.sort_values(by='order_id', ascending=False).head(10)
fig_kota = px.bar(city_orders, 
                  x='order_id', 
                  y='customer_city', 
                  orientation='h',
                  labels={'order_id': 'Jumlah Pesanan', 'customer_city': 'Kota'},
                  title="Top Kota dengan Pesanan Terbanyak",
                  hover_data={'order_id': True},
                  category_orders={'customer_city': city_orders['customer_city'].tolist()})
st.plotly_chart(fig_kota, use_container_width=True)
st.markdown("---")

# 🌎 Peta Lokasi Pelanggan di Brasil
st.subheader("🗺️ Peta Wilayah Geografis Brazil")
if "geolocation_zip_code_prefix" in geolocation_df.columns:
    filtered_data = geolocation_df if kota_terpilih == "Semua" else geolocation_df[geolocation_df["geolocation_city"] == kota_terpilih]
    unique_locations = filtered_data.drop_duplicates(subset='geolocation_zip_code_prefix')

    fig_map = px.scatter_mapbox(unique_locations, 
                                lat="geolocation_lat", lon="geolocation_lng", 
                                hover_name="geolocation_city", 
                                color_discrete_sequence=["maroon"], zoom=3, height=600)

    fig_map.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)  
else:
    st.error("Kolom 'geolocation_zip_code_prefix' tidak ditemukan di dataset!")
st.markdown("---")


# Kategori Produk dengan Kerugian Terbesar
st.subheader("📉 Kategori Produk dengan Kerugian Terbesar")
failed_orders = orders_df[orders_df['order_status'].isin(['canceled', 'unavailable'])]
failed_orders = failed_orders.merge(order_items_df, on='order_id', how='left')
failed_orders = failed_orders.merge(products_df[['product_id', 'product_category_name']], on='product_id', how='left')
failed_orders = failed_orders.merge(product_translation_df, on='product_category_name', how='left')

loss_per_category = failed_orders.groupby('product_category_name_english')['price'].sum().reset_index()
loss_per_category = loss_per_category.sort_values(by='price', ascending=False).head(10)
fig_kerugian = px.pie(loss_per_category, 
                      values='price', 
                      names='product_category_name_english',
                      title="Kategori Produk dengan Kerugian Terbesar",
                      hole=0.3)
st.plotly_chart(fig_kerugian, use_container_width=True)
st.markdown("---")

st.subheader("⚙️ Perubahan Rata-rata Nilai Pemesanan (AOV)")
payments_with_orders["order_purchase_date"] = pd.to_datetime(payments_with_orders["order_purchase_timestamp"]).dt.date
aov_by_date = payments_with_orders.groupby("order_purchase_date")["payment_value"].sum()
fig_aov = px.line(x=aov_by_date.index, 
                  y=aov_by_date.values, 
                  markers=True,
                  labels={'x': 'Tanggal', 'y': 'Total Nilai Pemesanan'},
                  title="Perubahan Rata-rata Nilai Pemesanan dari Waktu ke Waktu")
st.plotly_chart(fig_aov, use_container_width=True)
st.markdown("---")

st.subheader("🎯 Pengaruh Review Score Pelanggan")

order_reviews = order_reviews_df.merge(orders_df, on='order_id', how='inner')
order_reviews = order_reviews.merge(order_items_df, on='order_id', how='inner')
order_reviews = order_reviews.merge(order_payments_df, on='order_id', how='inner')
order_reviews = order_reviews.merge(products_df, on='product_id', how='inner')
order_reviews = order_reviews.merge(product_translation_df, on='product_category_name_english', how='left')

order_reviews['order_delivered_customer_date'] = pd.to_datetime(order_reviews['order_delivered_customer_date'])
order_reviews['order_estimated_delivery_date'] = pd.to_datetime(order_reviews['order_estimated_delivery_date'])
order_reviews['delivery_time'] = (order_reviews['order_delivered_customer_date'] - 
                                   order_reviews['order_estimated_delivery_date']).dt.days

order_reviews = order_reviews.dropna()

# Analisis distribusi review_score
fig_review_dist = px.histogram(order_reviews, x='review_score', nbins=5, 
                               title='Distribusi Review Score Pelanggan', 
                               color_discrete_sequence=['blue'])
st.plotly_chart(fig_review_dist, use_container_width=True)

# Analisis waktu pengiriman berdasarkan review_score
fig_delivery_time = px.box(order_reviews, x='review_score', y='delivery_time', 
                           title='Waktu Pengiriman Berdasarkan Review Score',
                           color='review_score')
st.plotly_chart(fig_delivery_time, use_container_width=True)

# Rata-rata review_score per kategori produk
avg_review_by_category = order_reviews.groupby('product_category_name_english')['review_score'].mean().reset_index()
fig_avg_review = px.bar(avg_review_by_category, x='review_score', y='product_category_name_english',
                        title='Rata-rata Review Score Berdasarkan Kategori Produk',
                        orientation='h', color='review_score', color_continuous_scale='Greens')
st.plotly_chart(fig_avg_review, use_container_width=True)

# Simulasi data korelasi faktor yang mempengaruhi review score
np.random.seed(42)
data = pd.DataFrame({
    'Review_Score': np.random.randint(1, 6, 500),
    'Delivery_Time': np.random.randint(1, 15, 500),  # Waktu pengiriman dalam hari
    'Product_Quality': np.random.randint(1, 11, 500),  # Skala 1-10
    'Customer_Service': np.random.randint(1, 11, 500),  # Skala 1-10
    'Price_Satisfaction': np.random.randint(1, 11, 500)  # Skala 1-10
})

correlation = data.corr()

# Visualisasi Korelasi antar Faktor
fig_correlation = px.imshow(correlation, text_auto=True, color_continuous_scale='PuBuGn',
                            title='Matriks Korelasi Antar Faktor yang Mempengaruhi Review Score')
st.plotly_chart(fig_correlation, use_container_width=True)

# Pengaruh Product Quality terhadap Review Score
fig_quality = px.box(data, x='Review_Score', y='Product_Quality',
                     title='Pengaruh Product Quality terhadap Review Score',
                     color='Review_Score')
st.plotly_chart(fig_quality, use_container_width=True)

# Pengaruh Delivery Time terhadap Review Score
fig_delivery = px.box(data, x='Review_Score', y='Delivery_Time',
                      title='Pengaruh Delivery Time terhadap Review Score',
                      color='Review_Score')
st.plotly_chart(fig_delivery, use_container_width=True)
st.markdown("---")


st.subheader("💳 Total Pengeluaran Customer Berdasarkan Tipe Pembayaran")
fig = px.bar(
    total_payment_type,
    x="payment_type",
    y="payment_value_million",
    text="payment_value_million",
    labels={'payment_type': 'Tipe Pembayaran', 'payment_value_million': 'Total Pengeluaran (Juta)'},
    color="payment_type",
    color_discrete_sequence=px.colors.sequential.Blues
)

fig.update_traces(texttemplate='%{text:.2f}M', textposition='outside')
fig.update_layout(xaxis_title="Tipe Pembayaran", yaxis_title="Total Pengeluaran (Juta)", showlegend=False)

st.plotly_chart(fig, use_container_width=True)
st.markdown("---")


# Simulasi Data Transaksi
data = {
    'TransactionID': [1, 1, 2, 2, 2, 3, 3, 4, 4],
    'Product': ['beleza_saude', 'informatica_acessorios', 'automotivo', 'cama_mesa_banho', 
                'moveis_decoracao', 'beleza_saude', 'automotivo', 'informatica_acessorios', 
                'cama_mesa_banho']
}

df = pd.DataFrame(data)

# Menghitung Frekuensi Produk
product_counts = df['Product'].value_counts().reset_index()
product_counts.columns = ['Product', 'Frequency']

# Streamlit Dashboard
st.subheader("📊 Frekuensi Produk yang Sering Dibeli Bersamaan ")

# Visualisasi Frekuensi Produk
fig = px.bar(
    product_counts,
    x="Product",
    y="Frequency",
    text="Frequency",
    title="Frekuensi Produk yang Dibeli",
    labels={"Product": "Nama Produk", "Frequency": "Jumlah Pembelian"},
    color="Product",
    color_discrete_sequence=px.colors.qualitative.Set3
)

fig.update_traces(textposition="outside")
fig.update_layout(xaxis_tickangle=-45)

st.plotly_chart(fig, use_container_width=True)
st.markdown("---")

st.title("🗂️ Data Sample E-Commerce Public")
st.subheader("Customers Dataset")
st.dataframe(customers_df.head(5))
st.markdown("---")
st.subheader("Geolocation Dataset")
st.dataframe(geolocation_df.head(5))
st.markdown("---")
st.subheader("Order Items Dataset")
st.dataframe(order_items_df.head(5))
st.markdown("---")
st.subheader("Order Payments Dataset")
st.dataframe(order_payments_df.head(5))
st.markdown("---")
st.subheader("Order Reviews Dataset")
st.dataframe(order_reviews_df.head(5))
st.markdown("---")
st.subheader("Orders Dataset")
st.dataframe(orders_df.head(5))
st.markdown("---")
st.subheader("Product Category Translation Dataset")
st.dataframe(product_translation_df.head(5))
st.markdown("---")
st.subheader("Products Dataset")
st.dataframe(products_df.head(5))
st.markdown("---")
st.subheader("Sellers Dataset")
st.dataframe(sellers_df.head(5))

st.markdown("---")
st.markdown("📌 **Dashboard ini dibuat oleh Kelompok 4 | Universitas Komputer Indonesia (UNIKOM)**")
