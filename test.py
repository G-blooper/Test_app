import os
import streamlit as st

st.write("This is test.")

path = os.path.join("logs", "IDlogin.txt")

if st.button("Push"):
    os.makedirs("test")
    if not os.path.exists(path):
        st.write("Path not found")
    else:
        st.write("Path exists")
