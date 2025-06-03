from PIL import Image, ImageDraw, ImageFont
from tkinter import filedialog, messagebox
from pathlib import Path
import tkinter as tk
import pandas as pd
import numpy as np
import subprocess
import traceback
import getpass
import shutil
import locale
import json
import sys
import os

# Base del programa
emisor = getpass.getuser()
global base_folder, output_folder, config_path
base_folder = Path.home() / "Documents" / "MG-TableGen Data"
output_folder = base_folder / "TablasV2"
config_path = base_folder / "config.json"
output_folder.mkdir(parents=True, exist_ok=True)
base_folder.mkdir(parents=True, exist_ok=True)
config = None

# Crear archivo de configuración si no existe
if not os.path.exists(config_path):
    with open(config_path, 'w') as f:
        #json.dump(default_config, f, indent=4)
        print("Archivo de configuración creado con valores por defecto.")

# Cargar configuración
with open(config_path, 'r') as f:
    config = json.load(f)
HideR, HideP, HideD, IgnoreOrigen = [], [], [], []
for key in config["HideR"]:
    if config["HideR"][key]:
        HideR.append(key)
        print(f"HideR added {key}")
for key in config["HideP"]:
    if config["HideP"][key]:
        HideP.append(key)
        print(f"HideP added {key}")
for key in config["HideD"]:
    if config["HideD"][key]:
        HideD.append(key)
        print(f"HideD added {key}")
for key in config["IgnoreOrigen"]:
    if config["IgnoreOrigen"][key]:
        IgnoreOrigen.append(key)
        print(f"IgnoreOrigen added {key}")
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
header_colors = {
        "DESTINO": "#44b599",
        "GAS 87": "#038b36",
        "GAS 91": "#d91614",
        "DIESEL": "#151515",
        "FCA": "#e59645",
        "T": "#487a6c"
    }
text_color_w = "white"
text_color_g = "gray"
text_color_b = "black"
text_color_debug = "#d1d1d1"
border_color = "#cdcfce"
row_colors = ["#f0f1f1", "#cacbcc"]

# Funcion para estandarizar strings de origenes
def StString(str):
    if str in config['origenes']:
        return config['origenes'][str]
    else:
        print(f"{str} not in config file!")
        raise

# Función para crear el string de fecha en base a la celda C127 de la hoja "Valores" para el Excel.
def fdate(fecha_obj):
    try:
        dias_personalizados = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO", "DOMINGO"]
        try:
            locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
        except:
            locale.setlocale(locale.LC_TIME, "Spanish_Spain.1252")
        dia_custom = dias_personalizados[fecha_obj.weekday()]
        resto_fecha = fecha_obj.strftime("%d de %B de %Y").upper()
        return f"{dia_custom}, {resto_fecha}"
    except Exception as e:
        messagebox.showerror("Error", f"Error al obtener la fecha del archivo.\nExcepción: {e}")

# Función para crear el footer con dimensión horizontal dinámica basada en la cantidad de pixeles disponibles.
def wrap_text(draw, text, font, max_width):
    try:
        paragraphs = text.split("\n\n")
        wrapped_lines = []
        for paragraph in paragraphs:
            words = paragraph.split()
            lines = []
            current_line = ""
            for word in words:
                test_line = f"{current_line} {word}".strip()
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] > max_width:
                    lines.append(current_line)
                    current_line = word
                else:
                    current_line = test_line
            lines.append(current_line)
            wrapped_lines.extend(lines)
            wrapped_lines.append("")
        return wrapped_lines[:-1]
    except Exception as e:
        messagebox.showerror("Error",f"Error al generar el Footer de condiciones... Esto no debería suceder nunca pero sucedió y nimodo.\nExcepción: {e}")

