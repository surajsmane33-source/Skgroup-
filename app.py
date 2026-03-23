
import streamlit as st
import pandas as pd
from datetime import date
import os

# फाईल सेटअप
DB_FILE = "sk_payroll.xlsx"
EXP_FILE = "sk_expenses.xlsx"
INC_FILE = "sk_income.xlsx"
CONFIG_FILE = "sk_config.xlsx"

def load_data(file, columns):
    if os.path.exists(file):
        try: return pd.read_excel(file)
        except: return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

# डेटा लोड करणे
df_pay = load_data(DB_FILE, ["Index", "Tarik", "Naw", "Status", "Advance"])
df_exp = load_data(EXP_FILE, ["Index", "Tarik", "Gadi_No", "Kothe", "Amt"])
df_inc = load_data(INC_FILE, ["Index", "Tarik", "Gadi_No", "Point", "Trips", "Amt"])
config = load_data(CONFIG_FILE, ["Type", "Name", "Join_Date"])

WORKERS = config[config["Type"] == "Worker"]
VEHICLES = config[config["Type"] == "Vehicle"]["Name"].tolist()

st.set_page_config(page_title="S K Group Manager", layout="wide")
st.title("🏗️ S K Group & Company Manager")

menu = st.sidebar.radio("मेनू निवडा", ["👷 कामगार हिशोब", "🚛 गाडी ट्रिप & खर्च", "⚙️ सेटिंग्ज (Add/Edit Name)"])

# --- १. कामगार हिशोब (Joining, Absent, Advance) ---
if menu == "👷 कामगार हिशोब":
    tab1, tab2 = st.tabs(["📝 नवीन नोंदणी", "📊 रिपोर्ट & Edit/Delete"])

    with tab1:
        with st.form("worker_entry"):
            w_n = st.selectbox("कामगार निवडा", WORKERS["Name"].tolist())
            w_d = st.date_input("तारीख", date.today())
            w_s = st.radio("स्थिती", ["Present", "Absent"])
            w_a = st.number_input("दिलेली उचल (Advance ₹)", min_value=0)
            if st.form_submit_button("जतन करा"):
                new_data = pd.DataFrame([{"Tarik": str(w_d), "Naw": w_n, "Status": w_s, "Advance": w_a}])
                df_pay = pd.concat([df_pay, new_data], ignore_index=True)
                df_pay.to_excel(DB_FILE, index=False)
                st.success("नोंद झाली!")
                st.rerun()

    with tab2:
        sel_w = st.selectbox("कामगार निवडा (रिपोर्ट साठी)", WORKERS["Name"].tolist())
        j_date = WORKERS[WORKERS["Name"] == sel_w]["Join_Date"].values[0]
        st.info(f"📅 जॉइनिंग तारीख: {j_date}")

        w_rep = df_pay[df_pay["Naw"] == sel_w]
        st.dataframe(w_rep, use_container_width=True)

        if not w_rep.empty:
            idx_to_del = st.selectbox("काढून टाकण्यासाठी किंवा बदलण्यासाठी Index निवडा", w_rep.index)
            if st.button("निवडलेली नोंद Delete करा"):
                df_pay = df_pay.drop(idx_to_del)
                df_pay.to_excel(DB_FILE, index=False)
                st.rerun()

# --- २. गाडी ट्रिप & खर्च ---
elif menu == "🚛 गाडी ट्रिप & खर्च":
    tab_t1, tab_t2, tab_t3 = st.tabs(["💰 ट्रिप नोंद (Income)", "⛽ खर्च नोंद (Expense)", "📊 गाडीनुसार रिपोर्ट"])

    with tab_t1:
        with st.form("trip_in"):
            v_n = st.selectbox("गाडी निवडा", VEHICLES)
            p_n = st.text_input("पॉइंटचे नाव")
            t_c = st.number_input("ट्रिप्स संख्या", min_value=1)
            t_a = st.number_input("मिळालेली रक्कम ₹", min_value=0)
            if st.form_submit_button("ट्रिप जतन करा"):
                new_i = pd.DataFrame([{"Tarik": str(date.today()), "Gadi_No": v_n, "Point": p_n, "Trips": t_c, "Amt": t_a}])
                df_inc = pd.concat([df_inc, new_i], ignore_index=True)
                df_inc.to_excel(INC_FILE, index=False)
                st.rerun()

    with tab_t2:
        with st.form("exp_in"):
            v_e = st.selectbox("गाडी निवडा", VEHICLES, key="ve")
            e_l = st.text_input("कुठे खर्च झाला?")
            e_a = st.number_input("खर्च रक्कम ₹", min_value=0)
            if st.form_submit_button("खर्च जतन करा"):
                new_e = pd.DataFrame([{"Tarik": str(date.today()), "Gadi_No": v_e, "Kothe": e_l, "Amt": e_a}])
                df_exp = pd.concat([df_exp, new_e], ignore_index=True)
                df_exp.to_excel(EXP_FILE, index=False)
                st.rerun()

    with tab_t3:
        sel_v = st.selectbox("गाडी निवडा (रिपोर्ट)", VEHICLES)
        col1, col2 = st.columns(2)
        v_i_data = df_inc[df_inc["Gadi_No"] == sel_v]
        v_e_data = df_exp[df_exp["Gadi_No"] == sel_v]

        col1.write("### ट्रिप्स/कमाई")
        col1.dataframe(v_i_data)
        col2.write("### खर्च")
        col2.dataframe(v_e_data)

        st.metric("गाडीचा निव्वळ नफा", f"₹{v_i_data['Amt'].sum() - v_e_data['Amt'].sum()}")

        if st.button("Delete Last Trip Entry"):
            df_inc = df_inc[df_inc["Gadi_No"] == sel_v].iloc[:-1]
            df_inc.to_excel(INC_FILE, index=False)
            st.rerun()

# --- ३. सेटिंग्ज ---
elif menu == "⚙️ सेटिंग्ज (Add/Edit Name)":
    st.subheader("नवीन गाडी किंवा कामगार जोडा")
    c_a, c_b = st.columns(2)
    with c_a:
        new_v = st.text_input("गाडी नंबर")
        if st.button("Save Gadi"):
            new_row = pd.DataFrame([{"Type": "Vehicle", "Name": new_v, "Join_Date": "-"}])
            config = pd.concat([config, new_row], ignore_index=True)
            config.to_excel(CONFIG_FILE, index=False)
            st.rerun()
    with c_b:
        new_w = st.text_input("कामगार नाव")
        j_d = st.date_input("जॉइनिंग तारीख")
        if st.button("Save Worker"):
            new_row = pd.DataFrame([{"Type": "Worker", "Name": new_w, "Join_Date": str(j_d)}])
            config = pd.concat([config, new_row], ignore_index=True)
            config.to_excel(CONFIG_FILE, index=False)
            st.rerun()

