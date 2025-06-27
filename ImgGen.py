from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

from Util import StString, fdate, sdate, wrap_text

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

def GenTable(cliente, origenes, destinos, precios, formato, fecha, IgnoreOrigen, HideD, HideP, HideR, cf, iva, flete, typeut, extra, base, benefs, ut, notas, isDetailed):
    ### START-Base ###
    print(f"Priting {cliente} in format {formato}")
    img_temp = Image.new("RGB", (1, 1))
    draw_temp = ImageDraw.Draw(img_temp)
    productos_validos = {
        key: values
        for key, values in precios.items()
        if any(not (isinstance(v, float) and np.isnan(v)) for v in values)
    }
    if not productos_validos:
        print(f"⚠️ Cliente {cliente} no tiene precios válidos. Tabla no generada.")
        return
    date = fdate(fecha)
    padding, header_height, row_height, x_offset = 50, 60, 50, 0
    column_widths = [150] + [150] * len(productos_validos)
    ### END-Base ###
    ### START-Fonts ###
    fontDebug = ImageFont.truetype("Fonts/AvenirLTProBlack.otf", 10)
    fontUI = ImageFont.truetype("C:/Windows/Fonts/seguiemj.ttf", 18)
    fontHeaders = ImageFont.truetype("Fonts/AvenirLTProBlack.otf", 20)
    fontDate = ImageFont.truetype("Fonts/AvenirLTProHeavy.otf", 15)
    fontText = ImageFont.truetype("Fonts/AvenirLTProHeavy.otf", 18)
    fontTextsmall = ImageFont.truetype("Fonts/AvenirLTProHeavy.otf", 15)
    fontTextsmaller = ImageFont.truetype("Fonts/AvenirLTProHeavy.otf", 11)
    ExpFooter = 0
    if len(productos_validos) == 3:
        fontFooters = ImageFont.truetype("Fonts/AvenirLTProBlack.otf", 20)
    elif len(productos_validos) == 2:
        fontFooters = ImageFont.truetype("Fonts/AvenirLTProBlack.otf", 17)
    else:
        ExpFooter = 20
        fontFooters = ImageFont.truetype("Fonts/AvenirLTProBlack.otf", 15)
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
        t_offset =+ 100
        headers = headers + ["FCA"]
        width, height = (200 + x_offset + t_offset + (150 * len(productos_validos))), (370 + y_offset + ExpFooter)
    elif formato == 3.0:
        t_offset =+ 100
        headers = headers + ["T"]
        width, height = (200 + x_offset + t_offset + (150 * len(productos_validos))), (370 + y_offset + ExpFooter)
    elif formato == 4.0 or isDetailed == 1:
        headers = headers + ["FCA"] + ["T"]
        t_offset =+ 200
        width, height = (200 + x_offset + t_offset + (150 * len(productos_validos))), (370 + y_offset + ExpFooter)
    else:
        print(f"⚠️ Cliente {cliente} no tiene un formato especificado. Tabla no generada.")
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
            draw.rounded_rectangle([(x + 5), y, (x_offset + w), y + h +20], fill=header_colors.get(header, "#333333"), radius=15)
            draw.text(((x_offset / 2) + x, y + h // 2 - 10), str(header), fill=text_color_w, font=fontHeaders)
            x += w - 7
        elif header == "FCA" or header == "T":
            draw.rounded_rectangle([(x_offset + x - 38), (84), (x + w + x_offset - 75), (157 + (len(destinos) * 50))], outline=border_color, radius=15)
            draw.rounded_rectangle([(x_offset + x - 35), y, (x_offset + x + w - 80), y + h +20], fill=header_colors.get(header, "#333333"), radius=15)
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
        destinoClean = destino.replace("FCA", "").replace("🚛", "").replace("(", "").replace(")", "").replace("DAP", "").replace("*", "").replace("-Spacer-", "")
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
                v_price = f"{productos_validos[key][row_idx]:.2f}" if not np.isnan(
                    productos_validos[key][row_idx]) else "     "
                if origen == "<DIFF>":
                    if float(v_price) > 0.0:
                        draw.rounded_rectangle([(t_offset + x_offset + x - 41), y, (t_offset + x_offset + x + column_widths[1] - 59), y + row_height], fill="#a3a3a3", radius=15)
                        draw.rounded_rectangle([(t_offset + x_offset + x - 41), y, (t_offset + x_offset + x + column_widths[1] - 59), y + 20], fill="#a3a3a3", radius=0)
                        v_price = f"+{productos_validos[key][row_idx]:.2f}" if not np.isnan(
                            productos_validos[key][row_idx]) else "     "
                        if row_idx + 1 != len(destinos):
                            draw.rounded_rectangle([(t_offset + x_offset + x - 41), y + row_height - 11, (t_offset + x_offset + x + column_widths[1] - 59), y + row_height], fill="#a3a3a3", radius=0)
                        draw.text(((t_offset + x_offset + x - 2), y + row_height // 2 - 10), v_price, fill="#B71C1C", font=fontText)
                    else:
                        draw.rounded_rectangle([(t_offset + x_offset + x - 41), y, (t_offset + x_offset + x + column_widths[1] - 59), y + row_height], fill="#a3a3a3", radius=15)
                        draw.rounded_rectangle([(t_offset + x_offset + x - 41), y, (t_offset + x_offset + x + column_widths[1] - 59), y + 20], fill="#a3a3a3", radius=0)
                        v_price = f"{productos_validos[key][row_idx]:.2f}" if not np.isnan(
                            productos_validos[key][row_idx]) else "     "
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
                    draw.rounded_rectangle([(t_offset + x_offset + x - 41), y, (t_offset + x_offset + x + column_widths[1] - 59), y + 20],
                        fill=row_color, radius=0)
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
                            ([(v_rack, "black", False), (v_benefs, "#5d187d", False), (v_flete, "#18537d", False)], -20, [45, 40]),
                            ([(v_cf, "#b56359", False), (v_ut, "#075e32", False), (v_extra, "#ff1c00", True)], -5, [45, 40])
                        ]
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
                    draw.rounded_rectangle([(x_offset + x + 8), y + row_height - 15, (x_offset + x + 115), y + row_height], fill=row_color, radius=0)
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
    if  isDetailed == 1:
        draw.text((width - bbox[2] - 100, height - 30), ISO_txt, fill=text_color_g, font=fontFooters)
        draw.text((30, 10), cliente, fill=text_color_debug, font=fontDebug)
        draw.text((120, 10), str(width) + "x" + str(height), fill=text_color_debug, font=fontDebug)
        draw.text((220, 10), "FType = " + str(formato), fill=text_color_debug, font=fontDebug)
        draw.text((10, 25), "X_Offset = " + str(x_offset), fill=text_color_debug, font=fontDebug)
        draw.text((100, 25), "Y_Offset = " + str(y_offset), fill=text_color_debug, font=fontDebug)
        draw.text((200, 25), "F_Offset = " + str(f_offset), fill=text_color_debug, font=fontDebug)
        draw.text((300, 25), "T_Offset = " + str(t_offset), fill=text_color_debug, font=fontDebug)
    ### END-Debug ###
    os.makedirs("TablasV2", exist_ok=True)
    img.save(f"TablasV2/{cliente}.png")

def GenMonkysCustomTable(fecha, datos_monkys):
    etiquetas = [
        "Precio Correo al 8%", "Precio Correo al 16%", "Descuento",
        "Seguro", "Flete", "Adder", "Precio Branded Formula 16%",
        "Referencia Nacional N9 100% al 16%", "Diferencial"
    ]
    anchura, altura = 1000, 600
    col_ancho, fila_alto = 180, 35
    margen, offset_col = 20, 150
    img = Image.new("RGB", (anchura, altura), "white")
    draw = ImageDraw.Draw(img)
    try:
        fuente = ImageFont.truetype("arial.ttf", 20)
    except:
        fuente = ImageFont.load_default(size=20)
    def texto_centrado(draw, texto, x, y, ancho, alto, fuente, fill="black"):
        bbox = draw.textbbox((0, 0), texto, font=fuente)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x_c = x + (ancho - w) / 2
        y_c = y + (alto - h) / 2
        draw.text((x_c, y_c), texto, fill=fill, font=fuente)
    texto_centrado(draw, "Analisis de Precios Diario", margen, margen, anchura - 2 * margen, 40, fuente)
    cols = ["Regular", "Premium", "Diesel"]
    colores = ["#32CD32", "#FF0000", "#000000"]
    y_inicio = margen + 50
    draw.rectangle([20, y_inicio, 170 + col_ancho, 560], fill="gray")
    texto_centrado(draw, sdate(fecha), 10, y_inicio, col_ancho + 170, 30, fuente)
    for i, col in enumerate(cols):
        x = margen + col_ancho * (i + 1) + offset_col
        draw.rectangle([x, y_inicio, x + col_ancho, y_inicio + fila_alto], fill=colores[i], outline="black", width=1)
        texto_centrado(draw, col, x, y_inicio, col_ancho, fila_alto, fuente, fill="white")
    gap = fila_alto
    for j, etiqueta in enumerate(etiquetas):
        extra_gap = 0
        if j >= 2:
            extra_gap += gap
        if j >= 6:
            extra_gap += gap
        if j >= 7:
            extra_gap += gap
        if j >= 8:
            extra_gap += gap
        y = y_inicio + (j + 1) * fila_alto + extra_gap
        texto_centrado(draw, etiqueta, margen + 10, y, col_ancho + offset_col - margen, fila_alto, fuente)
        for i in range(3):
            valor = datos_monkys.iloc[j, i]
            texto = f"{valor:.6f}" if isinstance(valor, float) else str(valor)
            x = margen + col_ancho * (i + 1) + offset_col
            draw.rectangle([x, y, x + col_ancho, y + fila_alto], outline="black", width=1)
            texto_centrado(draw, texto, x, y, col_ancho, fila_alto, fuente)
    img.save("NoTablasV2/Monkys.png")
    img.show()

