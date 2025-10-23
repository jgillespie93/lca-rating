import mysql.connector
from sshtunnel import SSHTunnelForwarder
import streamlit as st
# server = SSHTunnelForwarder(
#     ('34.132.17.254', 22),
#     ssh_username='m4-app',
#     ssh_pkey='/Users/jamesgillespie/.ssh/streamlit_m4',
#     remote_bind_address=('sql8.freesqldatabase.com', 3306),
#     local_bind_address=('127.0.0.1', 0)
# )
# server.start()
# print(server.local_bind_port) 
pwd = st.secrets.password
usr = st.secrets.user
db = st.secrets.database

try:
    conn = mysql.connector.connect(
        host="sql8.freesqldatabase.com",
        user= usr,
        password= pwd,
        database= db,
        port=3306
    )
    print("✅ Connected successfully!")
except mysql.connector.Error as err:
    print(f"❌ Error: {err}")

#server.stop()

    