# main.py
import sys
from pathlib import Path

# Añadir directorio del proyecto al path
sys.path.append(str(Path(__file__).parent))

from PyQt5.QtWidgets import QApplication
from gui.main_window import SimpleApp

def main():
    app = QApplication(sys.argv)
    window = SimpleApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
