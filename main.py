import streamlit as st

import os
import time
import urllib.request

st.title("ILAS2025 Dashboard")

st.session_state.DATAPATH = "data"

pages = [
    st.Page("statistics.py", title="Statistics"),
    st.Page("fuzzy-search.py", title="Fuzzy Search"),
    st.Page("registration-status.py", title="Registration Status")
]

st.sidebar.text_input("Password", type="password", key="password")

if st.session_state.password == st.secrets.password:

    if st.sidebar.button("Get data"): 
        for filename, url in st.secrets.csvs.items():
            urllib.request.urlretrieve(url, 
                                       os.path.join(st.session_state.DATAPATH, filename + ".csv"))
    
    for item in os.scandir(st.session_state.DATAPATH):
        if item.name.endswith("csv"):
            st.sidebar.write(item.name, time.ctime(item.stat().st_mtime))

pg = st.navigation(pages)
pg.run()