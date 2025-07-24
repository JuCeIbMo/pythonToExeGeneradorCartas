# core/pdf_processor.py
import PyPDF2
import json
from pathlib import Path
from datetime import datetime

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

def procesar_pdf(ruta_original, datos_actualizados, output_dir):
    """Procesa un PDF, actualiza campos relevantes usando los nombres exactos y guarda copia modificada"""
    try:
        # Crear ruta de salida
        nombre_archivo = Path(ruta_original).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_modificado = output_dir / f"{nombre_archivo}_modificado_{timestamp}.pdf"

        # Leer PDF original
        with open(ruta_original, 'rb') as archivo_entrada:
            lector = PyPDF2.PdfReader(archivo_entrada)
            escritor = PyPDF2.PdfWriter()

            # Copiar todas las páginas
            for pagina in lector.pages:
                escritor.add_page(pagina)

            # Copiar el diccionario de formularios (AcroForm) si existe
            if "/AcroForm" in lector.trailer["/Root"]:
                escritor._root_object.update({
                    PyPDF2.generic.NameObject("/AcroForm"): lector.trailer["/Root"]["/AcroForm"]
                })

            # Obtener los nombres exactos de los campos del PDF (con [0])
            campos_pdf = lector.get_form_text_fields()
            cambios = {}

            # Mapear campos relevantes a los nombres exactos del PDF
            mapeo = {
                "A_INSTR": "A_INSTR[0]",
                "A_DNI": "A_DNI[0]",
                "B_NOMEMB": "B_NOMEMB[0]",
                "B_MATRICULA": "B_MATRICULA[0]",
                "B_PANTALAN": "B_PANTALAN[0]",
                "B_AMARRE": "B_AMARRE[0]",
                "B_POTENCIA": "B_POTENCIA[0]",
                "B_ESLORA": "B_ESLORA[0]",
                "B_INSTAL": "B_INSTAL[0]"
            }

            for clave, nombre_pdf in mapeo.items():
                if nombre_pdf in campos_pdf and clave in datos_actualizados:
                    cambios[nombre_pdf] = str(datos_actualizados[clave])

            # Actualizar los campos en el PDF si hay cambios
            if cambios:
                escritor.update_page_form_field_values(
                    escritor.pages[0],
                    cambios
                )

            # Guardar PDF modificado
            with open(ruta_modificado, 'wb') as archivo_salida:
                escritor.write(archivo_salida)

        return str(ruta_modificado)

    except Exception as e:
        print(f"Error al procesar PDF: {str(e)}")
        return None
