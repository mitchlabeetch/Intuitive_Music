# Intuitives DAW — Neobrutalist Theme Specification

> **"Does this sound cool?"** — The only rule.

---

## 📚 Table of Contents

1. [Philosophy & Vision](#-philosophy--vision)
2. [Design Language](#-design-language)
3. [Color System](#-color-system)
4. [Typography](#-typography)
5. [Iconography](#-iconography)
6. [Component Guidelines](#-component-guidelines)
7. [Animation & Interaction](#-animation--interaction)
8. [Responsive Adaptation](#-responsive-adaptation)
9. [Accessibility](#-accessibility)
10. [Implementation Reference](#-implementation-reference)

---

## 🌟 Philosophy & Vision

### Core Principles

Intuitives reimagines music production by **removing barriers** and **embracing creativity**. The UI must embody:

| Principle              | UI Expression                                                      |
| ---------------------- | ------------------------------------------------------------------ |
| **Rule-Free**          | No conventional DAW visual constraints; bold, experimental layouts |
| **Experiment-First**   | Every control invites interaction; playful, tactile elements       |
| **Visual & Intuitive** | Chromasynesthesia color-coding; sound made visible                 |
| **No Learning Curve**  | Self-explanatory icons; progressive disclosure                     |
| **Accessible**         | High contrast; keyboard-friendly; screen reader compatible         |

### Neobrutalist Manifesto

Neobrutalism is the **anti-gloss** design movement. For Intuitives, this means:

- **Honest Materials**: No fake gradients mimicking glass or metal
- **Bold Borders**: Thick, confident outlines (3-4px black strokes)
- **Hard Shadows**: Zero-blur offset shadows creating depth
- **Raw Colors**: Saturated, clashing palettes that celebrate digital
- **Physical Feel**: Elements feel like stickers you can peel off

---

## 🎨 Design Language

### Visual Identity

```
┌─────────────────────────────────────────────────────────────┐
│  INTUITIVES                                                 │
│  ══════════                                                 │
│                                                             │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│   │  ▶ PLAY │  │  ■ STOP │  │  ● REC  │  │  ↻ LOOP │       │
│   └─────────┘  └─────────┘  └─────────┘  └─────────┘       │
│        │            │            │            │             │
│        └────────────┴────────────┴────────────┘             │
│                    Hard shadows create depth                │
└─────────────────────────────────────────────────────────────┘
```

### The "Sticker" Aesthetic

Every interactive element is a **discrete physical entity**:

- **Raised State**: `box-shadow: 4px 4px 0 #000`
- **Hover State**: `box-shadow: 2px 2px 0 #000` (slightly "lifted")
- **Pressed State**: `box-shadow: 0 0 0 #000` (flush with surface)

---

## 🎨 Color System

### Primary Action Color — "Electric Indigo"

| Role        | Color Name          | Hex Code  | Usage                                     |
| ----------- | ------------------- | --------- | ----------------------------------------- |
| **Primary** | **Electric Indigo** | `#6366F1` | Tools, toggles, FX, stop, general actions |

> **Why Electric Indigo?** It's distinctive, modern, and praised in design communities (used by TailwindCSS as `indigo-500`). Unlike overused purples/magentas, it provides a fresh, professional identity while maintaining vibrance.

### Chromasynesthesia Palette — "Note Colors"

Based on the Intuitives philosophy of **seeing sound**, each note maps to a color:

| Note | Color Name    | Hex Code  | Usage                   |
| ---- | ------------- | --------- | ----------------------- |
| C    | **Crimson**   | `#FF3366` | Record, alerts, solo    |
| D    | **Tangerine** | `#FF9933` | Loop, warnings          |
| E    | **Sunburst**  | `#FFEE33` | Highlights, selection   |
| F    | **Emerald**   | `#33FF66` | Play, success, AI zones |
| G    | **Cyan**      | `#33EEFF` | Markers, navigation     |
| A    | **Sapphire**  | `#3366FF` | Meters, analysis        |
| B    | **Violet**    | `#A855F7` | Creative accents        |

### Functional Palette

| Role                  | Light Mode | Dark Mode | Usage Context          |
| --------------------- | ---------- | --------- | ---------------------- |
| **Surface Primary**   | `#FFFEF0`  | `#1A1A1F` | Main background        |
| **Surface Secondary** | `#F5F5E8`  | `#252530` | Panels, cards          |
| **Surface Tertiary**  | `#E8E8D8`  | `#2F2F3A` | Nested containers      |
| **Border**            | `#1A1A1F`  | `#E5E5E0` | All component borders  |
| **Text Primary**      | `#1A1A1F`  | `#FFFEF0` | Headlines, labels      |
| **Text Secondary**    | `#4A4A4F`  | `#B0B0B5` | Descriptions, values   |
| **Text Muted**        | `#8A8A8F`  | `#6A6A6F` | Placeholders, disabled |

### State Palette

| State            | Color                        | Application                  |
| ---------------- | ---------------------------- | ---------------------------- |
| **On/Active**    | Chromasynesthesia color      | Active transport, enabled FX |
| **Off/Inactive** | `#4A4A4F` (Dark Gray)        | Inactive buttons             |
| **Hover**        | 10% lighter + shifted shadow | Pre-interaction feedback     |
| **Pressed**      | 10% darker + no shadow       | During interaction           |
| **Disabled**     | `#8A8A8F` @ 50% opacity      | Non-interactive state        |
| **Focus**        | `#FFEE33` 3px outline        | Keyboard navigation          |

### Palette Variables (YAML)

```yaml
# /palettes/intuitives.yaml

# Chromasynesthesia Scale
note_c: "#FF3366" # Crimson
note_d: "#FF9933" # Tangerine
note_e: "#FFEE33" # Sunburst
note_f: "#33FF66" # Emerald
note_g: "#33EEFF" # Cyan
note_a: "#3366FF" # Sapphire
note_b: "#FF33EE" # Magenta

# Functional (Dark Mode)
surface_primary: "#1A1A1F"
surface_secondary: "#252530"
surface_tertiary: "#2F2F3A"
border: "#E5E5E0"
text_primary: "#FFFEF0"
text_secondary: "#B0B0B5"
text_muted: "#6A6A6F"

# Primary Action
primary: "#6366F1" # Electric Indigo

# Transport
transport_play: "#33FF66"
transport_stop: "#6366F1" # Electric Indigo
transport_rec: "#FF3366"
transport_loop: "#FF9933"
transport_pause: "#33EEFF"

# Utility
white: "#FFFEF0"
black: "#1A1A1F"
shadow: "#000000"
```

---

## 📝 Typography

### Type Scale

| Level         | Font           | Size | Weight | Line Height | Usage           |
| ------------- | -------------- | ---- | ------ | ----------- | --------------- |
| **Display**   | Space Grotesk  | 48px | 700    | 1.1         | Splash, Modals  |
| **H1**        | Space Grotesk  | 32px | 700    | 1.2         | Window titles   |
| **H2**        | Space Grotesk  | 24px | 600    | 1.25        | Section headers |
| **H3**        | Space Grotesk  | 18px | 600    | 1.3         | Panel titles    |
| **Body**      | Inter          | 14px | 400    | 1.5         | General text    |
| **Body Bold** | Inter          | 14px | 600    | 1.5         | Emphasis        |
| **Small**     | Inter          | 12px | 400    | 1.4         | Hints, tooltips |
| **Mono**      | JetBrains Mono | 13px | 400    | 1.5         | Values, code    |
| **Transport** | Space Grotesk  | 28px | 700    | 1           | Clock display   |

### Font Loading (CSS)

```css
/* Google Fonts Import */
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600;700&display=swap");

/* Font Stack */
:root {
  --font-display: "Space Grotesk", system-ui, sans-serif;
  --font-body: "Inter", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", "SF Mono", monospace;
}
```

### Typography in C++ (Qt Stylesheet)

```cpp
// For native Qt widgets
QFont displayFont("Space Grotesk", 48, QFont::Bold);
QFont bodyFont("Inter", 14, QFont::Normal);
QFont monoFont("JetBrains Mono", 13, QFont::Normal);
monoFont.setStyleHint(QFont::Monospace);
```

---

## 🖼️ Iconography

### Icon Design Principles

1. **Canvas Size**: 44×44px (transport), 36×36px (track controls), 24×24px (toolbar)
2. **Stroke Width**: 2px minimum for clarity at all sizes
3. **Corner Radius**: 6px for icon backgrounds
4. **Border**: 3px black border on "on" states
5. **Inner Icon**: Uses `--text-primary` or white depending on background

### Icon Anatomy

```
┌──────────────────────────┐
│ ╭────────────────────╮   │
│ │                    │   │
│ │    ┌──────────┐    │   │ ← 44×44 canvas
│ │    │   ▶     │    │   │ ← centered icon glyph
│ │    └──────────┘    │   │
│ │                    │   │
│ ╰────────────────────╯   │
│        ↑                 │
│   3px border radius      │
│   + neobrutalist shadow  │
└──────────────────────────┘
```

### Icon States

| State              | Background              | Border        | Shadow           | Icon Fill |
| ------------------ | ----------------------- | ------------- | ---------------- | --------- |
| **On (Active)**    | Chromasynesthesia color | 3px `#000`    | `4px 4px 0 #000` | `#FFFEF0` |
| **Off (Inactive)** | `#4A4A4F`               | 3px `#1A1A1F` | `2px 2px 0 #000` | `#B0B0B5` |
| **Hover**          | 10% lighter             | 3px `#000`    | `6px 6px 0 #000` | `#FFFEF0` |
| **Pressed**        | 10% darker              | 3px `#000`    | `0 0 0 #000`     | `#FFFEF0` |
| **Disabled**       | `#6A6A6F`               | None          | None             | `#8A8A8F` |

### Icon Set Reference

| Icon               | Function              | On Color                    | Keyboard |
| ------------------ | --------------------- | --------------------------- | -------- |
| `play-on.svg`      | Start/Resume playback | `#33FF66` (Emerald)         | Space    |
| `stop-on.svg`      | Stop playback         | `#6366F1` (Electric Indigo) | Space    |
| `rec-on.svg`       | Record arm/record     | `#FF3366` (Crimson)         | R        |
| `loop-on.svg`      | Toggle loop           | `#FF9933` (Tangerine)       | L        |
| `mute-on.svg`      | Mute track            | `#6366F1` (Electric Indigo) | M        |
| `solo-on.svg`      | Solo track            | `#FF3366` (Crimson)         | S        |
| `power-on.svg`     | Enable/disable        | `#6366F1` (Electric Indigo) | —        |
| `fx-on.svg`        | Effects enabled       | `#6366F1` (Electric Indigo) | F        |
| `draw-on.svg`      | Pencil/draw mode      | `#6366F1` (Electric Indigo) | D        |
| `erase-on.svg`     | Eraser mode           | `#6366F1` (Electric Indigo) | E        |
| `select-on.svg`    | Selection mode        | `#6366F1` (Electric Indigo) | V        |
| `split-on.svg`     | Split tool            | `#6366F1` (Electric Indigo) | B        |
| `hide-on.svg`      | Hide/close            | `#6366F1` (Electric Indigo) | Esc      |
| `follow-on.svg`    | Follow playhead       | `#33EEFF` (Cyan)            | —        |
| `metronome-on.svg` | Metronome             | `#33EEFF` (Cyan)            | —        |
| `speaker-on.svg`   | Monitor output        | `#33FF66` (Emerald)         | —        |
| `dc-on.svg`        | DC offset filter      | `#3366FF` (Sapphire)        | —        |

---

## 🧩 Component Guidelines

### Transport Bar

```
┌────────────────────────────────────────────────────────────────┐
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐    ┌────────────────┐   ┌─────┐  │
│  │ ▶  │ │ ■  │ │ ●  │ │ ↻  │    │  00:00:00.000  │   │ BPM │  │
│  └────┘ └────┘ └────┘ └────┘    └────────────────┘   └─────┘  │
│    ⬇      ⬇      ⬇      ⬇              ⬇               ⬇      │
│  Play   Stop   Rec   Loop     Time Display (Mono)    Tempo    │
└────────────────────────────────────────────────────────────────┘
```

**CSS/Qt Stylesheet:**

```css
/* Transport container */
.transport-bar {
  background: var(--surface-secondary);
  border: 3px solid var(--border);
  border-radius: 8px;
  padding: 12px 16px;
  display: flex;
  gap: 8px;
  box-shadow: 4px 4px 0 var(--shadow);
}

/* Transport button */
.transport-btn {
  width: 44px;
  height: 44px;
  border: 3px solid var(--black);
  border-radius: 6px;
  cursor: pointer;
  transition: box-shadow 0.1s ease-out, transform 0.1s ease-out;
  box-shadow: 4px 4px 0 var(--shadow);
}

.transport-btn:hover {
  box-shadow: 6px 6px 0 var(--shadow);
  transform: translate(-1px, -1px);
}

.transport-btn:active {
  box-shadow: 0 0 0 var(--shadow);
  transform: translate(4px, 4px);
}

/* Time display */
.time-display {
  font-family: var(--font-mono);
  font-size: 28px;
  font-weight: 700;
  background: var(--surface-tertiary);
  color: var(--text-primary);
  padding: 8px 16px;
  border: 3px solid var(--border);
  border-radius: 6px;
  box-shadow: inset 2px 2px 0 rgba(0, 0, 0, 0.1);
}
```

### Track Header

```
┌────────────────────────────────────────────────────────────────┐
│  🎵 Track 1 - Drums                                            │
│  ┌──────┐  ┌──────┐  ┌──────┐     ╔════════════════════════╗   │
│  │  M   │  │  S   │  │  R   │     ║ ▂▃▅▇█▇▅▃▂▁▂▃▅▇█▇▅▃▂▁   ║   │
│  └──────┘  └──────┘  └──────┘     ╚════════════════════════╝   │
│   Mute     Solo     Rec Arm            Volume Meter            │
│                                                                │
│  ┌────────────────────────────┐                                │
│  │ ●━━━━━━━━━━━━━━━━━━━━━━━━ │  ← Volume Slider              │
│  └────────────────────────────┘                                │
│                                                                │
│  ┌────────────────────────────┐                                │
│  │ ◀━━━━━━●━━━━━━━━━━━━━━━▶ │  ← Pan Dial                   │
│  └────────────────────────────┘                                │
└────────────────────────────────────────────────────────────────┘
```

### Sliders & Knobs

#### Horizontal Slider

```css
.slider-h {
  height: 24px;
  background: var(--surface-tertiary);
  border: 3px solid var(--border);
  border-radius: 4px;
  box-shadow: inset 2px 2px 0 rgba(0, 0, 0, 0.1);
}

.slider-h__track {
  height: 100%;
  background: linear-gradient(
    90deg,
    var(--note-c),
    var(--note-e),
    var(--note-f),
    var(--note-g)
  );
  border-radius: 2px;
}

.slider-h__handle {
  width: 16px;
  height: 32px;
  background: var(--black);
  border: 2px solid var(--white);
  border-radius: 4px;
  cursor: grab;
  box-shadow: 2px 2px 0 var(--shadow);
}

.slider-h__handle:active {
  cursor: grabbing;
  box-shadow: 0 0 0 var(--shadow);
}
```

#### Rotary Knob

```
        ╭──────────╮
       ╱            ╲
      │    ╱╲       │
      │   ╱  ╲ ←──────── Indicator line
      │  ▼    ▼     │
       ╲            ╱
        ╰──────────╯
            ↑
      Arc shows travel
```

**Knob Specifications:**

- **Background (knob-bg.svg)**: 64×64px, dark gray gradient, thick border
- **Foreground (knob-fg.svg)**: Indicator line, rotates with value
- **Value Arc**: Chromasynesthesia color fill based on parameter type

### Dialog & Modal Windows

```
╔═══════════════════════════════════════════════════════════════╗
║  ┌─────────────────────────────────────────────────────────┐  ║
║  │  💾 SAVE PROJECT                                        │  ║
║  │                      ╳                                   │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║                                                               ║
║   Project Name:                                               ║
║  ┌──────────────────────────────────────────────────────────┐ ║
║  │ My Awesome Track                                         │ ║
║  └──────────────────────────────────────────────────────────┘ ║
║                                                               ║
║   Location:                                                   ║
║  ┌──────────────────────────────────────────────────────────┐ ║
║  │ ~/Music/Intuitives/                              [Browse]│ ║
║  └──────────────────────────────────────────────────────────┘ ║
║                                                               ║
║  ┌────────────────┐            ┌────────────────────────────┐ ║
║  │    Cancel      │            │         💾 Save            │ ║
║  └────────────────┘            └────────────────────────────┘ ║
╚═══════════════════════════════════════════════════════════════╝

   ↑                                ↑
   4px hard shadow                  Primary button = Emerald
```

### Dropdowns & Menus

```css
.dropdown {
  background: var(--surface-secondary);
  border: 3px solid var(--border);
  border-radius: 6px;
  padding: 8px 12px;
  box-shadow: 4px 4px 0 var(--shadow);
}

.dropdown__menu {
  background: var(--surface-primary);
  border: 3px solid var(--border);
  border-radius: 6px;
  margin-top: 4px;
  box-shadow: 4px 4px 0 var(--shadow);
}

.dropdown__item {
  padding: 8px 16px;
  border-bottom: 1px solid var(--surface-tertiary);
}

.dropdown__item:hover {
  background: var(--note-e); /* Sunburst highlight */
  color: var(--black);
}
```

---

## 🎬 Animation & Interaction

### Timing Functions

```css
:root {
  /* Neobrutalist: snappy, physical, no smoothness */
  --ease-snap: cubic-bezier(0.16, 1, 0.3, 1); /* quick start, abrupt stop */
  --ease-elastic: cubic-bezier(0.68, -0.6, 0.32, 1.6); /* overshoot */
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1); /* bouncy */

  /* Duration: keep it snappy */
  --duration-instant: 0.08s;
  --duration-fast: 0.15s;
  --duration-normal: 0.25s;
}
```

### Interaction States

| Action        | Animation                                | Duration | Easing  |
| ------------- | ---------------------------------------- | -------- | ------- |
| Button hover  | Shadow offset increase, slight translate | 0.1s     | snap    |
| Button press  | Shadow collapse, translate to 0          | 0.08s    | linear  |
| Slider drag   | Handle follows cursor, value jumps       | instant  | —       |
| Menu open     | Fade in + slight scale from top          | 0.15s    | snap    |
| Menu close    | Fade out                                 | 0.1s     | linear  |
| Dialog open   | Scale from 0.95 + fade                   | 0.2s     | spring  |
| Toggle switch | Snap between states                      | 0.15s    | elastic |

### Micro-Animations

**Transport Button Press:**

```css
@keyframes button-press {
  0% {
    transform: translate(0, 0);
    box-shadow: 4px 4px 0 var(--shadow);
  }
  50% {
    transform: translate(4px, 4px);
    box-shadow: 0 0 0 var(--shadow);
  }
  100% {
    transform: translate(0, 0);
    box-shadow: 4px 4px 0 var(--shadow);
  }
}
```

**Recording Pulse:**

```css
@keyframes rec-pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.rec-on.active {
  animation: rec-pulse 0.8s ease-in-out infinite;
}
```

**Play Button Bounce:**

```css
@keyframes play-bounce {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

.play-on:active {
  animation: play-bounce 0.2s var(--ease-spring);
}
```

---

## 📱 Responsive Adaptation

### Breakpoints

| Breakpoint  | Width      | Layout Changes                       |
| ----------- | ---------- | ------------------------------------ |
| **Desktop** | ≥1200px    | Full layout, all panels visible      |
| **Laptop**  | 900-1199px | Collapsible side panels              |
| **Tablet**  | 600-899px  | Stacked transport, tabbed panels     |
| **Mobile**  | <600px     | Single-panel view, drawer navigation |

### Adaptation Principles

1. **No Smooth Morphing**: Layouts snap between breakpoints
2. **Component Priority**: Transport always visible; panels collapse hierarchically
3. **Touch Targets**: Minimum 44×44px on touch devices
4. **Hard-edged Stacking**: Panels stack vertically with clear boundaries

### Responsive Examples

**Desktop (≥1200px):**

```
┌──────────────────────────────────────────────────────────────────┐
│  TRANSPORT                                                        │
├────────────┬─────────────────────────────────────┬───────────────┤
│  BROWSER   │                                     │    MIXER      │
│   PANEL    │         ARRANGEMENT VIEW            │    PANEL      │
│            │                                     │               │
└────────────┴─────────────────────────────────────┴───────────────┘
```

**Tablet (600-899px):**

```
┌─────────────────────────────────────┐
│  TRANSPORT (compact)                │
├─────────────────────────────────────┤
│                                     │
│        ARRANGEMENT VIEW             │
│                                     │
├─────────────────────────────────────┤
│  [Browser] [Mixer] [AI] (tab bar)   │
├─────────────────────────────────────┤
│       Active Tab Content            │
└─────────────────────────────────────┘
```

---

## ♿ Accessibility

### Color Contrast

All text and UI elements must meet **WCAG 2.1 AA** standards:

| Foreground            | Background     | Ratio  | Status |
| --------------------- | -------------- | ------ | ------ |
| `#FFFEF0` (text)      | `#1A1A1F` (bg) | 17.4:1 | ✅ AAA |
| `#B0B0B5` (secondary) | `#1A1A1F` (bg) | 7.8:1  | ✅ AAA |
| `#33FF66` (play)      | `#1A1A1F` (bg) | 10.2:1 | ✅ AAA |
| `#FF3366` (rec)       | `#1A1A1F` (bg) | 5.4:1  | ✅ AA  |
| `#FF33EE` (purple)    | `#1A1A1F` (bg) | 4.8:1  | ✅ AA  |

### Keyboard Navigation

| Key                 | Action                              |
| ------------------- | ----------------------------------- |
| `Tab` / `Shift+Tab` | Navigate between focusable elements |
| `Enter` / `Space`   | Activate buttons, toggle switches   |
| `Arrow Keys`        | Adjust sliders, navigate lists      |
| `Escape`            | Close dialogs, cancel operations    |
| `Space`             | Play/Stop                           |
| `R`                 | Record                              |
| `L`                 | Toggle Loop                         |

### Focus Indicators

```css
:focus-visible {
  outline: 3px solid var(--note-e); /* Sunburst yellow */
  outline-offset: 2px;
}

/* High contrast mode */
@media (prefers-contrast: high) {
  :focus-visible {
    outline: 4px solid var(--white);
    outline-offset: 3px;
  }
}
```

### Screen Reader Support

- All icons have `aria-label` attributes
- Transport state changes announced via `aria-live`
- Modal dialogs trap focus and announce title
- Slider values read as percentage or dB

---

## 💻 Implementation Reference

### C/C++ Qt Stylesheet (QSS)

```cpp
// theme_loader.cpp
const QString INTUITIVES_THEME = R"(
  /* Global Styles */
  QWidget {
    background-color: #1A1A1F;
    color: #FFFEF0;
    font-family: 'Inter', sans-serif;
    font-size: 14px;
  }

  /* Transport Buttons */
  QPushButton#transport_play {
    background-color: #33FF66;
    border: 3px solid #1A1A1F;
    border-radius: 6px;
    min-width: 44px;
    min-height: 44px;
  }

  QPushButton#transport_play:hover {
    background-color: #5BFF85;
  }

  QPushButton#transport_play:pressed {
    background-color: #28CC52;
  }

  QPushButton#transport_stop {
    background-color: #FF33EE;
    border: 3px solid #1A1A1F;
    border-radius: 6px;
  }

  QPushButton#transport_rec {
    background-color: #FF3366;
    border: 3px solid #1A1A1F;
    border-radius: 6px;
  }

  /* Sliders */
  QSlider::groove:horizontal {
    background: #2F2F3A;
    border: 2px solid #E5E5E0;
    height: 20px;
    border-radius: 4px;
  }

  QSlider::handle:horizontal {
    background: #1A1A1F;
    border: 2px solid #FFFEF0;
    width: 16px;
    height: 28px;
    margin: -4px 0;
    border-radius: 4px;
  }

  /* Knobs via Custom Painting */
  /* See native/intuitives_daw/src/widgets/knob.cpp */

  /* Panels */
  QFrame.panel {
    background-color: #252530;
    border: 3px solid #E5E5E0;
    border-radius: 8px;
  }

  /* Dialogs */
  QDialog {
    background-color: #1A1A1F;
    border: 4px solid #E5E5E0;
    border-radius: 12px;
  }
)";
```

### Python (PyQt/PySide)

```python
# theme.py
from PySide6.QtGui import QColor, QFont, QPalette

def apply_intuitives_theme(app):
    """Apply the Intuitives Neobrutalist theme."""

    palette = QPalette()

    # Surfaces
    palette.setColor(QPalette.Window, QColor("#1A1A1F"))
    palette.setColor(QPalette.WindowText, QColor("#FFFEF0"))
    palette.setColor(QPalette.Base, QColor("#252530"))
    palette.setColor(QPalette.AlternateBase, QColor("#2F2F3A"))

    # Text
    palette.setColor(QPalette.Text, QColor("#FFFEF0"))
    palette.setColor(QPalette.BrightText, QColor("#FFEE33"))

    # Buttons
    palette.setColor(QPalette.Button, QColor("#4A4A4F"))
    palette.setColor(QPalette.ButtonText, QColor("#FFFEF0"))

    # Highlights
    palette.setColor(QPalette.Highlight, QColor("#FF33EE"))
    palette.setColor(QPalette.HighlightedText, QColor("#FFFEF0"))

    app.setPalette(palette)

    # Set fonts
    app.setFont(QFont("Inter", 14))
```

### SVG Icon Template

```xml
<!-- Template for Intuitives Icons -->
<svg width="44" height="44" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
  <!-- Background with neobrutalist shadow simulation -->
  <rect x="2" y="2" width="40" height="40" rx="6" fill="#1A1A1F"/> <!-- Shadow layer -->
  <rect width="40" height="40" rx="6" fill="${ACTIVE_COLOR}"/>

  <!-- Border -->
  <rect x="1.5" y="1.5" width="37" height="37" rx="5"
        stroke="#1A1A1F" stroke-width="3" fill="none"/>

  <!-- Icon glyph centered -->
  <g transform="translate(8, 8)">
    <!-- Icon path here, 24x24 centered -->
    ${ICON_PATH}
  </g>
</svg>
```

---

## 📁 File Structure

```
themes/default/
├── theme.md                    # This specification document
├── default.inttheme            # Theme configuration file
├── intuitives.inttheme         # Neobrutalist theme config
├── palettes/
│   ├── default.yaml            # Primary palette (neobrutalist)
│   ├── dark.yaml               # Deeper dark variant
│   └── intuitives.yaml         # ✅ Complete Chromasynesthesia palette
├── vars/
│   ├── common.yaml             # ✅ Neobrutalist variables
│   └── default.yaml            # Legacy variables
├── system/
│   └── default.yaml            # ✅ System-level theme (sequencer, widgets)
├── templates/
│   └── default.qss             # Qt stylesheet template
└── assets/
    ├── dark/                   # "off" state icons (muted gray)
    │   ├── play-off.svg
    │   ├── stop-off.svg
    │   ├── rec-off.svg
    │   └── ... (22 total)
    ├── hover/                  # ✅ Hover state icons (15 files)
    │   ├── play-hover.svg      # Extended shadow, lighter color
    │   ├── stop-hover.svg
    │   ├── rec-hover.svg
    │   ├── loop-hover.svg
    │   ├── mute-hover.svg
    │   ├── solo-hover.svg
    │   ├── fx-hover.svg
    │   ├── draw-hover.svg
    │   ├── select-hover.svg
    │   ├── erase-hover.svg     # NEW
    │   ├── split-hover.svg     # NEW
    │   ├── metronome-hover.svg # NEW
    │   └── follow-hover.svg    # NEW
    ├── pressed/                # ✅ Pressed state icons (15 files)
    │   ├── play-pressed.svg    # No shadow, darker color, translated
    │   ├── stop-pressed.svg
    │   ├── rec-pressed.svg
    │   ├── loop-pressed.svg
    │   ├── mute-pressed.svg
    │   ├── solo-pressed.svg
    │   ├── fx-pressed.svg
    │   ├── draw-pressed.svg
    │   ├── select-pressed.svg
    │   ├── erase-pressed.svg   # NEW
    │   ├── split-pressed.svg   # NEW
    │   ├── metronome-pressed.svg # NEW
    │   └── follow-pressed.svg  # NEW
    ├── play-on.svg             # ✅ Emerald (#33FF66)
    ├── stop-on.svg             # ✅ Electric Indigo (#6366F1)
    ├── rec-on.svg              # ✅ Crimson (#FF3366)
    ├── loop-on.svg             # ✅ Tangerine (#FF9933)
    ├── mute-on.svg             # ✅ Electric Indigo (#6366F1)
    ├── solo-on.svg             # ✅ Crimson (#FF3366)
    ├── power-on.svg            # ✅ Electric Indigo (FIXED: symmetric)
    ├── fx-on.svg               # ✅ Electric Indigo
    ├── draw-on.svg             # ✅ Electric Indigo
    ├── erase-on.svg            # ✅ Electric Indigo
    ├── select-on.svg           # ✅ Electric Indigo
    ├── split-on.svg            # ✅ Electric Indigo
    ├── hide-on.svg             # ✅ Electric Indigo
    ├── follow-on.svg           # ✅ Cyan (#33EEFF)
    ├── metronome-on.svg        # ✅ Cyan
    ├── speaker-on.svg          # ✅ Emerald
    ├── dc-on.svg               # ✅ Sapphire (#3366FF)
    ├── edit-atm.svg            # ✅ Sunburst (#FFEE33)
    ├── edit-items.svg          # ✅ Sunburst
    ├── wave-editor.svg         # ✅ Sapphire
    ├── menu.svg                # ✅ Neobrutalist hamburger
    ├── panic.svg               # ✅ Neobrutalist alert (Crimson)
    ├── smooth.svg              # ✅ Neobrutalist automation curve
    ├── daw.svg                 # ✅ Small icon (FIXED: centered)
    ├── icon.svg                # ✅ App icon (FIXED: centered)
    ├── splash.svg              # ✅ Splash screen
    ├── knob-bg.svg             # ✅ Neobrutalist knob (NO ARC - drawn by code)
    ├── knob-fg.svg             # ✅ Indicator with Electric Indigo highlight
    ├── h-fader.svg             # ✅ Handle only (no track)
    ├── v-fader.svg             # ✅ Handle only (no track)
    ├── spinbox-up.svg          # ✅ Neobrutalist arrows
    ├── spinbox-down.svg
    └── zoom_slider_handle.svg
```

---

## 🔧 Python Icon Utility Module

A new `intui/neobrutalist_icons.py` module provides helper functions for creating QIcons with full state support:

```python
from intui.neobrutalist_icons import (
    get_play_icon,      # Transport
    get_stop_icon,
    get_rec_icon,
    get_loop_icon,
    get_metronome_icon,
    get_mute_icon,      # Track controls
    get_solo_icon,
    get_fx_icon,
    get_draw_icon,      # Tools
    get_select_icon,
    get_erase_icon,
    get_split_icon,
    get_follow_icon,    # Navigation
    get_power_icon,
    get_hide_icon,
    create_simple_icon,         # For single SVGs
    create_neobrutalist_icon,   # Custom icon builder
)
```

Each function returns a `QIcon` with:

- **Normal/On**: Colorful neobrutalist icon
- **Normal/Off**: Muted gray version (from dark/)
- **Active**: Hover state (from hover/)
- **Selected**: Pressed state (from pressed/)
- **Disabled**: Auto-dimmed based on off state

---

## 🎭 Interaction States

### State Transformation Rules

| State       | Shadow Offset | Position Shift | Color Change  |
| ----------- | ------------- | -------------- | ------------- |
| **Default** | `4px 4px`     | `0, 0`         | Base color    |
| **Hover**   | `6px 6px`     | `-1px, -1px`   | 10% lighter   |
| **Pressed** | `0 0`         | `4px, 4px`     | 10% darker    |
| **Focus**   | `4px 4px`     | `0, 0`         | + Yellow ring |

### CSS Implementation

```css
.btn-neobrutalist {
  box-shadow: 4px 4px 0 #000;
  transition: box-shadow 0.1s, transform 0.1s;
}

.btn-neobrutalist:hover {
  box-shadow: 6px 6px 0 #000;
  transform: translate(-1px, -1px);
  filter: brightness(1.1);
}

.btn-neobrutalist:active {
  box-shadow: 0 0 0 #000;
  transform: translate(4px, 4px);
  filter: brightness(0.9);
}
```

---

## ✅ Checklist for Theme Implementation

### Completed ✅

- [x] Update `palettes/default.yaml` with Chromasynesthesia colors
- [x] Create `palettes/intuitives.yaml` with full palette
- [x] Regenerate all SVG icons with neobrutalist styling
- [x] Update `vars/common.yaml` with new shadow variables
- [x] Create `system/default.yaml` with sequencer/widget colors
- [x] Create `hover/` state icons (19 icons including power, hide, speaker, dc)
- [x] Create `pressed/` state icons (19 icons including power, hide, speaker, dc)
- [x] Fix icon quality issues (centering, symmetry)
- [x] Add Electric Indigo (#6366F1) as primary action color
- [x] Test contrast ratios for accessibility
- [x] Document interaction states and transformations
- [x] Create `neobrutalist_icons.py` utility module
- [x] Refactor `transport.py` to use neobrutalist icons
- [x] Refactor `daw/transport.py` to use neobrutalist icons
- [x] Refactor `daw/sequencer/__init__.py` to use neobrutalist icons
- [x] Refactor `daw/sequencer/track.py` to use neobrutalist icons (menu, FX, solo, mute)
- [x] Refactor `daw/item_editor/editor.py` to use neobrutalist icons
- [x] Refactor `daw/item_editor/notes/__init__.py` to use neobrutalist icons (menu, draw, speaker)
- [x] Refactor `daw/item_editor/audio/__init__.py` to use neobrutalist icons (menu)
- [x] Refactor `daw/item_editor/automation.py` to use neobrutalist icons (menu, smooth)
- [x] Refactor `plugins/__init__.py` to use neobrutalist icons (plugins menu)
- [x] Refactor `wave_edit/__init__.py` to use neobrutalist icons (FX)
- [x] Fix knob-bg.svg (remove arc - drawn dynamically by code)
- [x] Fix knob-fg.svg with Electric Indigo highlight
- [x] Apply Qt stylesheet changes to default.qss for full neobrutalist styling
  - [x] QPushButton hover/pressed states
  - [x] QMenu styling with rounded corners
  - [x] QTabBar hover/selected states
  - [x] QCheckBox/QRadioButton with solid checked background
  - [x] QToolBar/QToolButton neobrutalist styling
  - [x] QSlider horizontal/vertical with hard handles
  - [x] QGroupBox with bold title badges
  - [x] QSpinBox/QDoubleSpinBox with styled buttons
  - [x] QProgressBar neobrutalist chunk styling
  - [x] Focus states with Electric Indigo highlight

### Pending 🔄

- [ ] Verify keyboard navigation works with new focus states
- [ ] Test animations are smooth at 60fps
- [ ] Validate responsive behavior at all breakpoints
- [ ] Screen reader testing for all interactive elements

---

<p align="center">
  <strong>🎵 Intuitives — "Does this sound cool?" 🎵</strong><br>
  <em>Neobrutalist Theme v1.2 — Full Component Integration</em>
</p>
