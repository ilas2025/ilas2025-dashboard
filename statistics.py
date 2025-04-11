import streamlit as st

import os
import pandas as pd

st.header("Statistics")

if st.session_state.password == st.secrets.password:
    
    reg = pd.read_csv(os.path.join(st.session_state.DATAPATH, "reg.csv")).set_index("PID").dropna(how="all")
    reg["full_name"] = (reg.FIRST_NAME + " " + reg.LAST_NAME).str.lower()
    reg = reg.loc[:,["TOTAL","藍新實收","EXCURSION","BANQUET","VEGGIE"]]
    
    paid_mask = ~pd.isna(reg.藍新實收)
    
    count = pd.DataFrame({
        "STATUS": paid_mask.apply(lambda x: "PAID" if x else "NOT_PAID"),
        "PARTICIPANTS": True,
        "VEGGIE": reg.VEGGIE == "Yes", 
        "EX_KH": reg.EXCURSION == "Kaohsiung harbor - 1,200 NTD", 
        "EX_LT": reg.EXCURSION == "Lotus Pond - 1,000 NTD",
        "BANQUET": reg.BANQUET == "Yes - 1,800 NTD",
    })
    
    count["VEG_BAN"] = count.VEGGIE & count.BANQUET
    
    pivot = count.groupby("STATUS").sum()
    pivot.loc["TOTAL"] = pivot.sum(axis=0)
    
    st.metric("Paid / Filled form", "%d / %d"%(paid_mask.sum(), paid_mask.shape[0]))
    
    st.dataframe(pivot)

