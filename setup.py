#!/usr/bin/env python

from setuptools import setup, find_packages
import os

# Read README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="haconiwa",
    version="0.1.0",
    author="Daisuke Motoki",
    author_email="kanri@kandaquantum.co.jp",
    description="AI協調開発支援Python CLIツール - 箱庭での開発を支援",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/haconiwa/haconiwa",
    project_urls={
        "Documentation": "https://haconiwa.readthedocs.io",
        "Issues": "https://github.com/haconiwa/haconiwa/issues",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "typer>=0.9.0",
        "libtmux>=0.23.2",
        "gitpython>=3.1.40",
        "prometheus-client>=0.17.1",
        "pyyaml>=6.0.1",
        "rich>=13.7.0",
        "click>=8.1.7",
    ],
    extras_require={
        "docker": ["docker>=6.1.3"],
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
            "bandit>=1.7.5",
            "isort>=5.12.0",
            "pre-commit>=3.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "haconiwa=haconiwa.cli:app",
        ],
    },
    include_package_data=True,
    license="MIT",
) 