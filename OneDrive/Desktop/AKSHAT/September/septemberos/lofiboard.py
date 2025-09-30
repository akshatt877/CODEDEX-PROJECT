import json
import os
import time
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QListWidget, QPushButton, QLabel, QLineEdit, QSplitter, 
                             QGraphicsDropShadowEffect, QComboBox, QListWidgetItem, 
                             QMessageBox, QInputDialog, QGroupBox, QTreeWidget, QTreeWidgetItem)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QFont, QColor, QIcon
import markdown2
from .animations import GlowEffect, PulsingWidget

class LoFiBoard(QWidget):
    def __init__(self):
        super().__init__()
        self.notes_file = "notes_database.json"
        self.categories_file = "note_categories.json"
        self.notes = self.load_notes()
        self.categories = self.load_categories()
        self.current_note_id = None
        self.current_category = "All Notes"
        self.setup_ui()
        self.setup_animations()
        
    def setup_ui(self):
        main_layout = QHBoxLayout()
        
        # Left panel - Enhanced notes management
        left_panel = QVBoxLayout()
        
        # Title and controls
        title_layout = QHBoxLayout()
        title_label = QLabel("🍂 My September Notes")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        left_panel.addLayout(title_layout)
        
        # Category management
        category_group = QGroupBox("📁 Categories")
        category_layout = QVBoxLayout()
        
        # Category selector and controls
        category_controls = QHBoxLayout()
        self.category_combo = QComboBox()
        self.category_combo.addItem("All Notes")
        self.category_combo.addItems(list(self.categories.keys()))
        self.category_combo.currentTextChanged.connect(self.filter_by_category)
        category_controls.addWidget(self.category_combo)
        
        new_category_btn = QPushButton("+ Cat")
        new_category_btn.setMaximumWidth(50)
        new_category_btn.clicked.connect(self.create_new_category)
        new_category_btn.setToolTip("Create New Category")
        category_controls.addWidget(new_category_btn)
        
        category_layout.addLayout(category_controls)
        category_group.setLayout(category_layout)
        left_panel.addWidget(category_group)
        
        # Search functionality
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search notes...")
        self.search_input.textChanged.connect(self.search_notes)
        search_layout.addWidget(self.search_input)
        
        clear_search_btn = QPushButton("×")
        clear_search_btn.setMaximumWidth(30)
        clear_search_btn.clicked.connect(self.clear_search)
        search_layout.addWidget(clear_search_btn)
        left_panel.addLayout(search_layout)
        
        # Note controls
        note_controls = QHBoxLayout()
        new_note_btn = QPushButton("+ New Note")
        new_note_btn.clicked.connect(self.create_new_note)
        
        # Add glow effect to new note button
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(218, 165, 32, 100))
        shadow.setOffset(0, 0)
        new_note_btn.setGraphicsEffect(shadow)
        
        delete_note_btn = QPushButton("🗑️ Delete")
        delete_note_btn.clicked.connect(self.delete_current_note)
        delete_note_btn.setStyleSheet("""
            QPushButton {
                background-color: #CD5C5C;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #B22222;
            }
        """)
        
        note_controls.addWidget(new_note_btn)
        note_controls.addWidget(delete_note_btn)
        left_panel.addLayout(note_controls)
        
        # Enhanced notes list with metadata
        self.notes_list = QTreeWidget()
        self.notes_list.setHeaderLabels(["📝 Notes", "📅 Date", "📁 Category"])
        self.notes_list.itemClicked.connect(self.load_selected_note)
        
        # Style the notes tree
        self.notes_list.setStyleSheet("""
            QTreeWidget {
                background-color: #FFF8DC;
                border: 2px solid #DEB887;
                border-radius: 8px;
                font-size: 11px;
            }
            QTreeWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F5DEB3;
            }
            QTreeWidget::item:selected {
                background-color: #DAA520;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #F0E68C;
            }
        """)
        
        # Add subtle shadow to notes list
        list_shadow = QGraphicsDropShadowEffect()
        list_shadow.setBlurRadius(10)
        list_shadow.setColor(QColor(139, 69, 19, 60))
        list_shadow.setOffset(2, 2)
        self.notes_list.setGraphicsEffect(list_shadow)
        
        left_panel.addWidget(self.notes_list)
        
        # Right panel - Note editor
        right_panel = QVBoxLayout()
        
        # Note title input with animations
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("✏️ Enter your note title...")
        self.title_input.setFont(QFont("Arial", 12, QFont.Bold))
        self.title_input.textChanged.connect(self.save_current_note)
        
        # Add focus animation
        self.title_input.focusInEvent = self.create_focus_animation(self.title_input, self.title_input.focusInEvent)
        self.title_input.focusOutEvent = self.create_focus_out_animation(self.title_input, self.title_input.focusOutEvent)
        
        right_panel.addWidget(self.title_input)
        
        # Splitter for editor and preview
        splitter = QSplitter(Qt.Horizontal)
        
        # Markdown editor
        editor_widget = QWidget()
        editor_layout = QVBoxLayout()
        editor_layout.addWidget(QLabel("📝 Editor (Markdown)"))
        
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Start typing your cozy notes here... Use **bold**, *italic*, # headers, etc.")
        self.editor.textChanged.connect(self.save_current_note)
        self.editor.textChanged.connect(self.update_preview)
        self.editor.setStyleSheet("""
            QTextEdit {
                background-color: #FFF8DC;
                border: 2px solid #DEB887;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                line-height: 1.4;
            }
        """)
        editor_layout.addWidget(self.editor)
        editor_widget.setLayout(editor_layout)
        
        # Preview pane
        preview_widget = QWidget()
        preview_layout = QVBoxLayout()
        
        # AI Summary button
        ai_summary_btn = QPushButton("🤖 Generate AI Summary")
        ai_summary_btn.clicked.connect(self.generate_ai_summary)
        ai_summary_btn.setStyleSheet("""
            QPushButton {
                background-color: #DAA520;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            QPushButton:hover {
                background-color: #B8860B;
            }
        """)
        preview_layout.addWidget(ai_summary_btn)
        
        preview_layout.addWidget(QLabel("👁️ Preview"))
        
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setStyleSheet("""
            QTextEdit {
                background-color: #FFFACD;
                border: 2px solid #DEB887;
                border-radius: 5px;
                padding: 15px;
                font-family: 'Georgia', 'Times New Roman', serif;
                font-size: 13px;
                line-height: 1.6;
            }
        """)
        preview_layout.addWidget(self.preview)
        preview_widget.setLayout(preview_layout)
        
        splitter.addWidget(editor_widget)
        splitter.addWidget(preview_widget)
        splitter.setSizes([400, 400])
        
        right_panel.addWidget(splitter)
        
        # Add panels to main layout
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setMaximumWidth(300)
        
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)
        
        self.setLayout(main_layout)
        self.refresh_notes_list()
        
    def setup_animations(self):
        # Falling leaves animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_falling_leaves)
        self.animation_timer.start(3000)  # Every 3 seconds
        
    def animate_falling_leaves(self):
        # Simple animation by updating window title with falling leaf emoji
        current_title = self.parent().parent().windowTitle()
        if "🍂" not in current_title:
            self.parent().parent().setWindowTitle(current_title + " 🍂")
        
    def load_categories(self):
        if os.path.exists(self.categories_file):
            try:
                with open(self.categories_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"General": "📋", "Ideas": "💡", "Tasks": "✅", "Personal": "🔒"}
        return {"General": "📋", "Ideas": "💡", "Tasks": "✅", "Personal": "🔒"}
    
    def save_categories(self):
        with open(self.categories_file, 'w', encoding='utf-8') as f:
            json.dump(self.categories, f, indent=2, ensure_ascii=False)
    
    def load_notes(self):
        if os.path.exists(self.notes_file):
            try:
                with open(self.notes_file, 'r', encoding='utf-8') as f:
                    loaded_notes = json.load(f)
                    # Migrate old format if needed
                    for note_id, note_data in loaded_notes.items():
                        if 'category' not in note_data:
                            note_data['category'] = 'General'
                        if 'id' not in note_data:
                            note_data['id'] = note_id
                    return loaded_notes
            except:
                return {}
        return {}
    
    def save_notes(self):
        with open(self.notes_file, 'w', encoding='utf-8') as f:
            json.dump(self.notes, f, indent=2, ensure_ascii=False)
    
    def refresh_notes_list(self):
        self.notes_list.clear()
        
        # Filter notes based on current category and search
        filtered_notes = {}
        search_text = getattr(self, 'search_input', None)
        search_term = search_text.text().lower() if search_text else ""
        
        for note_id, note_data in self.notes.items():
            # Category filter
            if self.current_category != "All Notes" and note_data.get('category', 'General') != self.current_category:
                continue
                
            # Search filter
            if search_term:
                title = note_data.get('title', '').lower()
                content = note_data.get('content', '').lower()
                if search_term not in title and search_term not in content:
                    continue
                    
            filtered_notes[note_id] = note_data
            
        # Sort notes by creation date (newest first)
        sorted_notes = sorted(filtered_notes.items(), 
                            key=lambda x: x[1].get('created', ''), 
                            reverse=True)
        
        for note_id, note_data in sorted_notes:
            title = note_data.get('title', 'Untitled Note')
            created = note_data.get('created', 'Unknown')
            category = note_data.get('category', 'General')
            category_icon = self.categories.get(category, '📋')
            
            # Format date nicely
            try:
                date_obj = datetime.strptime(created, '%Y-%m-%d %H:%M:%S')
                formatted_date = date_obj.strftime('%m/%d %H:%M')
            except:
                formatted_date = created[:10] if len(created) > 10 else created
            
            item = QTreeWidgetItem([
                f"{category_icon} {title}",
                formatted_date,
                category
            ])
            item.setData(0, Qt.UserRole, note_id)  # Store note ID
            self.notes_list.addTopLevelItem(item)
            
        # Resize columns to content
        self.notes_list.resizeColumnToContents(0)
        self.notes_list.resizeColumnToContents(1)
    
    def create_new_category(self):
        category_name, ok = QInputDialog.getText(self, 'New Category', 'Enter category name:')
        if ok and category_name.strip():
            category_name = category_name.strip()
            if category_name not in self.categories:
                # Simple icon mapping
                icon_map = {
                    'personal': '🔒', 'work': '💼', 'study': '📚', 'project': '🚀',
                    'meeting': '👥', 'todo': '✅', 'idea': '💡', 'recipe': '🍳',
                    'travel': '✈️', 'health': '🏥', 'finance': '💰', 'shopping': '🛒'
                }
                icon = icon_map.get(category_name.lower(), '📁')
                
                self.categories[category_name] = icon
                self.save_categories()
                self.category_combo.addItem(category_name)
                self.category_combo.setCurrentText(category_name)
                self.current_category = category_name
                self.refresh_notes_list()
                
    def filter_by_category(self, category):
        self.current_category = category
        self.refresh_notes_list()
        
    def search_notes(self, text):
        self.refresh_notes_list()
        
    def clear_search(self):
        self.search_input.clear()
        self.refresh_notes_list()
        
    def delete_current_note(self):
        if self.current_note_id and self.current_note_id in self.notes:
            title = self.notes[self.current_note_id].get('title', 'Unknown Note')
            reply = QMessageBox.question(self, 'Delete Note', 
                                       f'Are you sure you want to delete "{title}"?',
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                del self.notes[self.current_note_id]
                self.save_notes()
                self.refresh_notes_list()
                
                # Clear editor
                self.title_input.clear()
                self.editor.clear()
                self.preview.clear()
                self.current_note_id = None

    def create_new_note(self):
        note_id = str(int(time.time()))
        
        # Ask for category if more than just General exists
        category = self.current_category if self.current_category != "All Notes" else "General"
        
        self.notes[note_id] = {
            'id': note_id,
            'title': 'New Note',
            'content': '',
            'category': category,
            'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.save_notes()
        self.refresh_notes_list()
        
        # Select the new note automatically
        for i in range(self.notes_list.topLevelItemCount()):
            item = self.notes_list.topLevelItem(i)
            if item.data(0, Qt.UserRole) == note_id:
                self.notes_list.setCurrentItem(item)
                self.load_selected_note(item, 0)
                break
    
    def load_selected_note(self, item, column=0):
        if not item:
            return
            
        note_id = item.data(0, Qt.UserRole)
        if note_id and note_id in self.notes:
            note_data = self.notes[note_id]
            self.current_note_id = note_id
            
            # Temporarily disconnect signals to prevent save conflicts during loading
            try:
                self.title_input.textChanged.disconnect(self.save_current_note)
                self.editor.textChanged.disconnect(self.save_current_note)
                self.editor.textChanged.disconnect(self.update_preview)
            except TypeError:
                # Signals might not be connected yet
                pass
            
            # Load note data into editor
            self.title_input.setText(note_data.get('title', ''))
            self.editor.setText(note_data.get('content', ''))
            
            # Update category combo if needed
            note_category = note_data.get('category', 'General')
            current_combo_text = self.category_combo.currentText()
            if current_combo_text == "All Notes":
                # Temporarily change to show the note's category
                index = self.category_combo.findText(note_category)
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)
            
            # Reconnect signals after loading
            self.title_input.textChanged.connect(self.save_current_note)
            self.editor.textChanged.connect(self.save_current_note)
            self.editor.textChanged.connect(self.update_preview)
            
            # Update preview after everything is loaded
            self.update_preview()
    
    def save_current_note(self):
        if hasattr(self, 'current_note_id') and self.current_note_id and self.current_note_id in self.notes:
            self.notes[self.current_note_id]['title'] = self.title_input.text()
            self.notes[self.current_note_id]['content'] = self.editor.toPlainText()
            self.notes[self.current_note_id]['modified'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Update category if changed
            current_category = self.category_combo.currentText()
            if current_category != "All Notes":
                self.notes[self.current_note_id]['category'] = current_category
                
            self.save_notes()
            # Only refresh if title changed to avoid cursor jumping
            current_item = self.notes_list.currentItem()
            if current_item:
                current_title = current_item.text(0)
                new_title = self.title_input.text()
                if not current_title.endswith(new_title):
                    self.refresh_notes_list()
    
    def update_preview(self):
        markdown_text = self.editor.toPlainText()
        html = markdown2.markdown(markdown_text, extras=['fenced-code-blocks', 'tables'])
        self.preview.setHtml(html)
    
    def generate_ai_summary(self):
        content = self.editor.toPlainText()
        if not content.strip():
            return
            
        # Enhanced AI summary with analysis
        words = content.split()
        lines = content.split('\n')
        sentences = content.split('.')
        
        # Analyze content structure
        has_headers = any(line.strip().startswith('#') for line in lines)
        has_lists = any(line.strip().startswith(('-', '*', '1.', '2.')) for line in lines)
        has_code = '```' in content or '`' in content
        
        # Generate intelligent summary
        summary_parts = [f"📋 **AI Analysis Summary** ({len(words)} words, {len(sentences)} sentences)"]
        
        if len(words) < 10:
            summary_parts.append("📝 *Quick note* - Brief content for quick reference.")
        elif len(words) < 50:
            summary_parts.append("📄 *Short note* - Concise information, perfect for quick review.")
        elif len(words) < 200:
            summary_parts.append("📑 *Medium note* - Good amount of detail with key information.")
        else:
            summary_parts.append("📚 *Detailed note* - Comprehensive content with extensive information.")
            
        # Content structure analysis
        if has_headers:
            summary_parts.append("🏗️ *Well-structured* - Contains headers for organization.")
        if has_lists:
            summary_parts.append("📋 *List format* - Uses bullet points or numbered items.")
        if has_code:
            summary_parts.append("💻 *Technical content* - Contains code or technical formatting.")
            
        # Reading time estimate
        reading_time = max(1, len(words) // 200)  # Average 200 words per minute
        summary_parts.append(f"⏱️ *Estimated reading time*: {reading_time} minute{'s' if reading_time != 1 else ''}")
        
        # Category-specific insights
        if self.current_note_id and self.current_note_id in self.notes:
            category = self.notes[self.current_note_id].get('category', 'General')
            category_insights = {
                'Ideas': '💡 Consider developing these ideas further or linking to related concepts.',
                'Tasks': '✅ Break down complex tasks into smaller, actionable steps.',
                'Personal': '🔒 Personal reflection - consider what insights you can apply.',
                'Work': '💼 Work-related content - consider deadlines and follow-up actions.',
                'Study': '📚 Study material - create summary points for better retention.'
            }
            if category in category_insights:
                summary_parts.append(category_insights[category])
        
        summary = '\n'.join(summary_parts)
        summary += "\n\n🍂 *Generated by September AI Assistant*"
        
        # Add summary to the beginning of the note if not already present
        current_content = self.editor.toPlainText()
        if not current_content.startswith("📋 **AI Analysis Summary**"):
            new_content = summary + "\n\n---\n\n" + current_content
            self.editor.setText(new_content)
        else:
            # Update existing summary
            lines = current_content.split('\n')
            summary_end = -1
            for i, line in enumerate(lines):
                if line.strip() == '---':
                    summary_end = i
                    break
            if summary_end > 0:
                new_content = summary + "\n\n---\n\n" + '\n'.join(lines[summary_end + 1:])
                self.editor.setText(new_content)
    
    def create_focus_animation(self, widget, original_focus_in):
        def animated_focus_in(event):
            # Create glow effect on focus
            glow = QGraphicsDropShadowEffect()
            glow.setBlurRadius(20)
            glow.setColor(QColor(218, 165, 32, 150))
            glow.setOffset(0, 0)
            widget.setGraphicsEffect(glow)
            
            # Call original focus event
            original_focus_in(event)
            
        return animated_focus_in
    
    def create_focus_out_animation(self, widget, original_focus_out):
        def animated_focus_out(event):
            # Remove glow effect when focus is lost
            widget.setGraphicsEffect(None)
            
            # Call original focus event
            original_focus_out(event)
            
        return animated_focus_out
