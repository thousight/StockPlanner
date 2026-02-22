import streamlit as st
import concurrent.futures

try:
    with concurrent.futures.ThreadPoolExecutor() as e:
        res = e.submit(lambda: st.context.headers.get("User-Agent", "Not found")).result()
        print("THREAD RES:", res)
except Exception as e:
    print("THREAD ERR:", e)
