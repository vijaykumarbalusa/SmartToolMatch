import streamlit as st
import gspread
import json

service_account_info = json.loads(st.secrets["GSPREAD_SERVICE_ACCOUNT"])
gc = gspread.service_account_from_dict(service_account_info)
sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/13KVDHGDG7xITg7gLor1LphhSHJEI-_LGmy3NDUVDNi8/edit?usp=sharing")
worksheet = sh.sheet1
st.write(worksheet.get_all_records())
