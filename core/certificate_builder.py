# core/certificate_builder.py
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from pathlib import Path

def generar_certificados(datos_pdf, output_dir, logo_path):
    """Genera certificados PDF para todos los estudiantes"""
    # Extraer estudiantes
    estudiantes = []
    i = 1
    while f"D_{i}" in datos_pdf and f"D_{i+1}" in datos_pdf:
        estudiantes.append((datos_pdf[f"D_{i}"], datos_pdf[f"D_{i+1}"]))
        i += 2

    if not estudiantes:
        return []

    # Crear directorio para PDFs
    pdf_dir = output_dir / "PDFs"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    
    # Generar cada certificado
    for dni, nombre in estudiantes:
        output_path = pdf_dir / f"Certificado_{nombre.replace(' ', '_')}_{dni}.pdf"
        generar_certificado_individual({
            'dni': dni,
            'nombre': nombre
        }, datos_pdf, output_path, logo_path)
    
    return list(pdf_dir.glob("*.pdf"))

def generar_certificado_individual(datos_estudiante, datos_generales, output_path, logo_path):
    """Genera un certificado individual"""
    # Configuración básica del documento
    doc = SimpleDocTemplate(
        output_path, 
        pagesize=A4,
        leftMargin=50,
        rightMargin=50,
        topMargin=40,
        bottomMargin=60
    )
    styles = getSampleStyleSheet()
    elements = []
    
    # Estilo para texto normal
    normal_style = styles['BodyText']
    normal_style.fontSize = 12
    
    # Estilo para texto en negrita
    bold_style = styles['BodyText']
    bold_style.fontName = 'Helvetica-Bold'
    
    # Logo (si existe)
    if logo_path.exists():
        logo = Image(str(logo_path), width=120, height=60)
        elements.append(logo)
        elements.append(Spacer(1, 24))
    
    # Título
    title = Paragraph("LICENCIA DE NAVEGACIÓN", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 24))
    
    # Cuerpo del texto
    cuerpo = [
        "D. VICENTE RODRÍGUEZ ALONSO, con DNI: 46866307-N,",
        "en calidad de Director de: <b>ESCUELA NÁUTICA ALIBOAT</b>",
        f"declaro bajo mi responsabilidad que <b>{datos_estudiante['nombre']}</b> con DNI/PASAPORTE: <b>{datos_estudiante['dni']}</b>",
        "ha recibido la formación teórico-práctica exigida por el <b>Real Decreto 875/2014 de 10 de octubre</b>",
        "por el que se regulan las titulaciones para el gobierno de las embarcaciones de recreo.",
        "",
        f"Las prácticas para la obtención de esta licencia se realizaron en la embarcación <b>{datos_generales['B_NOMEMB']}</b>",
        f"con matrícula <b>{datos_generales['B_MATRICULA']}</b>, el <b>{datos_generales['D_DIA']} de {datos_generales['D_MES']} del {datos_generales['D_ANY']}</b>",
        "en el <b>Real Club de Regatas Alicante</b>.",
        "Para que conste y a petición del interesado, expido el presente certificado,",
        "copia fiel de lo que figura en el registro que a tal efecto se dispone.",
        "",
        f"En {datos_generales['D_LLOC']}, a <b>{datos_generales['D_DIA']} de {datos_generales['D_MES']} del {datos_generales['D_ANY']}</b>"
    ]
    
    for linea in cuerpo:
        if '<b>' in linea:
            elements.append(Paragraph(linea, bold_style))
        else:
            elements.append(Paragraph(linea, normal_style))
    
    elements.append(Spacer(1, 48))
    
    # Firmas
    firmas = [
        ("El instructor", datos_generales['A_INSTR'], datos_generales['A_DNI']),
        ("El director", "", ""),
        ("El interesado", datos_estudiante['nombre'], datos_estudiante['dni'])
    ]
    
    for titulo, nombre, dni in firmas:
        elements.append(Paragraph(f"<b>{titulo}</b>", normal_style))
        elements.append(Paragraph(nombre, normal_style))
        elements.append(Paragraph(dni, normal_style))
        elements.append(Spacer(1, 24))
    
    # Generar PDF
    doc.build(elements)
