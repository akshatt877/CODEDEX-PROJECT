import json
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QCalendarWidget, QTextEdit, QLineEdit, QTimeEdit, QComboBox,
                             QGroupBox, QGridLayout, QListWidget, QListWidgetItem, QGraphicsDropShadowEffect,
                             QProgressBar)
from PyQt5.QtCore import Qt, QTimer, QDate, QTime, QDateTime, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPixmap, QPainter, QTextCharFormat
import calendar
from datetime import datetime, timedelta
import random


class SepTempo(QWidget):
    def __init__(self):
        super().__init__()
        self.events_file = "calendar_events.json"
        self.events = self.load_events()
        self.seasonal_stickers = ["🍂", "🍁", "🍃", "🌰", "🎃", "🌾", "🍄", "☕"]
        self.setup_ui()
        self.setup_lo_fi_sync()

    def load_events(self):
        if os.path.exists(self.events_file):
            try:
                with open(self.events_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_events(self):
        with open(self.events_file, 'w') as f:
            json.dump(self.events, f, indent=2, default=str)

    def setup_ui(self):
        main_layout = QHBoxLayout()

        # Left Panel - Calendar
        left_panel = QVBoxLayout()

        # Title
        title = QLabel("📅 SepTempo - Seasonal Calendar")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #8B4513; margin: 10px;")
        left_panel.addWidget(title)

        # Calendar Widget
        calendar_group = QGroupBox("September Calendar")
        calendar_layout = QVBoxLayout()

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.date_selected)

        # Style the calendar
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: #FFF8DC;
                border: 3px solid #CD853F;
                border-radius: 10px;
            }
            QCalendarWidget QTableCornerButton::section {
                background-color: #DEB887;
                border: 2px solid #CD853F;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #CD853F;
                color: white;
            }
            QCalendarWidget QAbstractItemView:enabled {
                font-size: 12px;
                color: #8B4513;
                background-color: #FFFACD;
                selection-background-color: #DAA520;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #D3D3D3;
            }
        """)

        calendar_layout.addWidget(self.calendar)

        # Seasonal sticker selector
        sticker_layout = QHBoxLayout()
        sticker_layout.addWidget(QLabel("Add seasonal sticker:"))

        self.sticker_combo = QComboBox()
        self.sticker_combo.addItems(self.seasonal_stickers)
        sticker_layout.addWidget(self.sticker_combo)

        add_sticker_btn = QPushButton("🎨 Add Sticker")
        add_sticker_btn.clicked.connect(self.add_seasonal_sticker)
        sticker_layout.addWidget(add_sticker_btn)

        calendar_layout.addLayout(sticker_layout)
        calendar_group.setLayout(calendar_layout)
        left_panel.addWidget(calendar_group)

        # Right Panel - Event Management
        right_panel = QVBoxLayout()

        # Selected Date Display
        self.selected_date_label = QLabel(
            f"Selected: {datetime.now().strftime('%B %d, %Y')}")
        self.selected_date_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.selected_date_label.setStyleSheet("color: #CD853F; margin: 10px;")
        right_panel.addWidget(self.selected_date_label)

        # Event Creator
        event_group = QGroupBox("✨ Create New Event")
        event_layout = QGridLayout()

        event_layout.addWidget(QLabel("Event Title:"), 0, 0)
        self.event_title = QLineEdit()
        self.event_title.setPlaceholderText("📝 Enter event title...")
        event_layout.addWidget(self.event_title, 0, 1)

        event_layout.addWidget(QLabel("Time:"), 1, 0)
        self.event_time = QTimeEdit()
        self.event_time.setTime(QTime.currentTime())
        event_layout.addWidget(self.event_time, 1, 1)

        event_layout.addWidget(QLabel("Category:"), 2, 0)
        self.event_category = QComboBox()
        categories = ["📚 Study", "💼 Work", "🎯 Personal",
                      "🎉 Social", "🏃 Exercise", "🍽️ Food", "🎨 Creative"]
        self.event_category.addItems(categories)
        event_layout.addWidget(self.event_category, 2, 1)

        event_layout.addWidget(QLabel("Description:"), 3, 0)
        self.event_description = QTextEdit()
        self.event_description.setMaximumHeight(80)
        self.event_description.setPlaceholderText(
            "Optional event description...")
        event_layout.addWidget(self.event_description, 3, 1)

        create_event_btn = QPushButton("🌟 Create Event")
        create_event_btn.clicked.connect(self.create_event)
        event_layout.addWidget(create_event_btn, 4, 0, 1, 2)

        event_group.setLayout(event_layout)
        right_panel.addWidget(event_group)

        # Today's Events
        today_group = QGroupBox("📋 Today's Schedule")
        today_layout = QVBoxLayout()

        self.today_events_list = QListWidget()
        self.today_events_list.setMaximumHeight(150)
        today_layout.addWidget(self.today_events_list)

        today_group.setLayout(today_layout)
        right_panel.addWidget(today_group)

        # Smart Suggestions
        suggestions_group = QGroupBox("🤖 Smart Event Suggestions")
        suggestions_layout = QVBoxLayout()

        self.suggestions_display = QTextEdit()
        self.suggestions_display.setMaximumHeight(120)
        self.suggestions_display.setReadOnly(True)
        self.suggestions_display.setPlaceholderText(
            "AI-powered event suggestions will appear here...")
        suggestions_layout.addWidget(self.suggestions_display)

        generate_suggestions_btn = QPushButton("💡 Generate Suggestions")
        generate_suggestions_btn.clicked.connect(
            self.generate_smart_suggestions)
        suggestions_layout.addWidget(generate_suggestions_btn)

        suggestions_group.setLayout(suggestions_layout)
        right_panel.addWidget(suggestions_group)

        # Lo-Fi Sync Status
        lofi_group = QGroupBox("🎵 Lo-Fi Sync")
        lofi_layout = QVBoxLayout()

        self.lofi_status = QLabel("🎧 Syncing with ambient lo-fi rhythms...")
        self.lofi_status.setStyleSheet("color: #A0522D; font-style: italic;")
        lofi_layout.addWidget(self.lofi_status)

        self.productivity_meter = QProgressBar()
        self.productivity_meter.setRange(0, 100)
        self.productivity_meter.setValue(75)
        self.productivity_meter.setFormat("Productivity Flow: %p%")
        lofi_layout.addWidget(self.productivity_meter)

        lofi_group.setLayout(lofi_layout)
        right_panel.addWidget(lofi_group)

        # Add panels to main layout
        left_widget = QWidget()
        left_widget.setLayout(left_panel)

        right_widget = QWidget()
        right_widget.setLayout(right_panel)

        main_layout.addWidget(left_widget, 1)
        main_layout.addWidget(right_widget, 1)

        self.setLayout(main_layout)

        # Initialize
        self.current_date = QDate.currentDate()
        self.update_calendar_stickers()
        self.update_today_events()
        self.generate_smart_suggestions()

    def setup_lo_fi_sync(self):
        # Timer for lo-fi sync effects
        self.lofi_timer = QTimer()
        self.lofi_timer.timeout.connect(self.update_lofi_sync)
        self.lofi_timer.start(3000)  # Update every 3 seconds

        # Productivity flow simulation
        self.productivity_timer = QTimer()
        self.productivity_timer.timeout.connect(self.update_productivity_flow)
        self.productivity_timer.start(5000)  # Update every 5 seconds

    def update_lofi_sync(self):
        lofi_messages = [
            "🎧 Syncing with morning coffee vibes...",
            "🎵 Flowing with autumn breeze rhythms...",
            "🍂 Harmonizing with September energy...",
            "☕ Matching cozy study pace...",
            "🎶 Aligned with peaceful lo-fi beats..."
        ]

        message = random.choice(lofi_messages)
        self.lofi_status.setText(message)

    def update_productivity_flow(self):
        # Simulate productivity fluctuation
        current_value = self.productivity_meter.value()
        change = random.randint(-10, 15)
        new_value = max(20, min(100, current_value + change))
        self.productivity_meter.setValue(new_value)

        # Change color based on productivity level
        if new_value >= 80:
            color = "#228B22"  # Green
        elif new_value >= 60:
            color = "#DAA520"  # Gold
        else:
            color = "#CD853F"  # Brown

        self.productivity_meter.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: {color};
            }}
        """)

    def date_selected(self, date):
        self.current_date = date
        date_str = date.toString("MMMM dd, yyyy")
        self.selected_date_label.setText(f"Selected: {date_str}")
        self.update_today_events()

    def add_seasonal_sticker(self):
        date_key = self.current_date.toString("yyyy-MM-dd")
        sticker = self.sticker_combo.currentText()

        if date_key not in self.events:
            self.events[date_key] = {"events": [], "stickers": []}

        if "stickers" not in self.events[date_key]:
            self.events[date_key]["stickers"] = []

        self.events[date_key]["stickers"].append(sticker)
        self.save_events()
        self.update_calendar_stickers()

    def update_calendar_stickers(self):
        # Apply stickers to calendar dates
        format_with_sticker = QTextCharFormat()
        format_with_sticker.setBackground(QColor(255, 248, 220))
        format_with_sticker.setForeground(QColor(139, 69, 19))

        for date_str, data in self.events.items():
            if "stickers" in data and data["stickers"]:
                date = QDate.fromString(date_str, "yyyy-MM-dd")
                self.calendar.setDateTextFormat(date, format_with_sticker)

    def create_event(self):
        if not self.event_title.text().strip():
            return

        date_key = self.current_date.toString("yyyy-MM-dd")

        event_data = {
            "title": self.event_title.text(),
            "time": self.event_time.time().toString("hh:mm"),
            "category": self.event_category.currentText(),
            "description": self.event_description.toPlainText(),
            "created": datetime.now().isoformat()
        }

        if date_key not in self.events:
            self.events[date_key] = {"events": [], "stickers": []}

        if "events" not in self.events[date_key]:
            self.events[date_key]["events"] = []

        self.events[date_key]["events"].append(event_data)
        self.save_events()

        # Clear form
        self.event_title.clear()
        self.event_description.clear()

        self.update_today_events()
        self.update_calendar_stickers()

    def update_today_events(self):
        self.today_events_list.clear()
        date_key = self.current_date.toString("yyyy-MM-dd")

        if date_key in self.events and "events" in self.events[date_key]:
            events = self.events[date_key]["events"]
            events.sort(key=lambda x: x["time"])  # Sort by time

            for event in events:
                event_text = f"{event['time']} - {event['category']} {event['title']}"
                item = QListWidgetItem(event_text)

                # Color code by category
                category_colors = {
                    "📚 Study": QColor(173, 216, 230),
                    "💼 Work": QColor(255, 182, 193),
                    "🎯 Personal": QColor(221, 160, 221),
                    "🎉 Social": QColor(255, 218, 185),
                    "🏃 Exercise": QColor(144, 238, 144),
                    "🍽️ Food": QColor(255, 228, 196),
                    "🎨 Creative": QColor(255, 160, 122)
                }

                color = category_colors.get(
                    event['category'], QColor(245, 222, 179))
                item.setBackground(color)

                self.today_events_list.addItem(item)

        # Add stickers display
        if date_key in self.events and "stickers" in self.events[date_key]:
            stickers = self.events[date_key]["stickers"]
            if stickers:
                sticker_text = f"🎨 Stickers: {' '.join(stickers)}"
                sticker_item = QListWidgetItem(sticker_text)
                sticker_item.setBackground(QColor(255, 255, 224))
                self.today_events_list.addItem(sticker_item)

    def generate_smart_suggestions(self):
        current_hour = datetime.now().hour
        day_of_week = datetime.now().strftime("%A")

        # Time-based suggestions
        time_suggestions = {
            "morning": [
                "☕ Start with a cozy morning coffee ritual",
                "📚 Review today's priorities and goals",
                "🌅 Take a moment to appreciate the September morning",
                "📝 Quick journaling session to set intentions"
            ],
            "afternoon": [
                "🍃 Take a refreshing autumn walk",
                "🧘 5-minute mindfulness break",
                "📖 Catch up on reading or learning",
                "🍂 Organize your workspace for better flow"
            ],
            "evening": [
                "🕯️ Create a cozy evening atmosphere",
                "📱 Digital detox and reflect on the day",
                "🎵 Listen to calming lo-fi music",
                "📓 Plan tomorrow's adventures"
            ]
        }

        # Day-based suggestions
        day_suggestions = {
            "Monday": "🌟 Start the week with intention and energy",
            "Tuesday": "🎯 Focus on important tasks and deep work",
            "Wednesday": "⚖️ Find balance between work and self-care",
            "Thursday": "🚀 Push through with momentum and motivation",
            "Friday": "🎉 Celebrate the week's accomplishments",
            "Saturday": "🛋️ Relax and enjoy leisure activities",
            "Sunday": "🔄 Reflect, recharge, and prepare for next week"
        }

        # Determine time of day
        if 6 <= current_hour < 12:
            time_period = "morning"
        elif 12 <= current_hour < 18:
            time_period = "afternoon"
        else:
            time_period = "evening"

        suggestions = time_suggestions[time_period]
        selected_suggestions = random.sample(suggestions, 2)
        day_suggestion = day_suggestions.get(day_of_week, "")

        suggestion_text = f"""
🤖 **Smart Suggestions for {day_of_week} {time_period.title()}:**

• {selected_suggestions[0]}
• {selected_suggestions[1]}

💡 **{day_of_week} Focus:**
{day_suggestion}

🍂 **September Theme:**
Embrace the cozy productivity vibes of autumn while staying organized and mindful.

Generated at {datetime.now().strftime("%H:%M")} 🕐
        """

        self.suggestions_display.setText(suggestion_text.strip())
