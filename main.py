import os
import json
import requests
import gspread
from google.oauth2.service_account import Credentials

# 1. Google Sheets Authorization
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
service_account_info = json.loads(os.environ["GCP_SERVICE_ACCOUNT"])
creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
client = gspread.authorize(creds)

spreadsheet_id = os.environ["SPREADSHEET_ID"]
spreadsheet = client.open_by_key(spreadsheet_id)
sheet = spreadsheet.worksheet("RawData")

# 2. Fetch Data from NSE
url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br"
}

session = requests.Session()
session.get("https://www.nseindia.com", headers=headers, timeout=10)
response = session.get(url, headers=headers, timeout=10)
data = response.json()

# 3. Extract and Process Option Chain Data
records = data['filtered']['data']
rows = []

for item in records:
    strike = item.get('strikePrice')
    
    # CALLS Data
    ce = item.get('CE', {})
    ce_oi = ce.get('openInterest', 0)
    ce_coi = ce.get('changeinOpenInterest', 0)
    ce_vol = ce.get('totalTradedVolume', 0)
    ce_ltp = ce.get('lastPrice', 0)
    
    # PUTS Data
    pe = item.get('PE', {})
    pe_ltp = pe.get('lastPrice', 0)
    pe_vol = pe.get('totalTradedVolume', 0)
    pe_coi = pe.get('changeinOpenInterest', 0)
    pe_oi = pe.get('openInterest', 0)
    
    rows.append([ce_oi, ce_coi, ce_vol, ce_ltp, strike, pe_ltp, pe_vol, pe_coi, pe_oi])

headers_list = ["CALL OI", "CALL Chg OI", "CALL Volume", "CALL LTP", "STRIKE", "PUT LTP", "PUT Volume", "PUT Chg OI", "PUT OI"]

# 4. Write to Google Sheet (RawData Tab)
sheet.clear()
sheet.append_row(headers_list)
sheet.append_rows(rows)
print("Option Chain Data updated successfully in RawData tab!")
