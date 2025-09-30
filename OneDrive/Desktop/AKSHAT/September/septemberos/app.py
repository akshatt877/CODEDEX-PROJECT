from PyQt5.QtWidgets import QMainWindow, QTabWidget
from .lofiboard import LoFiBoard
from .studynest import StudyNest
from .equinox import Equinox
from .septempo import SepTempo
from .leaflet import Leaflet
from .theme import apply_september_theme
from .music import play_lofi_music


class SeptemberOSApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SeptemberOS – Cozy Productivity Suite 🍂")
        self.resize(1200, 800)  # Larger size for all modules
        apply_september_theme(self)
        play_lofi_music()

        self.tabs = QTabWidget()
        self.tabs.addTab(LoFiBoard(), "LoFiBoard 📝")
        self.tabs.addTab(StudyNest(), "StudyNest ⏳")
        self.tabs.addTab(Equinox(), "Equinox 🌤️")
        self.tabs.addTab(SepTempo(), "SepTempo 📅")
        self.tabs.addTab(Leaflet(), "Leaflet 🌿")

        self.setCentralWidget(self.tabs)
