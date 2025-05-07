# setup.py

from setuptools import setup, find_packages

setup(
    name="parsing_project",
    version="0.1.1",
    description="Invoice and line item parser for fixed-format daily sales registers",
    author="Kyle Allen Levocraft",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.7",
)
