import streamlit as st

import os
import pandas as pd

st.header("Registration status")

if st.session_state.password == st.secrets.password:
    
    reg = pd.read_csv(os.path.join(st.session_state.DATAPATH, "reg.csv")).set_index("PID").dropna(how="all")
    reg["full_name"] = (reg.FIRST_NAME + " " + reg.LAST_NAME).str.lower()
    reg = reg.loc[~reg.full_name.isna(),["EMAIL","TOTAL","藍新實收"]]
    
    minis = pd.read_csv(os.path.join(st.session_state.DATAPATH, "minis.csv")).set_index("MID")
    
    talks = pd.read_csv(os.path.join(st.session_state.DATAPATH, "talks.csv")).set_index("TID").dropna(how="all")

    posters = pd.read_csv(os.path.join(st.session_state.DATAPATH, "posters.csv"))

    srp = pd.read_csv(os.path.join(st.session_state.DATAPATH, "SRP.csv"))

    DATASOURCE = st.selectbox("Mini-symposium speakers data source", 
                               ["mini-speakers", "SRP-collector", "SRP"],
                               index=1)

    if DATASOURCE == "mini-speakers":
        m_speakers = pd.read_csv(os.path.join(st.session_state.DATAPATH, "mini-speakers.csv"))
    if DATASOURCE == "SRP-collector":
        srp_collector = pd.read_csv(os.path.join(st.session_state.DATAPATH, "SRP-collector.csv"))
        m_speakers = srp_collector.loc[srp_collector.TYPE.str.match("MS[0-9]{1,2}$").fillna(False)].copy()
        m_speakers["NAME"] = m_speakers.FIRST_NAME + " " + m_speakers.LAST_NAME
        m_speakers = m_speakers.loc[:,["TYPE","FIRST_NAME", "LAST_NAME","NAME"]]
        m_speakers = m_speakers.loc[pd.notna(m_speakers.NAME)]
    if DATASOURCE == "SRP":
        st.write("Not yet implemented.  Showing SRP-collector data now.")
        m_speakers = pd.read_csv(os.path.join(st.session_state.DATAPATH, "mini-speakers.csv"))
    
    ms_status = pd.DataFrame({
        "UNMATCH": None,
        "OFF": None,
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
    all_ms_join_list = []
    for ms in minis.index:
        st.subheader(ms + ": " + minis.loc[ms,"TITLE"])
        st.write(minis.loc[ms,"ORGANIZERS"])
        
        if DATASOURCE == "mini-speakers":
            from_m_speakers = m_speakers.loc[m_speakers.TYPE == ms, ["TYPE", "NAME"]].copy()
        else:
            from_m_speakers = m_speakers.loc[m_speakers.TYPE == ms, ["TYPE", "FIRST_NAME", "LAST_NAME", "NAME"]].copy()
            from_m_speakers.rename(columns={"FIRST_NAME": "FIRST_NAME_x", "LAST_NAME": "LAST_NAME_x"}, inplace=True)
        from_m_speakers["full_name"] = from_m_speakers.NAME.str.lower()
        from_talks = talks.loc[talks.TYPE.str.startswith(ms + ":"),["FIRST_NAME","LAST_NAME","EMAIL","TITLE"]]
        from_talks["full_name"] = (from_talks.FIRST_NAME + " " + from_talks.LAST_NAME).str.lower()
        
        ms_join = pd.merge(from_talks, reg, on="EMAIL", how="left")
        ms_join = pd.merge(from_m_speakers, ms_join, on="full_name", how="outer")
        ms_join.drop("full_name", axis=1, inplace=True)
        ms_join["REGISTERED"] = ms_join.藍新實收.apply(lambda x: "Yes" if pd.notna(x) else "No")
        all_ms_join_list.append(ms_join)
        
        ms_status.loc[ms,"UNMATCH"] = pd.isna(ms_join.NAME).sum()
        ms_status.loc[ms,"OFF"] = ms_join.shape[0] - ms_status.loc[ms,"EXPECTED"]
        ms_status.loc[ms,"NO_ABS"] = pd.isna(ms_join.LAST_NAME).sum()
        ms_status.loc[ms,"NOT_REG"] = pd.isna(ms_join.藍新實收).sum()

        st.dataframe(ms_status.loc[[ms]])
        # st.dataframe(from_m_speakers)
        # st.dataframe(from_talks)
        
        if show_all:
            st.dataframe(ms_join.iloc[:,1:])
        else:
            st.dataframe(ms_join.loc[:,["NAME","FIRST_NAME","LAST_NAME","TITLE","REGISTERED"]])
    
    st.subheader("All MS")

    all_ms_join = pd.concat(all_ms_join_list, ignore_index=True)
    if DATASOURCE == "mini-speakers":
        pass
    else:
        st.dataframe(all_ms_join)
        st.dataframe(all_ms_join.TYPE.str[2:])
        all_ms_join["MS_WEIGHT"] = all_ms_join.TYPE.str[2:].astype(int)
        all_ms_join.replace("Šmigoc", "Smigoc", inplace=True) # for Šmigoc sorting
        all_ms_join.sort_values(["MS_WEIGHT","LAST_NAME_x"], inplace=True)
        all_ms_join = all_ms_join.reindex()
        all_ms_join.drop(columns="MS_WEIGHT")

    if show_all:
        st.dataframe(all_ms_join)
    else:
        st.dataframe(all_ms_join.loc[:,["TYPE","NAME","TITLE"]])

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

    # SUMMARY
    st.subheader("Summary")

    st.dataframe(ms_status)