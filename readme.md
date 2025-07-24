CertificadosApp/
├── core/                     
│   ├── pdf_processor.py       # Procesamiento de PDFs (conserva tu lógica actual)
│   ├── report_generator.py    # Generación de reportes Excel (tu código actual)
│   ├── certificate_builder.py # Nueva generación con ReportLab
│   └── template_designer.py   # Diseñador visual de plantillas (opcional)
├── gui/                       
│   ├── main_window.py         # Ventana principal con todos los controles
│   ├── pdf_editor.py          # Editor de PDFs embebido (con PyMuPDF)
│   └── widgets.py             # Componentes personalizados
├── resources/                 
│   ├── templates/             # Plantillas de certificados (.json o .pdf)
│   ├── images/                # Logos e imágenes
│   └── output/                # Carpeta para resultados
├── config.py                   # Configuración persistente
└── main.py                     # Punto de entrada
