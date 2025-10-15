"""
Setup script for the College Football Prediction Model
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Inline install_requires instead of reading requirements.txt
requirements = [
    # Add your requirements here, e.g.:
    "numpy>=1.21.0",
    "scikit-learn>=0.24.0",
    "pandas>=1.3.0",
    # ... add other requirements as needed
]

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
