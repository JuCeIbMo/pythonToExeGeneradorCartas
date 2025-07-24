# core/certificate_builder.py
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import black
from pathlib import Path
from reportlab.platypus.flowables import Flowable

class HorizontalLine(Flowable):
    """Flowable que dibuja una línea horizontal perfectamente alineada"""
    def __init__(self, width, thickness=1):
        Flowable.__init__(self)
        self.width = width
        self.thickness = thickness
        self.height = thickness

    def draw(self):
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 0, self.width, 0)

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
    
    # Generar cada certificado (convertir rutas a strings)
    for dni, nombre in estudiantes:
        output_path = pdf_dir / f"Certificado_{nombre.replace(' ', '_')}_{dni}.pdf"
        generar_certificado_individual({
            'dni': dni,
            'nombre': nombre
        }, datos_pdf, str(output_path), str(logo_path))
    
    return list(pdf_dir.glob("*.pdf"))

def formatear_fecha(fecha_str):
    """Formatea fecha de dd/mm/yyyy a 'd de mes de yyyy'"""
    dia, mes, anio = fecha_str.split('/')
    meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
             'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    return f"{int(dia)} de {meses[int(mes)-1]} de {anio}"

def generar_certificado_individual(datos_estudiante, datos_generales, output_path, logo_path):
    """Genera un certificado individual con diseño profesional"""
    # Configuración exacta para 14 cm de contenido
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=1*cm,
        bottomMargin=(29.7*cm - 2*cm - 14*cm)  # 14cm de contenido
    )
    
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    cuerpo_style = ParagraphStyle(
        'Cuerpo',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=14,
        spaceBefore=0,
        spaceAfter=0,
        alignment=TA_JUSTIFY,
        firstLineIndent=24,
    )
    
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontName='Times-Bold',
        fontSize=14,
        alignment=1,
        spaceBefore=0,
        spaceAfter=0.2*cm
    )

    # Elementos del documento
    elements = []
    
    # Logo en esquina superior izquierda (FIXED)
    if logo_path and Path(logo_path).exists():
        logo = Image(str(logo_path), width=4*cm, height=2*cm)
        logo.hAlign = 'LEFT'
        elements.append(logo)
        elements.append(Spacer(1, -0.5*cm))  # Espacio después del logo
    
    # Título centrado
    elements.append(Paragraph("LICENCIA DE NAVEGACIÓN", title_style))
    
    # Cuerpo del texto
    texto = (
        f"D. <b>VICENTE RODRÍGUEZ ALONSO</b>, con DNI: <b>46866307-N</b>, "
        f"en calidad de Director de: <b>ESCUELA NÁUTICA ALIBOAT</b> declaro bajo mi responsabilidad que "
        f"<b>{datos_estudiante['nombre']}</b> con DNI/PASAPORTE: <b>{datos_estudiante['dni']}</b> ha recibido la formación teórico-práctica exigida por el "
        "<b>Real Decreto 875/2014 de 10 de octubre</b> por el que se regulan las titulaciones para el gobierno de las embarcaciones de recreo."
        "<br/><br/>"
        
        f"Las prácticas para la obtención de esta licencia se realizaron en la embarcación <b>{datos_generales['B_NOMEMB']}</b> "
        f"con matrícula <b>{datos_generales['B_MATRICULA']}</b>, el <b>{formatear_fecha(datos_generales['C_1'])}</b> "
        "en el <b>Real Club de Regatas Alicante</b>. Para que conste y a petición del interesado, expido el presente certificado, "
        "copia fiel de lo que figura en el registro que a tal efecto se dispone."
        "<br/><br/>"
        
        f"En {datos_generales['D_LLOC']}, a <b>{formatear_fecha(datos_generales['C_1'])}</b>"
    )
    
    elements.append(Paragraph(texto, cuerpo_style))
    elements.append(Spacer(1, 2.5*cm))
    
    # Firmas PERFECTAMENTE alineadas
    line_width = 4*cm  # Ancho de las líneas
    
    firmas_data = [
        # Líneas (perfectamente alineadas)
        [
            HorizontalLine(line_width),
            HorizontalLine(line_width),
            HorizontalLine(line_width)
        ],
        # Texto firmas
        [
            Paragraph("<b>El instructor</b>", ParagraphStyle('Firma', fontName='Times-Roman', fontSize=12, alignment=1, spaceBefore=0.3*cm, spaceAfter=0)),
            Paragraph("<b>El director</b>", ParagraphStyle('Firma', fontName='Times-Roman', fontSize=12, alignment=1, spaceBefore=0.3*cm, spaceAfter=0)),
            Paragraph("<b>El interesado</b>", ParagraphStyle('Firma', fontName='Times-Roman', fontSize=12, alignment=1, spaceBefore=0.3*cm, spaceAfter=0))
        ],
        # Nombres
        [
            Paragraph(datos_generales['A_INSTR'], ParagraphStyle('Firma', fontName='Times-Roman', fontSize=12, alignment=1, spaceBefore=0.2*cm)),
            Paragraph("", ParagraphStyle('Firma', fontName='Times-Roman', fontSize=12, alignment=1)),
            Paragraph(datos_estudiante['nombre'], ParagraphStyle('Firma', fontName='Times-Roman', fontSize=12, alignment=1, spaceBefore=0.2*cm))
        ],
        # DNI
        [
            Paragraph(f"DNI: {datos_generales['A_DNI']}", ParagraphStyle('Firma', fontName='Times-Roman', fontSize=12, alignment=1, spaceBefore=0.1*cm)),
            Paragraph("", ParagraphStyle('Firma', fontName='Times-Roman', fontSize=12, alignment=1)),
            Paragraph(f"DNI: {datos_estudiante['dni']}", ParagraphStyle('Firma', fontName='Times-Roman', fontSize=12, alignment=1, spaceBefore=0.1*cm))
        ]
    ]
    
    # Tabla con alineación PERFECTA
    tabla_firmas = Table(firmas_data, colWidths=[6*cm, 6*cm, 6*cm])
    tabla_firmas.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('LEADING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    
    elements.append(tabla_firmas)
    
    # Generar PDF
    doc.build(elements)
