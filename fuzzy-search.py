import streamlit as st

import os
import time
import urllib.request
import pandas as pd
from thefuzz import fuzz

st.header("Search in database")

if st.session_state.password == st.secrets.password:
    
    search_key = st.text_input("Search")

    show_all = st.toggle("Show all")

    ## Registration number
    st.markdown("## Registration number")

    reg_num = pd.read_csv(os.path.join(st.session_state.DATAPATH, "reg-num.csv"), header=1).set_index("REG")
    reg_num["FULL_NAME"] = (reg_num.FIRST_NAME + " " + reg_num.LAST_NAME).str.lower()
    reg_num = reg_num.loc[~reg_num.FULL_NAME.isna()]

    mask = reg_num.FULL_NAME.str.contains(search_key.lower())

    main_columns = ["FIRST_NAME", "LAST_NAME", "BADGE_NAME", "NOTE"]

    if mask.sum() <= 5:
        for ind,row in reg_num.loc[mask].iterrows():
            st.metric(row.FIRST_NAME + " " + row.LAST_NAME, ind)
    
    if show_all:
        st.dataframe(reg_num.loc[mask])
    else:
        st.dataframe(reg_num.loc[mask, main_columns])
    
    ## Registration data
    st.markdown("## Registration data")
    
    reg = pd.read_csv(os.path.join(st.session_state.DATAPATH, "reg.csv")).set_index("PID").dropna(how="all")
    reg["FULL_NAME"] = (reg.FIRST_NAME + " " + reg.LAST_NAME).str.lower()
    reg = reg.loc[~reg.FULL_NAME.isna()]
    
    mask = reg.FULL_NAME.str.contains(search_key.lower())
    
    main_columns = ["FIRST_NAME", "LAST_NAME", "TOTAL", "藍新實收"]
    
    if show_all:
        st.dataframe(reg.loc[mask])
    else:
        st.dataframe(reg.loc[mask, main_columns])
    
    ## Talks data
    st.markdown("## Talks data")
    
    talks = pd.read_csv(os.path.join(st.session_state.DATAPATH, "talks.csv")).set_index("TID").dropna(how="all")
    talks["FULL_NAME"] = (talks.FIRST_NAME + " " + talks.LAST_NAME).str.lower()
    talks = talks.loc[~talks.FULL_NAME.isna()]
    
    mask = talks.FULL_NAME.str.contains(search_key.lower())
    main_columns = ["FIRST_NAME", "LAST_NAME", "TYPE", "TITLE"]
    st.dataframe(talks.loc[mask, main_columns])
    
    ## Mini-symposium data
    st.markdown("## Mini-symposium data")
    
    mini_talks = pd.read_csv(os.path.join(st.session_state.DATAPATH, "mini-speakers.csv")).dropna(how="all")
    mini_talks["FULL_NAME"] = mini_talks.NAME.str.lower()
    
    mask = mini_talks.FULL_NAME.str.contains(search_key.lower())
    main_columns = ["NAME", "TYPE", "TITLE"]
    st.dataframe(mini_talks.loc[mask, main_columns])
    
    ## Fuzzy search
    st.markdown("## Fuzzy search")
    ratios = reg.FULL_NAME.apply(lambda x: fuzz.ratio(x, search_key))
    
    st.write(reg.FULL_NAME[ratios > 50])