import locale

def StString(str):
    StStr = str.replace("Nuevo Laredo", "NL")\
        .replace("CITGO", "CGO")\
        .replace("Puebla", "PUE") \
        .replace("Harlingen", "H") \
        .replace("El Paso", "EP") \
        .replace("Veracruz", "VR") \
        .replace("Tizayuca", "TZ") \
        .replace("Burgos Rey", "B-REY") \
        .replace("Burgos Azca", "B-AZC") \
        .replace("GP-Juarez", "T JRZ") \
        .replace("GP-Nogales", "T NOG") \
        .replace("GP-Mexicali", "T MXC") \
        .replace("GP-Chihuahua", "T CHI") \
        .replace("GP-Cadereyta", "T CAD") \
        .replace("GP-NuevoLaredo", "T NVL") \
        .replace("BLK-San Luis Potosi", "TCM-SLP") \
        .replace("BLK-Salinas Victoria", "BLK-SVIC") \
        .replace("MA-Veracruz", "T VER") \
        .replace("MA-Tula", "T TUL") \
        .replace("MA-Puebla", "T PUE")
    return StStr

def fdate(fecha_obj):
    dias_personalizados = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO", "DOMINGO"]
    try:
        locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
    except:
        locale.setlocale(locale.LC_TIME, "Spanish_Spain.1252")
    dia_custom = dias_personalizados[fecha_obj.weekday()]
    resto_fecha = fecha_obj.strftime("%d de %B de %Y").upper()
    return f"{dia_custom}, {resto_fecha}"

def sdate(fecha_obj):
    try:
        locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
    except:
        locale.setlocale(locale.LC_TIME, "Spanish_Spain.1252")
    resto_fecha = fecha_obj.strftime("%d/%B/%Y").upper()
    return f"{resto_fecha}"

def wrap_text(draw, text, font, max_width):
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
