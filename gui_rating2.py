import streamlit as st
import pandas as pd
import mysql.connector
import os
# -------------------------
# MySQL connection setup
# -------------------------
pwd = st.secrets.password
usr = st.secrets.user
db = st.secrets.database

def get_db_connection():
    conn = mysql.connector.connect(
        host="sql8.freesqldatabase.com",
        user= usr,
        password= pwd,
        database= db,
        port=3306
    )
    return conn

        # user= st.write("sql8802126",
        # password="jwZrdj3nbP",
        # database="sql8802126",
# -------------------------
# Streamlit setup
# -------------------------
st.set_page_config(page_title="LCA Lookup Rating Tool", layout="centered")
dirname = os.path.dirname(__file__)
lookup_path = os.path.join(dirname, "data/fullsentence_results_both_toy.csv")
lookup_df = pd.read_csv(lookup_path)

lookup_items = lookup_df.iloc[:, 0].astype(str).str.strip()
rating_cols = [5, 8, 11, 14]
lookup_df_ratings = lookup_df.iloc[:, rating_cols].astype(str).fillna("").applymap(str.strip)
source_cols = [6, 9, 12, 15]
lookup_df_sources = lookup_df.iloc[:, source_cols].astype(str).fillna("").applymap(str.strip)

if "researcher" not in st.session_state:
    st.session_state.researcher = None
if "index" not in st.session_state:
    st.session_state.index = 0

# Ask researcher name
if not st.session_state.researcher:
    name = st.text_input("Enter your name to start:", "")
    if st.button("Start") and name.strip():
        st.session_state.researcher = name.strip()
        st.rerun()

else:
    researcher = st.session_state.researcher
    st.title(f"LCA Lookup Rating Tool - {researcher}")

    i = st.session_state.index
    if i < len(lookup_df):
        item = lookup_items[i]
        st.subheader(f"Item: **{item}**")

        options = lookup_df_ratings.iloc[i].tolist()
        sources = lookup_df_sources.iloc[i].tolist()

        for idx, (option_text, source_text) in enumerate(zip(options, sources), start=1):
            if st.button(f"[{idx}] {option_text}", key=f"{i}_{idx}"):

                # Save directly to the database
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()

                    query = """
                        INSERT INTO ratings (researcher, item, chosen_match, source)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(query, (researcher, item, option_text, source_text))
                    conn.commit()

                    cursor.close()
                    conn.close()

                    st.success(f"✅ Saved {item} -> {option_text}")
                except Exception as e:
                    st.error(f"❌ Database error: {e}")

                # Move to next item
                st.session_state.index += 1
                st.rerun()

            st.markdown(f"<span style='color:blue; font-size:medium;'>{source_text}</span>", unsafe_allow_html=True)

    else:
        st.success("✅ All items rated! 🎉")
