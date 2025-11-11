import streamlit as st
import pandas as pd
import mysql.connector
import os
import time
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

# -------------------------
# Streamlit setup
# -------------------------
st.set_page_config(page_title="LCA Lookup Rating Tool", layout="centered")
dirname = os.path.dirname(__file__)
lookup_path = os.path.join(dirname, "data/fullsentence_results_only.csv")
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
if "pending_ratings" not in st.session_state:
    st.session_state.pending_ratings = [] 

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
                st.session_state.pending_ratings.append(
                    (researcher, lookup_items[i], option_text, source_text)
                )
                if len(st.session_state.pending_ratings) >= 10:
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        insert_query = """
                            INSERT INTO ratings (researcher, item, chosen_match, source)
                            VALUES (%s, %s, %s, %s)
                        """
                        cursor.executemany(insert_query, st.session_state.pending_ratings)
                        conn.commit()
                        st.session_state.pending_ratings.clear()  # reset cache
                        st.toast("Ratings batch saved to database.")
                    except Exception as e:
                        st.error(f"Database error: {e}")
                    finally:
                        cursor.close()
                        conn.close()
                st.toast(f"Item {i+1} rated")
                time.sleep(.5)
                st.session_state.index += 1
                st.rerun()

            # Display source below in blue
            st.markdown(f"<span style='color:blue; font-size:medium;'>{source_text}</span>", unsafe_allow_html=True)

        st.markdown("### 💡 Other (Researcher Suggested Database)")
        custom_term = st.text_input("Enter custom match term:", key=f"term_{i}_{st.session_state.index}")
        custom_source = st.text_input("Enter database/source name:", key=f"source_{i}_{st.session_state.index}")

        if st.button("Submit custom match", key=f"custom_{i}"):
            if custom_term.strip() and custom_source.strip():
                st.session_state.pending_ratings.append(
                    (researcher, lookup_items[i], custom_term.strip(), custom_source.strip())
                )

                # Flush every 10 cached ratings
                if len(st.session_state.pending_ratings) >= 10:
                    conn = None
                    cursor = None
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        insert_query = """
                            INSERT INTO ratings (researcher, item, chosen_match, source)
                            VALUES (%s, %s, %s, %s)
                        """
                        cursor.executemany(insert_query, st.session_state.pending_ratings)
                        conn.commit()
                        st.session_state.pending_ratings.clear()
                        st.toast("💾 Ratings batch saved to database.")
                    except Exception as e:
                        st.error(f"Database error: {e}")
                    finally:
                        if cursor:
                            cursor.close()
                        if conn:
                            conn.close()
                
                    del st.session_state[f"custom_term_{i}"]
                
                    del st.session_state[f"custom_source_{i}"]

                # 👋 Visual feedback before moving on
                st.toast(f"Item {i+1} rated")
                time.sleep(.5)
                st.session_state.index += 1
                st.rerun()
            else:
                st.warning("Please enter both a term and a database name before submitting.")

    else:
        st.success("✅ All items rated!")
           # If user finishes early and there are still pending ratings:
        if len(st.session_state.pending_ratings) >0:
            st.info("Saving remaining ratings to database...")
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                insert_query = """
                    INSERT INTO ratings (researcher, item, chosen_match, source)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.executemany(insert_query, st.session_state.pending_ratings)
                conn.commit()
                st.session_state.pending_ratings.clear()
                st.success("💾 Remaining ratings saved.")
            except Exception as e:
                st.error(f"Database error: {e}")
            finally:
                cursor.close()
                conn.close()
