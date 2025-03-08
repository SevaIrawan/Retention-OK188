import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ====================== SETUP DASHBOARD ====================== #
st.set_page_config(page_title="Analyst Data XCRM 2025", layout="wide")

# ====================== TAMPILAN HOME ====================== #
if "page" not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":
    st.markdown("<h1 style='text-align: center; color: blue;'>📊 Analyst Data XCRM 2025</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>🔹 Select Go To Dashboard on the left to begin data analysis.</h4>", unsafe_allow_html=True)

    # Tombol untuk masuk ke dashboard data
    if st.button("Go To Dashboard 📊"):
        st.session_state.page = "dashboard"
        st.rerun()
    st.stop()

# **Ketika user memilih "Home", kembali ke halaman utama**
if st.sidebar.radio("**Back**", ["🏠 Home"], index=0 if st.session_state.page == "home" else None) == "🏠 Home":
    st.session_state.page = "home"
    st.rerun()

# ====================== LOAD DATA UNIQUE MEMBER DARI FOLDER ====================== #
script_dir = os.path.dirname(__file__)  # Direktori skrip
unique_member_path = os.path.join(script_dir, "Unique_Member.xlsx")  # Path ke file

if os.path.exists(unique_member_path):
    df_unique = pd.read_excel(unique_member_path)
else:
    st.error("⚠️ File **Unique_Member.xlsx** tidak ditemukan! Pastikan file ada dalam folder yang sama.")

# ====================== SIDEBAR MENU ====================== #
st.sidebar.header("📂 **Filter Data**")

# **Pilih Rentang Tanggal**
date_range = st.sidebar.date_input("📅 **Pilih Rentang Tanggal**", [], key="date_range")

# ====================== FILTER DATA BERDASARKAN DATE RANGE ====================== #
def filter_by_date(df, date_column):
    """Fungsi untuk memfilter DataFrame berdasarkan rentang tanggal yang dipilih user."""
    if len(date_range) == 2:  # Jika user memilih 2 tanggal (Start & End)
        start_date, end_date = date_range
        df[date_column] = pd.to_datetime(df[date_column])  # Pastikan format datetime
        df = df[(df[date_column] >= start_date) & (df[date_column] <= end_date)]
    return df

# ====================== LOAD DATA TRANSAKSI & INPUT ====================== #
uploaded_file_transaction = st.sidebar.file_uploader("📥 **Upload Data Transaksi**", type=["xlsx"])
uploaded_file_input = st.sidebar.file_uploader("📥 **Upload Data Manual (Harian)**", type=["xlsx"])

if uploaded_file_transaction:
    df_transaction = pd.read_excel(uploaded_file_transaction)
    df_transaction = filter_by_date(df_transaction, "Date")  # **Filter Data Transaksi**

if uploaded_file_input:
    df_input = pd.read_excel(uploaded_file_input)
    df_input = filter_by_date(df_input, "Date")  # **Filter Data Manual**

# ====================== LOAD DATA TRANSAKSI & INPUT ====================== #
uploaded_file_transaction = st.sidebar.file_uploader("📥 **Upload Data Transaksi**", type=["xlsx"])
uploaded_file_input = st.sidebar.file_uploader("📥 **Upload Data Manual (Harian)**", type=["xlsx"])

if uploaded_file_transaction:
    df_transaction = pd.read_excel(uploaded_file_transaction)

if uploaded_file_input:
    df_input = pd.read_excel(uploaded_file_input)

# ====================== MENU: CUSTOMER YANG PINDAH ====================== #
if menu == "📊 Total Customers Successfully acquired & Target Achievement":
    st.subheader("📊 **Total Customers Successfully acquired & Target Achievement**")

    if uploaded_file_transaction:
        df_filtered = filter_by_date(df_transaction, "Date")  # **Gunakan Data yang Sudah Difilter**

        df_new_customers = df_filtered[df_filtered["Unique_Code"].isin(df_unique["Unique_Code"])]
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
        st.subheader("📈 **Trend Pindah Pelanggan Seiring Waktu**")
        daily_migration = df_new_customers.groupby("Date")["Unique_Code"].nunique().reset_index()
        daily_migration.rename(columns={"Unique_Code": "New_Customers"}, inplace=True)

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=daily_migration, x="Date", y="New_Customers", marker="o", linestyle="-", color="blue", ax=ax)
        ax.axhline(y=7, color="red", linestyle="dashed", label="Target Harian")
        ax.set_xlabel("Date")
        ax.set_ylabel("Total Customers Successfully acquired")
        ax.set_title("Trend Pindah Pelanggan Seiring Waktu")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

        # **Tampilkan DataFrame di bawah chart**
        st.write("📋 **Total Details of Successfully Acquired Customers**")
        st.dataframe(daily_migration)

    else:
        st.warning("⚠️ Silakan upload file **Transaction.xlsx**.")

