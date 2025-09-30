from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import QTimer, QPropertyAnimation, QEasingCurve, QRect, pyqtProperty
from PyQt5.QtGui import QPainter, QPixmap, QColor, QFont
import random
import math


class FallingLeaf(QLabel):
    def __init__(self, parent, leaf_char="🍂"):
        super().__init__(leaf_char, parent)
        self.setStyleSheet("""
            QLabel {
                background: transparent;
                font-size: 20px;
                color: #CD853F;
            }
        """)
        self.setFixedSize(30, 30)

        # Animation properties
        self.fall_speed = random.uniform(2000, 4000)  # ms to fall
        self.sway_amount = random.uniform(30, 80)
        self.rotation_speed = random.uniform(1, 3)

        # Position animation
        self.position_anim = QPropertyAnimation(self, b"pos")
        self.position_anim.setDuration(int(self.fall_speed))
        self.position_anim.setEasingCurve(QEasingCurve.InOutSine)

        # Start falling
        self.start_falling()

    def start_falling(self):
        parent_width = self.parent().width()
        parent_height = self.parent().height()

        # Start position (top, random x)
        start_x = random.randint(0, max(1, parent_width - 30))
        start_y = -30

        # End position (bottom, with sway)
        end_x = start_x + \
            random.randint(-int(self.sway_amount), int(self.sway_amount))
        end_x = max(0, min(end_x, parent_width - 30))
        end_y = parent_height + 30

        self.position_anim.setStartValue((start_x, start_y))
        self.position_anim.setEndValue((end_x, end_y))
        self.position_anim.finished.connect(self.remove_leaf)
        self.position_anim.start()

    def remove_leaf(self):
        self.deleteLater()


class FallingLeavesWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(0, 0, parent.width() if parent else 800,
                         parent.height() if parent else 600)
        self.setAttribute(81)  # Qt.WA_TransparentForMouseEvents

        self.leaf_timer = QTimer()
        self.leaf_timer.timeout.connect(self.create_leaf)
        # Create leaf every 2-5 seconds
        self.leaf_timer.start(random.randint(2000, 5000))

        self.leaf_chars = ["🍂", "🍁", "🍃"]

    def create_leaf(self):
        if self.parent():
            leaf_char = random.choice(self.leaf_chars)
            leaf = FallingLeaf(self, leaf_char)
            leaf.show()

        # Randomize next leaf timing
        self.leaf_timer.start(random.randint(3000, 7000))


class PulsingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._opacity = 1.0

        self.pulse_anim = QPropertyAnimation(self, b"opacity")
        self.pulse_anim.setDuration(2000)
        self.pulse_anim.setStartValue(0.7)
        self.pulse_anim.setEndValue(1.0)
        self.pulse_anim.setEasingCurve(QEasingCurve.InOutSine)
        self.pulse_anim.setLoopCount(-1)  # Infinite loop

    def start_pulsing(self):
        self.pulse_anim.start()

    def stop_pulsing(self):
        self.pulse_anim.stop()
        self.setOpacity(1.0)

    @pyqtProperty(float)
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self.setWindowOpacity(value)


class BreathingAnimation(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.breathing_timer = QTimer()
        self.breathing_timer.timeout.connect(self.breathe)
        self.breath_state = 0  # 0 = inhale, 1 = exhale
        self.breath_cycle = 0

    def start_breathing_guide(self):
        self.breathing_timer.start(4000)  # 4 second cycles

    def stop_breathing_guide(self):
        self.breathing_timer.stop()

    def breathe(self):
        if self.breath_state == 0:
            # Inhale phase
            self.parent().setStyleSheet(self.parent().styleSheet() + """
                QWidget { 
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #FFF8DC, stop:1 #F0E68C); 
                }
            """)
            self.breath_state = 1
        else:
            # Exhale phase
            self.parent().setStyleSheet(self.parent().styleSheet().replace(
                "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FFF8DC, stop:1 #F0E68C);",
                "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FFFACD, stop:1 #DEB887);"
            ))
            self.breath_state = 0


class FloatingParticles(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.particles = []
        self.particle_timer = QTimer()
        self.particle_timer.timeout.connect(self.update_particles)
        self.particle_timer.start(50)  # Update every 50ms

        # Create initial particles
        for _ in range(20):
            self.create_particle()

    def create_particle(self):
        if self.parent():
            particle = {
                'x': random.randint(0, self.parent().width()),
                'y': random.randint(0, self.parent().height()),
                'vx': random.uniform(-0.5, 0.5),
                'vy': random.uniform(-0.5, 0.5),
                'size': random.randint(2, 6),
                'color': random.choice(['#DEB887', '#CD853F', '#F5DEB3', '#FFE4B5']),
                'opacity': random.uniform(0.3, 0.7)
            }
            self.particles.append(particle)

    def update_particles(self):
        if not self.parent():
            return

        parent_width = self.parent().width()
        parent_height = self.parent().height()

        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']

            # Wrap around screen
            if particle['x'] < 0:
                particle['x'] = parent_width
            elif particle['x'] > parent_width:
                particle['x'] = 0

            if particle['y'] < 0:
                particle['y'] = parent_height
            elif particle['y'] > parent_height:
                particle['y'] = 0

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        for particle in self.particles:
            color = QColor(particle['color'])
            color.setAlphaF(particle['opacity'])
            painter.setBrush(color)
            painter.setPen(color)
            painter.drawEllipse(int(particle['x']), int(particle['y']),
                                particle['size'], particle['size'])


class GlowEffect:
    @staticmethod
    def apply_glow(widget, color="#CD853F", blur_radius=10):
        glow_style = f"""
            QWidget {{
                border: 2px solid transparent;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 248, 220, 0.9), 
                    stop:1 rgba(245, 222, 179, 0.9));
                box-shadow: 0 0 {blur_radius}px {color};
            }}
        """
        current_style = widget.styleSheet()
        widget.setStyleSheet(current_style + glow_style)


class WaveAnimation(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.wave_timer = QTimer()
        self.wave_timer.timeout.connect(self.update_wave)
        self.wave_offset = 0

    def start_wave(self):
        self.wave_timer.start(100)  # Update every 100ms

    def stop_wave(self):
        self.wave_timer.stop()

    def update_wave(self):
        self.wave_offset += 0.2
        if self.wave_offset > 2 * math.pi:
            self.wave_offset = 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw wave at bottom
        width = self.width()
        height = self.height()

        wave_height = 20
        wave_points = []

        for x in range(0, width + 10, 5):
            y = height - wave_height - 10 + \
                math.sin((x / 50.0) + self.wave_offset) * 10
            wave_points.append((x, y))

        # Draw the wave
        painter.setPen(QColor("#CD853F"))
        painter.setBrush(QColor(205, 133, 63, 50))  # Semi-transparent

        for i in range(len(wave_points) - 1):
            x1, y1 = wave_points[i]
            x2, y2 = wave_points[i + 1]
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
