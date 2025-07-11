import streamlit as st
import google.generativeai as genai

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say hello in three languages.")
    st.write(response.text)
except Exception as e:
    st.error(f"Gemini test failed: {e}")
