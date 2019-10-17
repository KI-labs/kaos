from setuptools import setup, find_packages

with open('./requirements.txt') as f:
    requirements = f.read().splitlines()


setup(
    name="kaos_integration_tests",
    version="1.0.0",
    author_email="kaos@ki-labs.com",
    python_requires='>=3.7',
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3.7'
    ]
)
