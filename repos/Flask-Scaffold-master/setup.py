from setuptools import setup, find_packages

version = '0.6.2'

setup(
    name='Flask-Scaffold',
    description=(
        "Prototype Database driven CRUD dashboards and RESTFUL API's in Python 3, Flask and Angularjs"),
    version=version,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask==0.10.1',
        'Flask-Mail==0.9.1',
        'Flask-Migrate==1.4.0',
        'Flask-RESTful==0.3.4',
        'Flask-SQLAlchemy==2.0',
        'Flask-Script==2.0.5',
        'PyJWT==1.4.0',
        'PyMySQL==0.6.6',
        'PyYAML==3.11',
        'autopep8==1.2.1',
        'inflect==0.2.5',
        'marshmallow==2.3.0',
        'marshmallow-jsonapi==0.3.0',
        'psycopg2==2.6',
        'pycrypto==2.6.1',
        'uWSGI==2.0.11.2',
    ],
    author='Leo-G',
    url='https://github.com/Leo-G/Flask-Scaffold',
    download_url=(
        'https://github.com/Leo-G/Flask-Scaffold/archieve/' + version),
)
