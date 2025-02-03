from ui import MemoryScanWindow
from PySide6.QtWidgets import QApplication
from pyboy import PyBoy
import sys

if __name__ == "__main__":
    pyboy = PyBoy("Castlevania - The Adventure (Europe).gb")
    app = QApplication(sys.argv)
    window = MemoryScanWindow(pyboy)
    window.show()
    app.exec()
