from datetime import timedelta
import pandas as pd
import numpy as np
import pyautogui
import datetime
import json
import glob
import math
import time
import os

import GoogleAPI
from ImgGen import GenTable, GenMonkysCustomTable

def clear_png_files(directory="TablasV2"):
    pattern = os.path.join(directory, "*.png")
    for filepath in glob.glob(pattern):
        try:
            os.remove(filepath)
        except OSError as e:
            print(f"No se pudo eliminar {filepath}: {e}")

def save_clientes_data(clientes_data, folder="TablasOld"):
    os.makedirs(folder, exist_ok=True)
    date_str = datetime.datetime.now().strftime("%m-%d-%Y")
    filename = f"{date_str}.json"
    filepath = os.path.join(folder, filename)
    def sanitize(obj):
        if isinstance(obj, dict):
            return {k: sanitize(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [sanitize(v) for v in obj]
        if isinstance(obj, np.ndarray):
            return sanitize(obj.tolist())
        if isinstance(obj, np.generic):
            return sanitize(obj.item())
        if isinstance(obj, float):
            if math.isnan(obj):
                return "N/A"
            return round(obj, 6)
        return obj
    cleaned_data = sanitize(clientes_data)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=4)
    print(f"Datos guardados en: {filepath}")

def leer_excel_dinamico(archivo, hoja):
    df = pd.read_excel(archivo, sheet_name=hoja, engine="openpyxl")
    total_filas = len(df)
    fila_actual = 0
    clientes_data = []
    while fila_actual < total_filas:
        if pd.notna(df.iloc[fila_actual, 0]):
            cliente = df.iloc[fila_actual, 0]
            notas = df.iloc[fila_actual, 17]
            format_val = df.iloc[fila_actual, 19]
            fila_inicio = fila_actual
            fila_actual += 1
            while fila_actual < total_filas:
                fila_vacia = df.iloc[fila_actual].isna().all()
                fila_siguiente_vacia = (df.iloc[fila_actual + 1].isna().all() if fila_actual + 1 < total_filas else False)
                if fila_vacia and fila_siguiente_vacia:
                    break
                fila_actual += 1
            origenes = df.iloc[fila_inicio:fila_actual, 2].tolist()
            destinos = df.iloc[fila_inicio:fila_actual, 5].tolist()
            precios_regular = df.iloc[fila_inicio:fila_actual, 6].tolist()
            precios_premium = df.iloc[fila_inicio:fila_actual, 7].tolist()
            precios_diesel = df.iloc[fila_inicio:fila_actual, 8].tolist()
            data_cf = df.iloc[fila_inicio:fila_actual, 9].tolist()
            typeut_regular = df.iloc[fila_inicio:fila_actual, 10].tolist()
            typeut_premium = df.iloc[fila_inicio:fila_actual, 11].tolist()
            typeut_diesel = df.iloc[fila_inicio:fila_actual, 12].tolist()
            data_iva = df.iloc[fila_inicio:fila_actual, 13].tolist()
            extra_regular = df.iloc[fila_inicio:fila_actual, 14].tolist()
            extra_premium = df.iloc[fila_inicio:fila_actual, 15].tolist()
            extra_diesel = df.iloc[fila_inicio:fila_actual, 16].tolist()
            base_regular = df.iloc[fila_inicio:fila_actual, 21].tolist()
            base_premium = df.iloc[fila_inicio:fila_actual, 22].tolist()
            base_diesel = df.iloc[fila_inicio:fila_actual, 23].tolist()
            data_flete = df.iloc[fila_inicio:fila_actual, 25].tolist()
            ut_regular = df.iloc[fila_inicio:fila_actual, 27].tolist()
            ut_premium = df.iloc[fila_inicio:fila_actual, 28].tolist()
            ut_diesel = df.iloc[fila_inicio:fila_actual, 29].tolist()
            benefs_regular = df.iloc[fila_inicio:fila_actual, 31].tolist()
            benefs_premium = df.iloc[fila_inicio:fila_actual, 32].tolist()
            benefs_diesel = df.iloc[fila_inicio:fila_actual, 32].tolist()

            clientes_data.append({
                "cliente": cliente,
                "origenes": origenes,
                "destinos": destinos,
                "formato": format_val,
                "notas": notas,
                "cf": data_cf,
                "iva": data_iva,
                "flete": data_flete,
                "precios": {
                    "GAS 87": precios_regular,
                    "GAS 91": precios_premium,
                    "DIESEL": precios_diesel
                },
                "typeut": {
                    "GAS 87": typeut_regular,
                    "GAS 91": typeut_premium,
                    "DIESEL": typeut_diesel
                },
                "extra": {
                    "GAS 87": extra_regular,
                    "GAS 91": extra_premium,
                    "DIESEL": extra_diesel
                },
                "base": {
                    "GAS 87": base_regular,
                    "GAS 91": base_premium,
                    "DIESEL": base_diesel
                },
                "ut": {
                    "GAS 87": ut_regular,
                    "GAS 91": ut_premium,
                    "DIESEL": ut_diesel
                },
                "benefs": {
                    "GAS 87": benefs_regular,
                    "GAS 91": benefs_premium,
                    "DIESEL": benefs_diesel
                }
            })
        fila_actual += 2

    df_valores = pd.read_excel(archivo, sheet_name="Valores", engine="openpyxl")
    fecha = df_valores.iloc[101, 2]
    datos_monkys = df_valores.iloc[0:9, 24:27]
    datos_pricing = df_valores.iloc[32, 14]
    datos_historicos_p1 = df_valores.iloc[32, 14]
    datos_historicos_p2 = df_valores.iloc[32, 15]
    datos_historicos_p3 = df_valores.iloc[32, 16]
    valores_gasydi = df_valores.iloc[11, 25]
    valores_madisa = df_valores.iloc[18, 27]
    return clientes_data, fecha, datos_pricing, datos_historicos_p1, datos_historicos_p2, datos_historicos_p3, datos_monkys, valores_gasydi, valores_madisa

def getActiveClients():
    BUSCADOS, actives, alive = ("ACTIVO", "PROSPECTO"), [], set()
    CC_Sheet = GoogleAPI.Conn_Drv('ControlComercial', 'CONTROL CLIENTES')
    C_Status = CC_Sheet.col_values(14)[5:1000]
    C_Table = CC_Sheet.col_values(35)[5:1000]
    C_Combined = [(status, table) for status, table in zip(C_Status, C_Table) if table not in ("", None)]
    for status, tabla in C_Combined:
        if any(palabra in status for palabra in BUSCADOS):
            if tabla not in alive:
                actives.append(tabla)
                alive.add(tabla)
    return actives

def fillBTerms(data):
    BT_Sheet = GoogleAPI.Conn_Drv('BalanceTerminales', 'SDB')
    BT_softlimit = BT_Sheet.cell(3, 1).value.replace(",", "")
    BT_Sheet.update_cell(int(BT_softlimit), 1, data)


def fillHGen(data_p1, data_p2, data_p3):
    HG_Sheet = GoogleAPI.Conn_Drv('GeneradorHistoricos', 'DB')
    HG_softlimit = HG_Sheet.cell(1, 1).value.replace(",", "")
    HG_Sheet.update_cell(int(HG_softlimit), 2, data_p1)
    HG_Sheet.update_cell(int(HG_softlimit), 3, data_p2)
    HG_Sheet.update_cell(int(HG_softlimit), 10, data_p3)

def AttatchTitles():
    files = [f for f in os.listdir("TablasV2") if os.path.isfile(os.path.join("TablasV2", f))]
    for idx, elemento in enumerate(files, start=1):
        ruta_completa = os.path.join("TablasV2", elemento)
        if os.path.isfile(ruta_completa):
            pyautogui.write(elemento.replace(".png", ""))
            time.sleep(0.30)
            pyautogui.hotkey('right')
            time.sleep(0.20)

if __name__ == "__main__":
    clear_png_files()
    archivo_excel = "C:/Users/XMGDL/Dropbox/LOBO/1. Precios/2025/6. jun 2025/PRECIOS 2.9 - 27jun2025.xlsx"
    hoja_excel, IgnoreOrigen = "T_New", []
    clientes_data, fecha, datos_pricing, datos_historicos_p1, datos_historicos_p2, datos_historicos_p3, datos_monkys, valores_gasydi, valores_madisa = leer_excel_dinamico(archivo_excel, hoja_excel)
    save_clientes_data(clientes_data)
    if pd.isna(valores_gasydi):
        IgnoreOrigen.append("BLK-Salinas Victoria")
        IgnoreOrigen.append("BLK-San Luis Potosi")
    # GenMonkysCustomTable(fecha, datos_monkys)
    # activeClients = getActiveClients()
    #fecha = fecha + timedelta(days=2)
    # HideD = ["Burgos Rey", "Burgos Azca", "GP-Reynosa", "GP-Juarez", "GP-Rosarito", "GP-Mexicali", "GP-Nogales", "GP-Chihuahua", "GP-Cadereyta", "GP-Nuevo Laredo", "BLK-Salinas Victoria", "BLK-San Luis Potosi", "RP-MAD", "T-AGS", "T-SLP", "T-QRO", "MA-Veracruz", "MA-Tula", "MA-Puebla"]
    HideD = [""]
    HideP = [""]
    HideR = [""]
    isDetailed = 0
    for cliente in clientes_data:
        GenTable(cliente["cliente"], cliente['origenes'], cliente["destinos"], cliente["precios"], cliente['formato'], fecha, IgnoreOrigen, HideD, HideP, HideR, cliente['cf'], cliente['iva'], cliente['flete'], cliente['typeut'],  cliente['extra'], cliente['base'], cliente['benefs'], cliente['ut'], cliente['notas'], isDetailed)
    input("Await........")
    print("3...")
    time.sleep(3)
    AttatchTitles()
    input("Send to drive?")
    fillBTerms(datos_historicos_p1)
    fillHGen(datos_historicos_p1, datos_historicos_p2, datos_historicos_p3)
