import streamlit as st
import pandas as pd
from datetime import date
import os  # ही ओळ असणे खूप गरजेचे आहे

# फाईल सेटअप
DB_FILE = "sk_group_payroll.xlsx"
# तुमच्या ४ कामगारांची खरी नावे येथे लिहा
WORKERS = ["KHANDU HAJARE", "OM JADHAV", "SURAJ SHINDE, "ABHISHEK PATOLE"]

# डेटाबेस लोड करणे किंवा नवीन बनवणे
if os.path.exists(DB_FILE):
    df = pd.read_excel(DB_FILE)
else:
    df = pd.DataFrame(columns=["तारीख", "नाव", "हजेरी", "पगार", "उचल (Advance)", "शिल्लक"])

st.set_page_config(page_title="S K Group Payroll", layout="wide")
st.title("🏗️ S K Group & Company - कामगार व्यवस्थापन")

# सायडबार फॉर्म
with st.sidebar:
    st.header("📌 रोजची नोंद")
    selected_worker = st.selectbox("कामगाराचे नाव निवडा", WORKERS)
    entry_date = st.date_input("तारीख", date.today())
    status = st.radio("हजेरी", ["पूर्ण दिवस", "अर्धा दिवस", "गैरहजर"])

    wage = 0
    if status == "पूर्ण दिवस": wage = 600
    elif status == "अर्धा दिवस": wage = 300

    daily_wage = st.number_input("आजचा पगार (₹)", value=wage)
    advance = st.number_input("आज दिलेली उचल (Advance ₹)", min_value=0)

    if st.button("नोंद जतन करा"):
        remaining = daily_wage - advance
        new_row = {"तारीख": str(entry_date), "नाव": selected_worker, "हजेरी": status,
                    "पगार": daily_wage, "उचल (Advance)": advance, "शिल्लक": remaining}

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_excel(DB_FILE, index=False)
        st.success(f"{selected_worker} यांची नोंद झाली!")
        st.rerun()

# मुख्य डॅशबोर्ड
tab1, tab2 = st.tabs(["📊 आजचा अहवाल", "🔍 कामगारानुसार शोध"])

with tab1:
    st.subheader("आजची उपस्थिती आणि व्यवहार")
    if not df.empty:
        # आजच्या तारखेचा डेटा दाखवणे
        today_data = df[df["तारीख"] == str(date.today())]
        if not today_data.empty:
            st.dataframe(today_data, use_container_width=True)
        else:
            st.info("आज अजून कोणतीही नोंद केलेली नाही.")
    else:
        st.info("डेटाबेस रिकामा आहे. कृपया पहिली नोंद करा.")

with tab2:
    search_name = st.selectbox("ज्याचा हिशोब पाहायचा आहे ते नाव निवडा", WORKERS)
    if not df.empty:
        worker_df = df[df["नाव"] == search_name]
        if not worker_df.empty:
            st.write(f"**{search_name} यांचा एकूण इतिहास:**")
            st.dataframe(worker_df)

            total_earned = worker_df["पगार"].sum()
            total_adv = worker_df["उचल (Advance)"].sum()
            total_bal = total_earned - total_adv

            c1, c2, c3 = st.columns(3)
            c1.metric("एकूण कमाई", f"₹{total_earned}")
            c2.metric("एकूण उचल", f"₹{total_adv}")
            c3.metric("बाकी देणे (Net Balance)", f"₹{total_bal}")
        else:
            st.warning("या कामगाराचा कोणताही डेटा उपलब्ध नाही.")
    else:
        st.info("अजून कोणताही डेटा भरलेला नाही.")

# रिपोर्ट डाउनलोड
st.divider()
if os.path.exists(DB_FILE):
    with open(DB_FILE, "rb") as f:
        st.download_button("Full Report (Excel) डाउनलोड करा", data=f, file_name="SK_Group_Report.xlsx")

