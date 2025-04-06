import streamlit as st

import os
import pandas as pd

st.header("Registration status")

if st.session_state.password == st.secrets.password:
    
    minis = pd.read_csv(os.path.join(st.session_state.DATAPATH, "minis.csv")).set_index("MID")
    
    m_speakers = pd.read_csv(os.path.join(st.session_state.DATAPATH, "mini-speakers.csv"))
    
    talks = pd.read_csv(os.path.join(st.session_state.DATAPATH, "talks.csv")).set_index("TID").dropna(how="all")
    
    st.subheader("Plenary talks")
    
    from_talks = talks.loc[talks.TYPE.str.startswith("Plenary"),["FIRST_NAME","LAST_NAME","EMAIL","TITLE"]]
    st.dataframe(from_talks)
    
    for ms in minis.index:
        st.subheader(ms + ": " + minis.loc[ms,"TITLE"])
        from_m_speakers = m_speakers.loc[m_speakers.TYPE == ms, ["NAME"]].copy()
        from_m_speakers["full_name"] = from_m_speakers.NAME.str.lower()
        from_talks = talks.loc[talks.TYPE.str.startswith(ms + ":"),["FIRST_NAME","LAST_NAME","EMAIL","TITLE"]]
        from_talks["full_name"] = (from_talks.FIRST_NAME + " " + from_talks.LAST_NAME).str.lower()
        ms_join = pd.merge(from_m_speakers, from_talks, on="full_name", how="outer")
        ms_join.drop("full_name", axis=1, inplace=True)
        # st.dataframe(from_m_speakers)
        # st.dataframe(from_talks)
        st.dataframe(ms_join)
        
    st.subheader("Contributed talks")
    
    from_talks = talks.loc[talks.TYPE.str.startswith("Contributed"),["FIRST_NAME","LAST_NAME","EMAIL","TITLE"]]
    st.dataframe(from_talks)


