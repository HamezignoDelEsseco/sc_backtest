from setuptools import setup, find_packages

setup(
    name="backtester",
    version="0.1.0",
    description="A modular backtesting framework on top of Sierra Chart's data",
    author="Raphael Hamez",
    packages=find_packages(exclude=("tests", "datasets")),
    python_requires=">=3.13",
)
