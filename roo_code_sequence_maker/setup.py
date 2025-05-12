#!/usr/bin/env python3
"""
Setup script for LTX Sequence Maker
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ltx-sequence-maker",
    version="0.1.0",
    author="Roo Code",
    author_email="info@example.com",
    description="A toolkit for creating color sequences for LTX juggling balls based on music analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/ltx-sequence-maker",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "librosa>=0.9.0",
        "numpy>=1.20.0",
        "matplotlib>=3.4.0",
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "ltx-analyze=roo_code_sequence_maker.examples.basic_analysis:main",
            "ltx-beat-patterns=roo_code_sequence_maker.examples.beat_patterns:main",
            "ltx-section-themes=roo_code_sequence_maker.examples.section_themes:main",
            "ltx-multiple-balls=roo_code_sequence_maker.examples.multiple_balls:main",
            "ltx-simple-sequence=roo_code_sequence_maker.examples.simple_sequence:main",
        ],
    },
)