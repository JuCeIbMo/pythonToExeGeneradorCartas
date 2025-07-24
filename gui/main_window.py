# gui/main_window.py
import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, 
    QComboBox, QLabel, QFileDialog, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import Qt
from pathlib import Path
from datetime import datetime
from core.pdf_processor import leer_campos_pdf
from core.report_generator import generar_reporte_estudiantes
from core.certificate_builder import generar_certificados

class SimpleApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aliboat (by: +59172906023)")
        self.resize(400, 300)
        
        # Habilitar drag & drop
        self.setAcceptDrops(True)
        
        # Variables
        self.pdf_path = None
        self.datos_pdf = {}
        
        # Configurar interfaz
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        # 1. Botón para actualizar datos del PDF
        btn_layout = QHBoxLayout()
        self.btn_actualizar = QPushButton("Actualizar Datos")
        self.btn_actualizar.clicked.connect(self.cargar_datos_pdf)
        btn_layout.addWidget(self.btn_actualizar)
        layout.addLayout(btn_layout)
        
        # 2. Selector de instructor
        layout.addWidget(QLabel("Instructor:"))
        self.combo_instructor = QComboBox()
        layout.addWidget(self.combo_instructor)
        
        # 3. Selector de barco
        layout.addWidget(QLabel("Barco:"))
        self.combo_barco = QComboBox()
        layout.addWidget(self.combo_barco)
        
        # Cargar datos de barcos e instructores
        self.cargar_datos_combobox()
        
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

    def cargar_pdf(self, ruta=None):
        if ruta is None:
            ruta, _ = QFileDialog.getOpenFileName(
                self, 
                "Seleccionar PDF de Prácticas", 
                "", 
                "PDF Files (*.pdf)"
            )
        if ruta:
            self.pdf_path = ruta
            self.cargar_datos_pdf()
            return True
        return False

    # ======================
    # Manejo de Drag & Drop
    # ======================
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith('.pdf'):
                if self.cargar_pdf(file_path):
                    self.lbl_estado.setText(f"PDF cargado: {Path(file_path).name}")
                break

    # ======================
    # Carga de datos
    # ======================
    def cargar_datos_combobox(self):
        try:
            with open('resources/datos.json', 'r', encoding='utf-8') as f:
                datos = json.load(f)
                
                self.combo_instructor.clear()
                self.combo_instructor.addItem("")  # Opción vacía
                for instructor in datos['instructores']:
                    # Almacenar objeto completo como dato de usuario
                    self.combo_instructor.addItem(instructor['nombre'], userData=instructor)
                
                self.combo_barco.clear()
                self.combo_barco.addItem("")  # Opción vacía
                for barco in datos['barcos']:
                    self.combo_barco.addItem(barco['nombre'])
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar datos: {str(e)}")
            self.lbl_estado.setText("Error cargando datos")

    def cargar_datos_pdf(self):
        if self.pdf_path is None:
            self.lbl_estado.setText("No hay PDF cargado")
            return False
            
        self.lbl_estado.setText("Leyendo PDF...")
        QApplication.processEvents()  # Actualizar UI
        
        self.datos_pdf = leer_campos_pdf(self.pdf_path)
        if not self.datos_pdf:
            self.lbl_estado.setText("Error: No se pudieron leer los campos")
            return False
            
        # DEBUG: Mostrar campos en consola
        print("\n=== CAMPOS DETECTADOS EN EL PDF ===")
        for campo, valor in self.datos_pdf.items():
            print(f"{campo}: {valor}")
        print("==================================\n")
        
        self.lbl_estado.setText(f"Datos cargados: {len(self.datos_pdf)} campos")
        return True

    def generar_documentos(self):
        if self.pdf_path is None:
            QMessageBox.warning(self, "Advertencia", "Por favor, cargue un archivo PDF primero")
            return
            
        if not self.datos_pdf:
            if not self.cargar_datos_pdf():
                return
        
        # Obtener datos seleccionados
        index_instructor = self.combo_instructor.currentIndex()
        instructor_obj = self.combo_instructor.itemData(index_instructor) if index_instructor > 0 else None
        barco = self.combo_barco.currentText()
        
        # Solo actualizar si hay instructor seleccionado
        datos_pdf_actualizados = self.datos_pdf.copy()
        if instructor_obj:
            datos_pdf_actualizados['A_INSTR'] = instructor_obj['nombre']
            datos_pdf_actualizados['A_DNI'] = instructor_obj['dni']
            print(f"DEBUG: Instructor actualizado - {instructor_obj['nombre']} (DNI: {instructor_obj['dni']})")
        # Si no hay instructor seleccionado, no modificar A_INSTR ni A_DNI

        # Si hay barco seleccionado, actualizar todos los campos del barco
        if barco and barco.strip():
            try:
                with open('resources/datos.json', 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                barco_obj = next((b for b in datos['barcos'] if b['nombre'] == barco), None)
                if barco_obj:
                    datos_pdf_actualizados['B_NOMEMB'] = barco_obj['nombre']
                    datos_pdf_actualizados['B_MATRICULA'] = barco_obj['matricula']
                    datos_pdf_actualizados['B_PANTALAN'] = barco_obj['pantalan']
                    datos_pdf_actualizados['B_AMARRE'] = barco_obj['amarre']
                    datos_pdf_actualizados['B_POTENCIA'] = barco_obj['potencia']
                    datos_pdf_actualizados['B_ESLORA'] = barco_obj['eslora']
                    datos_pdf_actualizados['B_INSTAL'] = barco_obj['instalacion']
                    print(f"DEBUG: Barco actualizado - {barco_obj}")
            except Exception as e:
                print(f"Error cargando datos del barco: {e}")
        
        # DEBUG: Mostrar campos modificados
        print("\n=== CAMPOS ACTUALIZADOS ===")
        print(f"A_INSTR: {datos_pdf_actualizados.get('A_INSTR', 'No modificado')}")
        print(f"B_NOMEMB: {datos_pdf_actualizados.get('B_NOMEMB', 'No modificado')}")
        print("===========================\n")
        
        # Crear carpeta de salida
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("output") / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generar certificados y guardar PDF modificado
        self.lbl_estado.setText("Generando documentos...")
        QApplication.processEvents()
        
        logo_path = Path("aliboat logo.png")
        
        # Guardar PDF modificado
        from core.pdf_processor import procesar_pdf
        pdf_modificado = procesar_pdf(
            self.pdf_path,
            datos_pdf_actualizados,
            output_dir
        )
        
        # Generar certificados
        certificados = generar_certificados(datos_pdf_actualizados, output_dir, logo_path)
        
        # Actualizar estado
        self.lbl_estado.setText(f"PDF modificado guardado: {Path(pdf_modificado).name}")
        
        # Extraer estudiantes para el reporte
        estudiantes = []
        i = 1
        while f"D_{i}" in datos_pdf_actualizados and f"D_{i+1}" in datos_pdf_actualizados:
            estudiantes.append((datos_pdf_actualizados[f"D_{i}"], datos_pdf_actualizados[f"D_{i+1}"]))
            i += 2
        
        # Generar reporte Excel
        self.lbl_estado.setText("Generando reporte Excel...")
        QApplication.processEvents()
        generar_reporte_estudiantes(datos_pdf_actualizados, estudiantes, output_dir)
        
        self.lbl_estado.setText(f"Documentos generados en: {output_dir}")
        QMessageBox.information(
            self, 
            "Éxito", 
            f"Proceso completado:\n- {len(certificados)} certificados\n- Reporte Excel\n\nGuardados en:\n{output_dir.resolve()}"
        )
