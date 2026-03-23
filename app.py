

import streamlit as st
import pandas as pd
from datetime import date
import os
import io

# File Setup
DB_FILE = "sk_payroll.xlsx"
EXP_FILE = "sk_expenses.xlsx"
VEHICLE_INCOME_FILE = "sk_vehicle_income.xlsx"
CONFIG_FILE = "sk_config.xlsx"

def load_data(file, columns):
    if os.path.exists(file):
        try: return pd.read_excel(file)
        except: return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

config_df = load_data(CONFIG_FILE, ["Type", "Name"])
WORKERS = config_df[config_df["Type"] == "Worker"]["Name"].tolist()
VEHICLES = config_df[config_df["Type"] == "Vehicle"]["Name"].tolist()

df = load_data(DB_FILE, ["Tarik", "Naw", "Status", "Pagar", "Advance"])
df_exp = load_data(EXP_FILE, ["Tarik", "Gadi_No", "Kothe", "Amt"])
df_inc = load_data(VEHICLE_INCOME_FILE, ["Tarik", "Gadi_No", "Point_Naw", "Trips", "Amt"])

st.set_page_config(page_title="S K Group - Pro Manager", layout="wide")

menu = st.sidebar.selectbox("Main Menu", ["📊 Dashboard", "👷 Kamgar Hisob", "🚛 Gadi & Trip Report", "⚙️ Add Gadi/Worker"])

# --- 1. Dashboard ---
if menu == "📊 Dashboard":
    st.title("🏗️ S K Group & Company")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Income", f"₹{df_inc['Amt'].sum()}")
    c2.metric("Total Expense", f"₹{df_exp['Amt'].sum()}")
    c3.metric("Net Profit", f"₹{df_inc['Amt'].sum() - df_exp['Amt'].sum()}")

# --- 2. Kamgar Hisob (Separate) ---
elif menu == "👷 Kamgar Hisob":
    sel_w = st.selectbox("Kamgar Nivda", WORKERS)
    w_data = df[df["Naw"] == sel_w]
    
    st.subheader(f"👤 {sel_w} yancha Report")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Ekun Advance (Uchal)", f"₹{w_data['Advance'].sum()}")
    with col2:
        st.metric("Ekun Absent", len(w_data[w_data['Status'] == 'Absent']))
    
    st.dataframe(w_data, use_container_width=True)
    
    # Share Logic
    share_text = f"S K Group Report\nKamgar: {sel_w}\nAdvance: {w_data['Advance'].sum()}\nAbsent: {len(w_data[w_data['Status'] == 'Absent'])}"
    st.text_area("Share karanyasathi copy kara:", share_text)

# --- 3. Gadi & Trip Report (Separate) ---
elif menu == "🚛 Gadi & Trip Report":
    sel_v = st.selectbox("Gadi Nivda", VEHICLES)
    v_inc = df_inc[df_inc['Gadi_No'] == sel_v]
    v_exp = df_exp[df_exp['Gadi_No'] == sel_v]
    
    st.subheader(f"🚛 {sel_v} Trip Hisob")
    
    # Trip Detail Table
    st.write("### Trip Details (Point-wise)")
    st.dataframe(v_inc, use_container_width=True)
    
    # Calculation
    total_trips = v_inc['Trips'].sum()
    total_income = v_inc['Amt'].sum()
    total_kharch = v_exp['Amt'].sum()
    profit = total_income - total_kharch
    
    c_v1, c_v2, c_v3 = st.columns(3)
    c_v1.metric("Total Trips", total_trips)
    c_v2.metric("Total Income", f"₹{total_income}")
    c_v3.metric("Profit", f"₹{profit}")

    # Share Feature
    v_share = f"Gadi Report: {sel_v}\nTotal Trips: {total_trips}\nIncome: {total_income}\nExpense: {total_kharch}\nProfit: {profit}"
    st.text_area("WhatsApp var share karanyasathi copy kara:", v_share)

# --- 4. Settings ---
elif menu == "⚙️ Add Gadi/Worker":
    st.subheader("Navin Gadi/Kamgar Add kara")
    col_a, col_b = st.columns(2)
    with col_a:
        new_v = st.text_input("Gadi Number")
        if st.button("Save Gadi"):
            pd.concat([config_df, pd.DataFrame([{"Type":"Vehicle","Name":new_v}])]).to_excel(CONFIG_FILE, index=False)
            st.rerun()
    with col_b:
        new_w = st.text_input("Kamgar Name")
        if st.button("Save Worker"):
            pd.concat([config_df, pd.DataFrame([{"Type":"Worker","Name":new_w}])]).to_excel(CONFIG_FILE, index=False)
            st.rerun()

