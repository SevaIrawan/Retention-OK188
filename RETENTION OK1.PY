import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
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

    if st.button("Go To Dashboard 📊"):
        st.session_state.page = "dashboard"
        st.rerun()
    st.stop()

# **Ketika user memilih "Home", kembali ke halaman utama**
if st.sidebar.radio("**Back**", ["🏠 Home"], index=0 if st.session_state.page == "home" else None) == "🏠 Home":
    st.session_state.page = "home"
    st.rerun()

# ====================== LOAD DATA ====================== #
st.sidebar.header("📂 **Filter Data**")

# **Pilih Rentang Tanggal**
date_range = st.sidebar.date_input("📅 **Pilih Rentang Tanggal**", [], key="date_range")

# ====================== FUNGSI FILTER DATE RANGE ====================== #
def filter_by_date(df, date_column):
    """Memfilter DataFrame berdasarkan rentang tanggal yang dipilih user."""
    if df is not None and not df.empty and len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range)

        if date_column in df.columns:
            df[date_column] = pd.to_datetime(df[date_column], errors='coerce')  # Konversi datetime
            df = df.dropna(subset=[date_column])  # Hapus NaN setelah konversi
            df = df[(df[date_column] >= start_date) & (df[date_column] <= end_date)]
    
    return df

# ====================== LOAD DATA TRANSAKSI & INPUT ====================== #
uploaded_file_transaction = st.sidebar.file_uploader("📥 **Upload Data Transaksi**", type=["xlsx"])
uploaded_file_input = st.sidebar.file_uploader("📥 **Upload Data Manual (Harian)**", type=["xlsx"])

# **Pastikan Variabel Terdefinisi**
df_transaction, df_input, df_filtered_transaction, df_filtered_input = None, None, None, None

if uploaded_file_transaction:
    df_transaction = pd.read_excel(uploaded_file_transaction)
    df_transaction["Date"] = pd.to_datetime(df_transaction["Date"])
    df_filtered_transaction = filter_by_date(df_transaction, "Date")

if uploaded_file_input:
    df_input = pd.read_excel(uploaded_file_input)
    df_input["Date"] = pd.to_datetime(df_input["Date"])
    df_filtered_input = filter_by_date(df_input, "Date")

# ====================== SIDEBAR MENU ====================== #
menu = st.sidebar.radio("📌 **Pilih Menu**", [
    "📊 Total Customers Successfully acquired & Target Achievement",
    "📈 Daily Active Member & Target Achievement",
    "💰 Daily Deposit Amount & Target Achievement",
    "🔁 New Member Retention"
])

# ====================== MENU: CUSTOMER YANG PINDAH ====================== #
if menu == "📊 Total Customers Successfully acquired & Target Achievement":
    st.subheader("📊 **Total Customers Successfully acquired & Target Achievement**")

    if uploaded_file_transaction:
        total_new_customers = df_filtered_transaction["Unique_Code"].nunique()

        # Target
        target_customers = 210
        achievement = (total_new_customers / target_customers) * 100

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🎯 Target Pindah", target_customers)
        with col2:
            st.metric("✅ Customer yang Pindah", total_new_customers)
        with col3:
            st.metric("📈 Pencapaian (%)", f"{achievement:.2f}%")

        # **📊 LINE CHART**
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=df_filtered_transaction.groupby("Date")["Unique_Code"].nunique().reset_index(), 
                     x="Date", y="Unique_Code", marker="o", linestyle="-", color="blue", ax=ax)

        ax.axhline(y=7, color="red", linestyle="dashed", label="Target Harian")
        ax.set_xlabel("Date")
        ax.set_ylabel("Total Customers Successfully acquired")
        ax.legend()
        ax.grid(True)

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator())

        st.pyplot(fig)

        # ✅ Tampilkan DataFrame
        st.write("📋 **Detail Data Total Customers**")
        st.dataframe(df_filtered_transaction)

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

        ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        st.pyplot(fig)

        st.write("📋 **Detail Data Retention Member Baru (Amount & Customer)**")
        st.dataframe(retention_summary)

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
