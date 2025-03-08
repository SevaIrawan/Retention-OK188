import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import seaborn as sns
import os
import base64

# ✅ Fungsi untuk menambahkan background hanya di halaman utama
def add_bg_home(image_file):
    """Menambahkan background hanya untuk halaman utama tanpa menutupi teks & logo"""
    with open(image_file, "rb") as f:
        img_data = f.read()
    
    # ✅ Konversi gambar ke Base64
    b64_img = base64.b64encode(img_data).decode()

    # ✅ Tambahkan CSS hanya untuk halaman utama
    bg_style = f"""
        <style>
        .stApp {{
            background: url("data:image/jpg;base64,{b64_img}") no-repeat center center fixed;
            background-size: cover;
        }}
        /* Pastikan tulisan tetap terlihat jelas */
        h1, h4, p, .stButton > button {{
            background: rgba(0, 0, 0, 0.2); /* Tambahkan efek transparansi */
            color: white;
            padding: 10px;
            border-radius: 10px;
        }}
        </style>
    """
    st.markdown(bg_style, unsafe_allow_html=True)

# ====================== SETUP DASHBOARD ====================== #
st.set_page_config(page_title="Analyst Data XCRM 2025", layout="wide")
# ✅ Terapkan background hanya untuk halaman utama dengan warna lebih redup

# ====================== LOGO PERUSAHAAN ====================== #
logo_path = "logo.png"  # Ganti dengan path logo yang sesuai

# ====================== TAMPILAN HOME ====================== #
if "page" not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":
    add_bg_home("background.jpg")  # ✅ Gunakan fungsi sebelum elemen UI
    # ✅ Tampilkan logo di halaman utama
    st.image(logo_path, width=150)
    st.markdown("""
        <h1 style='text-align: center; font-size: 85px; color: blue; font-weight: bold;'>
        📊 Analyst Data XCRM 2025
        </h1>
        <h3 style='text-align: center; font-size: 28px; color: white;'>
            🔹 Select <span style="font-weight: bold; color: yellow;">Go To Dashboard</span> on the left to begin data analysis.
        </h3>
        """, unsafe_allow_html=True)
    
    # Tombol untuk masuk ke dashboard data
    if st.button("Go To Dashboard 📊"):
        st.session_state.page = "dashboard"
        st.rerun()
    st.stop()

# ====================== LOAD DATA UNIQUE MEMBER DARI FOLDER ====================== #
script_dir = os.path.dirname(__file__)  # Direktori skrip
unique_member_path = os.path.join(script_dir, "Unique_Member.xlsx")  # Path ke file

if os.path.exists(unique_member_path):
    df_unique = pd.read_excel(unique_member_path)
else:
    st.error("⚠️ File **Unique_Member.xlsx** tidak ditemukan! Pastikan file ada dalam folder yang sama.")

# ====================== SIDEBAR MENU ====================== #
st.sidebar.image(logo_path, width=300)  # ✅ Tampilkan logo di sidebar
# **Ketika user memilih "Home", kembali ke halaman utama**
if st.sidebar.radio("****", ["🏠 Home"], index=0 if st.session_state.page == "home" else None) == "🏠 Home":
    st.session_state.page = "home"
    st.rerun()
st.sidebar.header("📂 **Filter Data**")

# **Pilih Rentang Tanggal**
date_range = st.sidebar.date_input("📅 **Select Date Range**", [], key="date_range")

# ====================== FUNGSI FILTER DATE RANGE ====================== #
def filter_by_date(df, date_column):
    """Memfilter DataFrame berdasarkan rentang tanggal yang dipilih user."""
    if df is not None and not df.empty and len(date_range) == 2:
        start_date, end_date = date_range

        # Konversi tanggal agar kompatibel
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        # Periksa apakah kolom ada dalam dataset
        if date_column in df.columns:
            df[date_column] = pd.to_datetime(df[date_column], errors='coerce')  # Pastikan format datetime
            df = df.dropna(subset=[date_column])  # Hapus NaN setelah konversi
            df = df[(df[date_column] >= start_date) & (df[date_column] <= end_date)]
    
    return df

# ====================== LOAD DATA TRANSAKSI & INPUT ====================== #
uploaded_file_transaction = st.sidebar.file_uploader("📥 **Upload Data Transaksi**", type=["xlsx"])
uploaded_file_input = st.sidebar.file_uploader("📥 **Upload Data Manual (Harian)**", type=["xlsx"])

# **Pastikan Variabel Terdefinisi**
df_transaction = None
df_input = None
df_filtered_transaction = None
df_filtered_input = None

# **Setelah file diupload, baca & filter**
if uploaded_file_transaction:
    df_transaction = pd.read_excel(uploaded_file_transaction)
    df_transaction["Date"] = pd.to_datetime(df_transaction["Date"])  # Konversi Date
    df_filtered_transaction = filter_by_date(df_transaction, "Date")  # ✅ Filter Data

if uploaded_file_input:
    df_input = pd.read_excel(uploaded_file_input)
    df_input["Date"] = pd.to_datetime(df_input["Date"])  # Konversi Date
    df_filtered_input = filter_by_date(df_input, "Date")  # ✅ Filter Data

# ====================== SIDEBAR MENU ====================== #
menu = st.sidebar.radio("📌 **Menu**", [
    "📊 Total Customers Successfully acquired & Target Achievement",
    "📈 Daily Active Member & Target Achievement",
    "💰 Daily Deposit Amount & Target Achievement",
    "🔁 New Member Retention"
])

