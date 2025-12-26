"""L-System Generator for Intuitives DAW

Lindenmayer Systems (L-Systems) for generating melodic and rhythmic patterns.
Includes visual feedback showing the evolution of the pattern.
"""
from typing import List, Dict, Optional, Tuple, Callable
from dataclasses import dataclass, field
import math
import random
import logging

logger = logging.getLogger(__name__)


@dataclass
class LSystemRule:
    """A single L-System production rule"""
    predecessor: str
    successor: str
    probability: float = 1.0  # For stochastic L-Systems


@dataclass
class LSystemConfig:
    """Configuration for an L-System"""
    axiom: str
    rules: List[LSystemRule]
    iterations: int = 4
    
    # Musical mapping
    angle_increment: float = 30.0  # Degrees for + and - operations
    length_factor: float = 0.8     # Scale factor for each iteration
    note_mapping: Dict[str, int] = field(default_factory=dict)


@dataclass
class LSystemState:
    """Current state during L-System interpretation"""
    x: float = 0.0
    y: float = 0.0
    angle: float = 90.0  # Start pointing up
    depth: int = 0
    note: int = 60       # Current MIDI note
    velocity: float = 0.8
    duration: float = 0.25


@dataclass
class LSystemOutput:
    """Output from L-System generation"""
    string: str
    notes: List[Dict]
    path: List[Tuple[float, float]]  # (x, y) coordinates for visualization
    segments: List[Tuple[float, float, float, float]]  # (x1, y1, x2, y2)


