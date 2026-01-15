import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

def save_to_google_sheet(data, sheet_name):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json", scope
    )
    client = gspread.authorize(creds)

    sheet = client.open(sheet_name).sheet1
    df = pd.DataFrame([data])
    sheet.append_rows(df.values.tolist())
