import json
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTextEdit, QComboBox, QGroupBox, QGridLayout, QSlider,
                             QListWidget, QSplitter, QGraphicsScene, QGraphicsView,
                             QGraphicsRectItem, QGraphicsTextItem, QGraphicsEllipseItem,
                             QGraphicsLineItem, QFrame)
from PyQt5.QtCore import Qt, QTimer, QRectF, QPointF, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPen, QBrush, QPainter
import random
import time
import ast


class AlgorithmVisualizer(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)

        # Visualization settings
        self.node_radius = 30
        self.node_spacing = 80
        self.animation_speed = 1000  # ms between steps

        # Current algorithm state
        self.current_step = 0
        self.algorithm_steps = []
        self.is_playing = False

        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.next_step)

        # Style the graphics view
        self.setStyleSheet("""
            QGraphicsView {
                background-color: #FFF8DC;
                border: 3px solid #CD853F;
                border-radius: 10px;
            }
        """)

    def visualize_array(self, array, highlight_indices=None, colors=None):
        self.scene.clear()

        if not array:
            return

        start_x = 50
        start_y = 100

        for i, value in enumerate(array):
            x = start_x + i * self.node_spacing
            y = start_y

            # Determine color
            if colors and i < len(colors):
                color = QColor(colors[i])
            elif highlight_indices and i in highlight_indices:
                color = QColor("#DAA520")  # Gold for highlighted
            else:
                color = QColor("#CD853F")  # Default brown

            # Draw rectangle for array element
            rect = QGraphicsRectItem(x, y, 60, 40)
            rect.setBrush(QBrush(color))
            rect.setPen(QPen(QColor("#8B4513"), 2))
            self.scene.addItem(rect)

            # Add value text
            text = QGraphicsTextItem(str(value))
            text.setPos(x + 15, y + 10)
            text.setFont(QFont("Arial", 12, QFont.Bold))
            text.setDefaultTextColor(QColor("white"))
            self.scene.addItem(text)

            # Add index label
            index_text = QGraphicsTextItem(str(i))
            index_text.setPos(x + 25, y - 25)
            index_text.setFont(QFont("Arial", 10))
            index_text.setDefaultTextColor(QColor("#8B4513"))
            self.scene.addItem(index_text)

    def visualize_tree(self, nodes, edges=None):
        self.scene.clear()

        if not nodes:
            return

        # Simple binary tree layout
        levels = {}
        for node in nodes:
            level = node.get('level', 0)
            if level not in levels:
                levels[level] = []
            levels[level].append(node)

        start_y = 50
        level_height = 100

        for level, level_nodes in levels.items():
            y = start_y + level * level_height
            node_spacing = max(100, 800 // (len(level_nodes) + 1))

            for i, node in enumerate(level_nodes):
                x = 50 + (i + 1) * node_spacing

                # Draw node circle
                circle = QGraphicsEllipseItem(x - self.node_radius, y - self.node_radius,
                                              self.node_radius * 2, self.node_radius * 2)
                circle.setBrush(QBrush(QColor("#CD853F")))
                circle.setPen(QPen(QColor("#8B4513"), 2))
                self.scene.addItem(circle)

                # Add node value
                text = QGraphicsTextItem(str(node.get('value', '')))
                text.setPos(x - 10, y - 10)
                text.setFont(QFont("Arial", 12, QFont.Bold))
                text.setDefaultTextColor(QColor("white"))
                self.scene.addItem(text)

        # Draw edges if provided
        if edges:
            for edge in edges:
                from_node = edge['from']
                to_node = edge['to']
                # Simple line drawing (would need proper node position tracking)
                line = QGraphicsLineItem(
                    from_node[0], from_node[1], to_node[0], to_node[1])
                line.setPen(QPen(QColor("#8B4513"), 2))
                self.scene.addItem(line)

    def start_animation(self, steps):
        self.algorithm_steps = steps
        self.current_step = 0
        self.is_playing = True
        self.animation_timer.start(self.animation_speed)

    def stop_animation(self):
        self.is_playing = False
        self.animation_timer.stop()

    def next_step(self):
        if self.current_step < len(self.algorithm_steps):
            step = self.algorithm_steps[self.current_step]

            if step['type'] == 'array':
                self.visualize_array(step['data'], step.get(
                    'highlight'), step.get('colors'))
            elif step['type'] == 'tree':
                self.visualize_tree(step['data'], step.get('edges'))

            self.current_step += 1
        else:
            self.stop_animation()

    def set_animation_speed(self, speed):
        self.animation_speed = speed
        if self.is_playing:
            self.animation_timer.start(self.animation_speed)


class Leaflet(QWidget):
    def __init__(self):
        super().__init__()
        self.algorithms_file = "algorithm_history.json"
        self.algorithm_history = self.load_algorithm_history()
        self.setup_ui()

    def load_algorithm_history(self):
        if os.path.exists(self.algorithms_file):
            try:
                with open(self.algorithms_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_algorithm_history(self):
        with open(self.algorithms_file, 'w') as f:
            json.dump(self.algorithm_history, f, indent=2)

    def setup_ui(self):
        main_layout = QHBoxLayout()

        # Left Panel - Algorithm Selection and Controls
        left_panel = QVBoxLayout()

        # Title
        title = QLabel("🌿 Leaflet - Algorithm Visual Debugger")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #8B4513; margin: 10px;")
        left_panel.addWidget(title)

        # Algorithm Selection
        algo_group = QGroupBox("🔍 Select Algorithm")
        algo_layout = QGridLayout()

        algo_layout.addWidget(QLabel("Algorithm Type:"), 0, 0)
        self.algorithm_combo = QComboBox()
        algorithms = [
            "Bubble Sort", "Selection Sort", "Insertion Sort", "Merge Sort",
            "Quick Sort", "Binary Search", "Linear Search", "DFS", "BFS"
        ]
        self.algorithm_combo.addItems(algorithms)
        algo_layout.addWidget(self.algorithm_combo, 0, 1)

        algo_layout.addWidget(QLabel("Input Data:"), 1, 0)
        self.input_data = QTextEdit()
        self.input_data.setMaximumHeight(60)
        self.input_data.setPlaceholderText(
            "Enter array: [5, 2, 8, 1, 9] or leave empty for random")
        algo_layout.addWidget(self.input_data, 1, 1)

        start_viz_btn = QPushButton("🚀 Start Visualization")
        start_viz_btn.clicked.connect(self.start_visualization)
        algo_layout.addWidget(start_viz_btn, 2, 0, 1, 2)

        algo_group.setLayout(algo_layout)
        left_panel.addWidget(algo_group)

        # Animation Controls
        controls_group = QGroupBox("🎮 Animation Controls")
        controls_layout = QGridLayout()

        self.play_btn = QPushButton("▶️ Play")
        self.play_btn.clicked.connect(self.play_animation)
        self.play_btn.setEnabled(False)
        controls_layout.addWidget(self.play_btn, 0, 0)

        self.pause_btn = QPushButton("⏸️ Pause")
        self.pause_btn.clicked.connect(self.pause_animation)
        self.pause_btn.setEnabled(False)
        controls_layout.addWidget(self.pause_btn, 0, 1)

        self.step_btn = QPushButton("⏭️ Step")
        self.step_btn.clicked.connect(self.step_animation)
        self.step_btn.setEnabled(False)
        controls_layout.addWidget(self.step_btn, 0, 2)

        self.reset_btn = QPushButton("🔄 Reset")
        self.reset_btn.clicked.connect(self.reset_animation)
        self.reset_btn.setEnabled(False)
        controls_layout.addWidget(self.reset_btn, 1, 0)

        controls_layout.addWidget(QLabel("Speed:"), 1, 1)
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(100, 3000)  # 100ms to 3000ms
        self.speed_slider.setValue(1000)
        self.speed_slider.valueChanged.connect(self.update_animation_speed)
        controls_layout.addWidget(self.speed_slider, 1, 2)

        controls_group.setLayout(controls_layout)
        left_panel.addWidget(controls_group)

        # Copilot Logic Tips
        tips_group = QGroupBox("🤖 Copilot Logic Tips")
        tips_layout = QVBoxLayout()

        self.copilot_tips = QTextEdit()
        self.copilot_tips.setMaximumHeight(150)
        self.copilot_tips.setReadOnly(True)
        self.copilot_tips.setPlaceholderText(
            "AI-powered algorithm insights and tips will appear here...")
        tips_layout.addWidget(self.copilot_tips)

        generate_tips_btn = QPushButton("💡 Get Algorithm Tips")
        generate_tips_btn.clicked.connect(self.generate_copilot_tips)
        tips_layout.addWidget(generate_tips_btn)

        tips_group.setLayout(tips_layout)
        left_panel.addWidget(tips_group)

        # Algorithm History
        history_group = QGroupBox("📚 Recent Visualizations")
        history_layout = QVBoxLayout()

        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(100)
        self.history_list.itemDoubleClicked.connect(self.load_from_history)
        history_layout.addWidget(self.history_list)

        history_group.setLayout(history_layout)
        left_panel.addWidget(history_group)

        # Right Panel - Visualization Area
        right_panel = QVBoxLayout()

        # Current Algorithm Info
        self.current_algo_label = QLabel("🔄 Ready to visualize algorithms")
        self.current_algo_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.current_algo_label.setStyleSheet("color: #CD853F; margin: 10px;")
        self.current_algo_label.setAlignment(Qt.AlignCenter)
        right_panel.addWidget(self.current_algo_label)

        # Visualization Area
        self.visualizer = AlgorithmVisualizer()
        self.visualizer.setMinimumSize(600, 400)
        right_panel.addWidget(self.visualizer)

        # Step Information
        step_info_group = QGroupBox("📊 Current Step Information")
        step_info_layout = QVBoxLayout()

        self.step_info = QTextEdit()
        self.step_info.setMaximumHeight(120)
        self.step_info.setReadOnly(True)
        self.step_info.setPlaceholderText(
            "Step-by-step algorithm explanation will appear here...")
        step_info_layout.addWidget(self.step_info)

        step_info_group.setLayout(step_info_layout)
        right_panel.addWidget(step_info_group)

        # Add panels to main layout
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setMaximumWidth(350)

        right_widget = QWidget()
        right_widget.setLayout(right_panel)

        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)

        self.setLayout(main_layout)
        self.refresh_history()

    def start_visualization(self):
        algorithm = self.algorithm_combo.currentText()
        input_text = self.input_data.toPlainText().strip()

        # Parse input or generate random data
        if input_text:
            try:
                if input_text.startswith('[') and input_text.endswith(']'):
                    data = ast.literal_eval(input_text)
                else:
                    data = [int(x.strip()) for x in input_text.split(',')]
            except:
                data = [random.randint(1, 99) for _ in range(8)]
        else:
            data = [random.randint(1, 99) for _ in range(8)]

        # Generate algorithm steps
        steps = self.generate_algorithm_steps(algorithm, data)

        if steps:
            self.visualizer.start_animation(steps)
            self.current_algo_label.setText(f"🔄 Visualizing: {algorithm}")

            # Enable controls
            self.play_btn.setEnabled(True)
            self.pause_btn.setEnabled(True)
            self.step_btn.setEnabled(True)
            self.reset_btn.setEnabled(True)

            # Add to history
            history_entry = {
                "algorithm": algorithm,
                "data": data,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            self.algorithm_history.append(history_entry)
            self.save_algorithm_history()
            self.refresh_history()

            # Generate initial tips
            self.generate_copilot_tips()

    def generate_algorithm_steps(self, algorithm, data):
        """Generate step-by-step visualization data for algorithms"""
        steps = []

        if algorithm == "Bubble Sort":
            arr = data.copy()
            steps.append({
                'type': 'array',
                'data': arr.copy(),
                'description': "Initial array - Bubble Sort will compare adjacent elements"
            })

            n = len(arr)
            for i in range(n):
                for j in range(0, n - i - 1):
                    # Highlight comparison
                    steps.append({
                        'type': 'array',
                        'data': arr.copy(),
                        'highlight': [j, j + 1],
                        'description': f"Comparing elements at positions {j} and {j+1}: {arr[j]} vs {arr[j+1]}"
                    })

                    if arr[j] > arr[j + 1]:
                        arr[j], arr[j + 1] = arr[j + 1], arr[j]
                        steps.append({
                            'type': 'array',
                            'data': arr.copy(),
                            'colors': ['#90EE90' if k == j or k == j+1 else '#CD853F' for k in range(len(arr))],
                            'description': f"Swapped {arr[j+1]} and {arr[j]} - array is now: {arr}"
                        })

        elif algorithm == "Linear Search":
            arr = data.copy()
            # Search for middle element
            target = arr[len(arr)//2] if arr else 0

            steps.append({
                'type': 'array',
                'data': arr.copy(),
                'description': f"Linear Search: Looking for {target} in the array"
            })

            for i, val in enumerate(arr):
                steps.append({
                    'type': 'array',
                    'data': arr.copy(),
                    'highlight': [i],
                    'description': f"Checking position {i}: {val} {'==' if val == target else '!='} {target}"
                })

                if val == target:
                    steps.append({
                        'type': 'array',
                        'data': arr.copy(),
                        'colors': ['#90EE90' if k == i else '#CD853F' for k in range(len(arr))],
                        'description': f"Found {target} at position {i}! Search complete."
                    })
                    break

        else:
            # Default case - just show the array
            steps.append({
                'type': 'array',
                'data': data,
                'description': f"{algorithm} visualization - This is a simplified demo"
            })

        return steps

    def play_animation(self):
        if hasattr(self.visualizer, 'algorithm_steps') and self.visualizer.algorithm_steps:
            self.visualizer.is_playing = True
            self.visualizer.animation_timer.start(
                self.visualizer.animation_speed)

    def pause_animation(self):
        self.visualizer.stop_animation()

    def step_animation(self):
        self.visualizer.stop_animation()
        self.visualizer.next_step()

    def reset_animation(self):
        self.visualizer.stop_animation()
        self.visualizer.current_step = 0
        if hasattr(self.visualizer, 'algorithm_steps') and self.visualizer.algorithm_steps:
            first_step = self.visualizer.algorithm_steps[0]
            if first_step['type'] == 'array':
                self.visualizer.visualize_array(first_step['data'])

    def update_animation_speed(self, value):
        self.visualizer.set_animation_speed(value)

    def generate_copilot_tips(self):
        algorithm = self.algorithm_combo.currentText()

        algorithm_tips = {
            "Bubble Sort": """
🔍 **Bubble Sort Analysis:**
• Time Complexity: O(n²) - quadratic time
• Space Complexity: O(1) - constant space
• Stable: Yes - maintains relative order of equal elements
• Best for: Educational purposes, small datasets

💡 **Optimization Tips:**
• Add early termination if no swaps occur
• Use cocktail sort for slight improvement
• Consider merge sort for larger datasets

🍂 **Cozy Learning Note:**
Take your time understanding each comparison - like leaves settling naturally into place!
            """,

            "Linear Search": """
🔍 **Linear Search Analysis:**
• Time Complexity: O(n) - linear time
• Space Complexity: O(1) - constant space  
• Works on: Unsorted and sorted arrays
• Best for: Small datasets, unsorted data

💡 **When to Use:**
• Data is unsorted
• Dataset is small (< 100 elements)
• Simplicity is preferred over efficiency

🍂 **Cozy Learning Note:**
Like scanning autumn leaves one by one - methodical but thorough!
            """,

            "Binary Search": """
🔍 **Binary Search Analysis:**
• Time Complexity: O(log n) - logarithmic time
• Space Complexity: O(1) iterative, O(log n) recursive
• Requirement: Array must be sorted
• Best for: Large sorted datasets

💡 **Key Insight:**
Divides search space in half each step - very efficient!
Like finding a specific page in a book by opening to the middle first.

🍂 **Cozy Learning Note:**
Elegant like the golden ratio in autumn spirals!
            """
        }

        tips = algorithm_tips.get(algorithm, f"""
🔍 **{algorithm} Overview:**
This is a fundamental algorithm worth understanding deeply.

💡 **General Tips:**
• Trace through with small examples first
• Understand the invariants (what stays true)
• Consider best, average, and worst cases
• Practice implementing variations

🍂 **Cozy Learning Note:**
Every algorithm has its season - some are better for different data patterns!
        """)

        self.copilot_tips.setText(tips.strip())

    def refresh_history(self):
        self.history_list.clear()
        recent_history = self.algorithm_history[-10:]  # Last 10 entries

        for entry in recent_history:
            history_text = f"{entry['algorithm']} - {entry['timestamp']}"
            self.history_list.addItem(history_text)

    def load_from_history(self, item):
        # Find the corresponding history entry
        item_text = item.text()
        for entry in self.algorithm_history:
            if f"{entry['algorithm']} - {entry['timestamp']}" == item_text:
                # Set up the UI with historical data
                self.algorithm_combo.setCurrentText(entry['algorithm'])
                self.input_data.setText(str(entry['data']))
                break
