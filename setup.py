from setuptools import setup, find_packages

setup(
    name="Context-Aware Architecture",
    version="0.0.1",
    author="Zaki Chammaa",
    description="Architecture for context-aware systems",
    keywords=["iot", "sensor", "context"],
    packages=find_packages(".", exclude=["tests", "tests.*"]),
)
