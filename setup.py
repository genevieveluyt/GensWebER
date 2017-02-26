from setuptools import setup

setup(
    name='gensweber',
    packages=['gensweber'],
    include_package_data=True,
    install_requires=[
        'flask',
        'mysql-connector'
    ],
)