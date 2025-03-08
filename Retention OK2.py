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

if st.sidebar.radio("**Back**", ["🏠 Home"], index=0 if st.session_state.page == "home" else None) == "🏠 Home":
    st.session_state.page = "home"
    st.rerun()

# ====================== LOAD DATA UNIQUE MEMBER DARI FOLDER ====================== #
script_dir = os.path.dirname(__file__)  
unique_member_path = os.path.join(script_dir, "Unique_Member.xlsx")  

if os.path.exists(unique_member_path):
    df_unique = pd.read_excel(unique_member_path)
else:
    st.error("⚠️ File **Unique_Member.xlsx** tidak ditemukan!")

# ====================== SIDEBAR MENU ====================== #
st.sidebar.header("📂 **Filter Data**")
date_range = st.sidebar.date_input("📅 **Pilih Rentang Tanggal**", [], key="date_range")

# ====================== FUNGSI FILTER DATE RANGE ====================== #
def filter_by_date(df, date_column):
    """Memfilter DataFrame berdasarkan rentang tanggal yang dipilih user."""
    if df is not None and not df.empty and len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range)

        if date_column in df.columns:
            df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
            df = df.dropna(subset=[date_column])
            df = df[(df[date_column] >= start_date) & (df[date_column] <= end_date)]
    
    return df

# ====================== LOAD DATA TRANSAKSI & INPUT ====================== #
uploaded_file_transaction = st.sidebar.file_uploader("📥 **Upload Data Transaksi**", type=["xlsx"])
uploaded_file_input = st.sidebar.file_uploader("📥 **Upload Data Manual (Harian)**", type=["xlsx"])

df_transaction, df_input = None, None
df_filtered_transaction, df_filtered_input = None, None

if uploaded_file_transaction:
    df_transaction = pd.read_excel(uploaded_file_transaction)
    df_transaction["Date"] = pd.to_datetime(df_transaction["Date"], errors="coerce")
    df_filtered_transaction = filter_by_date(df_transaction, "Date")

if uploaded_file_input:
    df_input = pd.read_excel(uploaded_file_input)
    df_input["Date"] = pd.to_datetime(df_input["Date"], errors="coerce")
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

    if df_filtered_transaction is not None:
        df_new_customers = df_filtered_transaction[df_filtered_transaction["Unique_Code"].isin(df_unique["Unique_Code"])]
        total_new_customers = df_new_customers["Unique_Code"].nunique()

        target_customers = 210
        achievement = (total_new_customers / target_customers) * 100

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🎯 Target Pindah", target_customers)
        with col2:
            st.metric("✅ Customer yang Pindah", total_new_customers)
        with col3:
            st.metric("📈 Pencapaian (%)", f"{achievement:.2f}%")

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

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator())

        st.pyplot(fig)
        st.write("📋 **Detail Data Total Customers**")
        st.dataframe(df_filtered_transaction)

# ====================== MENU: JUMLAH TOTAL CASE HARIAN ====================== #
elif menu == "📈 Daily Active Member & Target Achievement":
    st.subheader("📈 **Daily Active Member & Target Achievement**")
    if df_filtered_input is not None:
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(x=df_filtered_input["Date"], y=df_filtered_input["Members"], marker="o", linestyle="-", color="blue", ax=ax)

        ax.axhline(y=70, color="red", linestyle="dashed", label="Target Harian")
        ax.set_xlabel("Date")
        ax.set_ylabel("Daily Active Members")
        ax.legend()
        ax.grid(True)

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator())

        st.pyplot(fig)
        st.write("📋 **Detail Data Total Case Harian**")
        st.dataframe(df_filtered_input)

# ====================== FITUR SAVE & DOWNLOAD ====================== #
st.sidebar.subheader("📥 **Simpan & Unduh Data**")
if df_transaction is not None:
    df_transaction.to_excel("Transaction_Data.xlsx", index=False)
    st.sidebar.download_button(
        label="📥 Download Excel",
        data=open("Transaction_Data.xlsx", "rb"),
        file_name="Transaction_Data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
