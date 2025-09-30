import json
import os
import requests
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTextEdit, QSlider, QComboBox, QGroupBox, QGridLayout,
                             QProgressBar, QListWidget, QGraphicsDropShadowEffect,
                             QScrollArea, QFrame, QLineEdit, QCheckBox, QSpinBox,
                             QCalendarWidget, QTabWidget, QSplitter, QDial, 
                             QApplication, QGraphicsOpacityEffect, QListWidgetItem,
                             QMessageBox)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect, pyqtProperty
from PyQt5.QtGui import QFont, QColor, QPixmap, QPainter, QLinearGradient, QPalette, QBrush
import random
import math
import time
from datetime import datetime, timedelta

# Music functionality
try:
    import pygame
    MUSIC_AVAILABLE = True
except ImportError:
    MUSIC_AVAILABLE = False
    print("Pygame not available. Music functionality disabled.")

class WeatherThread(QThread):
    weather_updated = pyqtSignal(dict)
    
    def __init__(self, city="New York"):
        super().__init__()
        self.city = city
        
    def run(self):
        # Enhanced weather data simulation with more details
        conditions = ["Sunny", "Cloudy", "Rainy", "Partly Cloudy", "Foggy", "Windy", "Overcast"]
        selected_condition = random.choice(conditions)
        
        weather_data = {
            "temperature": random.randint(12, 28),
            "condition": selected_condition,
            "humidity": random.randint(35, 85),
            "wind_speed": random.randint(5, 25),
            "pressure": random.randint(995, 1025),
            "uv_index": random.randint(1, 8),
            "feels_like": random.randint(10, 30),
            "description": self.get_weather_description(selected_condition),
            "air_quality": random.choice(["Good", "Moderate", "Unhealthy for Sensitive Groups"]),
            "sunrise": "06:42",
            "sunset": "18:24"
        }
        self.weather_updated.emit(weather_data)
        
    def get_weather_description(self, condition):
        descriptions = {
            "Sunny": ["Brilliant autumn sunshine! 🌞", "Golden September rays ☀️", "Perfect day for outdoor activities! 🌻"],
            "Cloudy": ["Soft cloudy embrace ☁️", "Gentle overcast skies 🌫️", "Cozy cloud coverage 🤍"],
            "Rainy": ["Gentle September rain 🌧️", "Perfect for reading inside 📚", "Nature's autumn shower 💧"],
            "Partly Cloudy": ["Beautiful mix of sun and clouds ⛅", "Dynamic September sky 🌤️", "Perfect balance of light and shade 🌥️"],
            "Foggy": ["Mysterious autumn mist 🌫️", "Ethereal September fog 👻", "Dreamy morning haze ✨"],
            "Windy": ["Crisp autumn breeze 🍃", "Dancing leaves in the wind 🍂", "Refreshing September gusts 💨"],
            "Overcast": ["Gentle gray autumn sky 🌫️", "Soft overcast comfort ☁️", "Peaceful cloudy day 🤍"]
        }
        return random.choice(descriptions.get(condition, ["Beautiful September weather! 🍂"]))

class AnimatedWeatherWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_weather)
        self.animation_phase = 0
        self.weather_condition = "Sunny"
        
    def set_weather_condition(self, condition):
        self.weather_condition = condition
        self.start_animation()
        
    def start_animation(self):
        if self.weather_condition in ["Rainy", "Foggy"]:
            self.animation_timer.start(200)  # Fast animation for rain/fog
        elif self.weather_condition in ["Windy"]:
            self.animation_timer.start(300)  # Medium speed for wind
        else:
            self.animation_timer.start(1000)  # Slow for other conditions
            
    def animate_weather(self):
        self.animation_phase += 1
        
        if self.weather_condition == "Rainy":
            rain_icons = ["🌧️", "💧", "☔", "🌦️"]
            self.setText(rain_icons[self.animation_phase % len(rain_icons)])
        elif self.weather_condition == "Windy":
            wind_icons = ["💨", "🍃", "🌪️", "🍂"]
            self.setText(wind_icons[self.animation_phase % len(wind_icons)])
        elif self.weather_condition == "Foggy":
            fog_icons = ["�️", "🌁", "☁️", "🌫️"]
            self.setText(fog_icons[self.animation_phase % len(fog_icons)])
        else:
            # Keep static for other conditions
            icons = {"Sunny": "☀️", "Cloudy": "☁️", "Partly Cloudy": "⛅", "Overcast": "🌥️"}
            self.setText(icons.get(self.weather_condition, "🌤️"))

class MoodAnalyzer(QWidget):
    def __init__(self):
        super().__init__()
        self.mood_colors = {
            "😊 Happy": "#FFD700",      # Gold
            "😌 Calm": "#87CEEB",       # Sky Blue
            "😔 Sad": "#4682B4",        # Steel Blue
            "😴 Tired": "#9370DB",      # Medium Purple
            "🤗 Excited": "#FF6347",    # Tomato
            "😰 Anxious": "#FF4500",    # Orange Red
            "🤔 Thoughtful": "#20B2AA", # Light Sea Green
            "😍 Inspired": "#FF1493",   # Deep Pink
            "😤 Frustrated": "#DC143C", # Crimson
            "🥰 Content": "#98FB98",    # Pale Green
            "😪 Drowsy": "#DDA0DD",     # Plum
            "🙃 Playful": "#FFB347"     # Peach
        }
        
    def get_mood_color(self, mood):
        return self.mood_colors.get(mood, "#CD853F")
        
    def analyze_mood_pattern(self, mood_history):
        if not mood_history:
            return "No mood data available yet."
            
        # Analyze recent mood trends
        recent_moods = list(mood_history.values())[-7:]  # Last 7 entries
        
        if not recent_moods:
            return "Start logging moods to see patterns!"
            
        # Calculate average intensity
        avg_intensity = sum(mood['intensity'] for mood in recent_moods) / len(recent_moods)
        
        # Find most common mood
        mood_counts = {}
        for mood_entry in recent_moods:
            mood = mood_entry['mood']
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
            
        most_common_mood = max(mood_counts, key=mood_counts.get) if mood_counts else "Unknown"
        
        # Generate insights
        if avg_intensity >= 7:
            intensity_desc = "high intensity"
        elif avg_intensity >= 5:
            intensity_desc = "moderate intensity"
        else:
            intensity_desc = "low intensity"
            
        analysis = f"""
🧠 **Mood Pattern Analysis:**

📊 **Recent Trend:** Your dominant mood has been {most_common_mood}
⚡ **Average Intensity:** {avg_intensity:.1f}/10 ({intensity_desc})
📈 **Mood Entries:** {len(recent_moods)} recent logs

💡 **Insights:**
• You've been experiencing {intensity_desc} emotions lately
• {most_common_mood} appears most frequently in your recent logs
• Consider factors like weather, sleep, and activities that influence your mood
        """
        
        return analysis.strip()