# ====================== MENU: CUSTOMER YANG PINDAH ====================== #
if menu == "📊 Total Customers Successfully acquired & Target Achievement":
    st.subheader("📊 **Total Customers Successfully acquired & Target Achievement**")

    if uploaded_file_transaction:
        df_new_customers = df_filtered_transaction[df_filtered_transaction["Unique_Code"].isin(df_unique["Unique_Code"])]
        total_new_customers = df_new_customers["Unique_Code"].nunique()

        # Target
        target_customers = 210
        achievement = (total_new_customers / target_customers) * 100

        # Menampilkan KPI
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🎯 Target Pindah", target_customers)
        with col2:
            st.metric("✅ Customer yang Pindah", total_new_customers)
        with col3:
            st.metric("📈 Pencapaian (%)", f"{achievement:.2f}%")

        # **📊 LINE CHART PENCAPAIAN TARGET**
        st.subheader("📈 **Customer movement trend over time**")
        daily_migration = df_new_customers.groupby("Date")["Unique_Code"].nunique().reset_index()
        daily_migration.rename(columns={"Unique_Code": "New_Customers"}, inplace=True)

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=daily_migration, x="Date", y="New_Customers", marker="o", linestyle="-", color="blue", ax=ax)

        ax.axhline(y=7, color="red", linestyle="dashed", label="Target Harian")
        ax.set_xlabel("Date")
        ax.set_ylabel("Total Customers Successfully acquired")
        ax.set_title("Customer movement trend over time")
        ax.legend()
        ax.grid(True)

        # **Format sumbu X agar hanya menampilkan tanggal**
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator())

        st.pyplot(fig)
        
        # ✅ Tampilkan DataFrame
        st.write("📋 **Detail Data Total Customers**")
        st.dataframe(df_filtered_transaction)

# ====================== MENU: JUMLAH TOTAL CASE HARIAN ====================== #
elif menu == "📈 Daily Active Member & Target Achievement":
    st.subheader("📈 **Daily Active Member & Target Achievement**")
    if uploaded_file_input:
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(x=df_filtered_input["Date"], y=df_filtered_input["Members"], marker="o", linestyle="-", color="blue", ax=ax)

        ax.axhline(y=70, color="red", linestyle="dashed", label="Target Harian")
        ax.set_xlabel("Date")
        ax.set_ylabel("Daily Active Members")
        ax.legend()
        ax.grid(True)

        # **Format sumbu X agar hanya menampilkan tanggal**
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator())

        st.pyplot(fig)

        # **Tampilkan DataFrame di bawah chart**
        st.write("📋 **Detail Data Total Case Harian**")
        st.dataframe(df_filtered_input)

# ====================== MENU: JUMLAH DEPOSIT HARIAN ====================== #
elif menu == "💰 Daily Deposit Amount & Target Achievement":
    st.subheader("💰 **Daily Deposit Amount & Target Achievement**")
    
    if df_filtered_input is not None and not df_filtered_input.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(x=df_filtered_input["Date"], y=df_filtered_input["Amount"], marker="o", linestyle="-", color="green", ax=ax)

        ax.axhline(y=13706, color="red", linestyle="dashed", label="Target")
        ax.set_xlabel("Date")
        ax.set_ylabel("Deposit Amount (SGD)")
        ax.legend()
        ax.grid(True)

        # **Format sumbu X agar hanya menampilkan tanggal**
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator())

        st.pyplot(fig)

        # **Tampilkan DataFrame di bawah chart**
        st.write("📋 **Detail Data Total Penjualan Harian**")
        st.dataframe(df_filtered_input)
    else:
        st.warning("⚠️ Tidak ada data dalam rentang tanggal yang dipilih!")

# ====================== MENU: NEW MEMBER RETENTION ====================== #
elif menu == "🔁 New Member Retention":
    st.subheader("🔁 **New Member Retention**")
    
    if df_filtered_transaction is not None and not df_filtered_transaction.empty:
        retention_data = df_filtered_transaction.groupby("Unique_Code").agg({"Date": "nunique", "Amount": "sum"})
        retention_summary = retention_data.groupby("Date").agg({"Amount": "sum", "Date": "count"})
        retention_summary.rename(columns={"Date": "Customer"}, inplace=True)

        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar(retention_summary.index, retention_summary["Customer"], color="purple", alpha=0.7)

        ax.grid(axis='y', linestyle='--', alpha=0.7)
        ax.set_xlabel("Retention Days")
        ax.set_ylabel("Customer")
        ax.set_title("🔁 New Member Retention")

        for bar, amount in zip(bars, retention_summary["Amount"]):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height + 2, 
                f"${int(amount):,}", ha='center', va='bottom', fontsize=10, color='black', fontweight='bold')

        # **Format sumbu X agar hanya menampilkan angka bulat**
        ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))

        st.pyplot(fig)
        st.write("📋 **Detail Data Retention Member Baru (Amount & Customer)**")
        st.dataframe(retention_summary)
    else:
        st.warning("⚠️ Tidak ada data dalam rentang tanggal yang dipilih!")

# ====================== FITUR SAVE & DOWNLOAD ====================== #
st.sidebar.subheader("📥 **Simpan & Unduh Data**")
if df_transaction is not None:
    output_excel = df_transaction.to_excel("Transaction_Data.xlsx", index=False)
    st.sidebar.download_button(
        label="📥 Download Excel",
        data=open("Transaction_Data.xlsx", "rb"),
        file_name="Transaction_Data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
