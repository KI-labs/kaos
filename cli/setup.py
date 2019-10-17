from setuptools import setup, find_packages

with open('./requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="kaos",
    version="1.0.0",
    author_email="kaos@ki-labs.com",
    python_requires='>=3.7',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': ['kaos = kaos_cli.main:start']
    },
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3.7'
    ]
)
