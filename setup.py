from setuptools import setup

setup(
    name='analogon',
    packages=['Server'],
    include_package_data=True,
    install_requires=[
        'flask',
        'sqlalchemy',
        'flask-sqlalchemy',
        'requests',
        'lxml',
        'geoalchemy2',
        'shapely',
        'telegraph'
    ],
)