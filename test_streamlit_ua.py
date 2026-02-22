import streamlit as st
st.write(st.context.headers.get("User-Agent", "Not found"))