# ====================== MENU: JUMLAH TOTAL CASE HARIAN ====================== #
elif menu == "📈 Daily Active Member & Target Achievement":
    st.subheader("📈 **Daily Active Member & Target Achievement**")
    if uploaded_file_input:
        fig, ax = plt.subplots(figsize=(10, 5))
        df_filtered_input = filter_by_date(df_input, "Date")  # 🔹 GUNAKAN DATA YANG SUDAH DIFILTER
        sns.lineplot(x=df_filtered_input["Date"], y=df_filtered_input["Members"], marker="o", linestyle="-", color="blue", ax=ax)
        ax.axhline(y=70, color="red", linestyle="dashed", label="Target Harian")
        ax.set_xlabel("Date")
        ax.set_ylabel("Daily Active Members")
        ax.legend()
        ax.grid(True)  # **Tambahkan Gridline**
        st.pyplot(fig)

        # **Tampilkan DataFrame di bawah chart**
        st.write("📋 **Detail Data Total Case Harian**")
        st.dataframe(df_input)

    else:
        st.warning("⚠️ Silakan upload file Input.xlsx!")

# ====================== MENU: JUMLAH TOTAL PENJUALAN HARIAN ====================== #
elif menu == "💰 Daily Deposit Amount & Target Achievement":
    st.subheader("💰 **Daily Deposit Amount & Target Achievement**")
    if uploaded_file_input:
        fig, ax = plt.subplots(figsize=(10, 5))
        df_filtered_input = filter_by_date(df_input, "Date")  # 🔹 GUNAKAN DATA YANG SUDAH DIFILTER
        sns.lineplot(x=df_filtered_input["Date"], y=df_filtered_input["Amount"], marker="o", linestyle="-", color="green", ax=ax)
        ax.axhline(y=13706, color="red", linestyle="dashed", label="Target")
        ax.set_xlabel("Date")
        ax.set_ylabel("Deposit Amount (SGD)")
        ax.legend()
        ax.grid(True)  # **Tambahkan Gridline**
        st.pyplot(fig)

        # **Tampilkan DataFrame di bawah chart**
        st.write("📋 **Detail Data Total Penjualan Harian**")
        st.dataframe(df_input)

    else:
        st.warning("⚠️ Silakan upload file Input.xlsx!")

# ====================== MENU: JUMLAH RETENTION MEMBER BARU ====================== #
elif menu == "🔁 New Member Retention":
    st.subheader("🔁 **New Member Retention**")
    if uploaded_file_transaction:
        # Hitung jumlah hari aktif setiap member
        retention_counts = df_transaction.groupby("Unique_Code")["Date"].nunique()

        df_filtered = filter_by_date(df_transaction, "Date")  # 🔹 GUNAKAN DATA YANG SUDAH DIFILTER
        retention_data = df_filtered.groupby("Unique_Code").agg({"Date": "nunique", "Amount": "sum"})
        # Hitung jumlah customer & total Amount per Retention Days
        retention_summary = retention_data.groupby("Date").agg({"Amount": "sum", "Date": "count"})
        retention_summary.rename(columns={"Date": "Customer"}, inplace=True)

        fig, ax = plt.subplots(figsize=(10, 5))

        # **Plot batang bar untuk Customer**
        bars = ax.bar(retention_summary.index, retention_summary["Customer"], color="purple", alpha=0.7)

        # **Tambahkan Gridline**
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        # **Menampilkan Amount di dalam batang bar (Text Vertikal)**
        for bar, amount in zip(bars, retention_summary["Amount"]):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height / 2,  # Posisikan teks di tengah batang
                    f"${int(amount):,}", ha='center', va='center', fontsize=8, color='white', fontweight='bold',
                    rotation=90)  # **Text dalam bentuk vertikal**

        # **Label sumbu & judul**
        ax.set_xlabel("Retention Days")
        ax.set_ylabel("Customer")
        ax.set_title("🔁 New Member Retention")

        # **Tampilkan chart di Streamlit**
        st.pyplot(fig)

        # **Tampilkan DataFrame di bawah chart**
        st.write("📋 **Detail Data Retention Member Baru (Amount & Customer)**")
        st.dataframe(retention_summary)

    else:
        st.warning("⚠️ Silakan upload file Transaction.xlsx!")

# ====================== FITUR SAVE & DOWNLOAD ====================== #
st.sidebar.subheader("📥 **Simpan & Unduh Data**")
if uploaded_file_transaction:
    output_excel = df_transaction.to_excel("Transaction_Data.xlsx", index=False)
    st.sidebar.download_button(
        label="📥 Download Excel",
        data=open("Transaction_Data.xlsx", "rb"),
        file_name="Transaction_Data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
