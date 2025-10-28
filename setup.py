from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cornhole-coach",
    version="0.1.0",
    author="Cornhole Coach Team",
    description="Physics engine for calculating optimal cornhole throw trajectories",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/beanbag-trajectory",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "matplotlib>=3.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
        ],
    },
)
