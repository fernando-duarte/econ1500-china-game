"""
Setup script for the China Growth Game package.
"""

from setuptools import setup, find_packages

setup(
    name="china_growth_game",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.95.0",
        "uvicorn>=0.21.1",
        "numpy>=1.24.2",
        "pandas>=2.0.0",
        "pydantic>=2.0.0",
    ],
    author="Fernando Duarte",
    author_email="duarte@alum.mit.edu",
    description="An economic simulation game for teaching economic growth concepts",
    keywords="economics, growth, simulation, game, education",
    python_requires=">=3.9",
)
