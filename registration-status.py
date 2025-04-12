import streamlit as st

import os
import pandas as pd

st.header("Registration status")

if st.session_state.password == st.secrets.password:
    
    reg = pd.read_csv(os.path.join(st.session_state.DATAPATH, "reg.csv")).set_index("PID").dropna(how="all")
    reg["full_name"] = (reg.FIRST_NAME + " " + reg.LAST_NAME).str.lower()
    reg = reg.loc[~reg.full_name.isna(),["EMAIL","TOTAL","藍新實收"]]
    
    minis = pd.read_csv(os.path.join(st.session_state.DATAPATH, "minis.csv")).set_index("MID")
    
    m_speakers = pd.read_csv(os.path.join(st.session_state.DATAPATH, "mini-speakers.csv"))
    
    talks = pd.read_csv(os.path.join(st.session_state.DATAPATH, "talks.csv")).set_index("TID").dropna(how="all")

    posters = pd.read_csv(os.path.join(st.session_state.DATAPATH, "posters.csv"))

    srp = pd.read_csv(os.path.join(st.session_state.DATAPATH, "SRP.csv"))

    ms_status = pd.DataFrame({
        "UNMATCH": None,
        "EXPECTED": m_speakers.groupby("TYPE")["NAME"].count(),
        "NO_ABS": None,
        "NOT_REG": None,
    }, index=minis.index)

    st.write("Registration data is linked through the abstract data, so missing registration can possibly due to missing abstract")

    show_all = st.toggle("Show all")
    
    # PLENARY
    st.subheader("Plenary talks")
    
    from_srp = srp.loc[srp.SESSION.str.match("P[0-9]{1,2}$"),["FIRST_NAME","LAST_NAME"]]
    # from_srp["full_name"] = (srp.FIRST_NAME + " " + srp.LAST_NAME).str.lower()
    from_talks = talks.loc[talks.TYPE.str.startswith("Plenary"),["FIRST_NAME","LAST_NAME","EMAIL","TITLE"]]
    # from_talks["full_name"] = (from_talks.FIRST_NAME + " " + from_talks.LAST_NAME).str.lower()

    p_join = pd.merge(from_talks, reg, on="EMAIL", how="left")
    p_join = pd.merge(from_srp, p_join, on=["FIRST_NAME", "LAST_NAME"], how="outer")
    

    st.dataframe(p_join)

    # MINI
    for ms in minis.index:
        st.subheader(ms + ": " + minis.loc[ms,"TITLE"])
        from_m_speakers = m_speakers.loc[m_speakers.TYPE == ms, ["NAME"]].copy()
        from_m_speakers["full_name"] = from_m_speakers.NAME.str.lower()
        from_talks = talks.loc[talks.TYPE.str.startswith(ms + ":"),["FIRST_NAME","LAST_NAME","EMAIL","TITLE"]]
        from_talks["full_name"] = (from_talks.FIRST_NAME + " " + from_talks.LAST_NAME).str.lower()
        
        ms_join = pd.merge(from_talks, reg, on="EMAIL", how="left")
        ms_join = pd.merge(from_m_speakers, ms_join, on="full_name", how="outer")
        ms_join.drop("full_name", axis=1, inplace=True)
        ms_join["REGISTERED"] = ms_join.藍新實收.apply(lambda x: "Yes" if pd.notna(x) else "No")
        
        ms_status.loc[ms,"UNMATCH"] = pd.isna(ms_join.NAME).sum()
        ms_status.loc[ms,"NO_ABS"] = pd.isna(ms_join.LAST_NAME).sum()
        ms_status.loc[ms,"NOT_REG"] = pd.isna(ms_join.藍新實收).sum()
        
        st.dataframe(ms_status.loc[[ms]])
        # st.dataframe(from_m_speakers)
        # st.dataframe(from_talks)
        

        if show_all:
            st.dataframe(ms_join)
        else:
            st.dataframe(ms_join.loc[:,["NAME","FIRST_NAME","LAST_NAME","TITLE","REGISTERED"]])
        
    # CONTRIBUTED
    st.subheader("Contributed talks")
    
    from_talks = talks.loc[talks.TYPE.str.startswith("Contributed"),["FIRST_NAME","LAST_NAME","EMAIL","TITLE"]]
    ct_join = pd.merge(from_talks, reg, on="EMAIL", how="left")

    ct_status = {
        "EXPECTED": ct_join.shape[0],
        "NOT_REG": pd.isna(ct_join.藍新實收).sum()
    }
    st.write(ct_status)
    st.dataframe(ct_join)

    # POSTER
    st.subheader("Posters")

    ps_join = pd.merge(posters, reg, on="EMAIL", how="left")

    ps_status = {
        "EXPECTED": ps_join.shape[0],
        "NOT_REG": pd.isna(ps_join.藍新實收).sum()
    }
    st.write(ps_status)
    st.dataframe(ps_join)

    st.subheader("Summary")

    st.dataframe(ms_status)