# gui/main_window.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, 
    QComboBox, QLabel, QFileDialog, QMessageBox, QHBoxLayout
)
from pathlib import Path
from datetime import datetime
from core.pdf_processor import leer_campos_pdf
from core.report_generator import generar_reporte_estudiantes
from core.certificate_builder import generar_certificados

class SimpleApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generador de Certificados")
        self.resize(400, 300)
        
        # Variables
        self.pdf_path = "PRACTICAS OKCAHA 20-07-2025 RELLENADO.pdf"  # Ruta por defecto
        self.datos_pdf = {}
        
        # Configurar interfaz
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        # 1. Botón para cargar PDF
        btn_layout = QHBoxLayout()
        self.btn_cargar = QPushButton("Cargar PDF")
        self.btn_cargar.clicked.connect(self.cargar_pdf)
        btn_layout.addWidget(self.btn_cargar)
        
        self.btn_actualizar = QPushButton("Actualizar Datos")
        self.btn_actualizar.clicked.connect(self.cargar_datos_pdf)
        btn_layout.addWidget(self.btn_actualizar)
        layout.addLayout(btn_layout)
        
        # 2. Selector de instructor
        layout.addWidget(QLabel("Instructor:"))
        self.combo_instructor = QComboBox()
        self.combo_instructor.addItems(["Juan Pérez", "María García", "Carlos López"])
        layout.addWidget(self.combo_instructor)
        
        # 3. Selector de embarcación
        layout.addWidget(QLabel("Embarcación:"))
        self.combo_embarcacion = QComboBox()
        self.combo_embarcacion.addItems(["Velero Águila", "Lancha Rápida", "Yate de Lujo"])
        layout.addWidget(self.combo_embarcacion)
        
        # 4. Botón de generación
        self.btn_generar = QPushButton("Generar Certificados y Reporte")
        self.btn_generar.clicked.connect(self.generar_documentos)
        layout.addWidget(self.btn_generar)
        
        # 5. Estado
        self.lbl_estado = QLabel("Listo para comenzar")
        layout.addWidget(self.lbl_estado)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        # Cargar PDF inicial
        self.cargar_datos_pdf()

    def cargar_pdf(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, 
            "Seleccionar PDF de Prácticas", 
            "", 
            "PDF Files (*.pdf)"
        )
        if ruta:
            self.pdf_path = ruta
            self.cargar_datos_pdf()

    def cargar_datos_pdf(self):
        self.lbl_estado.setText("Leyendo PDF...")
        QApplication.processEvents()  # Actualizar UI
        
        self.datos_pdf = leer_campos_pdf(self.pdf_path)
        if not self.datos_pdf:
            self.lbl_estado.setText("Error: No se pudieron leer los campos")
            return False
        
        self.lbl_estado.setText(f"Datos cargados: {len(self.datos_pdf)} campos")
        return True

    def generar_documentos(self):
        if not self.datos_pdf:
            if not self.cargar_datos_pdf():
                return
        
        # Actualizar datos con selecciones
        self.datos_pdf['A_INSTR'] = self.combo_instructor.currentText()
        self.datos_pdf['B_NOMEMB'] = self.combo_embarcacion.currentText()
        
        # Crear carpeta de salida
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("output") / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generar certificados
        self.lbl_estado.setText("Generando certificados...")
        QApplication.processEvents()
        
        logo_path = Path("aliboat logo.png")
        certificados = generar_certificados(self.datos_pdf, output_dir, logo_path)
        
        # Extraer estudiantes para el reporte
        estudiantes = []
        i = 1
        while f"D_{i}" in self.datos_pdf and f"D_{i+1}" in self.datos_pdf:
            estudiantes.append((self.datos_pdf[f"D_{i}"], self.datos_pdf[f"D_{i+1}"]))
            i += 2
        
        # Generar reporte Excel
        self.lbl_estado.setText("Generando reporte Excel...")
        QApplication.processEvents()
        generar_reporte_estudiantes(self.datos_pdf, estudiantes, output_dir)
        
        self.lbl_estado.setText(f"Documentos generados en: {output_dir}")
        QMessageBox.information(
            self, 
            "Éxito", 
            f"Proceso completado:\n- {len(certificados)} certificados\n- Reporte Excel\n\nGuardados en:\n{output_dir.resolve()}"
        )
