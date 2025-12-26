# Contributing to Intuitives DAW

<p align="center">
  <strong>Welcome! We're excited you want to contribute! 🎉</strong>
</p>

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Ways to Contribute](#ways-to-contribute)
3. [Getting Started](#getting-started)
4. [Development Workflow](#development-workflow)
5. [Code Standards](#code-standards)
6. [Testing](#testing)
7. [Documentation](#documentation)
8. [Pull Request Process](#pull-request-process)
9. [Community](#community)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming, inclusive, and harassment-free experience for everyone, regardless of:

- Age, body size, disability, ethnicity, gender identity and expression
- Level of experience, education, socio-economic status
- Nationality, personal appearance, race, religion
- Sexual identity and orientation

### Our Standards

**Positive behaviors:**
- ✅ Being respectful and welcoming
- ✅ Accepting constructive criticism gracefully
- ✅ Focusing on what's best for the community
- ✅ Showing empathy towards others
- ✅ Celebrating diversity of perspectives

**Unacceptable behaviors:**
- ❌ Harassment, trolling, or insulting comments
- ❌ Personal or political attacks
- ❌ Publishing others' private information
- ❌ Any conduct that would be inappropriate in a professional setting

### Enforcement

Instances of unacceptable behavior may be reported to conduct@intuitivesdaw.com. All complaints will be reviewed and investigated promptly and fairly.

---

## Ways to Contribute

### For Everyone

#### 🎵 Create & Share
- **Make Music** - Use Intuitives and share your creations
- **Create Tutorials** - Write guides, record videos
- **Translate** - Help localize the interface and documentation
- **Give Feedback** - Tell us what works and what doesn't

#### 🐛 Report Issues
- **Bug Reports** - Found a bug? Let us know!
- **Feature Requests** - Have an idea? Suggest it!
- **Documentation Issues** - Found a typo or unclear explanation?

### For Developers

#### 💻 Code Contributions
- **Fix Bugs** - Pick an issue and fix it
- **Add Features** - Implement requested features
- **Optimize Performance** - Make it faster
- **Refactor Code** - Improve code quality

#### 🔌 Create Plugins
- **Audio Effects** - New sound processors
- **MIDI Tools** - Note manipulation tools
- **Generators** - Algorithmic composition tools
- **Visualizers** - Visual feedback tools

#### 🤖 AI Integration
- **Local Models** - Integrate new AI models
- **Training Datasets** - Contribute training data
- **Model Optimization** - Improve inference speed

### For Designers

#### 🎨 Design Contributions
- **UI/UX Design** - Improve the interface
- **Icons & Graphics** - Create visual assets
- **Themes** - Design color schemes
- **Brand Assets** - Logo variations, banners

### For Writers

#### 📖 Documentation
- **User Guides** - Step-by-step tutorials
- **API Documentation** - Code references
- **Blog Posts** - Technical articles
- **Case Studies** - Real-world usage examples

---

## Getting Started

### Prerequisites

- **Python 3.9+** - `python --version`
- **Git** - `git --version`
- **GitHub Account** - For pull requests
- **(Optional) Node.js 16+** - For frontend development
- **(Optional) C/C++ Compiler** - For native engine development

### Setup Development Environment

#### 1. Fork & Clone

```bash
# Fork on GitHub first, then:
git clone https://github.com/YOUR_USERNAME/Intuitive_Music.git
cd Intuitive_Music

# Add upstream remote
git remote add upstream https://github.com/mitchlabeetch/Intuitive_Music.git

# Verify remotes
git remote -v
```

#### 2. Create Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows
```

#### 3. Install Development Dependencies

```bash
# Install package in editable mode with dev dependencies
pip install -e ".[dev]"

# Or manually:
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

#### 4. Verify Installation

```bash
# Run tests
pytest

# Check code style
black --check src/
flake8 src/

# Try CLI
intuitive-daw --help
```

#### 5. Build Native Components (Optional)

```bash
cd native/intuitives_daw
./build.sh --debug
cd ../..
```

### Project Structure

```
Intuitive_Music/
├── src/                    # Python source code
│   └── intuitive_daw/
│       ├── core/           # Core DAW functionality
│       ├── audio/          # Audio processing
│       ├── midi/           # MIDI processing
│       ├── ai/             # AI integration
│       ├── api/            # REST API
│       └── cli.py          # Command-line interface
├── native/                 # Native C/C++ code
│   └── intuitives_daw/
│       ├── stargate_engine/  # Audio engine
│       └── src/            # Native app code
├── frontend/               # React web UI
│   └── src/
├── tests/                  # Test suite
├── docs/                   # Documentation
├── plugins/                # Plugin examples
├── examples/               # Usage examples
└── scripts/                # Utility scripts
```

---

## Development Workflow

### 1. Choose an Issue

```bash
# Browse issues: https://github.com/mitchlabeetch/Intuitive_Music/issues

# Look for:
# - "good first issue" label (for beginners)
# - "help wanted" label (community contributions welcome)
# - "bug" label (bugs to fix)
# - "enhancement" label (new features)
```

### 2. Create a Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/my-feature-name

# Or for bug fixes:
git checkout -b fix/issue-description
```

**Branch naming:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test improvements

### 3. Make Changes

```bash
# Edit code
code src/intuitive_daw/...

# Test frequently
pytest tests/test_specific.py

# Run linters
black src/
flake8 src/
```

### 4. Commit Changes

```bash
# Stage changes
git add src/intuitive_daw/...

# Commit with descriptive message
git commit -m "Add chord progression generator

- Implement Markov chain-based chord generation
- Add support for multiple music styles
- Include unit tests
- Update documentation

Fixes #123"
```

**Commit message format:**
```
<type>: <short summary>

<detailed description>

<footer>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Formatting
- `refactor:` - Code restructuring
- `test:` - Tests
- `chore:` - Maintenance

### 5. Push & Create Pull Request

```bash
# Push to your fork
git push origin feature/my-feature-name

# Create PR on GitHub
# Fill out the PR template
```

---

## Code Standards

### Python Style

#### PEP 8 Compliance

```bash
# Format code
black src/

# Check style
flake8 src/

# Type check (optional)
mypy src/
```

#### Code Style Guidelines

```python
# ✅ Good
def process_audio(
    audio: np.ndarray,
    sample_rate: int = 48000,
    normalize: bool = True
) -> np.ndarray:
    """
    Process audio with effects.
    
    Args:
        audio: Input audio buffer (samples, channels)
        sample_rate: Sample rate in Hz
        normalize: Whether to normalize output
    
    Returns:
        Processed audio buffer
    
    Raises:
        ValueError: If audio shape is invalid
    """
    if audio.ndim != 2:
        raise ValueError(f"Expected 2D audio, got {audio.ndim}D")
    
    # Process audio
    processed = apply_effects(audio, sample_rate)
    
    if normalize:
        processed = normalize_audio(processed)
    
    return processed


# ❌ Bad
def proc(a,sr=48000,n=True):  # No docstring, unclear names
    if len(a.shape)!=2:raise ValueError()  # Bad formatting
    p=apply_effects(a,sr)  # Unclear variable names
    if n:p=normalize_audio(p)
    return p
```

#### Documentation

```python
# Module docstring
"""
Audio processing utilities.

This module provides functions for processing audio signals,
including filtering, effects, and analysis.
"""

# Class docstring
class AudioProcessor:
    """
    Process audio with configurable effects chain.
    
    This class provides a flexible framework for applying
    multiple audio effects in sequence.
    
    Attributes:
        sample_rate: Sample rate in Hz
        effects: List of effects to apply
    
    Example:
        >>> processor = AudioProcessor(sample_rate=48000)
        >>> processor.add_effect(ReverbEffect())
        >>> output = processor.process(input_audio)
    """
    pass

# Function docstring (Google style)
def analyze_spectrum(audio: np.ndarray, sample_rate: int) -> Dict[str, np.ndarray]:
    """
    Analyze frequency spectrum of audio.
    
    Args:
        audio: Input audio (samples, channels)
        sample_rate: Sample rate in Hz
    
    Returns:
        Dictionary containing:
            - "frequencies": Frequency bins
            - "magnitudes": Magnitude spectrum
            - "phases": Phase spectrum
    
    Raises:
        ValueError: If audio is empty
    
    Example:
        >>> spectrum = analyze_spectrum(audio, 48000)
        >>> frequencies = spectrum["frequencies"]
    """
    pass
```

### C/C++ Style

```cpp
// Header guards
#ifndef INTUITIVE_DAW_PROCESSOR_H
#define INTUITIVE_DAW_PROCESSOR_H

// Function documentation
/**
 * Process audio buffer with effects.
 * 
 * @param buffer Audio buffer to process (in-place)
 * @param length Number of samples
 * @param channels Number of channels
 * @return 0 on success, error code otherwise
 */
int process_audio(float* buffer, size_t length, int channels);

#endif  // INTUITIVE_DAW_PROCESSOR_H
```

### JavaScript/React Style

```javascript
// Use functional components
const AudioTrack = ({ trackId, volume, onVolumeChange }) => {
  const [isMuted, setIsMuted] = useState(false);
  
  // Clear function names
  const handleVolumeChange = (newVolume) => {
    onVolumeChange(trackId, newVolume);
  };
  
  return (
    <div className="audio-track">
      <VolumeSlider
        value={volume}
        onChange={handleVolumeChange}
        muted={isMuted}
      />
    </div>
  );
};

// PropTypes for documentation
AudioTrack.propTypes = {
  trackId: PropTypes.string.isRequired,
  volume: PropTypes.number.isRequired,
  onVolumeChange: PropTypes.func.isRequired,
};
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_audio.py

# Run specific test
pytest tests/test_audio.py::test_reverb_effect

# Run with coverage
pytest --cov=src/intuitive_daw --cov-report=html

# Run fast tests only (skip slow integration tests)
pytest -m "not slow"
```

### Writing Tests

#### Unit Tests

```python
# tests/test_audio.py
import pytest
import numpy as np
from intuitive_daw.audio.processor import ReverbEffect

class TestReverbEffect:
    """Test reverb audio effect"""
    
    @pytest.fixture
    def effect(self):
        """Create effect instance for testing"""
        effect = ReverbEffect(room_size=0.5)
        effect.sample_rate = 48000
        return effect
    
    @pytest.fixture
    def test_audio(self):
        """Create test audio"""
        return np.random.randn(4800, 2) * 0.1
    
    def test_output_shape(self, effect, test_audio):
        """Test that output shape matches input"""
        output = effect.process(test_audio)
        assert output.shape == test_audio.shape
    
    def test_output_range(self, effect, test_audio):
        """Test that output is in valid range"""
        output = effect.process(test_audio)
        assert np.all(output >= -1.0)
        assert np.all(output <= 1.0)
    
    def test_parameter_update(self, effect):
        """Test parameter updates"""
        effect.set_parameter("room_size", 0.8)
        assert effect.room_size == 0.8
    
    @pytest.mark.parametrize("room_size", [0.0, 0.5, 1.0])
    def test_various_room_sizes(self, effect, test_audio, room_size):
        """Test with different room sizes"""
        effect.set_parameter("room_size", room_size)
        output = effect.process(test_audio)
        assert output.shape == test_audio.shape
```

#### Integration Tests

```python
# tests/integration/test_project.py
import pytest
from intuitive_daw import Project
from intuitive_daw.core.track import AudioTrack

@pytest.mark.slow
class TestProjectIntegration:
    """Integration tests for project management"""
    
    def test_create_and_save_project(self, tmp_path):
        """Test full project lifecycle"""
        # Create project
        project = Project("Test Project")
        project.set_tempo(120)
        project.set_time_signature(4, 4)
        
        # Add tracks
        track = AudioTrack("Vocals")
        project.add_track(track)
        
        # Save
        project_path = tmp_path / "test_project"
        project.save(str(project_path))
        
        # Load
        loaded_project = Project.load(str(project_path))
        
        # Verify
        assert loaded_project.name == "Test Project"
        assert loaded_project.tempo == 120
        assert len(loaded_project.tracks) == 1
        assert loaded_project.tracks[0].name == "Vocals"
```

### Test Coverage

Aim for:
- **80%+ code coverage** for core functionality
- **100% coverage** for critical paths (audio processing, data persistence)
- **Integration tests** for user-facing features

```bash
# Generate coverage report
pytest --cov=src/intuitive_daw --cov-report=html

# View report
open htmlcov/index.html
```

---

## Documentation

### Code Documentation

Every public function, class, and module should have docstrings:

```python
def generate_chord_progression(
    key: str,
    length: int,
    style: str = "pop"
) -> List[str]:
    """
    Generate a chord progression.
    
    Args:
        key: Musical key (e.g., "C major", "A minor")
        length: Number of chords to generate
        style: Musical style (pop, jazz, classical, etc.)
    
    Returns:
        List of chord symbols (e.g., ["C", "Am", "F", "G"])
    
    Raises:
        ValueError: If key or style is invalid
    
    Example:
        >>> chords = generate_chord_progression("C major", 4, "pop")
        >>> print(chords)
        ["C", "Am", "F", "G"]
    """
    pass
```

### User Documentation

When adding features, update:

- **README.md** - If it affects installation or quick start
- **DOCUMENTATION.md** - For comprehensive feature documentation
- **API docs** - For programmatic usage
- **Examples** - Add example code

### Documentation Build

```bash
# Build documentation (if using Sphinx)
cd docs
make html

# View locally
open _build/html/index.html
```

---

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass locally
- [ ] Added tests for new features
- [ ] Updated documentation
- [ ] Committed with clear messages
- [ ] Rebased on latest main

```bash
# Update your branch
git fetch upstream
git rebase upstream/main

# Resolve conflicts if any
# Then force push (your branch only!)
git push --force-with-lease origin feature/my-feature
```

### PR Template

When creating a PR, fill out the template:

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature breaking existing functionality)
- [ ] Documentation update

## How Has This Been Tested?
Describe tests you ran.

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed my code
- [ ] Commented complex code
- [ ] Updated documentation
- [ ] No new warnings
- [ ] Added tests that prove fix/feature works
- [ ] New and existing tests pass locally

## Related Issues
Fixes #123
Relates to #456
```

### Review Process

1. **Automated Checks** - CI runs tests and linters
2. **Code Review** - Maintainer reviews code
3. **Feedback** - Address review comments
4. **Approval** - Maintainer approves PR
5. **Merge** - PR is merged to main

**Timeline:**
- Initial review: Usually within 3-5 days
- Follow-up reviews: 1-2 days
- Merge: After approval and CI passes

### After Merge

```bash
# Delete your branch
git branch -d feature/my-feature
git push origin --delete feature/my-feature

# Update main
git checkout main
git pull upstream main
```

---

## Community

### Communication Channels

#### Discord
- **#general** - General discussion
- **#development** - Development chat
- **#plugins** - Plugin development
- **#ai** - AI integration
- **#help** - Get help

Join: https://discord.gg/intuitives

#### GitHub Discussions
- **Ideas** - Feature suggestions
- **Q&A** - Questions and answers
- **Show and Tell** - Share your work

Visit: https://github.com/mitchlabeetch/Intuitive_Music/discussions

#### Forum
- Long-form discussions
- Tutorials and guides
- Community projects

Visit: https://forum.intuitivesdaw.com

### Community Guidelines

#### Be Welcoming
- Help newcomers
- Answer questions patiently
- Celebrate contributions

#### Be Constructive
- Give specific, actionable feedback
- Suggest alternatives
- Focus on the code, not the person

#### Be Respectful
- Assume good intentions
- Respect different perspectives
- Accept that you might be wrong

### Recognition

Contributors are recognized in:
- **CONTRIBUTORS.md** - All contributors listed
- **Release Notes** - Contribution highlights
- **Hall of Fame** - Top contributors
- **Social Media** - Shoutouts for major contributions

---

## Development Resources

### Learning

#### Audio DSP
- [The Scientist and Engineer's Guide to DSP](https://www.dspguide.com/)
- [Designing Audio Effect Plugins in C++](https://www.willpirkle.com/)
- [Audio Developer Conference talks](https://www.youtube.com/c/ADCconf)

#### Python Development
- [Real Python](https://realpython.com/)
- [Python Testing with pytest](https://pragprog.com/titles/bopytest/)

#### Music Theory for Programmers
- [Music Theory for Nerds](https://eev.ee/blog/2016/09/15/music-theory-for-nerds/)
- [Learning Music (Ableton)](https://learningmusic.ableton.com/)

### Tools

#### Code Quality
- **Black** - Code formatter
- **flake8** - Linter
- **mypy** - Type checker
- **pytest** - Testing framework

#### Profiling
- **cProfile** - Python profiler
- **py-spy** - Sampling profiler
- **memory_profiler** - Memory usage

#### Debugging
- **pdb** - Python debugger
- **ipdb** - Enhanced debugger
- **VSCode** - IDE with debugger

---

## Getting Help

### I Have a Question

1. **Check Documentation** - README, DOCUMENTATION.md
2. **Search Issues** - Someone may have asked already
3. **Ask on Discord** - #help channel
4. **Create Discussion** - GitHub Discussions Q&A

### I Found a Bug

1. **Check Existing Issues** - May already be reported
2. **Create Issue** - Use bug report template
3. **Provide Details**:
   - Steps to reproduce
   - Expected vs actual behavior
   - System info (OS, Python version)
   - Error messages/logs

### I Want to Add a Feature

1. **Check Roadmap** - May already be planned
2. **Create Discussion** - Discuss the idea first
3. **Get Feedback** - Ensure it aligns with project goals
4. **Create Issue** - If approved, create feature request
5. **Submit PR** - Implement and submit

---

## Thank You! 🎉

Every contribution matters, whether it's:
- A single typo fix in documentation
- A detailed bug report
- A complex feature implementation
- Helping someone in Discord
- Sharing your music made with Intuitives

**You're making music creation more accessible for everyone!**

---

<p align="center">
  <strong>Happy Contributing!</strong>
</p>

<p align="center">
  <em>Together, we're building the future of music creation</em>
</p>
