import json
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QProgressBar, QTextEdit, QSpinBox, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor
import time


class StudyNest(QWidget):
    def __init__(self):
        super().__init__()
        self.settings_file = "timer_settings.json"
        self.study_plans_file = "study_plans.json"
        self.load_settings()
        self.setup_timer_state()
        self.setup_ui()

    def setup_timer_state(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.is_running = False
        self.current_phase = "work"  # work, short_break, long_break
        self.session_count = 0
        self.time_left = self.work_duration * 60  # Convert to seconds

    def load_settings(self):
        default_settings = {
            "work_duration": 25,
            "short_break": 5,
            "long_break": 15,
            "sessions_until_long_break": 4
        }

        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    self.settings = {**default_settings, **json.load(f)}
            except:
                self.settings = default_settings
        else:
            self.settings = default_settings

        self.work_duration = self.settings["work_duration"]
        self.short_break_duration = self.settings["short_break"]
        self.long_break_duration = self.settings["long_break"]
        self.sessions_until_long_break = self.settings["sessions_until_long_break"]

    def save_settings(self):
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=2)

    def setup_ui(self):
        main_layout = QVBoxLayout()

        # Title
        title = QLabel("🏠 StudyNest - Cozy Pomodoro Timer")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #8B4513; margin: 10px;")
        main_layout.addWidget(title)

        # Timer display
        timer_group = QGroupBox("Current Session")
        timer_layout = QVBoxLayout()

        self.phase_label = QLabel("🍂 Work Time")
        self.phase_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.phase_label.setAlignment(Qt.AlignCenter)
        timer_layout.addWidget(self.phase_label)

        self.time_display = QLabel("25:00")
        self.time_display.setFont(QFont("Arial", 36, QFont.Bold))
        self.time_display.setAlignment(Qt.AlignCenter)
        self.time_display.setStyleSheet("""
            QLabel {
                color: #CD853F;
                background-color: #FFF8DC;
                border: 3px solid #DEB887;
                border-radius: 15px;
                padding: 20px;
                margin: 10px;
            }
        """)
        timer_layout.addWidget(self.time_display)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #DEB887;
                border-radius: 5px;
                text-align: center;
                background-color: #FFF8DC;
            }
            QProgressBar::chunk {
                background-color: #CD853F;
                border-radius: 3px;
            }
        """)
        timer_layout.addWidget(self.progress_bar)

        # Control buttons
        controls_layout = QHBoxLayout()

        self.start_btn = QPushButton("▶️ Start")
        self.start_btn.clicked.connect(self.start_timer)

        self.pause_btn = QPushButton("⏸️ Pause")
        self.pause_btn.clicked.connect(self.pause_timer)
        self.pause_btn.setEnabled(False)

        self.reset_btn = QPushButton("🔄 Reset")
        self.reset_btn.clicked.connect(self.reset_timer)

        self.skip_btn = QPushButton("⏭️ Skip Phase")
        self.skip_btn.clicked.connect(self.skip_phase)

        for btn in [self.start_btn, self.pause_btn, self.reset_btn, self.skip_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #CD853F;
                    color: white;
                    border: none;
                    padding: 12px 20px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #A0522D;
                }
                QPushButton:disabled {
                    background-color: #D3D3D3;
                    color: #A0A0A0;
                }
            """)
            controls_layout.addWidget(btn)

        timer_layout.addLayout(controls_layout)
        timer_group.setLayout(timer_layout)
        main_layout.addWidget(timer_group)

        # Statistics
        stats_group = QGroupBox("Today's Progress")
        stats_layout = QHBoxLayout()

        self.sessions_label = QLabel(f"🍅 Sessions: {self.session_count}")
        self.sessions_label.setFont(QFont("Arial", 12))

        self.streak_label = QLabel("🔥 Streak: 1 day")
        self.streak_label.setFont(QFont("Arial", 12))

        stats_layout.addWidget(self.sessions_label)
        stats_layout.addWidget(self.streak_label)
        stats_group.setLayout(stats_layout)
        main_layout.addWidget(stats_group)

        # Settings
        settings_group = QGroupBox("⚙️ Timer Settings")
        settings_layout = QGridLayout()

        settings_layout.addWidget(QLabel("Work Duration (min):"), 0, 0)
        self.work_spin = QSpinBox()
        self.work_spin.setRange(1, 60)
        self.work_spin.setValue(self.work_duration)
        self.work_spin.valueChanged.connect(self.update_settings)
        settings_layout.addWidget(self.work_spin, 0, 1)

        settings_layout.addWidget(QLabel("Short Break (min):"), 0, 2)
        self.short_break_spin = QSpinBox()
        self.short_break_spin.setRange(1, 30)
        self.short_break_spin.setValue(self.short_break_duration)
        self.short_break_spin.valueChanged.connect(self.update_settings)
        settings_layout.addWidget(self.short_break_spin, 0, 3)

        settings_layout.addWidget(QLabel("Long Break (min):"), 1, 0)
        self.long_break_spin = QSpinBox()
        self.long_break_spin.setRange(5, 60)
        self.long_break_spin.setValue(self.long_break_duration)
        self.long_break_spin.valueChanged.connect(self.update_settings)
        settings_layout.addWidget(self.long_break_spin, 1, 1)

        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)

        # AI Study Plan
        ai_group = QGroupBox("🤖 AI Study Assistant")
        ai_layout = QVBoxLayout()

        generate_plan_btn = QPushButton("📚 Generate Study Plan")
        generate_plan_btn.clicked.connect(self.generate_study_plan)
        generate_plan_btn.setStyleSheet("""
            QPushButton {
                background-color: #DAA520;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #B8860B;
            }
        """)
        ai_layout.addWidget(generate_plan_btn)

        self.study_plan_display = QTextEdit()
        self.study_plan_display.setMaximumHeight(150)
        self.study_plan_display.setPlaceholderText(
            "Your AI-generated study plan will appear here...")
        self.study_plan_display.setStyleSheet("""
            QTextEdit {
                background-color: #FFFACD;
                border: 2px solid #DEB887;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Georgia', serif;
                font-size: 11px;
            }
        """)
        ai_layout.addWidget(self.study_plan_display)

        ai_group.setLayout(ai_layout)
        main_layout.addWidget(ai_group)

        self.setLayout(main_layout)
        self.update_display()

    def start_timer(self):
        self.is_running = True
        self.timer.start(1000)  # Update every second
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.apply_ambient_transition("start")

    def pause_timer(self):
        self.is_running = False
        self.timer.stop()
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)

    def reset_timer(self):
        self.timer.stop()
        self.is_running = False
        self.time_left = self.get_current_phase_duration() * 60
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.update_display()

    def skip_phase(self):
        self.timer.stop()
        self.is_running = False
        self.complete_phase()

    def update_timer(self):
        self.time_left -= 1

        if self.time_left <= 0:
            self.complete_phase()

        self.update_display()

    def complete_phase(self):
        self.timer.stop()
        self.is_running = False

        if self.current_phase == "work":
            self.session_count += 1
            self.sessions_label.setText(f"🍅 Sessions: {self.session_count}")

            # Determine next break type
            if self.session_count % self.sessions_until_long_break == 0:
                self.current_phase = "long_break"
            else:
                self.current_phase = "short_break"
        else:
            self.current_phase = "work"

        self.time_left = self.get_current_phase_duration() * 60
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.apply_ambient_transition("complete")
        self.update_display()

    def get_current_phase_duration(self):
        if self.current_phase == "work":
            return self.work_duration
        elif self.current_phase == "short_break":
            return self.short_break_duration
        else:
            return self.long_break_duration

    def update_display(self):
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        self.time_display.setText(f"{minutes:02d}:{seconds:02d}")

        # Update phase label
        phase_icons = {
            "work": "🍂 Work Time",
            "short_break": "☕ Short Break",
            "long_break": "🛋️ Long Break"
        }
        self.phase_label.setText(phase_icons.get(
            self.current_phase, "🍂 Work Time"))

        # Update progress bar
        total_duration = self.get_current_phase_duration() * 60
        progress = ((total_duration - self.time_left) / total_duration) * 100
        self.progress_bar.setValue(int(progress))

    def apply_ambient_transition(self, event_type):
        # Simple color transitions for ambient effects
        if event_type == "start":
            if self.current_phase == "work":
                self.time_display.setStyleSheet("""
                    QLabel {
                        color: #8B4513;
                        background-color: #FFF8DC;
                        border: 3px solid #CD853F;
                        border-radius: 15px;
                        padding: 20px;
                        margin: 10px;
                    }
                """)
            else:
                self.time_display.setStyleSheet("""
                    QLabel {
                        color: #228B22;
                        background-color: #F0FFF0;
                        border: 3px solid #90EE90;
                        border-radius: 15px;
                        padding: 20px;
                        margin: 10px;
                    }
                """)

    def update_settings(self):
        self.work_duration = self.work_spin.value()
        self.short_break_duration = self.short_break_spin.value()
        self.long_break_duration = self.long_break_spin.value()

        self.settings.update({
            "work_duration": self.work_duration,
            "short_break": self.short_break_duration,
            "long_break": self.long_break_duration
        })
        self.save_settings()

        # Reset timer if not running
        if not self.is_running:
            self.time_left = self.get_current_phase_duration() * 60
            self.update_display()

    def generate_study_plan(self):
        # AI study plan simulation (replace with actual AI service)
        study_plans = [
            "🎯 **Focus Session Plan**:\n• 25 min: Deep work on primary task\n• 5 min: Stretch and hydrate\n• 25 min: Review and refine\n• Take notes on key insights 📝",

            "📚 **Learning Sprint**:\n• 25 min: Read new material\n• 5 min: Quick mental review\n• 25 min: Practice or apply concepts\n• Write summary in your own words ✍️",

            "🔄 **Review & Practice**:\n• 25 min: Review previous notes\n• 5 min: Quick break with fresh air\n• 25 min: Practice problems/exercises\n• Identify areas needing more work 🎯",

            "🌟 **Creative Session**:\n• 25 min: Brainstorm and ideate\n• 5 min: Step away and reflect\n• 25 min: Organize and develop ideas\n• Document your best insights 💡"
        ]

        import random
        selected_plan = random.choice(study_plans)
        self.study_plan_display.setText(selected_plan)
