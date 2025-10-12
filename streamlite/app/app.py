import streamlit as st
from queries import get_top_connected_users

st.title("Professional Network Analytics")

st.header("Top Connected Users")
top_users = get_top_connected_users(limit=10)
st.table(top_users)