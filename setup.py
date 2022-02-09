from setuptools import setup

# Important: Update this when making new releases!
# Be sure to update `version` in '__init__.py' as well
version = "1.0.0"

setup(
    name="algopytest",
    version=version,
    description="A pytest plugin to write Algorand smart contract test suites more easily",
    url="https://github.com/DamianB-BitFlipper/algopytest.git",
    author="Damian Barabonkov",
    author_email="damianb@alum.mit.edu",
    license="MIT",
    packages=["algopytest"],
    keywords=["Algorand", "Smart Contract", "Pytest", "Unit Tests", "Test Suite"],
    download_url=f"https://github.com/DamianB-BitFlipper/algopytest/archive/refs/tags/v{version}.tar.gz",
    install_requires=[
        "pytest",
        "py-algorand-sdk",
        "pyteal",
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
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
)
