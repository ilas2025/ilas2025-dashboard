import streamlit as st

import os
import time
import urllib.request
import pandas as pd
from thefuzz import fuzz

DATAPATH = "data"

st.title("Search in database")

if st.text_input("", type="password") == st.secrets.password:

    if st.button("Get data"): 
        for filename, url in st.secrets.csvs.items():
            urllib.request.urlretrieve(url,
                                       os.path.join(DATAPATH, filename + ".csv"))
    
    for item in os.scandir(DATAPATH):
        if item.name.endswith("csv"):
            st.write(item.name, time.ctime(item.stat().st_mtime))
    
    search_key = st.text_input("Search")
    
    ## Registration data
    st.markdown("## Registration data")
    
    reg = pd.read_csv(os.path.join(DATAPATH, "reg.csv")).set_index("PID").dropna(how="all")
    reg["FULL_NAME"] = (reg.FIRST_NAME + " " + reg.LAST_NAME).str.lower()
    reg = reg.loc[~reg.FULL_NAME.isna()]
    
    mask = reg.FULL_NAME.str.contains(search_key.lower())
    
    main_columns = ["FIRST_NAME", "LAST_NAME", "TOTAL", "藍新實收"]
    
    show_all = st.toggle("Show all")
    if show_all:
        st.dataframe(reg.loc[mask])
    else:
        st.dataframe(reg.loc[mask, main_columns])
    
    ## Talks data
    st.markdown("## Talks data")
    
    talks = pd.read_csv(os.path.join(DATAPATH, "talks.csv")).set_index("TID").dropna(how="all")
    talks["FULL_NAME"] = (talks.FIRST_NAME + " " + talks.LAST_NAME).str.lower()
    talks = talks.loc[~talks.FULL_NAME.isna()]
    
    mask = talks.FULL_NAME.str.contains(search_key.lower())
    main_columns = ["FIRST_NAME", "LAST_NAME", "TYPE", "TITLE"]
    st.dataframe(talks.loc[mask, main_columns])
    
    ## Mini-symposium data
    st.markdown("## Mini-symposium data")
    
    mini_talks = pd.read_csv(os.path.join(DATAPATH, "mini-speakers.csv")).dropna(how="all")
    mini_talks["FULL_NAME"] = mini_talks.NAME.str.lower()
    
    mask = mini_talks.FULL_NAME.str.contains(search_key.lower())
    main_columns = ["NAME", "TYPE", "TITLE"]
    st.dataframe(mini_talks.loc[mask, main_columns])
    
    ## Fuzzy search
    st.markdown("## Fuzzy search")
    ratios = reg.FULL_NAME.apply(lambda x: fuzz.ratio(x, search_key))
    
    st.write(reg.FULL_NAME[ratios > 50])