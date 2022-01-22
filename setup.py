from setuptools import setup

setup(
    name='algopytest',
    version='0.1.0',    
    description='A pytest plugin to write Algorand smart contract test suites more easily',
    url='https://github.com/DamianB-BitFlipper/algopytest.git',
    author='Damian Barabonkov',
    author_email='damianb@alum.mit.edu',
    license='MIT',
    packages=['algopytest'],
    install_requires=['pytest'],
    # This makes this plugin available to pytest
    entry_points={"pytest11": ["name_of_plugin = algopytest.fixtures"]},
    # Custom PyPI classifier for pytest plugins
    classifiers=["Framework :: Pytest"],
)
