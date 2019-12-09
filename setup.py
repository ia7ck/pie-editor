from setuptools import setup, find_packages

# https://setuptools.readthedocs.io/en/latest/setuptools.html#automatic-script-creation
setup(
    name="pie-editor",
    version="0.1",
    packages=find_packages(),
    install_requires=["Cython==0.29.9", "kivy==1.11.0",],
    entry_points={"gui_scripts": ["pie = main:main",]},
)
