import sys
from PyQt5.QtWidgets import QApplication
from septemberos.app import SeptemberOSApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SeptemberOSApp()
    window.show()
    sys.exit(app.exec_())