class LSystemGenerator:
    """
    L-System generator for music and visuals.
    
    Implements various L-System types:
    - Deterministic (D0L)
    - Stochastic (0L with probabilities)
    - Context-free parametric
    
    Usage:
        gen = LSystemGenerator()
        
        # Koch curve style melody
        config = LSystemConfig(
            axiom="F",
            rules=[LSystemRule("F", "F+F-F-F+F")],
            iterations=3
        )
        output = gen.generate(config)
        
        # Get MIDI notes
        notes = output.notes
        
        # Get visualization path
        path = output.path
    """
    
    # Preset configurations
    PRESETS = {
        "koch_curve": LSystemConfig(
            axiom="F",
            rules=[LSystemRule("F", "F+F-F-F+F")],
            iterations=3,
            angle_increment=90.0,
        ),
        "sierpinski_triangle": LSystemConfig(
            axiom="F-G-G",
            rules=[
                LSystemRule("F", "F-G+F+G-F"),
                LSystemRule("G", "GG"),
            ],
            iterations=4,
            angle_increment=120.0,
        ),
        "dragon_curve": LSystemConfig(
            axiom="FX",
            rules=[
                LSystemRule("X", "X+YF+"),
                LSystemRule("Y", "-FX-Y"),
            ],
            iterations=8,
            angle_increment=90.0,
        ),
        "plant_fractal": LSystemConfig(
            axiom="X",
            rules=[
                LSystemRule("X", "F+[[X]-X]-F[-FX]+X"),
                LSystemRule("F", "FF"),
            ],
            iterations=4,
            angle_increment=25.0,
        ),
        "penrose_tiling": LSystemConfig(
            axiom="[7]++[7]++[7]++[7]++[7]",
            rules=[
                LSystemRule("6", "81++91----71[-81----61]++"),
                LSystemRule("7", "+81--91[---61--71]+"),
                LSystemRule("8", "-61++71[+++81++91]-"),
                LSystemRule("9", "--81++++61[+91++++71]--71"),
                LSystemRule("1", ""),
            ],
            iterations=3,
            angle_increment=36.0,
        ),
        "musical_arpeggio": LSystemConfig(
            axiom="N",
            rules=[
                LSystemRule("N", "N+N-N"),  # Note pattern
            ],
            iterations=3,
            angle_increment=60.0,
            note_mapping={"N": 0},  # Relative semitones
        ),
        "rhythmic_pattern": LSystemConfig(
            axiom="X",
            rules=[
                LSystemRule("X", "[X][+X][-X]"),
            ],
            iterations=3,
            angle_increment=120.0,
        ),
    }
    
    def __init__(self):
        self._stack: List[LSystemState] = []
        self._current_time: float = 0.0
    
    def generate(
        self,
        config: LSystemConfig,
        seed: Optional[int] = None
    ) -> LSystemOutput:
        """
        Generate L-System output.
        
        Args:
            config: L-System configuration
            seed: Random seed for stochastic L-Systems
        
        Returns:
            LSystemOutput with string, notes, and visualization data
        """
        if seed is not None:
            random.seed(seed)
        
        # Generate the L-System string
        current = config.axiom
        for _ in range(config.iterations):
            current = self._apply_rules(current, config.rules)
        
        # Interpret the string
        notes, path, segments = self._interpret(
            current, config, 
            base_note=60, 
            base_velocity=0.8
        )
        
        return LSystemOutput(
            string=current,
            notes=notes,
            path=path,
            segments=segments,
        )
    
    def _apply_rules(self, string: str, rules: List[LSystemRule]) -> str:
        """Apply production rules to generate next iteration"""
        result = []
        
        for char in string:
            replaced = False
            
            # Find matching rules
            matching_rules = [r for r in rules if r.predecessor == char]
            
            if matching_rules:
                # Stochastic selection
                if len(matching_rules) > 1:
                    # Weighted random selection
                    total_prob = sum(r.probability for r in matching_rules)
                    rand_val = random.random() * total_prob
                    cumulative = 0.0
                    
                    for rule in matching_rules:
                        cumulative += rule.probability
                        if rand_val <= cumulative:
                            result.append(rule.successor)
                            replaced = True
                            break
                else:
                    # Deterministic or single stochastic rule
                    rule = matching_rules[0]
                    if rule.probability >= 1.0 or random.random() < rule.probability:
                        result.append(rule.successor)
                        replaced = True
            
            if not replaced:
                result.append(char)
        
        return ''.join(result)
    
    def _interpret(
        self,
        string: str,
        config: LSystemConfig,
        base_note: int = 60,
        base_velocity: float = 0.8
    ) -> Tuple[List[Dict], List[Tuple[float, float]], List[Tuple[float, float, float, float]]]:
        """
        Interpret L-System string as music and visuals.
        
        Interpretation symbols:
        - F, G, A-Z: Draw forward (generate note)
        - f: Move forward (no note)
        - +: Turn right
        - -: Turn left
        - [: Push state (save position)
        - ]: Pop state (restore position)
        - |: Reverse direction (180°)
        - 0-9: Set note offset
        """
        self._stack = []
        state = LSystemState(note=base_note, velocity=base_velocity)
        self._current_time = 0.0
        
        notes = []
        path = [(state.x, state.y)]
        segments = []
        
        step_length = 10.0  # Base step length for visualization
        
        i = 0
        while i < len(string):
            char = string[i]
            
            if char.isupper() and char not in ('X', 'Y'):
                # Draw forward - generate note
                old_x, old_y = state.x, state.y
                
                # Calculate new position
                rad = math.radians(state.angle)
                state.x += step_length * math.cos(rad) * (config.length_factor ** state.depth)
                state.y += step_length * math.sin(rad) * (config.length_factor ** state.depth)
                
                path.append((state.x, state.y))
                segments.append((old_x, old_y, state.x, state.y))
                
                # Generate MIDI note
                note_offset = config.note_mapping.get(char, 0)
                notes.append({
                    'note': state.note + note_offset,
                    'velocity': int(state.velocity * 127),
                    'start': self._current_time,
                    'duration': state.duration,
                })
                
                self._current_time += state.duration
            
            elif char == 'f':
                # Move forward without note
                rad = math.radians(state.angle)
                state.x += step_length * math.cos(rad) * (config.length_factor ** state.depth)
                state.y += step_length * math.sin(rad) * (config.length_factor ** state.depth)
                path.append((state.x, state.y))
            
            elif char == '+':
                # Turn right
                state.angle += config.angle_increment
                state.note += 1  # Go up a semitone
            
            elif char == '-':
                # Turn left
                state.angle -= config.angle_increment
                state.note -= 1  # Go down a semitone
            
            elif char == '|':
                # Reverse direction
                state.angle += 180.0
            
            elif char == '[':
                # Push state
                self._stack.append(LSystemState(
                    x=state.x, y=state.y, angle=state.angle,
                    depth=state.depth, note=state.note,
                    velocity=state.velocity, duration=state.duration
                ))
                state.depth += 1
                state.velocity *= 0.9  # Softer in branches
            
            elif char == ']':
                # Pop state
                if self._stack:
                    popped = self._stack.pop()
                    state.x = popped.x
                    state.y = popped.y
                    state.angle = popped.angle
                    state.depth = popped.depth
                    state.note = popped.note
                    state.velocity = popped.velocity
                    state.duration = popped.duration
            
            elif char.isdigit():
                # Set note offset
                state.note = base_note + int(char) * 2
            
            i += 1
        
        return notes, path, segments
    
    def generate_from_preset(
        self,
        preset_name: str,
        iterations: Optional[int] = None,
        seed: Optional[int] = None
    ) -> LSystemOutput:
        """
        Generate from a preset L-System.
        
        Args:
            preset_name: Name of preset (see PRESETS)
            iterations: Override number of iterations
            seed: Random seed
        
        Returns:
            LSystemOutput
        """
        if preset_name not in self.PRESETS:
            raise ValueError(f"Unknown preset: {preset_name}. Available: {list(self.PRESETS.keys())}")
        
        config = self.PRESETS[preset_name]
        
        if iterations is not None:
            # Create modified config
            config = LSystemConfig(
                axiom=config.axiom,
                rules=config.rules,
                iterations=iterations,
                angle_increment=config.angle_increment,
                length_factor=config.length_factor,
                note_mapping=config.note_mapping,
            )
        
        return self.generate(config, seed)
    
    @staticmethod
    def list_presets() -> List[str]:
        """Get list of available presets"""
        return list(LSystemGenerator.PRESETS.keys())


