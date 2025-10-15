"""
Setup script for the College Football Prediction Model
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="cfbmodel",
    version="2.0.0",
    author="Zach Ring",
    description="A machine learning model for predicting college football game outcomes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zachringnight/cfbmodel",
    packages=find_packages(include=['cfbmodel*']),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "cfbmodel=cfbmodel.main:main",
        ],
    },
    include_package_data=True,
    keywords="college football prediction machine-learning sports-analytics",
)
