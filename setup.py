from setuptools import setup, find_packages

setup(
    name="my_package",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.18.5",
        "pandas>=1.0.5",
    ],
    entry_points={
        "console_scripts": [
            "my_script=my_package.my_script:main",
        ]
    },
)
