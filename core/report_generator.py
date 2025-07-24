# core/report_generator.py
import io
from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import TextStringObject, NameObject, NumberObject
from PyPDF2.generic import DictionaryObject, ArrayObject, FloatObject
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
from reportlab.pdfgen import canvas

def separar_nombre_completo(nombre_completo):
    """Separa nombres y apellidos usando coma como separador"""
    if ',' in nombre_completo:
        # Formato: "Apellidos, Nombres"
        partes = nombre_completo.strip().split(',', 1)
        nombres = partes[0].strip()
        apellidos = partes[1].strip() if len(partes) > 1 else ""
        
        # Dividir apellidos en dos partes si es necesario
        apellidos_partes = apellidos.split()
        if len(apellidos_partes) >= 2:
            apellido1 = apellidos_partes[0]
            apellido2 = " ".join(apellidos_partes[1:])
        else:
            apellido1 = apellidos
            apellido2 = ""
            
        return nombres, apellido1, apellido2
    else:
        # Mantener lógica original si no hay coma
        partes = nombre_completo.strip().split()
        if len(partes) == 0:
            return ("", "", "")
        elif len(partes) == 1:
            return (partes[0], "", "")
        elif len(partes) == 2:
            return (partes[0], partes[1], "")
        else:
            return (" ".join(partes[:-2]), partes[-2], partes[-1])

def crear_campo_editable(page, x, y, width, height, field_name):
    """Crea un campo de texto editable en una posición específica"""
    field = DictionaryObject()
    field.update({
        NameObject("/FT"): NameObject("/Tx"),
        NameObject("/Type"): NameObject("/Annot"),
        NameObject("/Subtype"): NameObject("/Widget"),
        NameObject("/T"): TextStringObject(field_name),
        NameObject("/Rect"): ArrayObject([
            FloatObject(x),
            FloatObject(y),
            FloatObject(x + width),
            FloatObject(y + height)
        ]),
        NameObject("/F"): NumberObject(4),
        NameObject("/Ff"): NumberObject(0),
        NameObject("/Q"): NumberObject(1),
        NameObject("/DA"): TextStringObject("/Helvetica 10 Tf 0 0 0 rg"),
        NameObject("/Border"): ArrayObject([FloatObject(1), FloatObject(1), FloatObject(1)]),
        NameObject("/C"): ArrayObject([FloatObject(0), FloatObject(0), FloatObject(1)]),
    })
    
    if "/Annots" not in page:
        page[NameObject("/Annots")] = ArrayObject()
    page["/Annots"].append(field)
    return field

def generar_pdf_con_campos(datos, output_path):
    """Genera PDF con campos editables usando ReportLab y acroForm (100% compatible)"""
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.lib.units import mm
    from reportlab.lib.colors import black, HexColor

    # Configuración
    margen_izquierdo = 15*mm
    margen_superior = 15*mm
    col_widths = [20*mm, 30*mm, 75*mm, 30*mm, 75*mm]
    columna_licencia = 3
    alto_fila = 8*mm
    encabezados = ["FECHA", "DNI", "APELLIDOS Y NOMBRE", "N° LICENCIA", "INSTRUCTOR"]

    # Preparar datos de tabla
    tabla_datos = [encabezados]
    for estudiante in datos:
        nombre_completo = f"{estudiante['apellido1']} {estudiante['apellido2']} {estudiante['nombre']}".strip()
        tabla_datos.append([
            estudiante['fecha'],
            estudiante['dni'],
            nombre_completo,
            "",  # Campo editable
            estudiante['instructor']
        ])

    num_filas = len(tabla_datos)
    ancho_total = sum(col_widths) + margen_izquierdo*2
    alto_total = margen_superior + alto_fila * num_filas + 15*mm

    c = canvas.Canvas(output_path, pagesize=(ancho_total, alto_total))
    c.setFont("Helvetica", 10)

    # Dibujar tabla
    y = alto_total - margen_superior
    for fila_idx, fila in enumerate(tabla_datos):
        x = margen_izquierdo
        for col_idx, valor in enumerate(fila):
            c.setStrokeColor(black)
            c.setFillColor(HexColor('#92D050') if fila_idx == 0 else "white")
            c.rect(x, y - alto_fila, col_widths[col_idx], alto_fila, fill=1)
            c.setFillColor(black)
            c.drawCentredString(x + col_widths[col_idx]/2, y - alto_fila/2 - 3, str(valor))
            x += col_widths[col_idx]
        y -= alto_fila

    # Añadir campos editables en la columna de licencia (solo filas de datos, omitir encabezado)
    y = alto_total - margen_superior - alto_fila * 2  # Empieza en la segunda fila
    for i in range(2, num_filas+1):  # Incluye la última fila
        x = margen_izquierdo + sum(col_widths[:columna_licencia])
        c.acroForm.textfield(
            name=f"licencia_{i-1}",
            tooltip=f"N° Licencia fila {i-1}",
            x=x+2, y=y+2, width=col_widths[columna_licencia]-4, height=alto_fila-4,
            borderStyle='solid', borderWidth=0.5, forceBorder=True,
            fontName="Helvetica", fontSize=10,
            fillColor=None, textColor=black
        )
        y -= alto_fila

    c.save()

def generar_reporte_estudiantes(datos_pdf, estudiantes_info, output_dir):
    """Genera reporte PDF en lugar de Excel"""
    # Preparar datos para PDF
    reporte_data = []
    
    for dni, nombre_completo in estudiantes_info:
        nombre, apellido1, apellido2 = separar_nombre_completo(nombre_completo)
        
        reporte_data.append({
            'fecha': datos_pdf.get('C_1', ''),
            'dni': dni,
            'nombre': nombre,
            'apellido1': apellido1,
            'apellido2': apellido2,
            'instructor': datos_pdf.get("A_INSTR", "")
        })

    # Generar PDF con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reporte_path = output_dir / f"Reporte_estudiantes_{timestamp}.pdf"
    generar_pdf_con_campos(reporte_data, str(reporte_path))
    
    return str(reporte_path)
