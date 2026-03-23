
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

# Config Load (Workers with Joining Date)
config_df = load_data(CONFIG_FILE, ["Type", "Name", "Start_Date"])
if "Start_Date" not in config_df.columns:
    config_df["Start_Date"] = str(date.today())

WORKERS_LIST = config_df[config_df["Type"] == "Worker"]
VEHICLES = config_df[config_df["Type"] == "Vehicle"]["Name"].tolist()

df = load_data(DB_FILE, ["Tarik", "Naw", "Status", "Pagar", "Advance"])
df_exp = load_data(EXP_FILE, ["Tarik", "Gadi_No", "Kothe", "Amt"])
df_inc = load_data(VEHICLE_INCOME_FILE, ["Tarik", "Gadi_No", "Point_Naw", "Trips", "Amt"])

st.set_page_config(page_title="S K Group - Manager", layout="wide")

menu = st.sidebar.selectbox("Main Menu", ["🏠 Dashboard", "📝 Navin Entry", "👷 Kamgar Report", "🚛 Gadi Report", "⚙️ Settings (Add Gadi/Worker)"])

# --- 1. Settings (Joining Date Nondvanyasathi) ---
if menu == "⚙️ Settings (Add Gadi/Worker)":
    st.subheader("⚙️ Navin Gadi kiva Kamgar Joada")
    col1, col2 = st.columns(2)

    with col1:
        new_v = st.text_input("Gadi Number")
        if st.button("Gadi Save Kara"):
            new_v_row = pd.DataFrame([{"Type": "Vehicle", "Name": new_v, "Start_Date": "-"}])
            config_df = pd.concat([config_df, new_v_row], ignore_index=True)
            config_df.to_excel(CONFIG_FILE, index=False)
            st.rerun()

    with col2:
        new_w = st.text_input("Kamgarache Naw")
        j_date = st.date_input("Kamgar kadhi pasun chalu jhala? (Joining Date)", date.today())
        if st.button("Kamgar Save Kara"):
            new_w_row = pd.DataFrame([{"Type": "Worker", "Name": new_w, "Start_Date": str(j_date)}])
            config_df = pd.concat([config_df, new_w_row], ignore_index=True)
            config_df.to_excel(CONFIG_FILE, index=False)
            st.rerun()

    st.divider()
    st.write("Sadhya asleli list:")
    st.dataframe(config_df, use_container_width=True)

# --- 2. Navin Entry ---
elif menu == "📝 Navin Entry":
    st.subheader("📝 Daily Nond")
    t1, t2, t3 = st.tabs(["🚛 Gadi Trip", "⛽ Gadi Kharch", "👤 Kamgar Absent/Advance"])

    with t1:
        with st.form("trip"):
            v_no = st.selectbox("Gadi Nivda", VEHICLES)
            p_n = st.text_input("Point che Naw")
            t_c = st.number_input("Trips", min_value=1, value=1)
            t_a = st.number_input("Rakkam", min_value=0)
            if st.form_submit_button("Save Trip"):
                new_i = {"Tarik": str(date.today()), "Gadi_No": v_no, "Point_Naw": p_n, "Trips": t_c, "Amt": t_a}
                df_inc = pd.concat([df_inc, pd.DataFrame([new_i])], ignore_index=True)
                df_inc.to_excel(VEHICLE_INCOME_FILE, index=False)
                st.rerun()

    with t3:
        with st.form("worker"):
            w_n = st.selectbox("Kamgar Nivda", WORKERS_LIST["Name"].tolist())
            w_s = st.radio("Status", ["Absent", "Present (Fakt Advance)"])
            w_adv = st.number_input("Advance (Uchal)", min_value=0)
            if st.form_submit_button("Save Worker Entry"):
                new_p = {"Tarik": str(date.today()), "Naw": w_n, "Status": w_s, "Pagar": 0, "Advance": w_adv}
                df = pd.concat([df, pd.DataFrame([new_p])], ignore_index=True)
                df.to_excel(DB_FILE, index=False)
                st.rerun()

# --- 3. Kamgar Report ---
elif menu == "👷 Kamgar Report":
    sel_w = st.selectbox("Kamgar Nivda", WORKERS_LIST["Name"].tolist())
    # Joining Date Shodhne
    joining_date = WORKERS_LIST[WORKERS_LIST["Name"] == sel_w]["Start_Date"].values[0]

    st.subheader(f"👤 {sel_w} yancha Report")
    st.info(f"📅 **Mahina Chalu Jhala (Joining Date):** {joining_date}")

    w_data = df[df["Naw"] == sel_w]
    st.dataframe(w_data, use_container_width=True)
    st.write(f"**Ekun Advance:** ₹{w_data['Advance'].sum()}")

# --- Bakiche Report ---
elif menu == "🏠 Dashboard":
    st.title("S K Group Dashboard")
    st.metric("Total Profit", f"₹{df_inc['Amt'].sum() - df_exp['Amt'].sum()}")

elif menu == "🚛 Gadi Report":
    sel_v = st.selectbox("Gadi Nivda", VEHICLES)
    v_inc = df_inc[df_inc['Gadi_No'] == sel_v]
    st.dataframe(v_inc, use_container_width=True)
    st.metric("Total Trips", v_inc['Trips'].sum())

