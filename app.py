import streamlit as st
import pandas as pd
from datetime import date
import os
import plotly.express as px

# File Setup
DB_FILE = "sk_payroll.xlsx"
EXP_FILE = "sk_expenses.xlsx"

# Tumchi mahiti
WORKERS = ["KHANDU HAJARE", "OM JADHAV", "SURAJ SHINDE", "ABHISHEK PATOLE"]
VEHICLES = ["Gadi No 1", "Gadi No 2", "Gadi No 3", "Other"] # Tumchi gadi numbers yethal lihaha

def load_data(file, columns):
    if os.path.exists(file):
        try: return pd.read_excel(file)
        except: return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

df = load_data(DB_FILE, ["Tarik", "Naw", "Status", "Pagar_Type", "Pagar", "Advance"])
df_exp = load_data(EXP_FILE, ["Tarik", "MH24AB7551", "Kothe", "Kharch_Type", "Amt", "Detail"])

st.set_page_config(page_title="S K Group Manager", layout="wide")
st.title("🏗️ S K Group & Company - Business Manager")

menu = st.sidebar.selectbox("Menu", ["🚩 Absent Nondva", "🚛 Gadi Kharch", "📊 Report & Delete"])

# --- 1. Absent Nondva ---
if menu == "🚩 Absent Nondva":
    st.subheader("🚩 Kamgar Absent Nond (Baaki divas Present dharle jaatil)")
    with st.form("absent_form"):
        a_date = st.date_input("Tarik", date.today())
        absent_worker = st.selectbox("Absent aslelya kamgarache naw", WORKERS)
        p_type = st.radio("Pagar Type", ["Daily", "Monthly"])
        st.info("Tip: Fakt Absent asel tarach yethal nond kara. Nond kelyas tya divasacha pagar 0 dharla jaail.")

        if st.form_submit_button("Absent Nondva"):
            new_row = {"Tarik": str(a_date), "Naw": absent_worker, "Status": "Absent", "Pagar_Type": p_type, "Pagar": 0, "Advance": 0}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_excel(DB_FILE, index=False)
            st.error(f"{absent_worker} yanchi {a_date} chi Absent nondavli geli.")
            st.rerun()

    # Advance nondvanyasathi vegla section
    st.divider()
    st.subheader("💸 Advance (Uchal) Dene")
    with st.form("adv_form"):
        adv_worker = st.selectbox("Kamgar निवडा", WORKERS)
        adv_amt = st.number_input("Advance Rakkam (₹)", min_value=0)
        if st.form_submit_button("Advance Jatan Kara"):
            new_adv = {"Tarik": str(date.today()), "Naw": adv_worker, "Status": "Present", "Pagar_Type": "N/A", "Pagar": 0, "Advance": adv_amt}
            df = pd.concat([df, pd.DataFrame([new_adv])], ignore_index=True)
            df.to_excel(DB_FILE, index=False)
            st.success("Advance chi nond jhali!")
            st.rerun()

# --- 2. Gadi Kharch ---
elif menu == "🚛 Gadi Kharch":
    st.subheader("🚛 Gadi-wise Kharch (Diesel/Maintenance)")
    with st.form("v_exp"):
        v_date = st.date_input("Tarik", date.today())
        v_no = st.selectbox("Gadi Number", VEHICLES)
        v_loc = st.text_input("Kothe (Location)")
        v_type = st.selectbox("Kharchacha Prakar", ["Diesel", "Repairing", "Driver Kharch", "Other"])
        v_amt = st.number_input("Rakkam (₹)", min_value=0)
        v_det = st.text_area("Detail (Kashasathi?)")

        if st.form_submit_button("Kharch Jatan Kara"):
            new_v = {"Tarik": str(v_date), "Gadi_No": v_no, "Kothe": v_loc, "Kharch_Type": v_type, "Amt": v_amt, "Detail": v_det}
            df_exp = pd.concat([df_exp, pd.DataFrame([new_v])], ignore_index=True)
            df_exp.to_excel(EXP_FILE, index=False)
            st.success(f"{v_no} cha kharch seve jhala!")
            st.rerun()

    st.write("### Maagil Gadi Kharch")
    st.dataframe(df_exp, use_container_width=True)

# --- 3. Report & Delete ---
elif menu == "📊 Report & Delete":
    st.subheader("📊 Sampurna Hisob")

    t1, t2 = st.tabs(["Kamgar Report", "Gadi Report"])

    with t1:
        s_worker = st.selectbox("Kamgar निवडा", WORKERS)
        w_data = df[df["Naw"] == s_worker]
        st.dataframe(w_data)
        st.write(f"Ekun Absent: {len(w_data[w_data['Status']=='Absent'])}")
        st.write(f"Ekun Advance: ₹{w_data['Advance'].sum()}")

        if not w_data.empty:
            ridx = st.selectbox("Delete karanyasathi Index nivda", w_data.index)
            if st.button("Delete Worker Entry"):
                df = df.drop(ridx)
                df.to_excel(DB_FILE, index=False)
                st.rerun()

    with t2:
        s_v = st.selectbox("Gadi निवडा", VEHICLES)
        v_data = df_exp[df_exp["Gadi_No"] == s_v]
        st.dataframe(v_data)
        st.metric(f"{s_v} Ekun Kharch", f"₹{v_data['Amt'].sum()}")

        if not v_data.empty:
            vidx = st.selectbox("Delete karanyasathi Index nivda", v_data.index, key="vdel")
            if st.button("Delete Gadi Entry"):
                df_exp = df_exp.drop(vidx)
                df_exp.to_excel(EXP_FILE, index=False)
                st.rerun()

