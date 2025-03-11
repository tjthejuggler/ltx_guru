#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("sequence_maker_README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="sequence_maker",
    version="0.1.0",
    author="LTX Guru",
    author_email="info@ltxguru.com",
    description="A tool for creating color sequences for LTX juggling balls",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ltxguru/sequence_maker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Artistic Software",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "sequence_maker=sequence_maker.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "sequence_maker": ["resources/*"],
    },
)