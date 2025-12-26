# Intuitives Theme Guidelines: Neobrutalist Evolution

## 🎨 Visual Identity & Philosophy

The **Intuitives** aesthetic is a fusion of **Neobrutalism** and **Chromasynesthesia**. It rejects the pseudo-realistic "skeuomorphic" look of traditional DAWs in favor of a bold, high-contrast, and utilitarian interface that feels alive and experimental.

### Core Principles

1. **Bold Boundaries**: Every element is defined by thick, solid borders. No soft shadows; only hard, offset "drop-blocks".
2. **Functional Color**: Color is never just decoration. In Intuitives, color **is** pitch (Chromasynesthesia), intensity, or state.
3. **Motion as Feedback**: Every interaction must feel physical. Buttons should "sink", sliders should "bounce", and waveforms should "shimmer".
4. **Adaptive Context**: The UI responds to the music. If the tempo is fast, the UI animations speed up. If the sound is "bright", the theme shifts towards higher luminance.

---

## 🖌️ Color System: Chromasynesthesia Spectrum

We use a standard 12-note color mapping inspired by Scriabin and modern synesthesia research.

| Note   | Color     | Hex       | Role            |
| :----- | :-------- | :-------- | :-------------- |
| **C**  | Crimson   | `#FF5C5C` | Grounding, Root |
| **C#** | Vermilion | `#FF8C4C` | Tension         |
| **D**  | Amber     | `#FFB84C` | Warmth, Joy     |
| **D#** | Saffron   | `#FFE04C` | Vibrancy        |
| **E**  | Citron    | `#E8FF4C` | Brightness      |
| **F**  | Lime      | `#8CFF4C` | Nature, Growth  |
| **F#** | Emerald   | `#4CFF8C` | Sharpness       |
| **G**  | Cyan      | `#4CFFFF` | Space, Air      |
| **G#** | Azure     | `#4C8CFF` | Depth           |
| **A**  | Indigo    | `#4C4CFF` | Stability       |
| **A#** | Violet    | `#8C4CFF` | Complexity      |
| **B**  | Magenta   | `#FF4CFF` | Resolution      |

### UI Neutrals

- **Background (Base)**: `#050505` (Deep Space)
- **Panel (Surface)**: `#12121A` (Obsidian)
- **Border**: `#F8FAFC` (Ghost White) or `#000000` (Depending on contrast)
- **Hard Shadow**: `#000000` with 100% opacity, 4px offset.

---

## 🅰️ Typography

Use modern, highly legible sans-serif fonts that support the "raw" feeling of neobrutalism.

- **Primary Font**: `Outfit` (Headings, Branding)
- **Secondary Font**: `Inter` (UI elements, Small text)
- **Mono Font**: `JetBrains Mono` (Parameters, Code, Matrix values)

### Hierarchy

- **H1 (Logo)**: 32px, Bold, All Caps, 2px Letter Spacing.
- **H2 (Section)**: 24px, Semi-Bold.
- **Body**: 13px, Regular.
- **Labels**: 11px, Medium, All Caps.

---

## 🧊 Component Guidelines

### 1. Buttons (The "Push" Effect)

- **Resting**: 2px solid border, no shadow.
- **Hover**: 2px solid border, 4px hard shadow (offset bottom-right).
- **Active (Pressed)**: No shadow, translated 4px down-right to "fill" the shadow space.
- **Colors**: Use Primary Purple (`#7C3AED`) or Secondary Cyan (`#06B6D4`).

### 2. Sliders (The "Vibe" Control)

- **Track**: 3px solid black line.
- **Thumb**: Large square (16x16px) with a bold color. Thumb should "glow" when touched.
- **Interaction**: Spring animation on release. If the user "flings" a slider, the value should overshoot slightly and settle (elastic easing).

### 3. Waveform Displays

- **Style**: Vector-based, solid fill.
- **Colors**: Gradient from Blue (low freq) to Red (high freq).
- **Animation**: Real-time spectral blurring when effects are applied (e.g., reverb makes the waveform "ghost" slightly).

### 4. Mixer Strips

- **Neobrutalist cards**: Each track is a card with a thick border.
- **Metamorphosis**: When a track is soloed, all other tracks "collapse" into thin lines, while the soloed track expands with more details.

---

## 💻 Implementation: C / C++ Theme Engine

The theme is controlled via the `Intuitives::Theme` subsystem. Constants are defined in `intuitives_theme.h`.

```cpp
// intuitives_theme.h
#ifndef INTUITIVES_THEME_H
#define INTUITIVES_THEME_H

#define INT_COLOR_BG          0x050505FF
#define INT_COLOR_PANEL       0x12121AFF
#define INT_COLOR_BORDER      0xF8FAFCFF
#define INT_COLOR_SHADOW      0x000000FF

#define INT_BORDER_WIDTH      2
#define INT_SHADOW_OFFSET     4

typedef struct {
    uint32_t color;
    float border_width;
    float corner_radius; // Usually 0 for strict neobrutalism
    bool has_hard_shadow;
} IntStyle;

// Theme mapping for Chromasynesthesia
static const uint32_t CHROMA_MAP[12] = {
    0xFF5C5CFF, // C
    0xFF8C4CFF, // C#
    0xFFB84CFF, // D
    0xFFE04CFF, // D#
    0xE8FF4CFF, // E
    0x8CFF4CFF, // F
    0x4CFF8CFF, // F#
    0x4CFFFFFF, // G
    0x4C8CFFFF, // G#
    0x4C4CFFFF, // A
    0x8C4CFFFF, // A#
    0xFF4CFFFF  // B
};

#endif
```

### Rendering Logic (Pseudo-code)

```cpp
void draw_button(const char* label, Rect rect, IntStyle style) {
    if (is_pressed) {
        // Move button into the shadow area
        rect.x += INT_SHADOW_OFFSET;
        rect.y += INT_SHADOW_OFFSET;
        draw_rect_filled(rect, style.color);
        draw_rect_outline(rect, INT_COLOR_BORDER, INT_BORDER_WIDTH);
    } else {
        // Draw hard shadow
        Rect shadow = {rect.x + INT_SHADOW_OFFSET, rect.y + INT_SHADOW_OFFSET, rect.w, rect.h};
        draw_rect_filled(shadow, INT_COLOR_SHADOW);

        // Draw button
        draw_rect_filled(rect, style.color);
        draw_rect_outline(rect, INT_COLOR_BORDER, INT_BORDER_WIDTH);
    }
    draw_text_centered(rect, label, FONT_INTER, COLOR_TEXT_PRIMARY);
}
```

---

## ⚡ Animations & Response

- **Global Ease**: `cubic-bezier(0.34, 1.56, 0.64, 1)` (Back-Out/Spring).
- **Framerate**: Maintain 120fps on ProMotion displays.
- **Latency**: Input-to-UI response < 5ms.

---

## 📱 Responsiveness

The UI uses a **Grid System**:

- **Small Screens**: Single Column, collapsed sidebars.
- **Medium Screens**: Two Columns (Sequencer + Inspector).
- **Large Screens**: Multi-Panel (Sequencer, Mixer, AI Assistant, Visualizer).

---

## 🏷️ Branding: The Intuitives Logo

The logo is a stylized **'i'** that morphs into a **sine wave**.

- **Orientation**: Top-Left.
- **Animation**: On launch, the sine wave "pulses" in sync with a default heartbeat sound.

---

**Status**: 100% Native | 100% Sovereign | 100% Intuitive
