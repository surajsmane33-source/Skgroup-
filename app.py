                
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
        try:
            temp_df = pd.read_excel(file)
            # जर काही कॉलम मिसिंग असतील तर ते ॲड करणे
            for col in columns:
                if col not in temp_df.columns:
                    temp_df[col] = "-"
            return temp_df
        except:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

# डेटा लोड करणे (महत्त्वाचे बदल येथे केले आहेत)
config = load_data(CONFIG_FILE, ["Type", "Name", "Join_Date"])
df_pay = load_data(DB_FILE, ["Tarik", "Naw", "Status", "Advance"])
df_exp = load_data(EXP_FILE, ["Tarik", "Gadi_No", "Kothe", "Amt"])
df_inc = load_data(INC_FILE, ["Tarik", "Gadi_No", "Point", "Trips", "Amt"])

WORKERS = config[config["Type"] == "Worker"]
VEHICLES = config[config["Type"] == "Vehicle"]["Name"].tolist()

st.set_page_config(page_title="S K Group Manager", layout="wide")
st.title("🏗️ S K Group & Company Manager")

menu = st.sidebar.radio("मेनू निवडा", ["👷 कामगार हजेरी & हिशोब", "🚛 गाडी ट्रिप & खर्च", "⚙️ सेटिंग्ज (Add Name/Gadi)"])

# --- १. कामगार हिशोब ---
if menu == "👷 कामगार हजेरी & हिशोब":
    tab1, tab2 = st.tabs(["📝 नवीन हजेरी नोंदवा", "📊 कामगार रिपोर्ट & Delete"])

    with tab1:
        if not WORKERS.empty:
            with st.form("worker_entry"):
                w_n = st.selectbox("कामगार निवडा", WORKERS["Name"].tolist())
                w_d = st.date_input("तारीख", date.today())
                w_s = st.radio("स्थिती", ["Present", "Absent"])
                w_a = st.number_input("दिलेली उचल (Advance ₹)", min_value=0)
                if st.form_submit_button("नोंद जतन करा"):
                    new_data = pd.DataFrame([{"Tarik": str(w_d), "Naw": w_n, "Status": w_s, "Advance": w_a}])
                    df_pay = pd.concat([df_pay, new_data], ignore_index=True)
                    df_pay.to_excel(DB_FILE, index=False)
                    st.success("नोंद जतन झाली!")
                    st.rerun()
        else:
            st.warning("कृपया आधी 'सेटिंग्ज' मध्ये जाऊन कामगाराचे नाव ॲड करा.")

    with tab2:
        if not WORKERS.empty:
            sel_w = st.selectbox("कामगार निवडा", WORKERS["Name"].tolist(), key="report_w")

            # जॉइनिंग तारीख सुरक्षितपणे काढणे
            worker_info = WORKERS[WORKERS["Name"] == sel_w]
            j_date = worker_info["Join_Date"].values[0] if not worker_info.empty else "-"
            st.info(f"📅 कामावर रुजू तारीख: {j_date}")

            w_rep = df_pay[df_pay["Naw"] == sel_w]
            st.write(f"**{sel_w}** चा एकूण हिशोब:")
            st.dataframe(w_rep, use_container_width=True)

            if not w_rep.empty:
                idx_to_del = st.selectbox("डिलीट करण्यासाठी इंडेक्स निवडा", w_rep.index)
                if st.button("निवडलेली नोंद डिलीट करा"):
                    df_pay = df_pay.drop(idx_to_del)
                    df_pay.to_excel(DB_FILE, index=False)
                    st.rerun()
        else:
            st.info("डेटा उपलब्ध नाही.")

