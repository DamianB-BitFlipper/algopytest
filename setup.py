from setuptools import find_packages, setup

# Important: Update this when making new releases!
# Be sure to update `version` in '__init__.py' as well
version = "2.0.0"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="algopytest-framework",
    version=version,
    description="AlgoPytest is a framework which hides away all of the complexity and repetitiveness that comes with testing Algorand Smart Contracts.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DamianB-BitFlipper/algopytest.git",
    author="Damian Barabonkov",
    author_email="damianb@alum.mit.edu",
    license="MIT",
    packages=find_packages(),
    keywords=["Algorand", "Smart Contract", "Pytest", "Unit Tests", "Test Suite"],
    download_url=f"https://github.com/DamianB-BitFlipper/algopytest/archive/refs/tags/v{version}.tar.gz",
    install_requires=[
        "pytest",
        "py-algorand-sdk>=2.0.0",
        "pyteal",
        "typing_extensions",
    ],
    # This makes this plugin available to pytest
    entry_points={"pytest11": ["name_of_plugin = algopytest.fixtures"]},
    # Custom PyPI classifier for pytest plugins
    classifiers=[
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing :: Unit",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
