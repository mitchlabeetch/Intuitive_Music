"""
INTUITIVES DAW - Generator Panel

AI and procedural music generation tools.
"Does this sound cool?" - The only rule.
"""

from intui.sgqt import *
from intlib.brand import (
    APP_NAME,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_TERTIARY,
    CHROMA_COLORS,
)


class GeneratorPanel(QWidget):
    """
    Panel for AI/Procedural music generation tools.
    
    Features:
    - Markov Melody Generator
    - Genetic Algorithm Evolution
    - Cellular Automata Rhythms
    - L-System Patterns
    - Text-to-Melody
    - Color-to-Harmony
    """
    
    # Signals
    melody_generated = Signal(list)  # List of (note, velocity, start, duration)
    rhythm_generated = Signal(list)  # List of trigger times
    harmony_generated = Signal(list)  # List of chord degrees
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('generator_panel')
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Title
        title = QLabel("🎲 GENERATIVE TOOLS")
        title.setObjectName('generator_title')
        layout.addWidget(title)
        
        # Tool selector
        self.tool_tabs = QTabWidget()
        layout.addWidget(self.tool_tabs)
        
        # === MARKOV TAB ===
        markov_widget = QWidget()
        markov_layout = QVBoxLayout(markov_widget)
        
        markov_desc = QLabel(
            "Generate melodies using probabilistic Markov chains.\n"
            "Higher temperature = more randomness."
        )
        markov_desc.setWordWrap(True)
        markov_desc.setObjectName('transparent')
        markov_layout.addWidget(markov_desc)
        
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("Temperature:"))
        self.markov_temp = QSlider(QtCore.Qt.Orientation.Horizontal)
        self.markov_temp.setRange(0, 100)
        self.markov_temp.setValue(70)
        temp_layout.addWidget(self.markov_temp)
        self.markov_temp_label = QLabel("0.7")
        temp_layout.addWidget(self.markov_temp_label)
        self.markov_temp.valueChanged.connect(
            lambda v: self.markov_temp_label.setText(f"{v/100:.2f}")
        )
        markov_layout.addLayout(temp_layout)
        
        notes_layout = QHBoxLayout()
        notes_layout.addWidget(QLabel("Notes:"))
        self.markov_notes = QSpinBox()
        self.markov_notes.setRange(4, 64)
        self.markov_notes.setValue(16)
        notes_layout.addWidget(self.markov_notes)
        markov_layout.addLayout(notes_layout)
        
        markov_btn = QPushButton("Generate Markov Melody")
        markov_btn.setObjectName('accent_button')
        markov_btn.clicked.connect(self.on_generate_markov)
        markov_layout.addWidget(markov_btn)
        markov_layout.addStretch()
        
        self.tool_tabs.addTab(markov_widget, "🎲 Markov")
        
        # === GENETIC TAB ===
        genetic_widget = QWidget()
        genetic_layout = QVBoxLayout(genetic_widget)
        
        genetic_desc = QLabel(
            "Evolve melodies through natural selection.\n"
            "More generations = more refined results."
        )
        genetic_desc.setWordWrap(True)
        genetic_desc.setObjectName('transparent')
        genetic_layout.addWidget(genetic_desc)
        
        gen_layout = QHBoxLayout()
        gen_layout.addWidget(QLabel("Generations:"))
        self.genetic_generations = QSpinBox()
        self.genetic_generations.setRange(10, 500)
        self.genetic_generations.setValue(50)
        gen_layout.addWidget(self.genetic_generations)
        genetic_layout.addLayout(gen_layout)
        
        pop_layout = QHBoxLayout()
        pop_layout.addWidget(QLabel("Population:"))
        self.genetic_population = QSpinBox()
        self.genetic_population.setRange(8, 64)
        self.genetic_population.setValue(16)
        pop_layout.addWidget(self.genetic_population)
        genetic_layout.addLayout(pop_layout)
        
        genetic_btn = QPushButton("Evolve Melody")
        genetic_btn.setObjectName('accent_button')
        genetic_btn.clicked.connect(self.on_generate_genetic)
        genetic_layout.addWidget(genetic_btn)
        genetic_layout.addStretch()
        
        self.tool_tabs.addTab(genetic_widget, "🧬 Genetic")
        
        # === CELLULAR TAB ===
        cellular_widget = QWidget()
        cellular_layout = QVBoxLayout(cellular_widget)
        
        cellular_desc = QLabel(
            "Generate rhythms using cellular automata rules.\n"
            "Different rules create different patterns."
        )
        cellular_desc.setWordWrap(True)
        cellular_desc.setObjectName('transparent')
        cellular_layout.addWidget(cellular_desc)
        
        rule_layout = QHBoxLayout()
        rule_layout.addWidget(QLabel("Rule:"))
        self.cellular_rule = QComboBox()
        self.cellular_rule.addItems([
            "Rule 30 (Chaotic)",
            "Rule 90 (Sierpinski)",
            "Rule 110 (Complex)",
            "Rule 184 (Traffic)",
        ])
        rule_layout.addWidget(self.cellular_rule)
        cellular_layout.addLayout(rule_layout)
        
        density_layout = QHBoxLayout()
        density_layout.addWidget(QLabel("Density:"))
        self.cellular_density = QSlider(QtCore.Qt.Orientation.Horizontal)
        self.cellular_density.setRange(10, 90)
        self.cellular_density.setValue(30)
        density_layout.addWidget(self.cellular_density)
        self.cellular_density_label = QLabel("30%")
        density_layout.addWidget(self.cellular_density_label)
        self.cellular_density.valueChanged.connect(
            lambda v: self.cellular_density_label.setText(f"{v}%")
        )
        cellular_layout.addLayout(density_layout)
        
        cellular_btn = QPushButton("Generate Cellular Rhythm")
        cellular_btn.setObjectName('accent_button')
        cellular_btn.clicked.connect(self.on_generate_cellular)
        cellular_layout.addWidget(cellular_btn)
        cellular_layout.addStretch()
        
        self.tool_tabs.addTab(cellular_widget, "🔲 Cellular")
        
        # === TEXT TAB ===
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        
        text_desc = QLabel(
            "Convert any text into a melody.\n"
            "Each character becomes a note."
        )
        text_desc.setWordWrap(True)
        text_desc.setObjectName('transparent')
        text_layout.addWidget(text_desc)
        
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Type anything here...")
        self.text_input.setMaximumHeight(100)
        text_layout.addWidget(self.text_input)
        
        text_btn = QPushButton("Convert Text to Melody")
        text_btn.setObjectName('accent_button')
        text_btn.clicked.connect(self.on_generate_text)
        text_layout.addWidget(text_btn)
        text_layout.addStretch()
        
        self.tool_tabs.addTab(text_widget, "📝 Text")
        
        # === COLOR TAB ===
        color_widget = QWidget()
        color_layout = QVBoxLayout(color_widget)
        
        color_desc = QLabel(
            "Pick a color to generate a harmony.\n"
            "Hue → Root note, Saturation → Chord type."
        )
        color_desc.setWordWrap(True)
        color_desc.setObjectName('transparent')
        color_layout.addWidget(color_desc)
        
        # Color picker buttons (simplified)
        color_grid = QGridLayout()
        self.color_buttons = []
        colors = [
            ("#ff5c5c", "C"), ("#ff8c4c", "C#"), ("#ffb84c", "D"),
            ("#ffe04c", "D#"), ("#e8ff4c", "E"), ("#8cff4c", "F"),
            ("#4cff8c", "F#"), ("#4cffff", "G"), ("#4c8cff", "G#"),
            ("#4c4cff", "A"), ("#8c4cff", "A#"), ("#ff4cff", "B"),
        ]
        for i, (color, note) in enumerate(colors):
            btn = QPushButton(note)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {color};
                    border: 2px solid transparent;
                    border-radius: 8px;
                    padding: 12px;
                    color: #0a0a0f;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    border-color: white;
                }}
            """)
            btn.clicked.connect(lambda checked, c=color, n=i: self.on_color_selected(c, n))
            color_grid.addWidget(btn, i // 4, i % 4)
            self.color_buttons.append(btn)
        color_layout.addLayout(color_grid)
        
        self.selected_color_label = QLabel("Selected: None")
        self.selected_color_label.setObjectName('transparent')
        color_layout.addWidget(self.selected_color_label)
        
        color_btn = QPushButton("Generate Harmony from Color")
        color_btn.setObjectName('accent_button')
        color_btn.clicked.connect(self.on_generate_color)
        color_layout.addWidget(color_btn)
        color_layout.addStretch()
        
        self.tool_tabs.addTab(color_widget, "🎨 Color")
        
        # Current color state
        self.selected_color = None
        self.selected_note = None
    
    # === EVENT HANDLERS ===
    
    def on_generate_markov(self):
        temperature = self.markov_temp.value() / 100.0
        num_notes = self.markov_notes.value()
        print(f"🎲 Generating Markov melody: temp={temperature}, notes={num_notes}")
        # TODO: Call engine IPC
        self.melody_generated.emit([])
    
    def on_generate_genetic(self):
        generations = self.genetic_generations.value()
        population = self.genetic_population.value()
        print(f"🧬 Evolving melody: gen={generations}, pop={population}")
        # TODO: Call engine IPC
        self.melody_generated.emit([])
    
    def on_generate_cellular(self):
        rule_text = self.cellular_rule.currentText()
        rule = int(rule_text.split()[1])
        density = self.cellular_density.value() / 100.0
        print(f"🔲 Generating cellular rhythm: rule={rule}, density={density}")
        # TODO: Call engine IPC
        self.rhythm_generated.emit([])
    
    def on_generate_text(self):
        text = self.text_input.toPlainText()
        if not text.strip():
            text = "Intuitives"
        print(f"📝 Converting text to melody: '{text[:20]}...'")
        # TODO: Call engine IPC
        self.melody_generated.emit([])
    
    def on_color_selected(self, color, note_index):
        self.selected_color = color
        self.selected_note = note_index
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.selected_color_label.setText(
            f"Selected: {note_names[note_index]} ({color})"
        )
        self.selected_color_label.setStyleSheet(f"color: {color};")
    
    def on_generate_color(self):
        if self.selected_color is None:
            print("🎨 No color selected, using random")
            import random
            self.selected_note = random.randint(0, 11)
        print(f"🎨 Generating harmony from color note={self.selected_note}")
        # TODO: Call engine IPC
        self.harmony_generated.emit([])


class ChromasynesthesiaWidget(QWidget):
    """
    Visual indicator that shows the current color based on pitch.
    Updates in real-time based on audio analysis.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('chroma_indicator')
        self.setMinimumSize(60, 60)
        self.setMaximumSize(60, 60)
        self.current_color = QColor("#7c3aed")
        self.target_color = self.current_color
        
        # Animation timer
        self.animation_timer = QtCore.QTimer(self)
        self.animation_timer.timeout.connect(self._animate_color)
        self.animation_timer.start(16)  # ~60fps
    
    def set_note(self, midi_note):
        """Set color based on MIDI note (chromasynesthesia mapping)"""
        note_in_octave = midi_note % 12
        color_hex = CHROMA_COLORS.get(note_in_octave, "#7c3aed")
        self.target_color = QColor(color_hex)
    
    def set_color(self, color):
        """Set target color directly"""
        if isinstance(color, str):
            self.target_color = QColor(color)
        else:
            self.target_color = color
    
    def _animate_color(self):
        """Smoothly interpolate current color toward target"""
        if self.current_color == self.target_color:
            return
        
        # Interpolate RGB
        r = self.current_color.red() + (self.target_color.red() - self.current_color.red()) * 0.15
        g = self.current_color.green() + (self.target_color.green() - self.current_color.green()) * 0.15
        b = self.current_color.blue() + (self.target_color.blue() - self.current_color.blue()) * 0.15
        
        self.current_color = QColor(int(r), int(g), int(b))
        self.update()
    
    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter, QBrush, QPen
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw outer glow
        glow_color = QColor(self.current_color)
        glow_color.setAlpha(80)
        painter.setBrush(QBrush(glow_color))
        painter.setPen(QPen(QtCore.Qt.PenStyle.NoPen))
        painter.drawEllipse(2, 2, 56, 56)
        
        # Draw main circle
        painter.setBrush(QBrush(self.current_color))
        painter.setPen(QPen(QColor(255, 255, 255, 50), 2))
        painter.drawEllipse(8, 8, 44, 44)
