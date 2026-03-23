import streamlit as st
import pandas as pd
from datetime import date
import os
import plotly.express as px

# फाईल सेटअप
DB_FILE = "sk_group_payroll.xlsx"
EXP_FILE = "sk_group_expenses.xlsx"
WORKERS = ["KHANDU HAJARE", "OM JADHAV", "SURAJ SHINDE", "ABHISHEK PATOLE"]

def load_data(file, columns):
    if os.path.exists(file):
        try:
            return pd.read_excel(file)
        except:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

df = load_data(DB_FILE, ["तारीख", "नाव", "हजेरी", "पगार प्रकार", "पगार", "उचल (Advance)", "शिल्लक"])
df_exp = load_data(EXP_FILE, ["तारीख", "खर्चाचा प्रकार", "तपशील", "रक्कम"])

st.set_page_config(page_title="S K Group & Company", layout="wide")
st.title("🏗️ S K Group & Company - Professional Manager")

menu = st.sidebar.selectbox("मेनू निवडा", ["👷 कामगार हजेरी", "💸 इतर खर्च (Expenses)", "📊 एकूण रिपोर्ट"])

# --- १. कामगार हजेरी आणि डिलीट ---
if menu == "👷 कामगार हजेरी":
    st.subheader("कामगार हजेरी आणि पगार नोंद")
    with st.expander("➕ नवीन हजेरी नोंदवा"):
        with st.form("worker_form"):
            col1, col2 = st.columns(2)
            with col1:
                selected_worker = st.selectbox("कामगाराचे नाव", WORKERS)
                pay_type = st.radio("पगार प्रकार", ["रोजंदारी (Daily)", "महिन्याचा (Monthly)"])
                entry_date = st.date_input("तारीख", date.today())
            with col2:
                status = st.radio("हजेरी", ["पूर्ण दिवस", "अर्धा दिवस", "गैरहजर"])
                wage_def = 600 if status == "पूर्ण दिवस" and pay_type == "रोजंदारी (Daily)" else (300 if status == "अर्धा दिवस" and pay_type == "रोजंदारी (Daily)" else 0)
                daily_wage = st.number_input("आजचा पगार (₹)", value=wage_def)
                advance = st.number_input("दिलेली उचल (Advance ₹)", min_value=0)

            if st.form_submit_button("नोंद जतन करा"):
                new_row = {"तारीख": str(entry_date), "नाव": selected_worker, "हजेरी": status, "पगार प्रकार": pay_type, "पगार": daily_wage, "उचल (Advance)": advance, "शिल्लक": daily_wage - advance}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                df.to_excel(DB_FILE, index=False)
                st.success("नोंद झाली!")
                st.rerun()

    st.divider()
    st.subheader("🔍 हिशोब पहा आणि चुकीची नोंद डिलीट करा")
    search_name = st.selectbox("कामगार निवडा", WORKERS)
    worker_df = df[df["नाव"] == search_name]

    if not worker_df.empty:
        st.dataframe(worker_df, use_container_width=True)
        row_to_del = st.selectbox("डिलीट करण्यासाठी नोंद निवडा (Index No.)", worker_df.index, key="del_worker")
        if st.button("❌ निवडलेली हजेरी डिलीट करा"):
            df = df.drop(row_to_del)
            df.to_excel(DB_FILE, index=False)
            st.warning("हजेरीची नोंद यशस्वीरित्या काढून टाकली!")
            st.rerun()

# --- २. इतर खर्च आणि डिलीट ---
elif menu == "💸 इतर खर्च (Expenses)":
    st.subheader("इतर खर्च (डिझेल, साहित्य, इ.)")
    with st.expander("➕ नवीन खर्च नोंदवा"):
        with st.form("exp_form"):
            e_date = st.date_input("तारीख", date.today())
            e_type = st.selectbox("खर्चाचा प्रकार", ["डिझेल/इंधन", "सिमेंट/खडी/वाळू", "मशिनरी भाडे", "दुरुस्ती (Repairing)", "जेवण/नाश्ता", "इतर"])
            e_desc = st.text_input("तपशील")
            e_amt = st.number_input("रक्कम (₹)", min_value=0)
            if st.form_submit_button("खर्च जतन करा"):
                new_exp = {"तारीख": str(e_date), "खर्चाचा प्रकार": e_type, "तपशील": e_desc, "रक्कम": e_amt}
                df_exp = pd.concat([df_exp, pd.DataFrame([new_exp])], ignore_index=True)
                df_exp.to_excel(EXP_FILE, index=False)
                st.success("खर्चाची नोंद झाली!")
                st.rerun()

    st.divider()
    st.subheader("🔍 खर्चाचा इतिहास आणि डिलीट")
    if not df_exp.empty:
        st.dataframe(df_exp, use_container_width=True)
        exp_to_del = st.selectbox("डिलीट करण्यासाठी खर्च निवडा (Index No.)", df_exp.index, key="del_exp")
        if st.button("❌ निवडलेला खर्च डिलीट करा"):
            df_exp = df_exp.drop(exp_to_del)
            df_exp.to_excel(EXP_FILE, index=False)
            st.warning("खर्चाची नोंद काढून टाकली!")
            st.rerun()
    else:
        st.info("कोणताही खर्च नोंदवलेला नाही.")

# --- ३. एकूण रिपोर्ट ---
elif menu == "📊 एकूण रिपोर्ट":
    st.subheader("व्यवसायाचा लेखाजोखा")
    total_worker_pay = df["पगार"].sum()
    total_worker_adv = df["उचल (Advance)"].sum()
    total_other_exp = df_exp["रक्कम"].sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("कामगार एकूण पगार", f"₹{total_worker_pay}")
    c2.metric("दिलेली एकूण उचल", f"₹{total_worker_adv}")
    c3.metric("इतर खर्च (Expenses)", f"₹{total_other_exp}")

    if not df_exp.empty:
        fig_exp = px.pie(df_exp, values='रक्कम', names='खर्चाचा प्रकार', title='खर्चाचे वर्गीकरण')
        st.plotly_chart(fig_exp, use_container_width=True)