# --- २. गाडी ट्रिप & खर्च ---
elif menu == "🚛 गाडी ट्रिप & खर्च":
    tab_t1, tab_t2, tab_t3 = st.tabs(["💰 नवीन ट्रिप नोंद", "⛽ नवीन खर्च नोंद", "📊 गाडीनुसार रिपोर्ट"])

    with tab_t1:
        if VEHICLES:
            with st.form("trip_in"):
                v_n = st.selectbox("गाडी निवडा", VEHICLES)
                p_n = st.text_input("पॉइंटचे नाव (कुठून-कुठे)")
                t_c = st.number_input("ट्रिप्स संख्या", min_value=1, value=1)
                t_a = st.number_input("रक्कम ₹", min_value=0)
                if st.form_submit_button("ट्रिप जतन करा"):
                    new_i = pd.DataFrame([{"Tarik": str(date.today()), "Gadi_No": v_n, "Point": p_n, "Trips": t_c, "Amt": t_a}])
                    df_inc = pd.concat([df_inc, new_i], ignore_index=True)
                    df_inc.to_excel(INC_FILE, index=False)
                    st.rerun()
        else:
            st.warning("आधी सेटिंग्जमध्ये गाडी नंबर ॲड करा.")

    with tab_t2:
        if VEHICLES:
            with st.form("exp_in"):
                v_e = st.selectbox("गाडी निवडा", VEHICLES, key="ve_entry")
                e_l = st.text_input("खर्चाचा तपशील (उदा. डिझेल, टायर)")
                e_a = st.number_input("खर्च रक्कम ₹", min_value=0)
                if st.form_submit_button("खर्च जतन करा"):
                    new_e = pd.DataFrame([{"Tarik": str(date.today()), "Gadi_No": v_e, "Kothe": e_l, "Amt": e_a}])
                    df_exp = pd.concat([df_exp, new_e], ignore_index=True)
                    df_exp.to_excel(EXP_FILE, index=False)
                    st.rerun()

    with tab_t3:
        if VEHICLES:
            sel_v = st.selectbox("गाडी निवडा", VEHICLES, key="v_report")
            v_i_data = df_inc[df_inc["Gadi_No"] == sel_v]
            v_e_data = df_exp[df_exp["Gadi_No"] == sel_v]

            st.metric("गाडीचा एकूण नफा", f"₹{v_i_data['Amt'].sum() - v_e_data['Amt'].sum()}")

            col_a, col_b = st.columns(2)
            col_a.write("📊 ट्रिप/कमाई")
            col_a.dataframe(v_i_data)
            col_b.write("⛽ खर्च")
            col_b.dataframe(v_e_data)

            if not v_i_data.empty or not v_e_data.empty:
                st.warning("डेटा डिलीट करण्यासाठी रिपोर्टमधील एक्सेल फाईल तपासा किंवा शेवटची नोंद डिलीट करा.")

# --- ३. सेटिंग्ज ---
elif menu == "⚙️ सेटिंग्ज (Add Name/Gadi)":
    st.subheader("⚙️ नवीन मास्टर नोंदणी")
    col_x, col_y = st.columns(2)

    with col_x:
        st.write("### 🚛 नवीन गाडी ॲड करा")
        new_v_no = st.text_input("गाडी नंबर (उदा. MH 44 1234)")
        if st.button("गाडी सेव्ह करा"):
            if new_v_no:
                new_row = pd.DataFrame([{"Type": "Vehicle", "Name": new_v_no, "Join_Date": "-"}])
                config = pd.concat([config, new_row], ignore_index=True)
                config.to_excel(CONFIG_FILE, index=False)
                st.success("गाडी नंबर सेव्ह झाला!")
                st.rerun()

    with col_y:
        st.write("### 👷 नवीन कामगार ॲड करा")
        new_worker_name = st.text_input("कामगाराचे नाव")
        joining_date = st.date_input("जॉइनिंग तारीख")
        if st.button("कामगार सेव्ह करा"):
            if new_worker_name:
                new_row = pd.DataFrame([{"Type": "Worker", "Name": new_worker_name, "Join_Date": str(joining_date)}])
                config = pd.concat([config, new_row], ignore_index=True)
                config.to_excel(CONFIG_FILE, index=False)
                st.success("कामगार सेव्ह झाला!")
                st.rerun()

    st.divider()
    st.write("सध्याची मास्टर यादी:")
    st.dataframe(config, use_container_width=True)

                                         
