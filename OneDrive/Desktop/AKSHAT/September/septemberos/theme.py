from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import QTimer
from .animations import FallingLeavesWidget, FloatingParticles, WaveAnimation


def apply_september_theme(window):
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(245, 222, 179))  # Warm wheat
    palette.setColor(QPalette.WindowText, QColor(80, 40, 20))  # Cozy brown
    palette.setColor(QPalette.Base, QColor(255, 248, 220))    # Cornsilk
    palette.setColor(QPalette.AlternateBase, QColor(255, 228, 181))  # Moccasin
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 224))
    palette.setColor(QPalette.ToolTipText, QColor(80, 40, 20))
    palette.setColor(QPalette.Text, QColor(80, 40, 20))
    palette.setColor(QPalette.Button, QColor(222, 184, 135))  # Burlywood
    palette.setColor(QPalette.ButtonText, QColor(80, 40, 20))
    palette.setColor(QPalette.BrightText, QColor(255, 69, 0))  # OrangeRed
    window.setPalette(palette)

    # Enhanced styling with animations and gradients
    window.setStyleSheet("""
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #FFF8DC, stop:0.5 #F5DEB3, stop:1 #DEB887);
            font-family: 'Segoe UI', 'Georgia', serif;
        }
        
        QTabWidget::pane {
            border: 3px solid #CD853F;
            border-radius: 15px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(255, 248, 220, 0.95), 
                stop:1 rgba(245, 222, 179, 0.95));
            margin-top: 10px;
        }
        
        QTabWidget::tab-bar {
            alignment: center;
        }
        
        QTabBar::tab {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #DEB887, stop:1 #CD853F);
            color: white;
            padding: 12px 24px;
            margin: 2px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 14px;
            min-width: 120px;
            transition: all 0.3s ease;
        }
        
        QTabBar::tab:selected {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #DAA520, stop:1 #B8860B);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        QTabBar::tab:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #F4A460, stop:1 #D2691E);
            transform: translateY(-1px);
        }
        
        QGroupBox {
            font-weight: bold;
            font-size: 14px;
            color: #8B4513;
            border: 2px solid #CD853F;
            border-radius: 10px;
            margin: 10px 5px;
            padding-top: 15px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(255, 250, 205, 0.8), 
                stop:1 rgba(255, 228, 181, 0.8));
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 20px;
            padding: 5px 10px;
            background: #CD853F;
            color: white;
            border-radius: 5px;
        }
        
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #DEB887, stop:1 #CD853F);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 12px;
            transition: all 0.3s ease;
        }
        
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #F4A460, stop:1 #D2691E);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(205, 133, 63, 0.4);
        }
        
        QPushButton:pressed {
            transform: translateY(1px);
            box-shadow: 0 2px 4px rgba(205, 133, 63, 0.3);
        }
        
        QPushButton:disabled {
            background: #D3D3D3;
            color: #A0A0A0;
            transform: none;
            box-shadow: none;
        }
        
        QTextEdit, QListWidget {
            border: 2px solid #DEB887;
            border-radius: 8px;
            padding: 10px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(255, 248, 220, 0.95), 
                stop:1 rgba(255, 255, 255, 0.95));
            selection-background-color: #F4A460;
            font-size: 13px;
            line-height: 1.5;
        }
        
        QTextEdit:focus, QListWidget:focus {
            border: 3px solid #DAA520;
            box-shadow: 0 0 10px rgba(218, 165, 32, 0.3);
        }
        
        QLineEdit {
            border: 2px solid #DEB887;
            border-radius: 6px;
            padding: 8px 12px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #FFFACD, stop:1 #FFF8DC);
            font-size: 13px;
            transition: all 0.3s ease;
        }
        
        QLineEdit:focus {
            border: 3px solid #DAA520;
            box-shadow: 0 0 8px rgba(218, 165, 32, 0.3);
            background: #FFFFF0;
        }
        
        QProgressBar {
            border: 2px solid #DEB887;
            border-radius: 8px;
            text-align: center;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #FFF8DC, stop:1 #F5DEB3);
            font-weight: bold;
            color: #8B4513;
            height: 25px;
        }
        
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #DAA520, stop:0.5 #CD853F, stop:1 #B8860B);
            border-radius: 6px;
            margin: 2px;
        }
        
        QSpinBox {
            border: 2px solid #DEB887;
            border-radius: 5px;
            padding: 5px;
            background: #FFFACD;
            font-size: 12px;
            font-weight: bold;
            color: #8B4513;
        }
        
        QSpinBox::up-button, QSpinBox::down-button {
            background: #CD853F;
            border-radius: 3px;
            width: 18px;
        }
        
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {
            background: #DAA520;
        }
        
        QLabel {
            color: #8B4513;
            font-weight: 500;
        }
        
        /* Scrollbar styling */
        QScrollBar:vertical {
            border: 2px solid #DEB887;
            background: #FFF8DC;
            width: 16px;
            border-radius: 8px;
        }
        
        QScrollBar::handle:vertical {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #CD853F, stop:1 #DAA520);
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #DAA520, stop:1 #B8860B);
        }
    """)

    # Add falling leaves animation
    def add_animations():
        if hasattr(window, 'falling_leaves'):
            return

        window.falling_leaves = FallingLeavesWidget(window)
        window.falling_leaves.setGeometry(
            0, 0, window.width(), window.height())
        window.falling_leaves.show()
        window.falling_leaves.lower()  # Keep behind other widgets

        # Add floating particles for extra ambiance
        window.particles = FloatingParticles(window)
        window.particles.setGeometry(0, 0, window.width(), window.height())
        window.particles.show()
        window.particles.lower()

        # Add wave animation at bottom
        window.wave = WaveAnimation(window)
        window.wave.setGeometry(0, window.height() - 50, window.width(), 50)
        window.wave.start_wave()
        window.wave.show()
        window.wave.lower()

    # Delay animation start to ensure window is fully initialized
    QTimer.singleShot(1000, add_animations)

    # Handle window resize for animations
    def on_resize():
        if hasattr(window, 'falling_leaves'):
            window.falling_leaves.setGeometry(
                0, 0, window.width(), window.height())
        if hasattr(window, 'particles'):
            window.particles.setGeometry(0, 0, window.width(), window.height())
        if hasattr(window, 'wave'):
            window.wave.setGeometry(
                0, window.height() - 50, window.width(), 50)

    # Override resize event
    original_resize = window.resizeEvent

    def new_resize_event(event):
        original_resize(event)
        on_resize()
    window.resizeEvent = new_resize_event