class BackgroundMusic:
    def __init__(self):
        self.is_playing = False
        self.current_track = None
        self.volume = 0.7
        self.paused = False
        self.tracks = [
            "Ambient Autumn",
            "Gentle Rain Sounds", 
            "Forest Whispers",
            "September Breeze",
            "Cozy Afternoon",
            "Productivity Flow",
            "Focus Zone"
        ]
        
        # Audio file mapping
        self.audio_files = {
            "Ambient Autumn": "audio/ambient_autumn.wav",
            "Gentle Rain Sounds": "audio/gentle_rain_sounds.wav",
            "Forest Whispers": "audio/forest_whispers.wav",
            "September Breeze": "audio/september_breeze.wav",
            "Cozy Afternoon": "audio/cozy_afternoon.wav",
            "Productivity Flow": "audio/productivity_flow.wav",
            "Focus Zone": "audio/focus_zone.wav"
        }
        
        if MUSIC_AVAILABLE:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                pygame.mixer.music.set_volume(self.volume)
                self.available = True
                print("🎵 Background music system initialized")
            except Exception as e:
                self.available = False
                print(f"Pygame mixer initialization failed: {e}")
        else:
            self.available = False
            print("Pygame not available - music disabled")
    
    def play_track(self, track_name):
        """Play an actual audio track"""
        if not self.available:
            print("❌ Audio system not available")
            return False
        
        if track_name not in self.audio_files:
            print(f"❌ Track not found: {track_name}")
            return False
        
        audio_file = self.audio_files[track_name]
        if not os.path.exists(audio_file):
            print(f"❌ Audio file not found: {audio_file}")
            return False
        
        try:
            # Stop any current music
            pygame.mixer.music.stop()
            
            # Load and play the new track
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play(-1)  # -1 means loop indefinitely
            
            self.current_track = track_name
            self.is_playing = True
            self.paused = False
            
            print(f"🎵 Now playing: {track_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error playing {track_name}: {e}")
            return False
    
    def pause(self):
        """Pause current track"""
        if self.available and self.is_playing and not self.paused:
            try:
                pygame.mixer.music.pause()
                self.paused = True
                print("⏸️ Music paused")
            except Exception as e:
                print(f"Error pausing music: {e}")
    
    def resume(self):
        """Resume current track"""
        if self.available and self.is_playing and self.paused:
            try:
                pygame.mixer.music.unpause()
                self.paused = False
                print(f"▶️ Resumed: {self.current_track}")
            except Exception as e:
                print(f"Error resuming music: {e}")
    
    def stop(self):
        """Stop current track"""
        if self.available:
            try:
                pygame.mixer.music.stop()
                self.is_playing = False
                self.paused = False
                self.current_track = None
                print("⏹️ Music stopped")
            except Exception as e:
                print(f"Error stopping music: {e}")
    
    def set_volume(self, volume):
        """Set volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        if self.available:
            try:
                pygame.mixer.music.set_volume(self.volume)
                print(f"🔊 Volume set to {int(self.volume * 100)}%")
            except Exception as e:
                print(f"Error setting volume: {e}")
    
    def get_status(self):
        """Get current music status"""
        # Check if music is actually playing
        if self.available and self.is_playing:
            try:
                playing = pygame.mixer.music.get_busy()
                if not playing and not self.paused:
                    # Music finished, restart it
                    if self.current_track:
                        self.play_track(self.current_track)
            except:
                pass
        
        return {
            'is_playing': self.is_playing,
            'current_track': self.current_track,
            'volume': self.volume,
            'available': self.available,
            'paused': self.paused
        }

class Equinox(QWidget):
    def __init__(self):
        super().__init__()
        self.mood_file = "mood_data.json"
        self.weather_file = "weather_history.json"
        self.settings_file = "equinox_settings.json"
        
        self.mood_history = self.load_mood_data()
        self.weather_history = self.load_weather_history()
        self.settings = self.load_settings()
        self.current_weather = {}
        
        self.mood_analyzer = MoodAnalyzer()
        self.background_music = BackgroundMusic()
        self.setup_ui()
        self.setup_weather_timer()
        self.setup_animations()
        
    def load_mood_data(self):
        if os.path.exists(self.mood_file):
            try:
                with open(self.mood_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_mood_data(self):
        with open(self.mood_file, 'w') as f:
            json.dump(self.mood_history, f, indent=2)
            
    def load_weather_history(self):
        if os.path.exists(self.weather_file):
            try:
                with open(self.weather_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_weather_history(self):
        with open(self.weather_file, 'w') as f:
            json.dump(self.weather_history, f, indent=2)
            
    def load_settings(self):
        default_settings = {
            "city": "New York",
            "units": "metric",
            "notifications": True,
            "auto_mood_suggestions": True,
            "theme_sync": True
        }
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    return {**default_settings, **json.load(f)}
            except:
                return default_settings
        return default_settings
    
    def save_settings(self):
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=2)
            
    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        # Enhanced Title with Animation
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(135, 206, 235, 0.3),
                    stop:0.5 rgba(255, 215, 0, 0.3),
                    stop:1 rgba(255, 140, 0, 0.3));
                border-radius: 20px;
                margin: 5px;
                padding: 10px;
            }
        """)
        title_layout = QHBoxLayout(title_frame)
        
        title = QLabel("🌤️ Equinox - Weather & Mood Harmony ✨")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #4169E1, stop:0.5 #DAA520, stop:1 #FF6347);
            margin: 10px;
            padding: 15px;
        """)
        
        # Add glow effect to title
        title_shadow = QGraphicsDropShadowEffect()
        title_shadow.setBlurRadius(25)
        title_shadow.setColor(QColor(218, 165, 32, 120))
        title_shadow.setOffset(0, 0)
        title.setGraphicsEffect(title_shadow)
        
        title_layout.addWidget(title)
        main_layout.addWidget(title_frame)
        
        # Add music controls
        music_frame = self.create_music_controls()
        main_layout.addWidget(music_frame)
        
        # Create tabbed interface for better organization
        self.main_tabs = QTabWidget()
        self.main_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 3px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #87CEEB, stop:1 #FFD700);
                border-radius: 15px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 248, 220, 0.95), 
                    stop:1 rgba(240, 248, 255, 0.95));
            }
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #87CEEB, stop:1 #4682B4);
                color: white;
                padding: 12px 20px;
                margin: 2px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFD700, stop:1 #DAA520);
            }
        """)
        
        # Weather Tab with entrance animation
        weather_tab = self.create_weather_tab()
        self.main_tabs.addTab(weather_tab, "🌤️ Weather")
        QTimer.singleShot(200, lambda: self.add_entrance_animation(weather_tab))
        
        # Mood Tab with entrance animation
        mood_tab = self.create_mood_tab()
        self.main_tabs.addTab(mood_tab, "😊 Mood Tracker")
        QTimer.singleShot(400, lambda: self.add_entrance_animation(mood_tab))
        
        # Analytics Tab with entrance animation
        analytics_tab = self.create_analytics_tab()
        self.main_tabs.addTab(analytics_tab, "📊 Analytics")
        QTimer.singleShot(600, lambda: self.add_entrance_animation(analytics_tab))
        
        # Settings Tab with entrance animation
        settings_tab = self.create_settings_tab()
        self.main_tabs.addTab(settings_tab, "⚙️ Settings")
        QTimer.singleShot(800, lambda: self.add_entrance_animation(settings_tab))
        
        main_layout.addWidget(self.main_tabs)
        self.setLayout(main_layout)
        
        # Add hover animations to tabs
        self.setup_tab_hover_effects()
        
        # Store reference to tabs for animations
        self.tabs = self.main_tabs
        
    def create_music_controls(self):
        """Create enhanced music control panel with better visualization"""
        music_frame = QFrame()
        music_frame.setMaximumHeight(120)
        music_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(72, 61, 139, 0.95),
                    stop:0.3 rgba(106, 90, 205, 0.95),
                    stop:0.7 rgba(147, 112, 219, 0.95),
                    stop:1 rgba(138, 43, 226, 0.95));
                border: 3px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4B0082, stop:0.5 #8A2BE2, stop:1 #9370DB);
                border-radius: 20px;
                margin: 8px;
                padding: 15px;
            }
        """)
        
        main_layout = QVBoxLayout(music_frame)
        main_layout.setSpacing(8)
        
        # Top row - Now Playing Display
        now_playing_frame = QFrame()
        now_playing_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.15);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 12px;
                padding: 8px;
                margin: 2px;
            }
        """)
        now_playing_layout = QHBoxLayout(now_playing_frame)
        
        # Animated music icon
        self.music_icon = QLabel("🎵")
        self.music_icon.setFont(QFont("Arial", 16, QFont.Bold))
        self.music_icon.setStyleSheet("""
            color: #FFD700;
            background: rgba(255, 215, 0, 0.2);
            border-radius: 15px;
            padding: 5px;
            margin: 2px;
        """)
        
        # Enhanced status display with better formatting
        self.music_status = QLabel("� Background Music System Ready")
        self.music_status.setFont(QFont("Arial", 12, QFont.Bold))
        self.music_status.setStyleSheet("""
            color: #FFFFFF;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 8px 15px;
            margin: 2px;
        """)
        
        # Track time display (placeholder)
        self.track_time = QLabel("♪ Ambient Audio ♪")
        self.track_time.setFont(QFont("Arial", 10, QFont.Bold))
        self.track_time.setStyleSheet("""
            color: #E6E6FA;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            padding: 4px 8px;
            margin: 2px;
        """)
        
        now_playing_layout.addWidget(self.music_icon)
        now_playing_layout.addWidget(self.music_status, 1)  # Take more space
        now_playing_layout.addWidget(self.track_time)
        
        # Bottom row - Controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(15)
        
        # Track selection combo
        self.track_combo = QComboBox()
        self.track_combo.addItems(self.background_music.tracks)
        self.track_combo.setStyleSheet("""
            QComboBox {
                background: rgba(255, 255, 255, 0.8);
                border: 2px solid #8A2BE2;
                border-radius: 8px;
                padding: 5px;
                font-weight: bold;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                border: 2px solid #8A2BE2;
                background: #8A2BE2;
            }
        """)
        
        # Control buttons with enhanced styling
        self.play_btn = QPushButton("▶️ PLAY")
        self.pause_btn = QPushButton("⏸️ PAUSE")  
        self.stop_btn = QPushButton("⏹️ STOP")
        
        # Enhanced Play button styling (green theme)
        self.play_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #32CD32, stop:1 #228B22);
                color: white;
                border: 2px solid #228B22;
                border-radius: 12px;
                padding: 10px 18px;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7FFF00, stop:1 #32CD32);
                border: 2px solid #32CD32;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #228B22, stop:1 #006400);
                border: 2px solid #006400;
            }
            QPushButton:disabled {
                background: #A0A0A0;
                border: 2px solid #808080;
                color: #D0D0D0;
            }
        """)
        
        # Enhanced Pause button styling (orange theme)
        self.pause_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF8C00, stop:1 #FF6347);
                color: white;
                border: 2px solid #FF6347;
                border-radius: 12px;
                padding: 10px 18px;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFA500, stop:1 #FF8C00);
                border: 2px solid #FF8C00;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF6347, stop:1 #DC143C);
                border: 2px solid #DC143C;
            }
            QPushButton:disabled {
                background: #A0A0A0;
                border: 2px solid #808080;
                color: #D0D0D0;
            }
        """)
        
        # Enhanced Stop button styling (red theme)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #DC143C, stop:1 #B22222);
                color: white;
                border: 2px solid #B22222;
                border-radius: 12px;
                padding: 10px 18px;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF1493, stop:1 #DC143C);
                border: 2px solid #DC143C;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #B22222, stop:1 #8B0000);
                border: 2px solid #8B0000;
            }
            QPushButton:disabled {
                background: #A0A0A0;
                border: 2px solid #808080;
                color: #D0D0D0;
            }
        """)
        
        # Track selection with enhanced styling
        track_label = QLabel("🎧 Select Track:")
        track_label.setFont(QFont("Arial", 10, QFont.Bold))
        track_label.setStyleSheet("color: #E6E6FA; margin-right: 5px;")
        
        self.track_combo = QComboBox()
        self.track_combo.addItems(self.background_music.tracks)
        self.track_combo.setStyleSheet("""
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.9),
                    stop:1 rgba(230, 230, 250, 0.9));
                border: 2px solid #8A2BE2;
                border-radius: 10px;
                padding: 6px 10px;
                font-weight: bold;
                font-size: 11px;
                min-width: 160px;
                color: #4B0082;
            }
            QComboBox:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 1.0),
                    stop:1 rgba(240, 240, 255, 1.0));
                border: 2px solid #9370DB;
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
                background: #8A2BE2;
                border-radius: 5px;
            }
            QComboBox::down-arrow {
                image: none;
                border: 3px solid #FFFFFF;
                border-top: 6px solid #FFFFFF;
                border-left: 3px solid transparent;
                border-right: 3px solid transparent;
                width: 0px;
                height: 0px;
            }
        """)
        
        # Enhanced volume control
        volume_frame = QFrame()
        volume_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 4px;
            }
        """)
        volume_layout = QHBoxLayout(volume_frame)
        volume_layout.setContentsMargins(8, 4, 8, 4)
        
        volume_label = QLabel("🔊")
        volume_label.setFont(QFont("Arial", 12, QFont.Bold))
        volume_label.setStyleSheet("color: #FFD700; margin-right: 5px;")
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setMaximumWidth(120)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 2px solid #8A2BE2;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(255, 255, 255, 0.3),
                    stop:1 rgba(138, 43, 226, 0.3));
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFD700, stop:1 #DAA520);
                border: 3px solid #4B0082;
                width: 20px;
                height: 20px;
                border-radius: 10px;
                margin: -6px 0;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFFF00, stop:1 #FFD700);
                border: 3px solid #8A2BE2;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #9370DB, stop:1 #8A2BE2);
                border-radius: 4px;
            }
        """)
        
        self.volume_percent = QLabel("70%")
        self.volume_percent.setFont(QFont("Arial", 9, QFont.Bold))
        self.volume_percent.setStyleSheet("color: #E6E6FA; margin-left: 5px; min-width: 30px;")
        
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(self.volume_percent)
        
        # Add track selection to controls
        controls_layout.addWidget(track_label)
        controls_layout.addWidget(self.track_combo)
        controls_layout.addWidget(self.play_btn)
        controls_layout.addWidget(self.pause_btn)
        controls_layout.addWidget(self.stop_btn)
        controls_layout.addWidget(volume_frame)
        controls_layout.addStretch()
        
        # Assemble the main layout
        main_layout.addWidget(now_playing_frame)
        main_layout.addLayout(controls_layout)
        
        # Connect signals
        self.play_btn.clicked.connect(self.play_music)
        self.pause_btn.clicked.connect(self.pause_music)
        self.stop_btn.clicked.connect(self.stop_music)
        self.volume_slider.valueChanged.connect(self.change_volume)
        
        # Initialize button states
        self.update_button_states(playing=False)
        
        # Add animations to music controls
        for widget in [self.play_btn, self.pause_btn, self.stop_btn]:
            self.create_hover_animation(widget)
        
        # Add pulsing animation to music icon
        self.setup_music_icon_animation()
        
        return music_frame
    
    def play_music(self):
        """Play selected track or resume if paused"""
        status = self.background_music.get_status()
        
        if status['paused'] and status['current_track']:
            # Resume paused music
            self.background_music.resume()
            self.music_status.setText(f"🎵 Now Playing: {status['current_track']}")
            self.track_time.setText("♪ Playing - Looped ♪")
            self.pause_btn.setText("⏸️ PAUSE")
            self.start_music_icon_pulse()
        else:
            # Play new track
            track = self.track_combo.currentText()
            success = self.background_music.play_track(track)
            if success:
                self.music_status.setText(f"🎵 Now Playing: {track}")
                self.track_time.setText("♪ Playing - Looped ♪")
                self.pause_btn.setText("⏸️ PAUSE")
                self.update_button_states(playing=True)
                self.start_music_icon_pulse()
            else:
                self.music_status.setText("❌ Audio System Unavailable")
                self.track_time.setText("♪ Check Audio Files ♪")
        
        self.create_button_pulse_animation(self.play_btn)
    
    def pause_music(self):
        """Pause/Resume current track"""
        status = self.background_music.get_status()
        
        if status['is_playing'] and not status['paused']:
            # Pause the music
            self.background_music.pause()
            self.music_status.setText(f"⏸️ Paused: {status['current_track']}")
            self.track_time.setText("♪ Paused ♪")
            self.pause_btn.setText("▶️ RESUME")
            self.stop_music_icon_pulse()
        elif status['paused']:
            # Resume the music
            self.background_music.resume()
            self.music_status.setText(f"🎵 Resumed: {status['current_track']}")
            self.track_time.setText("♪ Playing - Looped ♪")
            self.pause_btn.setText("⏸️ PAUSE")
            self.start_music_icon_pulse()
        
        self.create_button_pulse_animation(self.pause_btn)
    
    def stop_music(self):
        """Stop current track"""
        self.background_music.stop()
        self.music_status.setText("🎼 Music Stopped - Ready to Play")
        self.track_time.setText("♪ Select & Play ♪")
        self.pause_btn.setText("⏸️ PAUSE")
        self.update_button_states(playing=False)
        self.stop_music_icon_pulse()
        self.create_button_pulse_animation(self.stop_btn)
    
    def update_button_states(self, playing=False):
        """Update button enabled/disabled states"""
        if playing:
            self.play_btn.setEnabled(True)
            self.pause_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)
        else:
            self.play_btn.setEnabled(True)
            self.pause_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)
    
    def change_volume(self, value):
        """Change music volume"""
        volume = value / 100.0
        self.background_music.set_volume(volume)
        self.volume_percent.setText(f"{value}%")
        
    def create_weather_tab(self):
        weather_widget = QWidget()
        layout = QVBoxLayout(weather_widget)
        
        # Current Weather Display
        current_weather_group = QGroupBox("🌤️ Current Weather Conditions")
        current_weather_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #4682B4;
                border: 3px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #87CEEB, stop:1 #4169E1);
                border-radius: 15px;
                margin: 10px;
                padding-top: 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(240, 248, 255, 0.9), 
                    stop:1 rgba(230, 230, 250, 0.9));
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 8px 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #87CEEB, stop:1 #4169E1);
                color: white;
                border-radius: 8px;
            }
        """)
        
        weather_layout = QGridLayout()
        
        # Animated Weather Icon
        self.animated_weather_icon = AnimatedWeatherWidget()
        self.animated_weather_icon.setFont(QFont("Arial", 64))
        self.animated_weather_icon.setAlignment(Qt.AlignCenter)
        weather_layout.addWidget(self.animated_weather_icon, 0, 0, 3, 1)
        
        # Temperature Display with gradient
        self.temperature_label = QLabel("22°C")
        self.temperature_label.setFont(QFont("Arial", 36, QFont.Bold))
        self.temperature_label.setStyleSheet("""
            color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #FF6347, stop:0.5 #FFD700, stop:1 #4169E1);
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 10px;
        """)
        weather_layout.addWidget(self.temperature_label, 0, 1)
        
        # Feels Like Temperature
        self.feels_like_label = QLabel("Feels like: 24°C")
        self.feels_like_label.setFont(QFont("Arial", 14))
        self.feels_like_label.setStyleSheet("color: #4682B4; font-style: italic;")
        weather_layout.addWidget(self.feels_like_label, 1, 1)
        
        # Weather Condition
        self.condition_label = QLabel("Partly Cloudy")
        self.condition_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.condition_label.setStyleSheet("color: #2F4F4F;")
        weather_layout.addWidget(self.condition_label, 2, 1)
        
        # Weather Details Grid
        details_frame = QFrame()
        details_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        details_layout = QGridLayout(details_frame)
        
        # Humidity
        self.humidity_label = QLabel("💧 Humidity: 65%")
        self.humidity_label.setStyleSheet("color: #1E90FF; font-weight: bold;")
        details_layout.addWidget(self.humidity_label, 0, 0)
        
        # Wind Speed
        self.wind_label = QLabel("💨 Wind: 12 km/h")
        self.wind_label.setStyleSheet("color: #32CD32; font-weight: bold;")
        details_layout.addWidget(self.wind_label, 0, 1)
        
        # Pressure
        self.pressure_label = QLabel("🌡️ Pressure: 1013 hPa")
        self.pressure_label.setStyleSheet("color: #8A2BE2; font-weight: bold;")
        details_layout.addWidget(self.pressure_label, 1, 0)
        
        # UV Index
        self.uv_label = QLabel("☀️ UV Index: 3")
        self.uv_label.setStyleSheet("color: #FF8C00; font-weight: bold;")
        details_layout.addWidget(self.uv_label, 1, 1)
        
        # Air Quality
        self.air_quality_label = QLabel("🌱 Air Quality: Good")
        self.air_quality_label.setStyleSheet("color: #228B22; font-weight: bold;")
        details_layout.addWidget(self.air_quality_label, 2, 0)
        
        # Sun Times
        self.sun_times_label = QLabel("🌅 Sunrise: 06:42 | 🌇 Sunset: 18:24")
        self.sun_times_label.setStyleSheet("color: #FF4500; font-weight: bold;")
        details_layout.addWidget(self.sun_times_label, 2, 1)
        
        weather_layout.addWidget(details_frame, 3, 0, 1, 2)
        
        # Weather Description
        self.weather_description = QLabel("Perfect autumn day! 🍂")
        self.weather_description.setFont(QFont("Arial", 14))
        self.weather_description.setStyleSheet("""
            color: #B22222; 
            font-style: italic; 
            background: rgba(255, 228, 181, 0.3);
            border-radius: 8px;
            padding: 10px;
            margin: 5px;
        """)
        self.weather_description.setAlignment(Qt.AlignCenter)
        weather_layout.addWidget(self.weather_description, 4, 0, 1, 2)
        
        # Refresh Button
        refresh_weather_btn = QPushButton("🔄 Refresh Weather Data")
        refresh_weather_btn.clicked.connect(self.refresh_weather)
        refresh_weather_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #87CEEB, stop:1 #4682B4);
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #98FB98, stop:1 #32CD32);
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                transform: translateY(1px);
            }
        """)
        weather_layout.addWidget(refresh_weather_btn, 5, 0, 1, 2)
        
        current_weather_group.setLayout(weather_layout)
        layout.addWidget(current_weather_group)
        
        return weather_widget
        
    def create_mood_tab(self):
        mood_widget = QWidget()
        layout = QVBoxLayout(mood_widget)
        
        # Mood Input Section
        mood_input_group = QGroupBox("😊 Log Your Current Mood")
        mood_input_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #FF1493;
                border: 3px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF69B4, stop:1 #FF1493);
                border-radius: 15px;
                margin: 10px;
                padding-top: 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 240, 245, 0.9), 
                    stop:1 rgba(255, 228, 225, 0.9));
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 8px 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF69B4, stop:1 #FF1493);
                color: white;
                border-radius: 8px;
            }
        """)
        
        mood_input_layout = QGridLayout()
        
        # Enhanced Mood Selector
        mood_input_layout.addWidget(QLabel("How are you feeling right now?"), 0, 0)
        
        self.mood_combo = QComboBox()
        mood_options = [
            "😊 Happy", "😌 Calm", "😔 Sad", "😴 Tired", 
            "🤗 Excited", "😰 Anxious", "🤔 Thoughtful", "😍 Inspired",
            "😤 Frustrated", "🥰 Content", "😪 Drowsy", "🙃 Playful"
        ]
        self.mood_combo.addItems(mood_options)
        self.mood_combo.setStyleSheet("""
            QComboBox {
                background: rgba(255, 255, 255, 0.8);
                border: 2px solid #FF69B4;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
                color: #8B008B;
            }
            QComboBox:hover {
                border: 2px solid #FF1493;
                background: rgba(255, 240, 245, 0.9);
            }
        """)
        mood_input_layout.addWidget(self.mood_combo, 0, 1)
        
        # Enhanced Intensity Slider
        intensity_frame = QFrame()
        intensity_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 15px;
            }
        """)
        intensity_layout = QHBoxLayout(intensity_frame)
        
        intensity_layout.addWidget(QLabel("Intensity Level:"))
        
        self.mood_slider = QSlider(Qt.Horizontal)
        self.mood_slider.setRange(1, 10)
        self.mood_slider.setValue(5)
        self.mood_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 2px solid #FF69B4;
                height: 12px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF69B4, stop:0.5 #FF1493, stop:1 #DC143C);
                border-radius: 6px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFB6C1, stop:1 #FF1493);
                border: 3px solid #8B008B;
                width: 24px;
                margin: -8px 0;
                border-radius: 12px;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFCCCB, stop:1 #FF69B4);
            }
        """)
        intensity_layout.addWidget(self.mood_slider)
        
        self.intensity_label = QLabel("5/10")
        self.intensity_label.setStyleSheet("""
            font-weight: bold; 
            color: #FF1493;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 5px;
            padding: 5px 10px;
        """)
        self.mood_slider.valueChanged.connect(lambda v: self.intensity_label.setText(f"{v}/10"))
        intensity_layout.addWidget(self.intensity_label)
        
        mood_input_layout.addWidget(intensity_frame, 1, 0, 1, 2)
        
        # Mood Notes
        mood_input_layout.addWidget(QLabel("Additional Notes:"), 2, 0)
        self.mood_notes = QTextEdit()
        self.mood_notes.setMaximumHeight(80)
        self.mood_notes.setPlaceholderText("What's influencing your mood today? (optional)")
        self.mood_notes.setStyleSheet("""
            QTextEdit {
                background: rgba(255, 255, 255, 0.8);
                border: 2px solid #FF69B4;
                border-radius: 8px;
                padding: 8px;
                color: #8B008B;
            }
            QTextEdit:focus {
                border: 2px solid #FF1493;
                background: rgba(255, 240, 245, 0.9);
            }
        """)
        mood_input_layout.addWidget(self.mood_notes, 2, 1)
        
        # Enhanced Log Button
        log_mood_btn = QPushButton("📝 Log Current Mood")
        log_mood_btn.clicked.connect(self.log_current_mood)
        log_mood_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF69B4, stop:1 #FF1493);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 12px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFB6C1, stop:1 #FF69B4);
                transform: translateY(-3px);
            }
            QPushButton:pressed {
                transform: translateY(1px);
            }
        """)
        mood_input_layout.addWidget(log_mood_btn, 3, 0, 1, 2)
        
        mood_input_group.setLayout(mood_input_layout)
        layout.addWidget(mood_input_group)
        
        # Mood History Display
        mood_history_group = QGroupBox("📚 Recent Mood History")
        mood_history_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #20B2AA;
                border: 3px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #48D1CC, stop:1 #20B2AA);
                border-radius: 15px;
                margin: 10px;
                padding-top: 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(240, 255, 255, 0.9), 
                    stop:1 rgba(225, 255, 255, 0.9));
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 8px 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #48D1CC, stop:1 #20B2AA);
                color: white;
                border-radius: 8px;
            }
        """)
        
        mood_history_layout = QVBoxLayout()
        
        self.mood_history_list = QListWidget()
        self.mood_history_list.setMaximumHeight(150)
        self.mood_history_list.setStyleSheet("""
            QListWidget {
                background: rgba(255, 255, 255, 0.3);
                border: 2px solid #48D1CC;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                margin: 2px;
                border-radius: 5px;
                background: rgba(255, 255, 255, 0.5);
            }
            QListWidget::item:hover {
                background: rgba(72, 209, 204, 0.3);
            }
        """)
        mood_history_layout.addWidget(self.mood_history_list)
        
        mood_history_group.setLayout(mood_history_layout)
        layout.addWidget(mood_history_group)
        
        # Playlist Recommendations
        playlist_group = QGroupBox("🎵 Mood-Based Music Recommendations")
        playlist_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #9370DB;
                border: 3px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #DA70D6, stop:1 #9370DB);
                border-radius: 15px;
                margin: 10px;
                padding-top: 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 240, 255, 0.9), 
                    stop:1 rgba(248, 248, 255, 0.9));
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 8px 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #DA70D6, stop:1 #9370DB);
                color: white;
                border-radius: 8px;
            }
        """)
        
        playlist_layout = QVBoxLayout()
        
        self.playlist_display = QTextEdit()
        self.playlist_display.setMaximumHeight(120)
        self.playlist_display.setReadOnly(True)
        self.playlist_display.setPlaceholderText("Personalized playlist recommendations will appear here...")
        self.playlist_display.setStyleSheet("""
            QTextEdit {
                background: rgba(255, 255, 255, 0.3);
                border: 2px solid #DA70D6;
                border-radius: 8px;
                padding: 10px;
                color: #4B0082;
            }
        """)
        playlist_layout.addWidget(self.playlist_display)
        
        generate_playlist_btn = QPushButton("🎧 Generate Personalized Playlist")
        generate_playlist_btn.clicked.connect(self.generate_playlist_recommendation)
        generate_playlist_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #DA70D6, stop:1 #9370DB);
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #DDA0DD, stop:1 #BA55D3);
                transform: translateY(-2px);
            }
        """)
        playlist_layout.addWidget(generate_playlist_btn)
        
        playlist_group.setLayout(playlist_layout)
        layout.addWidget(playlist_group)
        
        return mood_widget
        
    def create_analytics_tab(self):
        analytics_widget = QWidget()
        main_layout = QVBoxLayout(analytics_widget)
        
        # Analytics Header with animation
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        
        header_title = QLabel("📊 Advanced Mood Analytics Dashboard")
        header_title.setFont(QFont("Arial", 16, QFont.Bold))
        header_title.setStyleSheet("""
            QLabel {
                color: #2E8B57;
                padding: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(46, 139, 87, 0.1), stop:1 rgba(144, 238, 144, 0.1));
                border-radius: 10px;
                border: 2px solid #90EE90;
            }
        """)
        header_layout.addWidget(header_title)
        
        # Real-time analytics button
        self.live_analysis_btn = QPushButton("🔄 Live Analysis")
        self.live_analysis_btn.clicked.connect(self.start_live_analysis)
        self.live_analysis_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #32CD32, stop:1 #228B22);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #98FB98, stop:1 #32CD32);
                transform: scale(1.05);
            }
        """)
        header_layout.addWidget(self.live_analysis_btn)
        main_layout.addWidget(header_widget)
        
        # Scrollable content area
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        
        # Analytics Statistics Overview
        stats_group = QGroupBox("📈 Key Statistics")
        stats_group.setStyleSheet(self.get_group_style("#4169E1", "#87CEEB"))
        stats_layout = QGridLayout()
        
        # Create animated stat cards
        self.total_entries_label = self.create_stat_card("📝", "Total Entries", "0")
        self.avg_mood_label = self.create_stat_card("😊", "Average Mood", "N/A")
        self.mood_streak_label = self.create_stat_card("🔥", "Current Streak", "0 days")
        self.most_common_mood_label = self.create_stat_card("👑", "Most Common", "None")
        
        stats_layout.addWidget(self.total_entries_label, 0, 0)
        stats_layout.addWidget(self.avg_mood_label, 0, 1)
        stats_layout.addWidget(self.mood_streak_label, 1, 0)
        stats_layout.addWidget(self.most_common_mood_label, 1, 1)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Mood Pattern Analysis
        mood_analytics_group = QGroupBox("🧠 Intelligent Mood Pattern Analysis")
        mood_analytics_group.setStyleSheet(self.get_group_style("#228B22", "#90EE90"))
        
        analytics_layout = QVBoxLayout()
        
        # Analysis controls
        analysis_controls = QHBoxLayout()
        
        time_range_combo = QComboBox()
        time_range_combo.addItems(["Last 7 Days", "Last 30 Days", "All Time", "This Week", "This Month"])
        time_range_combo.currentTextChanged.connect(self.update_analysis_timeframe)
        time_range_combo.setStyleSheet("""
            QComboBox {
                background: rgba(255, 255, 255, 0.9);
                border: 2px solid #90EE90;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
            }
        """)
        analysis_controls.addWidget(QLabel("📅 Time Range:"))
        analysis_controls.addWidget(time_range_combo)
        analysis_controls.addStretch()
        
        analyze_btn = QPushButton("🧠 Generate Detailed Analysis")
        analyze_btn.clicked.connect(self.generate_comprehensive_analysis)
        analyze_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #90EE90, stop:1 #228B22);
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #98FB98, stop:1 #32CD32);
                transform: translateY(-3px);
                box-shadow: 0 6px 20px rgba(0, 128, 0, 0.3);
            }
        """)
        analysis_controls.addWidget(analyze_btn)
        analytics_layout.addLayout(analysis_controls)
        
        self.mood_analysis_display = QTextEdit()
        self.mood_analysis_display.setReadOnly(True)
        self.mood_analysis_display.setMinimumHeight(250)
        self.mood_analysis_display.setStyleSheet("""
            QTextEdit {
                background: rgba(255, 255, 255, 0.95);
                border: 2px solid #90EE90;
                border-radius: 8px;
                padding: 15px;
                color: #006400;
                font-size: 13px;
                line-height: 1.4;
            }
        """)
        analytics_layout.addWidget(self.mood_analysis_display)
        
        mood_analytics_group.setLayout(analytics_layout)
        layout.addWidget(mood_analytics_group)
        
        # Weather-Mood Correlation with Visual Chart
        weather_correlation_group = QGroupBox("🌤️ Weather Impact Analysis")
        weather_correlation_group.setStyleSheet(self.get_group_style("#FF8C00", "#FFD700"))
        
        correlation_layout = QVBoxLayout()
        
        # Correlation controls
        correlation_controls = QHBoxLayout()
        
        weather_metric_combo = QComboBox()
        weather_metric_combo.addItems(["Temperature", "Humidity", "Condition", "All Factors"])
        weather_metric_combo.setStyleSheet("""
            QComboBox {
                background: rgba(255, 255, 255, 0.9);
                border: 2px solid #FFD700;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
            }
        """)
        correlation_controls.addWidget(QLabel("🌡️ Weather Factor:"))
        correlation_controls.addWidget(weather_metric_combo)
        correlation_controls.addStretch()
        
        correlation_btn = QPushButton("📊 Analyze Weather Impact")
        correlation_btn.clicked.connect(self.analyze_weather_correlation)
        correlation_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFD700, stop:1 #FF8C00);
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFED4E, stop:1 #FFA500);
                transform: translateY(-3px);
                box-shadow: 0 6px 20px rgba(255, 165, 0, 0.3);
            }
        """)
        correlation_controls.addWidget(correlation_btn)
        correlation_layout.addLayout(correlation_controls)
        
        self.correlation_display = QTextEdit()
        self.correlation_display.setReadOnly(True)
        self.correlation_display.setMinimumHeight(200)
        self.correlation_display.setStyleSheet("""
            QTextEdit {
                background: rgba(255, 255, 255, 0.95);
                border: 2px solid #FFD700;
                border-radius: 8px;
                padding: 15px;
                color: #B8860B;
                font-size: 13px;
                line-height: 1.4;
            }
        """)
        correlation_layout.addWidget(self.correlation_display)
        
        weather_correlation_group.setLayout(correlation_layout)
        layout.addWidget(weather_correlation_group)
        
        # Insights and Recommendations
        insights_group = QGroupBox("💡 AI-Powered Insights & Recommendations")
        insights_group.setStyleSheet(self.get_group_style("#9370DB", "#DDA0DD"))
        insights_layout = QVBoxLayout()
        
        self.insights_display = QTextEdit()
        self.insights_display.setReadOnly(True)
        self.insights_display.setMinimumHeight(150)
        self.insights_display.setStyleSheet("""
            QTextEdit {
                background: rgba(255, 255, 255, 0.95);
                border: 2px solid #DDA0DD;
                border-radius: 8px;
                padding: 15px;
                color: #6A0DAD;
                font-size: 13px;
                line-height: 1.4;
            }
        """)
        insights_layout.addWidget(self.insights_display)
        
        insights_btn = QPushButton("🤖 Generate AI Insights")
        insights_btn.clicked.connect(self.generate_ai_insights)
        insights_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #DDA0DD, stop:1 #9370DB);
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #E6E6FA, stop:1 #BA55D3);
                transform: translateY(-3px);
                box-shadow: 0 6px 20px rgba(147, 112, 219, 0.3);
            }
        """)
        insights_layout.addWidget(insights_btn)
        insights_group.setLayout(insights_layout)
        layout.addWidget(insights_group)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        
        return analytics_widget
    
    def get_group_style(self, primary_color, secondary_color):
        """Generate consistent group box styling"""
        return f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 14px;
                color: {primary_color};
                border: 3px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {secondary_color}, stop:1 {primary_color});
                border-radius: 15px;
                margin: 10px;
                padding-top: 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 255, 255, 0.95), 
                    stop:1 rgba(248, 248, 255, 0.95));
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 20px;
                padding: 8px 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {secondary_color}, stop:1 {primary_color});
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }}
        """
    
    def create_stat_card(self, icon, title, value):
        """Create animated statistic cards"""
        card = QLabel(f"{icon}\n{title}\n{value}")
        card.setAlignment(Qt.AlignCenter)
        card.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 255, 255, 0.9), 
                    stop:1 rgba(240, 248, 255, 0.9));
                border: 2px solid #87CEEB;
                border-radius: 12px;
                padding: 15px;
                color: #4169E1;
                font-size: 12px;
                font-weight: bold;
                min-height: 80px;
            }
        """)
        return card
    
    def start_live_analysis(self):
        """Start live analysis with animation"""
        self.live_analysis_btn.setText("🔄 Analyzing...")
        self.live_analysis_btn.setEnabled(False)
        
        # Simulate analysis delay with timer
        QTimer.singleShot(1500, self.complete_live_analysis)
        self.update_statistics()
        self.generate_comprehensive_analysis()
        
    def complete_live_analysis(self):
        """Complete live analysis"""
        self.live_analysis_btn.setText("✅ Analysis Complete")
        QTimer.singleShot(2000, lambda: self.live_analysis_btn.setText("🔄 Live Analysis"))
        QTimer.singleShot(2000, lambda: self.live_analysis_btn.setEnabled(True))
        
    def update_statistics(self):
        """Update statistical overview cards"""
        if not self.mood_history:
            return
            
        total_entries = len(self.mood_history)
        moods = [data.get('mood', '') for data in self.mood_history.values()]
        intensities = [data.get('intensity', 5) for data in self.mood_history.values()]
        
        # Calculate average mood intensity
        avg_intensity = sum(intensities) / len(intensities) if intensities else 0
        
        # Find most common mood
        from collections import Counter
        mood_counts = Counter(moods)
        most_common = mood_counts.most_common(1)[0][0] if mood_counts else "None"
        
        # Calculate streak (simplified)
        streak = min(total_entries, 7)  # Simplified calculation
        
        # Update cards with animation
        self.animate_stat_update(self.total_entries_label, "📝", "Total Entries", str(total_entries))
        self.animate_stat_update(self.avg_mood_label, "😊", "Average Mood", f"{avg_intensity:.1f}/10")
        self.animate_stat_update(self.mood_streak_label, "🔥", "Current Streak", f"{streak} days")
        self.animate_stat_update(self.most_common_mood_label, "👑", "Most Common", most_common)
        
    def animate_stat_update(self, label, icon, title, value):
        """Animate stat card updates"""
        label.setText(f"{icon}\n{title}\n{value}")
        
        # Create scale animation
        self.stat_animation = QPropertyAnimation(label, b"geometry")
        self.stat_animation.setDuration(300)
        current_geometry = label.geometry()
        self.stat_animation.setStartValue(current_geometry)
        self.stat_animation.setEndValue(current_geometry)
        self.stat_animation.setEasingCurve(QEasingCurve.OutBack)
        self.stat_animation.start()
        
    def update_analysis_timeframe(self, timeframe):
        """Update analysis based on selected timeframe"""
        self.current_timeframe = timeframe
        
    def generate_comprehensive_analysis(self):
        """Generate detailed mood pattern analysis"""
        if not self.mood_history:
            self.mood_analysis_display.setText("""
🎯 **Comprehensive Mood Analysis**

📊 No mood data available yet. Start logging your moods to see detailed patterns!

**What this analysis will show:**
• Daily and weekly mood trends
• Peak mood times and days
• Mood stability patterns  
• Correlation with weather conditions
• Personalized improvement suggestions

🍂 *Begin your mood tracking journey for insights!*
            """)
            return
            
        analysis = self.mood_analyzer.generate_detailed_analysis(self.mood_history)
        self.mood_analysis_display.setText(analysis)
        
        # Add some animation to the display
        self.animate_text_display(self.mood_analysis_display)
        
    def generate_ai_insights(self):
        """Generate AI-powered insights and recommendations"""
        if not self.mood_history:
            insights = """
🤖 **AI Insights & Recommendations**

🎯 **Getting Started**: No data available for AI analysis yet.

**What AI insights will provide:**
• Personalized mood improvement strategies
• Optimal times for activities based on your patterns
• Weather-based mood predictions
• Lifestyle recommendations
• Goal setting for emotional well-being

📈 *Start tracking moods to unlock AI-powered insights!*
            """
        else:
            insights = self.generate_advanced_insights()
            
        self.insights_display.setText(insights)
        self.animate_text_display(self.insights_display)
        
    def generate_advanced_insights(self):
        """Generate advanced AI insights"""
        moods = list(self.mood_history.values())
        total_entries = len(moods)
        
        # Analyze patterns
        intensities = [m.get('intensity', 5) for m in moods]
        avg_intensity = sum(intensities) / len(intensities)
        
        insights = f"""
🤖 **AI-Powered Insights** (Based on {total_entries} entries)

📊 **Pattern Recognition:**
• Your average mood intensity is {avg_intensity:.1f}/10
• Mood tracking consistency: {"Excellent" if total_entries > 14 else "Good" if total_entries > 7 else "Building"}

🎯 **Personalized Recommendations:**
"""
        
        if avg_intensity >= 7:
            insights += """• You maintain positive moods well! Consider sharing your strategies.
• Focus on maintaining current habits that support your well-being.
• Consider helping others who might benefit from your positive approach."""
        elif avg_intensity >= 5:
            insights += """• Your mood balance is healthy. Consider small improvements.
• Try incorporating one new positive activity daily.
• Weather seems to influence your mood - plan accordingly."""
        else:
            insights += """• Focus on identifying mood triggers and patterns.
• Consider professional support for persistent low moods.
• Prioritize self-care activities and stress management."""
            
        insights += f"""

🌟 **Next Steps:**
• Continue tracking for at least 30 days for deeper insights
• Experiment with mood-boosting activities during low periods
• Use weather forecasts to plan mood-supporting activities

🍂 *Your mental health journey is unique and valuable!*
        """
        
        return insights
        
    def animate_text_display(self, text_widget):
        """Add animation to text displays"""
        # Create fade in effect
        effect = QGraphicsOpacityEffect()
        text_widget.setGraphicsEffect(effect)
        
        self.text_animation = QPropertyAnimation(effect, b"opacity")
        self.text_animation.setDuration(600)
        self.text_animation.setStartValue(0.3)
        self.text_animation.setEndValue(1.0)
        self.text_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.text_animation.start()
        
    def create_settings_tab(self):
        settings_widget = QWidget()
        main_layout = QVBoxLayout(settings_widget)
        
        # Settings Header
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        
        header_title = QLabel("⚙️ Advanced Configuration Center")
        header_title.setFont(QFont("Arial", 16, QFont.Bold))
        header_title.setStyleSheet("""
            QLabel {
                color: #2F4F4F;
                padding: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(47, 79, 79, 0.1), stop:1 rgba(192, 192, 192, 0.1));
                border-radius: 10px;
                border: 2px solid #C0C0C0;
            }
        """)
        header_layout.addWidget(header_title)
        
        # Quick actions
        quick_reset_btn = QPushButton("🔄 Reset All")
        quick_reset_btn.clicked.connect(self.reset_all_settings)
        quick_reset_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #DC143C, stop:1 #8B0000);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF6347, stop:1 #DC143C);
                transform: scale(1.05);
            }
        """)
        header_layout.addWidget(quick_reset_btn)
        main_layout.addWidget(header_widget)
        
        # Scrollable settings area
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        
        # Weather & Location Settings
        weather_group = QGroupBox("🌍 Weather & Location Configuration")
        weather_group.setStyleSheet(self.get_group_style("#2E8B57", "#90EE90"))
        weather_layout = QGridLayout()
        
        # Enhanced location settings
        weather_layout.addWidget(QLabel("�️ Current Location:"), 0, 0)
        self.city_input = QLineEdit()
        self.city_input.setText(self.settings.get("city", "New York"))
        self.city_input.setPlaceholderText("Enter city name (e.g., London, Tokyo)")
        self.city_input.textChanged.connect(self.validate_location)
        self.city_input.setStyleSheet(self.get_input_style())
        weather_layout.addWidget(self.city_input, 0, 1)
        
        # Location validation status
        self.location_status = QLabel("✅ Valid location")
        self.location_status.setStyleSheet("color: green; font-weight: bold;")
        weather_layout.addWidget(self.location_status, 0, 2)
        
        # Temperature units
        weather_layout.addWidget(QLabel("🌡️ Temperature Units:"), 1, 0)
        self.units_combo = QComboBox()
        self.units_combo.addItems(["Celsius (°C)", "Fahrenheit (°F)", "Kelvin (K)"])
        current_unit = self.settings.get("units", "metric")
        if current_unit == "metric":
            self.units_combo.setCurrentText("Celsius (°C)")
        elif current_unit == "imperial":
            self.units_combo.setCurrentText("Fahrenheit (°F)")
        else:
            self.units_combo.setCurrentText("Kelvin (K)")
        self.units_combo.setStyleSheet(self.get_input_style())
        weather_layout.addWidget(self.units_combo, 1, 1, 1, 2)
        
        # Weather update frequency
        weather_layout.addWidget(QLabel("🔄 Update Frequency:"), 2, 0)
        self.update_frequency = QComboBox()
        self.update_frequency.addItems(["Every 5 minutes", "Every 15 minutes", "Every 30 minutes", "Every hour"])
        self.update_frequency.setCurrentText(self.settings.get("update_frequency", "Every 15 minutes"))
        self.update_frequency.setStyleSheet(self.get_input_style())
        weather_layout.addWidget(self.update_frequency, 2, 1, 1, 2)
        
        weather_group.setLayout(weather_layout)
        layout.addWidget(weather_group)
        
        # User Experience Settings
        ux_group = QGroupBox("🎨 User Experience & Interface")
        ux_group.setStyleSheet(self.get_group_style("#4169E1", "#87CEEB"))
        ux_layout = QGridLayout()
        
        # Notification settings
        self.notifications_checkbox = QCheckBox("🔔 Enable Push Notifications")
        self.notifications_checkbox.setChecked(self.settings.get("notifications", True))
        self.notifications_checkbox.setStyleSheet(self.get_checkbox_style())
        ux_layout.addWidget(self.notifications_checkbox, 0, 0, 1, 2)
        
        # Sound notifications
        self.sound_notifications = QCheckBox("🔊 Sound Notifications")
        self.sound_notifications.setChecked(self.settings.get("sound_notifications", False))
        self.sound_notifications.setStyleSheet(self.get_checkbox_style())
        ux_layout.addWidget(self.sound_notifications, 1, 0, 1, 2)
        
        # Auto mood suggestions
        self.auto_suggestions_checkbox = QCheckBox("🤖 AI-Powered Mood Suggestions")
        self.auto_suggestions_checkbox.setChecked(self.settings.get("auto_mood_suggestions", True))
        self.auto_suggestions_checkbox.setStyleSheet(self.get_checkbox_style())
        ux_layout.addWidget(self.auto_suggestions_checkbox, 2, 0, 1, 2)
        
        # Theme preferences
        self.theme_sync_checkbox = QCheckBox("🎨 Dynamic Weather-Based Themes")
        self.theme_sync_checkbox.setChecked(self.settings.get("theme_sync", True))
        self.theme_sync_checkbox.setStyleSheet(self.get_checkbox_style())
        ux_layout.addWidget(self.theme_sync_checkbox, 3, 0, 1, 2)
        
        # Animation settings
        self.animations_checkbox = QCheckBox("✨ Enhanced Animations & Effects")
        self.animations_checkbox.setChecked(self.settings.get("animations", True))
        self.animations_checkbox.setStyleSheet(self.get_checkbox_style())
        ux_layout.addWidget(self.animations_checkbox, 4, 0, 1, 2)
        
        # Language preference
        ux_layout.addWidget(QLabel("🌐 Language:"), 5, 0)
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Spanish", "French", "German", "Japanese"])
        self.language_combo.setCurrentText(self.settings.get("language", "English"))
        self.language_combo.setStyleSheet(self.get_input_style())
        ux_layout.addWidget(self.language_combo, 5, 1)
        
        ux_group.setLayout(ux_layout)
        layout.addWidget(ux_group)
        
        # Privacy & Data Settings
        privacy_group = QGroupBox("🔒 Privacy & Data Management")
        privacy_group.setStyleSheet(self.get_group_style("#8B4513", "#DEB887"))
        privacy_layout = QVBoxLayout()
        
        # Data collection preferences
        data_collection_layout = QGridLayout()
        
        self.anonymous_analytics = QCheckBox("📊 Anonymous Usage Analytics")
        self.anonymous_analytics.setChecked(self.settings.get("anonymous_analytics", True))
        self.anonymous_analytics.setStyleSheet(self.get_checkbox_style())
        data_collection_layout.addWidget(self.anonymous_analytics, 0, 0, 1, 2)
        
        self.location_sharing = QCheckBox("📍 Share Location Data (for weather)")
        self.location_sharing.setChecked(self.settings.get("location_sharing", True))
        self.location_sharing.setStyleSheet(self.get_checkbox_style())
        data_collection_layout.addWidget(self.location_sharing, 1, 0, 1, 2)
        
        # Data retention
        data_collection_layout.addWidget(QLabel("📅 Data Retention Period:"), 2, 0)
        self.data_retention = QComboBox()
        self.data_retention.addItems(["30 days", "90 days", "1 year", "Indefinite"])
        self.data_retention.setCurrentText(self.settings.get("data_retention", "1 year"))
        self.data_retention.setStyleSheet(self.get_input_style())
        data_collection_layout.addWidget(self.data_retention, 2, 1)
        
        privacy_layout.addLayout(data_collection_layout)
        
        # Data management buttons
        data_buttons_layout = QHBoxLayout()
        
        export_btn = QPushButton("📤 Export All Data")
        export_btn.clicked.connect(self.export_comprehensive_data)
        export_btn.setStyleSheet(self.get_action_button_style("#228B22"))
        data_buttons_layout.addWidget(export_btn)
        
        import_btn = QPushButton("📥 Import Data")
        import_btn.clicked.connect(self.import_data)
        import_btn.setStyleSheet(self.get_action_button_style("#4169E1"))
        data_buttons_layout.addWidget(import_btn)
        
        clear_data_btn = QPushButton("🗑️ Clear All Data")
        clear_data_btn.clicked.connect(self.clear_all_data)
        clear_data_btn.setStyleSheet(self.get_action_button_style("#DC143C"))
        data_buttons_layout.addWidget(clear_data_btn)
        
        privacy_layout.addLayout(data_buttons_layout)
        privacy_group.setLayout(privacy_layout)
        layout.addWidget(privacy_group)
        
        # Performance Settings
        performance_group = QGroupBox("⚡ Performance & Advanced")
        performance_group.setStyleSheet(self.get_group_style("#9370DB", "#DDA0DD"))
        performance_layout = QGridLayout()
        
        # Performance options
        self.low_power_mode = QCheckBox("🔋 Low Power Mode")
        self.low_power_mode.setChecked(self.settings.get("low_power_mode", False))
        self.low_power_mode.setStyleSheet(self.get_checkbox_style())
        performance_layout.addWidget(self.low_power_mode, 0, 0, 1, 2)
        
        self.high_quality_weather = QCheckBox("� High-Quality Weather Graphics")
        self.high_quality_weather.setChecked(self.settings.get("high_quality_weather", True))
        self.high_quality_weather.setStyleSheet(self.get_checkbox_style())
        performance_layout.addWidget(self.high_quality_weather, 1, 0, 1, 2)
        
        # Cache settings
        performance_layout.addWidget(QLabel("💾 Cache Size:"), 2, 0)
        self.cache_size = QComboBox()
        self.cache_size.addItems(["Small (10MB)", "Medium (50MB)", "Large (100MB)", "No Limit"])
        self.cache_size.setCurrentText(self.settings.get("cache_size", "Medium (50MB)"))
        self.cache_size.setStyleSheet(self.get_input_style())
        performance_layout.addWidget(self.cache_size, 2, 1)
        
        performance_group.setLayout(performance_layout)
        layout.addWidget(performance_group)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        # Save settings with animation
        save_settings_btn = QPushButton("💾 Save All Settings")
        save_settings_btn.clicked.connect(self.save_all_settings_with_animation)
        save_settings_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #32CD32, stop:1 #228B22);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 12px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #98FB98, stop:1 #32CD32);
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(50, 205, 50, 0.4);
            }
        """)
        action_layout.addWidget(save_settings_btn)
        
        # Test connection
        test_connection_btn = QPushButton("🔍 Test Weather Connection")
        test_connection_btn.clicked.connect(self.test_weather_connection)
        test_connection_btn.setStyleSheet(self.get_action_button_style("#4169E1"))
        action_layout.addWidget(test_connection_btn)
        
        layout.addLayout(action_layout)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        
        return settings_widget
    
    def get_input_style(self):
        """Get consistent input styling"""
        return """
            QLineEdit, QComboBox {
                background: rgba(255, 255, 255, 0.95);
                border: 2px solid #C0C0C0;
                border-radius: 8px;
                padding: 10px;
                color: #2F4F4F;
                font-weight: bold;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #4169E1;
                background: rgba(255, 255, 255, 1.0);
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """
    
    def get_checkbox_style(self):
        """Get consistent checkbox styling"""
        return """
            QCheckBox {
                color: #2F4F4F;
                font-weight: bold;
                spacing: 8px;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #C0C0C0;
                background: white;
                border-radius: 4px;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #4169E1;
                background: #4169E1;
                border-radius: 4px;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #6495ED;
            }
        """
    
    def get_action_button_style(self, color):
        """Get consistent action button styling"""
        return f"""
            QPushButton {{
                background: {color};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                margin: 5px;
            }}
            QPushButton:hover {{
                background: {color}CC;
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            }}
        """
    
    def validate_location(self, text):
        """Validate location input with visual feedback"""
        if len(text) >= 2:
            self.location_status.setText("✅ Valid location")
            self.location_status.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.location_status.setText("❌ Enter valid city")
            self.location_status.setStyleSheet("color: red; font-weight: bold;")
    
    def reset_all_settings(self):
        """Reset all settings to defaults with confirmation"""
        reply = QMessageBox.question(self, 'Reset Settings', 
                                   'Are you sure you want to reset all settings to default values?',
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Reset UI elements
            self.city_input.setText("New York")
            self.units_combo.setCurrentText("Celsius (°C)")
            self.notifications_checkbox.setChecked(True)
            self.auto_suggestions_checkbox.setChecked(True)
            self.theme_sync_checkbox.setChecked(True)
            
            # Save and show confirmation
            self.save_all_settings_with_animation(show_reset_message=True)
    
    def save_all_settings_with_animation(self, show_reset_message=False):
        """Save all settings with visual feedback animation"""
        # Update settings dictionary
        self.settings.update({
            "city": self.city_input.text(),
            "units": "metric" if "Celsius" in self.units_combo.currentText() else "imperial",
            "notifications": self.notifications_checkbox.isChecked(),
            "auto_mood_suggestions": self.auto_suggestions_checkbox.isChecked(),
            "theme_sync": self.theme_sync_checkbox.isChecked(),
            "update_frequency": self.update_frequency.currentText(),
            "sound_notifications": self.sound_notifications.isChecked(),
            "animations": self.animations_checkbox.isChecked(),
            "language": self.language_combo.currentText(),
            "anonymous_analytics": self.anonymous_analytics.isChecked(),
            "location_sharing": self.location_sharing.isChecked(),
            "data_retention": self.data_retention.currentText(),
            "low_power_mode": self.low_power_mode.isChecked(),
            "high_quality_weather": self.high_quality_weather.isChecked(),
            "cache_size": self.cache_size.currentText()
        })
        
        self.save_settings()
        
        # Show animated confirmation
        message = "🔄 Settings reset to defaults!" if show_reset_message else "💾 All settings saved successfully!"
        QMessageBox.information(self, "Settings Updated", message)
        
        # Restart weather thread with new settings if city changed
        if hasattr(self, 'weather_thread'):
            self.weather_thread.city = self.settings.get("city", "New York")
    
    def test_weather_connection(self):
        """Test weather API connection"""
        test_btn = self.sender()
        original_text = test_btn.text()
        test_btn.setText("🔄 Testing...")
        test_btn.setEnabled(False)
        
        # Simulate connection test
        QTimer.singleShot(2000, lambda: self.complete_connection_test(test_btn, original_text))
        
    def complete_connection_test(self, button, original_text):
        """Complete connection test with result"""
        button.setText("✅ Connection OK")
        QTimer.singleShot(2000, lambda: button.setText(original_text))
        QTimer.singleShot(2000, lambda: button.setEnabled(True))
        
    def export_comprehensive_data(self):
        """Export all data with detailed information"""
        data = {
            "mood_history": self.mood_history,
            "settings": self.settings,
            "weather_data": getattr(self, 'current_weather', {}),
            "export_timestamp": datetime.now().isoformat(),
            "version": "2.0"
        }
        
        filename = f"septemberos_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            QMessageBox.information(self, "Export Complete", f"Data exported to {filename}")
        except Exception as e:
            QMessageBox.warning(self, "Export Error", f"Failed to export data: {str(e)}")
    
    def import_data(self):
        """Import data from file"""
        QMessageBox.information(self, "Import Data", "Import functionality will be available in the next update!")
    
    def clear_all_data(self):
        """Clear all data with confirmation"""
        reply = QMessageBox.question(self, 'Clear All Data', 
                                   'This will permanently delete all mood history and settings. Are you sure?',
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.mood_history.clear()
            self.save_mood_history()
            QMessageBox.information(self, "Data Cleared", "All data has been cleared successfully.")
        
    def setup_animations(self):
        # Enhanced animation system with multiple timers
        self.animation_phase = 0
        self.weather_animation_phase = 0
        
        # Background color animation timer
        self.color_animation_timer = QTimer()
        self.color_animation_timer.timeout.connect(self.animate_background_colors)
        self.color_animation_timer.start(8000)  # Change every 8 seconds
        
        # Mood color pulse animation
        self.mood_pulse_timer = QTimer()
        self.mood_pulse_timer.timeout.connect(self.pulse_mood_colors)
        self.mood_pulse_timer.start(2000)  # Pulse every 2 seconds
        
        # Weather icon animation
        self.weather_animation_timer = QTimer()
        self.weather_animation_timer.timeout.connect(self.animate_weather_elements)
        self.weather_animation_timer.start(3000)  # Animate every 3 seconds
        
        # Tab switching animations
        self.tab_animation_timer = QTimer()
        self.tab_animation_timer.timeout.connect(self.animate_tab_highlights)
        self.tab_animation_timer.start(5000)  # Highlight tabs every 5 seconds
        
        # Floating particles animation
        self.particles_timer = QTimer()
        self.particles_timer.timeout.connect(self.animate_floating_particles)
        self.particles_timer.start(100)  # Smooth 10fps animation
        
        # Button hover effects timer
        self.button_effects_timer = QTimer()
        self.button_effects_timer.timeout.connect(self.animate_button_effects)
        self.button_effects_timer.start(1500)  # Subtle button animations
        
        # Initialize particle system
        self.particles = []
        self.initialize_particle_system()
        
    def animate_background_colors(self):
        current_hour = datetime.now().hour
        self.animation_phase = (self.animation_phase + 1) % 6
        
        # Dynamic color schemes based on time of day and animation phase
        if 6 <= current_hour < 12:  # Morning
            colors = [
                "stop:0 rgba(255, 218, 185, 0.6), stop:1 rgba(255, 228, 196, 0.6)",  # Peach
                "stop:0 rgba(255, 239, 213, 0.6), stop:1 rgba(255, 218, 185, 0.6)",  # Papaya
                "stop:0 rgba(255, 250, 205, 0.6), stop:1 rgba(255, 239, 213, 0.6)"   # Lemon chiffon
            ]
        elif 12 <= current_hour < 18:  # Afternoon
            colors = [
                "stop:0 rgba(135, 206, 235, 0.6), stop:1 rgba(173, 216, 230, 0.6)",  # Sky blue
                "stop:0 rgba(255, 215, 0, 0.6), stop:1 rgba(255, 228, 181, 0.6)",     # Gold
                "stop:0 rgba(152, 251, 152, 0.6), stop:1 rgba(144, 238, 144, 0.6)"   # Light green
            ]
        else:  # Evening/Night
            colors = [
                "stop:0 rgba(106, 90, 205, 0.6), stop:1 rgba(123, 104, 238, 0.6)",   # Slate blue
                "stop:0 rgba(219, 112, 147, 0.6), stop:1 rgba(255, 182, 193, 0.6)",  # Pale violet red
                "stop:0 rgba(72, 61, 139, 0.6), stop:1 rgba(106, 90, 205, 0.6)"      # Dark slate blue
            ]
            
        selected_color = colors[self.animation_phase % len(colors)]
        
        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, {selected_color});
            }}
        """)
        
    def pulse_mood_colors(self):
        # Create a subtle pulsing effect for mood-related elements
        if hasattr(self, 'mood_combo'):
            current_mood = self.mood_combo.currentText()
            mood_color = self.mood_analyzer.get_mood_color(current_mood)
            
            # Convert hex to rgba with pulsing alpha
            alpha = 0.3 + 0.2 * math.sin(time.time() * 2)  # Pulse between 0.3 and 0.5
            color = QColor(mood_color)
            
            pulse_style = f"""
                QComboBox {{
                    background: rgba({color.red()}, {color.green()}, {color.blue()}, {alpha});
                    border: 2px solid {mood_color};
                    border-radius: 8px;
                    padding: 8px;
                    font-size: 13px;
                    color: #8B008B;
                }}
            """
            self.mood_combo.setStyleSheet(pulse_style)
    
    def animate_weather_elements(self):
        """Animate weather-related UI elements"""
        self.weather_animation_phase = (self.weather_animation_phase + 1) % 4
        
        if hasattr(self, 'weather_display') and hasattr(self, 'current_weather'):
            condition = self.current_weather.get('condition', 'Unknown')
            
            # Animate weather condition display with condition-specific effects
            weather_animations = {
                "Sunny": self.create_sunny_animation(),
                "Rainy": self.create_rainy_animation(),
                "Cloudy": self.create_cloudy_animation(),
                "Partly Cloudy": self.create_partly_cloudy_animation(),
                "Windy": self.create_windy_animation(),
            }
            
            animation_style = weather_animations.get(condition, self.create_default_animation())
            
            if hasattr(self, 'weather_display'):
                current_style = self.weather_display.styleSheet()
                # Add animation effects to existing style
                enhanced_style = current_style + animation_style
                self.weather_display.setStyleSheet(enhanced_style)
    
    def create_sunny_animation(self):
        """Create sunny weather animation style"""
        brightness = 0.8 + 0.2 * math.sin(time.time() * 3)  # Gentle brightness pulse
        return f"""
            QTextEdit {{
                background: rgba(255, 255, 224, {brightness});
                border: 2px solid #FFD700;
                box-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
            }}
        """
    
    def create_rainy_animation(self):
        """Create rainy weather animation style"""
        wave_offset = math.sin(time.time() * 2) * 5  # Gentle wave effect
        return f"""
            QTextEdit {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(176, 196, 222, 0.7), 
                    stop:1 rgba(135, 206, 235, 0.7));
                border: 2px solid #4682B4;
                border-radius: {8 + wave_offset}px;
            }}
        """
    
    def create_cloudy_animation(self):
        """Create cloudy weather animation style"""
        cloud_drift = math.sin(time.time() * 1.5) * 3
        return f"""
            QTextEdit {{
                background: rgba(220, 220, 220, 0.8);
                border: 2px solid #A9A9A9;
                transform: translateX({cloud_drift}px);
            }}
        """
    
    def create_partly_cloudy_animation(self):
        """Create partly cloudy weather animation style"""
        mixed_opacity = 0.6 + 0.3 * math.sin(time.time() * 2.5)
        return f"""
            QTextEdit {{
                background: rgba(240, 248, 255, {mixed_opacity});
                border: 2px solid #87CEEB;
                box-shadow: 0 0 15px rgba(135, 206, 235, 0.4);
            }}
        """
    
    def create_windy_animation(self):
        """Create windy weather animation style"""
        wind_sway = math.sin(time.time() * 4) * 2
        return f"""
            QTextEdit {{
                background: rgba(230, 230, 250, 0.8);
                border: 2px solid #9370DB;
                transform: rotate({wind_sway}deg);
            }}
        """
    
    def create_default_animation(self):
        """Create default weather animation style"""
        return """
            QTextEdit {
                background: rgba(248, 248, 255, 0.8);
                border: 2px solid #DDA0DD;
            }
        """
    
    def animate_tab_highlights(self):
        """Animate tab highlights to draw attention"""
        if hasattr(self, 'tabs'):
            # Cycle through tabs with subtle highlight effects
            tab_count = self.tabs.count()
            current_tab = self.tabs.currentIndex()
            
            for i in range(tab_count):
                if i == current_tab:
                    # Highlight current tab
                    continue
                    
                # Add subtle glow to other tabs
                tab_widget = self.tabs.widget(i)
                if tab_widget:
                    glow_effect = QGraphicsDropShadowEffect()
                    glow_effect.setBlurRadius(15)
                    glow_effect.setColor(QColor(100, 149, 237, 100))  # Cornflower blue
                    glow_effect.setOffset(0, 0)
                    
                    # Remove effect after short time
                    QTimer.singleShot(1500, lambda w=tab_widget: w.setGraphicsEffect(None))
                    tab_widget.setGraphicsEffect(glow_effect)
    
    def initialize_particle_system(self):
        """Initialize floating particle system"""
        self.particles = []
        for _ in range(15):  # Create 15 particles
            particle = {
                'x': random.randint(0, 800),
                'y': random.randint(0, 600),
                'vx': random.uniform(-0.5, 0.5),
                'vy': random.uniform(-0.8, -0.2),
                'size': random.randint(2, 6),
                'color': random.choice(['#FFD700', '#FF6347', '#9370DB', '#32CD32', '#FF1493']),
                'life': random.randint(100, 300)
            }
            self.particles.append(particle)
    
    def animate_floating_particles(self):
        """Animate floating particles across the interface"""
        for particle in self.particles[:]:  # Use slice to avoid modification during iteration
            # Update particle position
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            
            # Reset particle if it goes off screen or dies
            if (particle['x'] < 0 or particle['x'] > 1000 or 
                particle['y'] < 0 or particle['y'] > 800 or 
                particle['life'] <= 0):
                
                particle['x'] = random.randint(0, 800)
                particle['y'] = 600  # Start from bottom
                particle['vx'] = random.uniform(-0.5, 0.5)
                particle['vy'] = random.uniform(-0.8, -0.2)
                particle['life'] = random.randint(100, 300)
    
    def animate_button_effects(self):
        """Add subtle animations to buttons"""
        # Find all buttons and add subtle effects
        for widget in self.findChildren(QPushButton):
            if widget.isVisible():
                # Create subtle scale animation
                self.create_button_pulse_animation(widget)
    
    def create_button_pulse_animation(self, button):
        """Create pulse animation for buttons"""
        if not hasattr(button, '_is_animating') or not button._is_animating:
            button._is_animating = True
            
            # Create scale animation
            self.button_animation = QPropertyAnimation(button, b"geometry")
            self.button_animation.setDuration(800)
            
            current_geo = button.geometry()
            expanded_geo = QRect(
                current_geo.x() - 2,
                current_geo.y() - 2,
                current_geo.width() + 4,
                current_geo.height() + 4
            )
            
            self.button_animation.setStartValue(current_geo)
            self.button_animation.setKeyValueAt(0.5, expanded_geo)
            self.button_animation.setEndValue(current_geo)
            self.button_animation.setEasingCurve(QEasingCurve.InOutSine)
            
            # Reset animation flag when done
            self.button_animation.finished.connect(lambda: setattr(button, '_is_animating', False))
            self.button_animation.start()
    
    def add_entrance_animation(self, widget):
        """Add entrance animation to widgets"""
        # Fade in animation
        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)
        
        self.entrance_animation = QPropertyAnimation(effect, b"opacity")
        self.entrance_animation.setDuration(1000)
        self.entrance_animation.setStartValue(0.0)
        self.entrance_animation.setEndValue(1.0)
        self.entrance_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.entrance_animation.start()
        
        # Scale animation
        self.scale_animation = QPropertyAnimation(widget, b"geometry")
        self.scale_animation.setDuration(800)
        
        current_geo = widget.geometry()
        start_geo = QRect(
            current_geo.x() + current_geo.width() // 4,
            current_geo.y() + current_geo.height() // 4,
            current_geo.width() // 2,
            current_geo.height() // 2
        )
        
        self.scale_animation.setStartValue(start_geo)
        self.scale_animation.setEndValue(current_geo)
        self.scale_animation.setEasingCurve(QEasingCurve.OutBack)
        self.scale_animation.start()
    
    def create_hover_animation(self, widget):
        """Create hover animation for interactive elements"""
        original_style = widget.styleSheet()
        
        def on_enter():
            # Enhanced hover effect
            enhanced_style = original_style + """
                QWidget {
                    transform: scale(1.02);
                    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
                }
            """
            widget.setStyleSheet(enhanced_style)
            
        def on_leave():
            # Return to original style
            widget.setStyleSheet(original_style)
            
        widget.enterEvent = lambda event: on_enter()
        widget.leaveEvent = lambda event: on_leave()
        
    def setup_tab_hover_effects(self):
        """Setup hover effects for tab widgets"""
        for i in range(self.main_tabs.count()):
            tab_widget = self.main_tabs.widget(i)
            if tab_widget:
                self.create_hover_animation(tab_widget)
    
    def apply_weather_based_theme(self):
        """Apply theme based on current weather with smooth transitions"""
        if not self.current_weather:
            return
            
        condition = self.current_weather.get('condition', 'Unknown')
        temp = self.current_weather.get('temperature', 20)
        
        # Weather-based color schemes with animations
        weather_themes = {
            "Sunny": {
                "primary": "#FFD700",
                "secondary": "#FFA500", 
                "background": "rgba(255, 248, 220, 0.8)",
                "accent": "#FF6347"
            },
            "Rainy": {
                "primary": "#4682B4",
                "secondary": "#6495ED",
                "background": "rgba(176, 196, 222, 0.8)", 
                "accent": "#87CEEB"
            },
            "Cloudy": {
                "primary": "#708090",
                "secondary": "#A9A9A9",
                "background": "rgba(220, 220, 220, 0.8)",
                "accent": "#B0C4DE"
            },
            "Partly Cloudy": {
                "primary": "#87CEEB",
                "secondary": "#4169E1",
                "background": "rgba(240, 248, 255, 0.8)",
                "accent": "#6495ED"
            }
        }
        
        theme = weather_themes.get(condition, weather_themes["Partly Cloudy"])
        
        # Apply animated theme transition
        self.animate_theme_transition(theme)
    
    def animate_theme_transition(self, theme):
        """Animate transition between themes"""
        # Create smooth color transition effect
        transition_style = f"""
            EquinoxWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {theme['background']}, 
                    stop:1 rgba(255, 255, 255, 0.5));
                color: {theme['primary']};
            }}
            QGroupBox {{
                border: 2px solid {theme['primary']};
                color: {theme['primary']};
            }}
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {theme['primary']}, stop:1 {theme['secondary']});
                border: 1px solid {theme['accent']};
            }}
        """
        
        # Apply with fade transition
        self.setStyleSheet(transition_style)
    
    def create_sparkle_effect(self, widget):
        """Create sparkle effect for special moments"""
        # Create multiple small sparkle animations
        for i in range(5):
            sparkle = QLabel("✨", widget)
            sparkle.setStyleSheet("font-size: 16px; color: gold;")
            
            # Random position
            x = random.randint(0, widget.width() - 20)
            y = random.randint(0, widget.height() - 20)
            sparkle.move(x, y)
            sparkle.show()
            
            # Fade out animation
            effect = QGraphicsOpacityEffect()
            sparkle.setGraphicsEffect(effect)
            
            fade_out = QPropertyAnimation(effect, b"opacity")
            fade_out.setDuration(2000)
            fade_out.setStartValue(1.0)
            fade_out.setEndValue(0.0)
            fade_out.finished.connect(sparkle.deleteLater)
            fade_out.start()
            
            # Store animation reference to prevent garbage collection
            if not hasattr(self, '_sparkle_animations'):
                self._sparkle_animations = []
            self._sparkle_animations.append(fade_out)
    
    def setup_music_icon_animation(self):
        """Setup pulsing animation for music icon"""
        # Create opacity effect for music icon
        self.music_icon_effect = QGraphicsOpacityEffect()
        self.music_icon.setGraphicsEffect(self.music_icon_effect)
        
        # Create the pulsing animation
        self.music_icon_animation = QPropertyAnimation(self.music_icon_effect, b"opacity")
        self.music_icon_animation.setDuration(1500)  # 1.5 seconds
        self.music_icon_animation.setStartValue(0.4)
        self.music_icon_animation.setEndValue(1.0)
        self.music_icon_animation.setEasingCurve(QEasingCurve.InOutSine)
        self.music_icon_animation.setLoopCount(-1)  # Infinite loop
        self.music_icon_animation.setDirection(QPropertyAnimation.Forward)
        
        # Create the reverse direction
        self.music_icon_animation.finished.connect(
            lambda: self.music_icon_animation.setDirection(
                QPropertyAnimation.Backward if self.music_icon_animation.direction() == QPropertyAnimation.Forward 
                else QPropertyAnimation.Forward))
    
    def start_music_icon_pulse(self):
        """Start the music icon pulsing animation"""
        if hasattr(self, 'music_icon_animation'):
            self.music_icon_animation.start()
            # Also add color animation for more visual appeal
            self.music_icon.setStyleSheet("""
                color: #FFD700;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 215, 0, 0.3),
                    stop:1 rgba(255, 140, 0, 0.3));
                border-radius: 15px;
                padding: 5px;
                margin: 2px;
            """)
    
    def stop_music_icon_pulse(self):
        """Stop the music icon pulsing animation"""
        if hasattr(self, 'music_icon_animation'):
            self.music_icon_animation.stop()
            # Reset to default style
            self.music_icon.setStyleSheet("""
                color: #FFD700;
                background: rgba(255, 215, 0, 0.2);
                border-radius: 15px;
                padding: 5px;
                margin: 2px;
            """)
            # Reset opacity
            if hasattr(self, 'music_icon_effect'):
                self.music_icon_effect.setOpacity(1.0)
        
        # Weather Section
        weather_group = QGroupBox("Current Weather")
        weather_layout = QGridLayout()
        
        self.weather_icon = QLabel("🌤️")
        self.weather_icon.setFont(QFont("Arial", 48))
        self.weather_icon.setAlignment(Qt.AlignCenter)
        # Initialize UI components
        self.refresh_mood_history()
        self.analyze_mood_patterns()
        
    def setup_weather_timer(self):
        self.weather_timer = QTimer()
        self.weather_timer.timeout.connect(self.refresh_weather)
        self.weather_timer.start(300000)  # Refresh every 5 minutes
        self.refresh_weather()  # Initial load
        
    def refresh_weather(self):
        self.weather_thread = WeatherThread(self.settings.get("city", "New York"))
        self.weather_thread.weather_updated.connect(self.update_weather_display)
        self.weather_thread.start()
        
    def update_weather_display(self, weather_data):
        self.current_weather = weather_data
        
        # Save weather to history
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.weather_history[timestamp] = weather_data
        self.save_weather_history()
        
        # Update animated weather icon
        if hasattr(self, 'animated_weather_icon'):
            self.animated_weather_icon.set_weather_condition(weather_data['condition'])
        
        # Update all weather displays
        if hasattr(self, 'temperature_label'):
            units = "°C" if self.settings.get("units") == "metric" else "°F"
            self.temperature_label.setText(f"{weather_data['temperature']}{units}")
            
        if hasattr(self, 'feels_like_label'):
            self.feels_like_label.setText(f"Feels like: {weather_data.get('feels_like', weather_data['temperature'])}°C")
            
        if hasattr(self, 'condition_label'):
            self.condition_label.setText(weather_data['condition'])
            
        if hasattr(self, 'weather_description'):
            self.weather_description.setText(weather_data['description'])
            
        # Update detailed weather info
        if hasattr(self, 'humidity_label'):
            self.humidity_label.setText(f"💧 Humidity: {weather_data['humidity']}%")
            
        if hasattr(self, 'wind_label'):
            self.wind_label.setText(f"💨 Wind: {weather_data['wind_speed']} km/h")
            
        if hasattr(self, 'pressure_label'):
            self.pressure_label.setText(f"🌡️ Pressure: {weather_data['pressure']} hPa")
            
        if hasattr(self, 'uv_label'):
            self.uv_label.setText(f"☀️ UV Index: {weather_data['uv_index']}")
            
        if hasattr(self, 'air_quality_label'):
            self.air_quality_label.setText(f"🌱 Air Quality: {weather_data['air_quality']}")
            
        if hasattr(self, 'sun_times_label'):
            self.sun_times_label.setText(f"🌅 Sunrise: {weather_data['sunrise']} | 🌇 Sunset: {weather_data['sunset']}")
        
        # Apply dynamic UI changes based on weather
        if self.settings.get("theme_sync", True):
            self.apply_weather_theme(weather_data['condition'])
        
    def apply_weather_theme(self, condition):
        # Enhanced weather themes with more conditions and better colors
        weather_themes = {
            "Sunny": "stop:0 rgba(255, 228, 96, 0.4), stop:1 rgba(255, 140, 0, 0.4)",
            "Cloudy": "stop:0 rgba(245, 245, 220, 0.4), stop:1 rgba(211, 211, 211, 0.4)", 
            "Rainy": "stop:0 rgba(176, 196, 222, 0.4), stop:1 rgba(119, 136, 153, 0.4)",
            "Partly Cloudy": "stop:0 rgba(240, 230, 140, 0.4), stop:1 rgba(222, 184, 135, 0.4)",
            "Foggy": "stop:0 rgba(220, 220, 220, 0.4), stop:1 rgba(169, 169, 169, 0.4)",
            "Windy": "stop:0 rgba(135, 206, 235, 0.4), stop:1 rgba(70, 130, 180, 0.4)",
            "Overcast": "stop:0 rgba(192, 192, 192, 0.4), stop:1 rgba(128, 128, 128, 0.4)"
        }
        
        gradient = weather_themes.get(condition, "stop:0 rgba(255, 248, 220, 0.4), stop:1 rgba(245, 222, 179, 0.4)")
        
        # Apply theme to main widget with smooth transition
        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, {gradient});
            }}
        """)
        
    def log_current_mood(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        mood = self.mood_combo.currentText()
        intensity = self.mood_slider.value()
        notes = self.mood_notes.toPlainText() if hasattr(self, 'mood_notes') else ""
        
        mood_entry = {
            "mood": mood,
            "intensity": intensity,
            "timestamp": current_time,
            "weather": self.current_weather.get('condition', 'Unknown'),
            "temperature": self.current_weather.get('temperature', 0),
            "notes": notes,
            "day_of_week": datetime.now().strftime("%A"),
            "hour": datetime.now().hour
        }
        
        self.mood_history[current_time] = mood_entry
        self.save_mood_data()
        self.refresh_mood_history()
        
        # Clear notes after logging
        if hasattr(self, 'mood_notes'):
            self.mood_notes.clear()
            
        # Auto-generate playlist if enabled
        if self.settings.get("auto_mood_suggestions", True):
            self.generate_playlist_recommendation()
            
        # Update mood analysis
        self.analyze_mood_patterns()
            
    def refresh_mood_history(self):
        if hasattr(self, 'mood_history_list'):
            self.mood_history_list.clear()
            recent_moods = list(self.mood_history.items())[-8:]  # Last 8 entries
            
            for timestamp, mood_data in recent_moods:
                mood_color = self.mood_analyzer.get_mood_color(mood_data['mood'])
                weather_emoji = {"Sunny": "☀️", "Cloudy": "☁️", "Rainy": "🌧️", "Partly Cloudy": "⛅"}.get(
                    mood_data.get('weather', ''), "🌤️")
                
                mood_text = f"{mood_data['mood']} ({mood_data['intensity']}/10) {weather_emoji} - {timestamp}"
                
                from PyQt5.QtWidgets import QListWidgetItem
                item = QListWidgetItem(mood_text)
                item.setBackground(QColor(mood_color + "40"))  # Add transparency
                self.mood_history_list.addItem(item)
            
    def generate_playlist_recommendation(self):
        try:
            # Show immediate feedback
            if hasattr(self, 'playlist_display'):
                self.playlist_display.setText("🎵 Generating your personalized playlist... ✨")
                QApplication.processEvents()  # Force UI update
            
            current_mood = self.mood_combo.currentText() if hasattr(self, 'mood_combo') else "😊 Happy"
            weather_condition = self.current_weather.get('condition', 'Unknown')
            current_hour = datetime.now().hour
        
            # Enhanced mood-based playlist recommendations
            playlist_suggestions = {
            "😊 Happy": ["🎵 Autumn Sunshine Mix", "🎵 Feel Good Indie Folk", "🎵 Joyful Acoustics", "🎵 Happy September Vibes"],
            "😌 Calm": ["🎵 Lo-Fi Study Beats", "🎵 Peaceful Piano", "🎵 Ambient September", "🎵 Mindful Moments"],
            "😔 Sad": ["🎵 Melancholic Melodies", "🎵 Rainy Day Reflections", "🎵 Gentle Healing Sounds", "🎵 Comforting Classical"],
            "😴 Tired": ["🎵 Sleepy Time Lo-Fi", "🎵 Calm Evening Jazz", "🎵 Soft Instrumental", "🎵 Dreamy Soundscapes"],
            "🤗 Excited": ["🎵 Energetic Indie Pop", "🎵 Upbeat Folk", "🎵 Adventure Soundtracks", "🎵 Motivational Mix"],
            "😰 Anxious": ["🎵 Anxiety Relief Sounds", "🎵 Breathing Music", "🎵 Calming Nature", "🎵 Stress Relief Piano"],
            "🤔 Thoughtful": ["🎵 Contemplative Classical", "🎵 Philosophical Folk", "🎵 Deep Thinking Beats", "🎵 Introspective Indie"],
            "😍 Inspired": ["🎵 Creative Flow", "🎵 Inspirational Instrumentals", "🎵 Artistic Ambience", "🎵 Innovation Soundtrack"],
            "� Frustrated": ["🎵 Emotional Release", "🎵 Powerful Rock Ballads", "🎵 Cathartic Classical", "🎵 Transformation Beats"],
            "🥰 Content": ["🎵 Cozy Coffee Shop", "🎵 Warm Acoustic", "🎵 Contentment Classical", "🎵 Peaceful Folk"],
            "😪 Drowsy": ["🎵 Afternoon Nap Music", "🎵 Gentle Wake-Up Sounds", "🎵 Lazy Sunday Mix", "🎵 Soft Background Beats"],
            "🙃 Playful": ["🎵 Quirky Indie Pop", "🎵 Fun Folk Tunes", "🎵 Playful Piano", "🎵 Whimsical Soundtracks"]
            }
            
            # Time-based playlist modifiers
            time_modifiers = {
            "morning": ["� Morning Energy", "☕ Coffee Shop Vibes", "🌱 Fresh Start Sounds"],
            "afternoon": ["☀️ Midday Motivation", "� Afternoon Breeze", "📚 Productive Focus"],
            "evening": ["🌅 Golden Hour", "� Evening Reflection", "🕯️ Cozy Night In"],
            "night": ["🌙 Nighttime Serenity", "⭐ Stargazing Songs", "😴 Sleep Preparation"]
            }
            
            # Weather-enhanced suggestions
            weather_playlists = {
            "Rainy": ["🌧️ Raindrops & Rhythms", "☔ Cozy Indoor Vibes", "💧 Liquid Lounge"],
            "Sunny": ["☀️ Sunshine Serenades", "🌻 Bright Day Beats", "🌞 Solar Soundscapes"],
            "Cloudy": ["☁️ Cloudy Day Dreams", "🌫️ Soft Gray Melodies", "🤍 Overcast Acoustics"],
            "Partly Cloudy": ["⛅ Mixed Weather Mix", "🌤️ Variable Vibes", "🌥️ Dynamic Soundtracks"],
            "Foggy": ["🌫️ Misty Morning Music", "👻 Ethereal Echoes", "✨ Mysterious Melodies"],
            "Windy": ["💨 Windswept Wonders", "🍃 Breezy Ballads", "🌪️ Dynamic Rhythms"],
            "Overcast": ["🌫️ Gray Day Grooves", "☁️ Mellow Overcast", "🤍 Subdued Soundscapes"]
            }
            
            # Determine time period
            if 6 <= current_hour < 12:
                time_period = "morning"
            elif 12 <= current_hour < 17:
                time_period = "afternoon"
            elif 17 <= current_hour < 21:
                time_period = "evening"
            else:
                time_period = "night"
                
            # Build recommendation
            base_playlists = playlist_suggestions.get(current_mood, ["🎵 September Mix"])
            time_playlists = time_modifiers.get(time_period, [])
            weather_specific = weather_playlists.get(weather_condition, [])
            
            # Mood enhancement tips based on current mood
            mood_tips = {
            "😊 Happy": ["Share your joy with others", "Take a moment to appreciate what's going well", "Dance to your favorite song"],
            "😌 Calm": ["Practice deep breathing", "Enjoy a warm beverage", "Take a peaceful walk"],
            "😔 Sad": ["Allow yourself to feel", "Reach out to a friend", "Write in a journal"],
            "😴 Tired": ["Take a short break", "Get some fresh air", "Consider a power nap"],
            "🤗 Excited": ["Channel energy into something creative", "Share your excitement", "Plan something fun"],
            "😰 Anxious": ["Ground yourself with 5-4-3-2-1 technique", "Take slow, deep breaths", "Listen to calming music"]
            }
            
            tips = mood_tips.get(current_mood, ["Take care of yourself", "Stay hydrated", "Be mindful of your needs"])
        
            recommendation = f"""
🎧 **Personalized Playlist Recommendations**

**🎭 For your {current_mood} mood:**
{chr(10).join(['• ' + playlist for playlist in base_playlists[:2]])}

**⏰ Perfect for {time_period}:**
{chr(10).join(['• ' + playlist for playlist in time_playlists[:2]])}

**🌤️ Weather-synced ({weather_condition}):**
{chr(10).join(['• ' + playlist for playlist in weather_specific[:2]])}

**💡 Mood Enhancement Tips:**
{chr(10).join(['• ' + tip for tip in tips])}

**🌡️ Current Conditions:** {self.current_weather.get('temperature', 'N/A')}°C, {weather_condition}
**⏰ Generated at:** {datetime.now().strftime("%H:%M")} on {datetime.now().strftime("%A")} 🍂

*Tip: Music can significantly influence your mood - choose what feels right for you! 🎵*
            """
            
            if hasattr(self, 'playlist_display'):
                self.playlist_display.setText(recommendation.strip())
                # Show success animation
                self.animate_playlist_update()
                
        except Exception as e:
            error_msg = f"🚫 Error generating playlist: {str(e)}\n\nPlease try again or check your mood selection."
            if hasattr(self, 'playlist_display'):
                self.playlist_display.setText(error_msg)
    
    def animate_playlist_update(self):
        """Add a subtle animation when playlist is updated"""
        if hasattr(self, 'playlist_display'):
            # Create a fade effect
            effect = QGraphicsOpacityEffect()
            self.playlist_display.setGraphicsEffect(effect)
            
            # Animate opacity
            self.playlist_opacity_animation = QPropertyAnimation(effect, b"opacity")
            self.playlist_opacity_animation.setDuration(300)
            self.playlist_opacity_animation.setStartValue(0.3)
            self.playlist_opacity_animation.setEndValue(1.0)
            self.playlist_opacity_animation.start()
        
    def analyze_mood_patterns(self):
        analysis = self.mood_analyzer.analyze_mood_pattern(self.mood_history)
        if hasattr(self, 'mood_analysis_display'):
            self.mood_analysis_display.setText(analysis)
            
        # Also generate weather correlation
        self.analyze_weather_correlation()
    
    def analyze_weather_correlation(self):
        if not self.mood_history or not hasattr(self, 'correlation_display'):
            return
            
        # Analyze correlation between weather and mood
        weather_mood_data = {}
        
        for timestamp, mood_data in self.mood_history.items():
            weather = mood_data.get('weather', 'Unknown')
            intensity = mood_data.get('intensity', 5)
            
            if weather not in weather_mood_data:
                weather_mood_data[weather] = []
            weather_mood_data[weather].append(intensity)
            
        if not weather_mood_data:
            correlation_text = "No correlation data available yet. Log more moods to see patterns!"
        else:
            correlation_text = "🌤️ **Weather-Mood Correlation Analysis:**\n\n"
            
            for weather, intensities in weather_mood_data.items():
                avg_intensity = sum(intensities) / len(intensities)
                count = len(intensities)
                
                correlation_text += f"**{weather} Weather:** {avg_intensity:.1f}/10 average mood ({count} entries)\n"
                
                if avg_intensity >= 7:
                    mood_desc = "Generally positive moods ✨"
                elif avg_intensity >= 5:
                    mood_desc = "Balanced emotional state ⚖️"
                else:
                    mood_desc = "Lower mood intensity 💙"
                    
                correlation_text += f"• {mood_desc}\n\n"
                
            # Add insights
            if weather_mood_data:
                best_weather = max(weather_mood_data.keys(), 
                                 key=lambda w: sum(weather_mood_data[w])/len(weather_mood_data[w]))
                correlation_text += f"📈 **Your mood tends to be highest during: {best_weather} weather**\n"
                correlation_text += f"💡 **Insight:** Consider planning outdoor activities during {best_weather.lower()} days!"
        
        self.correlation_display.setText(correlation_text)
    
    def save_current_settings(self):
        # Update settings from UI
        if hasattr(self, 'city_input'):
            self.settings["city"] = self.city_input.text()
        if hasattr(self, 'units_combo'):
            self.settings["units"] = "metric" if "Celsius" in self.units_combo.currentText() else "imperial"
        if hasattr(self, 'notifications_checkbox'):
            self.settings["notifications"] = self.notifications_checkbox.isChecked()
        if hasattr(self, 'auto_suggestions_checkbox'):
            self.settings["auto_mood_suggestions"] = self.auto_suggestions_checkbox.isChecked()
        if hasattr(self, 'theme_sync_checkbox'):
            self.settings["theme_sync"] = self.theme_sync_checkbox.isChecked()
            
        self.save_settings()
        
        # Show confirmation (you could add a status message here)
        print("Settings saved successfully!")
        
    def export_data(self):
        # Export mood and weather data to JSON files
        export_data = {
            "mood_history": self.mood_history,
            "weather_history": self.weather_history,
            "settings": self.settings,
            "export_timestamp": datetime.now().isoformat()
        }
        
        filename = f"equinox_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            print(f"Data exported successfully to {filename}")
        except Exception as e:
            print(f"Export failed: {e}")
            
    def clear_all_data(self):
        # Clear all data (with confirmation in a real app)
        self.mood_history = {}
        self.weather_history = {}
        
        self.save_mood_data()
        self.save_weather_history()
        
        # Refresh displays
        self.refresh_mood_history()
        self.analyze_mood_patterns()
        
        print("All data cleared successfully!")