class LSystemVisualizer:
    """
    Visualizer for L-System patterns.
    Generates SVG or provides data for real-time rendering.
    """
    
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
    
    def to_svg(
        self,
        output: LSystemOutput,
        stroke_color: str = "#00AAFF",
        background: str = "#1a1a1a"
    ) -> str:
        """
        Generate SVG visualization from L-System output.
        
        Args:
            output: LSystemOutput from generator
            stroke_color: Line color
            background: Background color
        
        Returns:
            SVG string
        """
        if not output.segments:
            return f'<svg width="{self.width}" height="{self.height}"></svg>'
        
        # Calculate bounds
        min_x = min(s[0] for s in output.segments)
        max_x = max(s[2] for s in output.segments)
        min_y = min(s[1] for s in output.segments)
        max_y = max(s[3] for s in output.segments)
        
        # Add padding
        padding = 20
        data_width = max_x - min_x + 0.001
        data_height = max_y - min_y + 0.001
        
        scale = min(
            (self.width - 2 * padding) / data_width,
            (self.height - 2 * padding) / data_height
        )
        
        # Transform function
        def tx(x): return (x - min_x) * scale + padding
        def ty(y): return self.height - ((y - min_y) * scale + padding)
        
        # Build SVG
        lines = [
            f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">',
            f'<rect width="100%" height="100%" fill="{background}"/>',
        ]
        
        # Draw segments with gradient opacity
        num_segments = len(output.segments)
        for i, (x1, y1, x2, y2) in enumerate(output.segments):
            opacity = 0.3 + 0.7 * (i / num_segments)  # Fade in
            lines.append(
                f'<line x1="{tx(x1):.1f}" y1="{ty(y1):.1f}" '
                f'x2="{tx(x2):.1f}" y2="{ty(y2):.1f}" '
                f'stroke="{stroke_color}" stroke-width="1.5" '
                f'stroke-opacity="{opacity:.2f}" stroke-linecap="round"/>'
            )
        
        lines.append('</svg>')
        return '\n'.join(lines)
    
    def get_normalized_path(self, output: LSystemOutput) -> List[Tuple[float, float]]:
        """
        Get normalized path coordinates (0-1 range).
        
        Args:
            output: LSystemOutput
        
        Returns:
            List of (x, y) tuples normalized to 0-1
        """
        if not output.path:
            return []
        
        xs = [p[0] for p in output.path]
        ys = [p[1] for p in output.path]
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        range_x = max_x - min_x + 0.001
        range_y = max_y - min_y + 0.001
        
        return [
            ((x - min_x) / range_x, (y - min_y) / range_y)
            for x, y in output.path
        ]


# Convenience functions
def generate_lsystem(
    preset: str = "plant_fractal",
    iterations: int = 4,
    seed: Optional[int] = None
) -> LSystemOutput:
    """Quick L-System generation"""
    gen = LSystemGenerator()
    return gen.generate_from_preset(preset, iterations, seed)


def lsystem_to_midi(output: LSystemOutput) -> List[Dict]:
    """Extract MIDI notes from L-System output"""
    return output.notes


def lsystem_to_svg(output: LSystemOutput, **kwargs) -> str:
    """Generate SVG visualization"""
    viz = LSystemVisualizer()
    return viz.to_svg(output, **kwargs)
