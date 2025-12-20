"""Setup script for Intuitive Music DAW"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="intuitive-music-daw",
    version="0.1.0",
    author="Intuitive Music Team",
    description="An AI-assisted Digital Audio Workstation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mitchlabeetch/Intuitive_Music",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "Flask>=3.0.0",
        "Flask-CORS>=4.0.0",
        "Flask-SocketIO>=5.3.5",
        "soundfile>=0.12.1",
        "librosa>=0.10.1",
        "numpy>=1.24.3",
        "scipy>=1.11.4",
        "mido>=1.3.2",
        "openai>=1.6.1",
        "SQLAlchemy>=2.0.25",
    ],
    entry_points={
        "console_scripts": [
            "intuitive-daw=intuitive_daw.cli:main",
        ],
    },
)
