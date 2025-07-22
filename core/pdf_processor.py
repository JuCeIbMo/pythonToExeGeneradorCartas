# core/pdf_processor.py
import PyPDF2
from pathlib import Path

def procesar_campos_pdf(campos):
    """Filtra y limpia los campos del PDF"""
    datos_limpios = {}
    for nombre_campo, valor_campo in campos.items():
        if isinstance(nombre_campo, str) and nombre_campo.startswith(('A_','B_','C_', 'D_')):
            if valor_campo is not None and valor_campo != '':
                nombre_limpio = nombre_campo.split('[')[0]
                datos_limpios[nombre_limpio] = str(valor_campo).strip()
    return datos_limpios

def leer_campos_pdf(ruta_pdf):
    """Lee los campos del PDF y devuelve un diccionario"""
    try:
        with open(ruta_pdf, 'rb') as archivo:
            lector_pdf = PyPDF2.PdfReader(archivo)
            if not lector_pdf.get_form_text_fields():
                print(f"No se encontraron campos en '{ruta_pdf}'")
                return None
            return procesar_campos_pdf(lector_pdf.get_form_text_fields())
    except Exception as e:
        print(f"Error al leer PDF: {str(e)}")
        return None
