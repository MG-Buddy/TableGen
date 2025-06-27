from oauth2client.service_account import ServiceAccountCredentials
import gspread

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
credsFile = 'credentials.json'

Drv_ControlComercial = 'https://docs.google.com/spreadsheets/d/13eevoj8np8fTgD0UOIEIHQmsv35CO8h4hol-U9VO3L8'
Drv_BalanceTerminales = 'https://docs.google.com/spreadsheets/d/1_eqSmCG6xVAfhtqbThpSv7J2nCxcoEB2CHANvoelOTc'
Drv_GeneradorHistoricos = 'https://docs.google.com/spreadsheets/d/1fXt3sWOQamJBgrow1o_ljoyT9Ig7li1VzYr13uUs5jE'

def Conn_Drv(Drv, Sht):
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    if Drv == "BalanceTerminales":
        sheet = client.open_by_url(Drv_BalanceTerminales)
        worksheet = sheet.worksheet(Sht)
    elif Drv == "GeneradorHistoricos":
        sheet = client.open_by_url(Drv_GeneradorHistoricos)
        worksheet = sheet.worksheet(Sht)
    elif Drv == "ControlComercial":
        sheet = client.open_by_url(Drv_ControlComercial)
        worksheet = sheet.worksheet(Sht)
    else:
        return 0
    return worksheet

