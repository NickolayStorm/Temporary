from setuptools import setup

setup(
    name='analogon',
    packages=['analogon'],
    include_package_data=True,
    install_requires=[
        'flask',
        'sqlalchemy',
        'flask-sqlalchemy',
        'requests',
        'lxml'
    ],
)