# Función para generación de tablas de precios, requiere los datos de cada tabla para su generación.
def GenTable(cliente, origenes, destinos, precios, formato, fecha, IgnoreOrigen, HideR, HideP, HideD, isDetailed, cf=None, iva=None, flete=None, base=None, extra=None, ut=None, benefs=None, typeut=None, notas=None):
    try:
        ### START-Base ###
        print(f"Priting {cliente} in format {formato} - Ignoring {IgnoreOrigen}")
        img_temp = Image.new("RGB", (1, 1))
        draw_temp = ImageDraw.Draw(img_temp)
        productos_validos = {
            key: values
            for key, values in precios.items()
            if any(not (isinstance(v, float) and np.isnan(v)) for v in values)
        }
        if not productos_validos:
            print(f"⚠️ Cliente {cliente} no tiene precios válidos. Tabla no generada.")
            messagebox.showerror("Error", f"El cliente {cliente} no tiene precios válidos. Tabla no Generada")
            return
        date = fdate(fecha)
        padding, header_height, row_height, x_offset = 50, 60, 50, 0
        column_widths = [150] + [150] * len(productos_validos)
        ### END-Base ###
        ### START-Fonts ###
        font_path = resource_path("Fonts/AvenirLTProBlack.otf")
        font_path_2 = resource_path("Fonts/AvenirLTProHeavy.otf")
        fontDebug = ImageFont.truetype(font_path, 10)
        fontUI = ImageFont.truetype(font_path, 18)
        fontHeaders = ImageFont.truetype(font_path, 20)
        fontDate = ImageFont.truetype(font_path_2, 15)
        fontText = ImageFont.truetype(font_path_2, 18)
        fontTextsmall = ImageFont.truetype(font_path_2, 15)
        fontTextsmaller = ImageFont.truetype(font_path_2, 11)
        ExpFooter = 0
        if len(productos_validos) == 3:
            fontFooters = ImageFont.truetype(font_path, 20)
        elif len(productos_validos) == 2:
            fontFooters = ImageFont.truetype(font_path, 17)
        else:
            ExpFooter = 20
            fontFooters = ImageFont.truetype(font_path, 15)
        ### END-Fonts ###
        ### START-CalcCol0 ###
        y_offset = len(destinos) * 52
        headers = ["DESTINO"]
        for i, header in enumerate(headers):
            for row_idx, destino in enumerate(destinos):
                origen_actual = origenes[row_idx]
                if origen_actual in IgnoreOrigen:
                    print(f"⚠️ {cliente} - Saltando destino '{destino}' - origen '{origen_actual}' blacklisted")
                    continue
                if isDetailed == 1:
                    bbox = draw_temp.textbbox((0, 0), f"{destino}  {iva[row_idx]}", font=fontText)
                else:
                    bbox = draw_temp.textbbox((0, 0), destino, font=fontText)
                if x_offset < bbox[2]:
                    x_offset = bbox[2]
            w, h = column_widths[i], header_height
            if x_offset < w:
                x_offset = 150
        bbox = draw_temp.textbbox((0, 0), date, font=fontDate)
        f_offset = bbox[2]
        ### END-CalcCol0 ###
        ### START-Txt ###
        if isDetailed == 1:
            Cond_txt = f'TABLA INFORMATIVA\tNO COMPARTIR.\n\nNotas: {notas}'
            ISO_txt = 'Debug-001-ImgGen.py_v3.7'
        else:
            Cond_txt = '- En caso de que la mercancía requiera reparto en diferentes estaciones, se considerará un cargo adicional.\n\n- Todos los precios están cotizados en modalidad "full" y están sujetos a las condiciones y obligaciones del contrato.'
            ISO_txt = 'FO2-PR-SUM-01'
        ### END-Txt ###
        ### START-Struct ###
        if formato == 1.0:
            t_offset = 0
            width, height = (200 + x_offset + t_offset + (150 * len(productos_validos))), (370 + y_offset + ExpFooter)
        elif formato == 2.0:
            t_offset = + 100
            headers = headers + ["FCA"]
            width, height = (200 + x_offset + t_offset + (150 * len(productos_validos))), (370 + y_offset + ExpFooter)
        elif formato == 3.0:
            t_offset = + 100
            headers = headers + ["T"]
            width, height = (200 + x_offset + t_offset + (150 * len(productos_validos))), (370 + y_offset + ExpFooter)
        elif formato == 4.0 or isDetailed == 1:
            headers = headers + ["FCA"] + ["T"]
            t_offset = + 200
            width, height = (200 + x_offset + t_offset + (150 * len(productos_validos))), (370 + y_offset + ExpFooter)
        else:
            messagebox.showerror("Error", f"El cliente {cliente} no tiene un formato correcto (1-4). Tabla no generada.")
            return
        ### END-Struct ###
        ### START-Row0 ###
        headers = headers + list(productos_validos.keys())
        x_offset -= 50
        img = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(img)
        truck_img = Image.open("LilTruck.png").convert("RGBA")
        draw.rounded_rectangle([width - 380, 15, width + 180 - f_offset, 65], outline=border_color, radius=5)
        x0, y0, x1, y1 = width - 380, 15, width + 180 - f_offset, 65
        rect_width = x1 - x0
        bbox = draw.textbbox((0, 0), date, font=fontDate)
        text_width = bbox[2] - bbox[0]
        center_x = x0 + (rect_width - text_width) // 2
        draw.text((center_x, 33), date, fill=text_color_b, font=fontDate)
        x = padding
        for i, header in enumerate(headers):
            y = padding + 40
            if header == "DESTINO":
                draw.rounded_rectangle([(x + 1), (84), (w + x_offset + 3), (157 + (len(destinos) * 50))], outline=border_color, radius=15)
                draw.rounded_rectangle([(x + 5), y, (x_offset + w), y + h + 20], fill=header_colors.get(header, "#333333"), radius=15)
                draw.text(((x_offset / 2) + x, y + h // 2 - 10), str(header), fill=text_color_w, font=fontHeaders)
                x += w - 7
            elif header == "FCA" or header == "T":
                draw.rounded_rectangle([(x_offset + x - 38), (84), (x + w + x_offset - 75), (157 + (len(destinos) * 50))], outline=border_color, radius=15)
                draw.rounded_rectangle([(x_offset + x - 35), y, (x_offset + x + w - 80), y + h + 20], fill=header_colors.get(header, "#333333"), radius=15)
                if header == "T":
                    draw.text((x_offset + x + 15 - 50, y + h // 2 - 10), "        " + str(header), fill=text_color_w, font=fontHeaders)
                else:
                    truck_img = truck_img.resize((50, 30))
                    img.paste(truck_img, (x + x_offset - 6, y + h // 2 - 15), truck_img)
                x += 115
            else:
                draw.rounded_rectangle([(x_offset + x + 6 - 43), (84), (x + w + x_offset - 48), (157 + (len(destinos) * 50))], outline=border_color, radius=13)
                draw.rounded_rectangle([(x_offset + x + 10 - 43), y, (x_offset + x + w - 52), y + h + 20], fill=header_colors.get(header, "#333333"), radius=15)
                draw.text((x_offset + x + 15 - 50, y + h // 2 - 10), "     " + str(header), fill=text_color_w, font=fontHeaders)
                x += w - 7
        ### END-Row0 ###
        ### START-Row1+ ###
        for row_idx, destino in enumerate(destinos):
            origen_actual = origenes[row_idx]
            if origen_actual in IgnoreOrigen:
                continue
            y = padding + header_height + row_idx * row_height + 40
            row_color = row_colors[row_idx % 2]
            if destino == "Diferencial":
                row_color = "#9c9c9c"
            x = padding
            destinoClean = destino.replace("FCA", "").replace("🚛", "").replace("(", "").replace(")", "").replace("DAP","").replace("*", "").replace("-Spacer-", "")
            if destino != "-Spacer-":
                draw.rounded_rectangle([(x + 5), y, (x_offset + w), y + row_height], fill=row_color, radius=15)
                draw.rounded_rectangle([(x + 5), y, (x_offset + w), y + 15], fill=row_color, radius=0)
                if row_idx + 1 != len(destinos):
                    draw.rounded_rectangle([(x + 5), y + row_height - 11, (x_offset + w), y + row_height], fill=row_color, radius=0)
            else:
                draw.rounded_rectangle([(x + 5), y, (x_offset + w), y + row_height], fill="white", radius=15)
                draw.rounded_rectangle([(x + 5), y, (x_offset + w), y + 15], fill="white", radius=0)
                if row_idx + 1 != len(destinos):
                    draw.rounded_rectangle([(x + 5), y + row_height - 11, (x_offset + w), y + row_height], fill="white", radius=0)
            try:
                if isDetailed == 1:
                    bbox = draw.textbbox((0, 0), f"{destinoClean}  {iva[row_idx]}", font=fontText)
                    text_width = bbox[2] - bbox[0]
                    center_x = x + 50 + (x_offset - text_width) // 2
                    draw.text((center_x, y + row_height // 2 - 10), f"{destinoClean}  {iva[row_idx]}", fill="black", font=fontText)
                else:
                    bbox = draw.textbbox((0, 0), destinoClean, font=fontText)
                    text_width = bbox[2] - bbox[0]
                    center_x = x + 50 + (x_offset - text_width) // 2
                    draw.text((center_x, y + row_height // 2 - 10), destinoClean, fill="black", font=fontText)
            except TypeError:
                messagebox.showwarning("Advertencia", f"Typerror al escribir el destino {row_idx} del cliente {cliente}")
                draw.text((x + 20, y + row_height // 2 - 10), "nulled TE", fill="black", font=fontText)
            if formato == 4.0:
                x += column_widths[0] - 120
            if formato == 2.0 or formato == 3.0:
                x += column_widths[0] + 15
            else:
                x += column_widths[0]
            ### START-Prices ###
            for key in productos_validos:
                origen = origenes[row_idx]
                ### START-NonPrices ###
                if origen == "<TAR COMP>" or origen == "<DIFF>" or origen == "<SPACER>":
                    v_price = f"{productos_validos[key][row_idx]:.2f}" if not np.isnan(productos_validos[key][row_idx]) else "     "
                    if origen == "<DIFF>":
                        if float(v_price) > 0.0:
                            draw.rounded_rectangle([(t_offset + x_offset + x - 41), y, (t_offset + x_offset + x + column_widths[1] - 59), y + row_height], fill="#a3a3a3", radius=15)
                            draw.rounded_rectangle([(t_offset + x_offset + x - 41), y, (t_offset + x_offset + x + column_widths[1] - 59), y + 20], fill="#a3a3a3", radius=0)
                            v_price = f"+{productos_validos[key][row_idx]:.2f}" if not np.isnan(productos_validos[key][row_idx]) else "     "
                            if row_idx + 1 != len(destinos):
                                draw.rounded_rectangle([(t_offset + x_offset + x - 41), y + row_height - 11, (t_offset + x_offset + x + column_widths[1] - 59), y + row_height], fill="#a3a3a3", radius=0)
                            draw.text(((t_offset + x_offset + x - 2), y + row_height // 2 - 10), v_price, fill="#B71C1C", font=fontText)
                        else:
                            draw.rounded_rectangle([(t_offset + x_offset + x - 41), y, (t_offset + x_offset + x + column_widths[1] - 59), y + row_height], fill="#a3a3a3", radius=15)
                            draw.rounded_rectangle([(t_offset + x_offset + x - 41), y, (t_offset + x_offset + x + column_widths[1] - 59), y + 20], fill="#a3a3a3", radius=0)
                            v_price = f"{productos_validos[key][row_idx]:.2f}" if not np.isnan(   productos_validos[key][row_idx]) else "     "
                            if row_idx + 1 != len(destinos):
                                draw.rounded_rectangle([(t_offset + x_offset + x - 41), y + row_height - 11, (t_offset + x_offset + x + column_widths[1] - 59), y + row_height], fill="#a3a3a3", radius=0)
                            draw.text(((t_offset + x_offset + x - 2), y + row_height // 2 - 10), v_price, fill="#1B5E20", font=fontText)
                    elif origen == "<SPACER>":
                        draw.rounded_rectangle([(t_offset + x_offset + x - 41), y, (t_offset + x_offset + x + column_widths[1] - 59), y + row_height], fill="white", radius=15)
                        draw.rounded_rectangle([(t_offset + x_offset + x - 41), y, (t_offset + x_offset + x + column_widths[1] - 59), y + 20], fill="white", radius=0)
                        if row_idx + 1 != len(destinos):
                            draw.rounded_rectangle([(t_offset + x_offset + x - 41), y + row_height - 11, (t_offset + x_offset + x + column_widths[1] - 59), y + row_height], fill="white", radius=0)
                    else:
                        draw.rounded_rectangle([(t_offset + x_offset + x - 41), y, (t_offset + x_offset + x + column_widths[1] - 59), y + row_height], fill=row_color, radius=15)
                        draw.rounded_rectangle([(t_offset + x_offset + x - 41), y, (t_offset + x_offset + x + column_widths[1] - 59), y + 20], fill=row_color, radius=0)
                        if row_idx + 1 != len(destinos):
                            draw.rounded_rectangle([(t_offset + x_offset + x - 41), y + row_height - 11, (t_offset + x_offset + x + column_widths[1] - 59), y + row_height], fill=row_color, radius=0)
                        draw.text(((t_offset + x_offset + x - 2), y + row_height // 2 - 10), f"${v_price}", fill="#292627", font=fontText)
                ### END-NonPrices ###
                ### START-PricesDETAILED ###
                else:
                    if isDetailed == 1:
                        if key == "GAS 87" and origen in HideR:
                            v_price = "     -"
                        if key == "GAS 91" and origen in HideP:
                            v_price = "     -"
                        if key == "DIESEL" and origen in HideD:
                            v_price = "     -"
                        else:
                            v_price = f"${productos_validos[key][row_idx]:.2f}" if not np.isnan(productos_validos[key][row_idx]) else "     -"
                        v_rack = f"{base[key][row_idx]:.2f}" if not np.isnan(base[key][row_idx]) else ""
                        v_benefs = f"{benefs[key][row_idx]:.2f}" if not np.isnan(benefs[key][row_idx]) else ""
                        v_flete = f"{flete[row_idx]:.2f}" if isinstance(flete[row_idx], (int, float, np.floating)) and not np.isnan(flete[row_idx]) else ""
                        v_cf = f"{cf[row_idx]:.2f}" if isinstance(cf[row_idx], (int, float, np.floating)) and not np.isnan(cf[row_idx]) else ""
                        v_ut = f"{ut[key][row_idx]:.2f}" if isinstance(ut[key][row_idx], (int, float, np.floating)) and not np.isnan(ut[key][row_idx]) else ""
                        v_extra = f"{extra[key][row_idx]:.2f}" if isinstance(extra[key][row_idx], (int, float, np.floating)) and not np.isnan(extra[key][row_idx]) else ""
                        draw.rounded_rectangle([(t_offset + x_offset + x - 41), y, (t_offset + x_offset + x + column_widths[1] - 59), y + row_height], fill=row_color, radius=15)
                        draw.rounded_rectangle([(t_offset + x_offset + x - 41), y, (t_offset + x_offset + x + column_widths[1] - 59), y + 20], fill=row_color, radius=0)
                        if row_idx + 1 != len(destinos):
                            draw.rounded_rectangle([(t_offset + x_offset + x - 41), y + row_height - 11, (t_offset + x_offset + x + column_widths[1] - 59), y + row_height], fill=row_color, radius=0)
                        if v_price != "     -":
                            sections = [
                                ([(v_rack, "black", False), (v_benefs, "#5d187d", False), (v_flete, "#18537d", False)],
                                 -20,
                                 [45, 40]),
                                ([(v_cf, "#b56359", False), (v_ut, "#075e32", False), (v_extra, "#ff1c00", True)], -5,
                                 [45, 40])]
                            for vars_list, y_off, spacings in sections:
                                x_det = -35
                                for idx, (val, color, skip_if_zero) in enumerate(vars_list):
                                    if not val or (skip_if_zero and val == "0.00"):
                                        continue
                                    draw.text((t_offset + x_offset + x + x_det, y + row_height // 2 + y_off), val, fill=color, font=fontTextsmaller)
                                    if idx < len(spacings):
                                        x_det += spacings[idx]
                            if typeut[key][row_idx] not in ("Maestra", "Fronteras", "N/A"):
                                typeut[key][row_idx], tipo_color = "Fija", "orange"
                            else:
                                tipo_color = "green"
                            draw.text((t_offset + x_offset + x - 30, y + row_height // 2 + 10), typeut[key][row_idx], fill=tipo_color, font=fontTextsmaller)
                        draw.text((t_offset + x_offset + x + 30, y + row_height // 2 + 10), v_price, fill="black", font=fontTextsmall)
                    ### END-PricesDETAILED ###
                    ### START-PricesNORMAL ###
                    else:
                        if key == "GAS 87" and origen in HideR:
                            v_price = "     -"
                        if key == "GAS 91" and origen in HideP:
                            v_price = "     -"
                        if key == "DIESEL" and origen in HideD:
                            v_price = "     -"
                        else:
                            v_price = f"${productos_validos[key][row_idx]:.2f}" if not np.isnan(productos_validos[key][row_idx]) else "     -"
                        draw.rounded_rectangle([(t_offset + x_offset + x - 41), y, (t_offset + x_offset + x + column_widths[1] - 59), y + row_height], fill=row_color, radius=15)
                        draw.rounded_rectangle([(t_offset + x_offset + x - 41), y, (t_offset + x_offset + x + column_widths[1] - 59), y + 20], fill=row_color, radius=0)
                        if row_idx + 1 != len(destinos):
                            draw.rounded_rectangle([(t_offset + x_offset + x - 41), y + row_height - 11, (t_offset + x_offset + x + column_widths[1] - 59), y + row_height], fill=row_color, radius=0)
                        draw.text(((t_offset + x_offset + x - 2), y + row_height // 2 - 10), v_price, fill="black", font=fontText)
                    ### END-PricesNORMAL ###
                x += w - 7
            x = column_widths[0]
            ### END-Prices ###
            ### START-Formatfull ###
            if formato == 2.0 or formato == 3.0 or formato == 4.0:
                if destino == "-Spacer-":
                    row_color = "white"
                draw.rounded_rectangle([(x_offset + x + 8), y, (x_offset + x + 115), y + row_height], fill=row_color, radius=15)
                draw.rounded_rectangle([(x_offset + x + 8), y, (x_offset + x + 115), y + 15], fill=row_color, radius=0)
                if row_idx + 1 != len(destinos):
                    draw.rounded_rectangle([(x_offset + x + 8), y + row_height - 15, (x_offset + x + 115), y + row_height], fill=row_color, radius=0)
                if "🚛" in destino or "FCA" in destino:
                    draw.text(((x_offset + x + 17), y + row_height // 2 - 10), "       X", fill="black", font=fontUI)
                x += w - 35
                if formato == 4.0:
                    if destino == "-Spacer-":
                        row_color = "white"
                    draw.rounded_rectangle([(x_offset + x + 8), y, (x_offset + x + 115), y + row_height], fill=row_color, radius=15)
                    draw.rounded_rectangle([(x_offset + x + 8), y, (x_offset + x + 115), y + 15], fill=row_color, radius=0)
                    if row_idx + 1 != len(destinos):
                        draw.rounded_rectangle(
                            [(x_offset + x + 8), y + row_height - 15, (x_offset + x + 115), y + row_height], fill=row_color, radius=0)
                    if "DAP" in destino:
                        origen = StString(origenes[row_idx])
                        bbox = draw.textbbox((0, 0), origen, font=fontText)
                        text_width = bbox[2] - bbox[0]
                        center_x = x_offset + x + 17 + (85 - text_width) // 2
                        draw.text((center_x, y + row_height // 2 - 10), origen, fill=text_color_b, font=fontText)
            x = column_widths[0]
            if formato == 3.0:
                draw.rounded_rectangle([(x_offset + x + 8), y, (x_offset + x + 115), y + row_height], fill=row_color, radius=15)
                draw.rounded_rectangle([(x_offset + x + 8), y, (x_offset + x + 115), y + 15], fill=row_color, radius=0)
                if row_idx + 1 != len(destinos):
                    draw.rounded_rectangle([(x_offset + x + 8), y + row_height - 15, (x_offset + x + 115), y + row_height], fill=row_color, radius=0)
                if "DAP" in destino:
                    origen = StString(origenes[row_idx])
                    bbox = draw.textbbox((0, 0), origen, font=fontText)
                    text_width = bbox[2] - bbox[0]
                    center_x = x_offset + x + 17 + (85 - text_width) // 2
                    draw.text((center_x, y + row_height // 2 - 10), origen, fill=text_color_b, font=fontText)
            ### END-Formatfull ###
        ### END-Row1+ ###
        ### START-Footer ###
        max_footer_width = width - 100
        footer_lines = wrap_text(draw, Cond_txt, fontFooters, max_footer_width)
        y_footer = y_offset + 120 + 70
        for line in footer_lines:
            draw.text((50, y_footer), line, fill=text_color_g, font=fontFooters)
            y_footer += 25
        bbox = draw.textbbox((0, 0), ISO_txt, font=fontFooters)
        draw.text((width - bbox[2] - 100, height - 30), ISO_txt, fill=text_color_g, font=fontFooters)
        ### END-Footer ###
        ### START-Debug ###
        if isDetailed == 1:
            draw.text((width - bbox[2] - 100, height - 30), ISO_txt, fill=text_color_g, font=fontFooters)
            draw.text((30, 10), cliente, fill=text_color_debug, font=fontDebug)
            draw.text((120, 10), str(width) + "x" + str(height), fill=text_color_debug, font=fontDebug)
            draw.text((220, 10), "FType = " + str(formato), fill=text_color_debug, font=fontDebug)
            draw.text((10, 25), "X_Offset = " + str(x_offset), fill=text_color_debug, font=fontDebug)
            draw.text((100, 25), "Y_Offset = " + str(y_offset), fill=text_color_debug, font=fontDebug)
            draw.text((200, 25), "F_Offset = " + str(f_offset), fill=text_color_debug, font=fontDebug)
            draw.text((300, 25), "T_Offset = " + str(t_offset), fill=text_color_debug, font=fontDebug)
            ### END-Debug ###
        img.save(output_folder / f"{cliente}.png")
    except Exception as e:
        messagebox.showerror("Error", f"Error al generar la tabla: {cliente}.\nExcepción {e}")

# Elimina todos los archivos .png de la carpeta "TablasV2" donde se guardan las tablas de precios cada vez que se ejecuta el programa para evitar duplicados.
def limpiar_carpeta_tablas():
    folder = output_folder
    if folder.exists():
        for file_path in folder.iterdir():
            try:
                if file_path.is_file() or file_path.is_symlink():
                    file_path.unlink()
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
            except Exception as e:
                messagebox.showwarning("Aviso", f"Error al eliminar el archivo {file_path}: {e}")


# Accede a la hoja "T_New" del archivo para obtener las tablas de precios.
def leer_excel_dinamico(archivo, hoja, isDetailed):
    print(f"Read dyn file {archivo}/{hoja} - ReadType {isDetailed}")
    try:
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
                if isDetailed:
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
                else:
                    origenes = df.iloc[fila_inicio:fila_actual, 2].tolist()
                    destinos = df.iloc[fila_inicio:fila_actual, 5].tolist()
                    precios_regular = df.iloc[fila_inicio:fila_actual, 6].tolist()
                    precios_premium = df.iloc[fila_inicio:fila_actual, 7].tolist()
                    precios_diesel = df.iloc[fila_inicio:fila_actual, 8].tolist()
                    clientes_data.append({
                        "cliente": cliente,
                        "origenes": origenes,
                        "destinos": destinos,
                        "formato": format_val,
                        "precios": {
                            "GAS 87": precios_regular,
                            "GAS 91": precios_premium,
                            "DIESEL": precios_diesel
                        }
                    })
            fila_actual += 2
        df_valores = pd.read_excel(archivo, sheet_name="Valores", engine="openpyxl")
        fecha = df_valores.iloc[101, 2]
        valores_gasydi = df_valores.iloc[11, 25]
        return clientes_data, fecha, valores_gasydi
    except Exception as e:
        messagebox.showerror("Error", f"Error al leer el archivo {archivo}.\nExcepción {e}")

# Addon para ventana desplegable que permita la seleccion de un archivo .xlsx
def select_file():
    filepath = filedialog.askopenfilename(
        title="Selecciona un archivo Excel",
        filetypes=[("Excel files", "*.xlsx")]
    )
    if filepath:
        file_path_var.set(filepath)
        ruta_relativa = "~" + filepath.replace(str(Path.home()), "")
        select_button.config(text=ruta_relativa)
        try:
            global clientes_data, fecha, IgnoreOrigen
            clientes_data, fecha, gasydi = leer_excel_dinamico(filepath, "T_New", precios_desglosados_var.get())
            if pd.isna(gasydi):
                print(f"Gasydi not ready (returned {gasydi})")
                IgnoreOrigen.append("BLK-Salinas Victoria")
                IgnoreOrigen.append("BLK-San Luis Potosi")
            fecha_label.config(text=f"Fecha Tablas: {fdate(fecha)}")
            print(clientes_data)
            opciones = ["**TODOS**"] + [c["cliente"] for c in clientes_data]
            cliente_selector.set("**TODOS**")
            menu = cliente_dropdown["menu"]
            menu.delete(0, "end")
            for opcion in opciones:
                menu.add_command(label=opcion, command=lambda value=opcion: cliente_selector.set(value))
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {e}")
        finally:
            cliente_dropdown.config(state="normal")
            generate_button.config(state="normal")
            precios_check.config(state="disabled")

# Función principal encargada de la ejecución, desencadenada por el boton de la interfaz.
def generar_tablas():
    global IgnoreOrigen, HideR, HideP, HideD
    print(f"Debug___: {IgnoreOrigen}")
    limpiar_carpeta_tablas()
    archivo_excel = file_path_var.get()
    if not archivo_excel:
        return
    try:
        seleccionado = cliente_selector.get()
        detailed = precios_desglosados_var.get()
        isDetailed = 1 if detailed else 0
        def ejecutar_generacion(cliente):
            common_args = {
                "cliente": cliente["cliente"],
                "origenes": cliente['origenes'],
                "destinos": cliente["destinos"],
                "precios": cliente["precios"],
                "formato": cliente["formato"],
                "fecha": fecha,
                "IgnoreOrigen": IgnoreOrigen,
                "HideR": HideR,
                "HideP": HideP,
                "HideD": HideD,
                "isDetailed": isDetailed
            }
            if detailed:
                GenTable(
                    **common_args,
                    cf=cliente["cf"],
                    iva=cliente["iva"],
                    flete=cliente["flete"],
                    base=cliente["base"],
                    extra=cliente["extra"],
                    ut=cliente["ut"],
                    benefs=cliente["benefs"],
                    typeut=cliente["typeut"],
                    notas=cliente["notas"]
                )
            else:
                GenTable(**common_args)
        if seleccionado == "**TODOS**":
            for cliente in clientes_data:
                ejecutar_generacion(cliente)
        else:
            cliente = next(c for c in clientes_data if c["cliente"] == seleccionado)
            ejecutar_generacion(cliente)
        abrir_carpeta_imagenes()
    except Exception as e:
        det = str(traceback.print_exc())
        messagebox.showerror("Errror", f"Error al generar tablas: {e}\n{det}")

# Vuelve a llenar los datos del varfig para poder asegurar prints con requisitos actualizados
def recargar_config():
    global config, IgnoreOrigen, HideR, HideP, HideD
    with open(config_path, "r") as f:
        config = json.load(f)
    IgnoreOrigen = [k for k, v in config["IgnoreOrigen"].items() if v]
    HideR = [k for k, v in config["HideR"].items() if v]
    HideP = [k for k, v in config["HideP"].items() if v]
    HideD = [k for k, v in config["HideD"].items() if v]

# Funcion secundaria, se ejecuta automáticamente al finalizar la generación de tablas y muestra las imagenes generadas.
def abrir_carpeta_imagenes():
    folder = output_folder
    if sys.platform.startswith('win'):
        os.startfile(str(folder))
    elif sys.platform.startswith('darwin'):
        subprocess.call(["open", str(folder)])
    else:
        subprocess.call(["xdg-open", str(folder)])

def abrir_config():
    ventana_config = tk.Toplevel()
    ventana_config.title("Configuración Avanzada")
    ventana_config.geometry("600x775")
    ventana_config.resizable(True, True)
    encabezados = ["Origen", "Alias", "Hide-Origen", "Hide-Reg", "Hide-Prem", "Hide-Die"]
    for col, texto in enumerate(encabezados):
        tk.Label(ventana_config, text=texto, font=('Arial', 10, 'bold')).grid(row=0, column=col, padx=10, pady=5)
    check_vars = {}
    alias_vars = {}
    origenes = list(config["origenes"].keys())
    for i, origen in enumerate(origenes):
        tk.Label(ventana_config, text=origen).grid(row=i+1, column=0, sticky="w", padx=10)
        alias = config["origenes"].get(origen, "")
        alias_var = tk.StringVar(value=alias)
        entry = tk.Entry(ventana_config, textvariable=alias_var, width=12)
        entry.grid(row=i + 1, column=1, padx=5)
        alias_vars[origen] = alias_var
        for j, key in enumerate(["IgnoreOrigen", "HideR", "HideP", "HideD"], start=1):
            var = tk.BooleanVar(value=config[key].get(origen, False))
            cb = tk.Checkbutton(ventana_config, variable=var)
            cb.grid(row=i+1, column=j+1, padx=5)
            check_vars.setdefault(origen, {})[key] = var
    def guardar_config():
        global IgnoreOrigen, HideR, HideP, HideD
        for origen in origenes:
            for key in ["IgnoreOrigen", "HideR", "HideP", "HideD"]:
                config[key][origen] = check_vars[origen][key].get()
            nuevo_alias = alias_vars[origen].get().strip()
            config["origenes"][origen] = nuevo_alias
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        IgnoreOrigen = [k for k, v in config["IgnoreOrigen"].items() if v]
        HideR = [k for k, v in config["HideR"].items() if v]
        HideP = [k for k, v in config["HideP"].items() if v]
        HideD = [k for k, v in config["HideD"].items() if v]
        ventana_config.destroy()
    btn_guardar = tk.Button(ventana_config, text="Guardar", command=guardar_config, width=20)
    btn_guardar.grid(row=len(origenes)+2, column=0, columnspan=6, pady=20)

# Interfaz main
root = tk.Tk()
root.title("Generador de Tablas v1.7")
root.geometry("500x250")
root.resizable(False, False)
if sys.platform == "darwin":
    root.tk.call("set", "::tk::mac::useSystemMenuBar", "0")
file_path_var = tk.StringVar()
precios_desglosados_var = tk.BooleanVar(value=False)
precios_check = tk.Checkbutton(
    root,
    text="Precios Desglosados",
    variable=precios_desglosados_var,
    onvalue=True,
    offvalue=False
)
precios_check.pack()
select_button = tk.Button(root, text="Seleccionar Archivo Excel", command=select_file, width=30, height=2)
select_button.pack(pady=10)
dropdown_frame = tk.Frame(root)
dropdown_frame.pack(pady=5)
tk.Label(dropdown_frame, text="Generar tabla de:").pack(side="left", padx=(0, 10))
cliente_selector = tk.StringVar(value="**TODOS**")
cliente_dropdown = tk.OptionMenu(dropdown_frame, cliente_selector, "**TODOS**")
cliente_dropdown.config(width=25, state="disabled")
cliente_dropdown.pack(side="left")
fecha_label = tk.Label(root, text="Fecha Tablas: -")
fecha_label.pack(pady=2)
generate_button = tk.Button(root, text="Generar Tablas", command=generar_tablas, width=30, height=2)
generate_button.config(state="disabled")
generate_button.pack(pady=10)
config_button = tk.Button(root, text="Avanzado", command=abrir_config, width=30)
config_button.pack(pady=5)
root.mainloop()