import gspread
import pandas as pd

# Authenticate with your service account
gc = gspread.service_account(filename='smarttoolmatch-5e859910ddc2.json')

# Open your Google Sheet by name
sh = gc.open('SmartToolMatch_AI_Tools_Master_Sheet') 

# Open your worksheet/tab (usually 'Sheet1')
worksheet = sh.worksheet('Sheet1') 

# Get all records (each row as a dict)
data = worksheet.get_all_records()

# Load into a pandas DataFrame (easy for Streamlit)
df = pd.DataFrame(data)

print(df.head())  # Print first few rows to check everything works
