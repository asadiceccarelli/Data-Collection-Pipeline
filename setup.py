from setuptools import setup
from setuptools import find_packages

setup(
    name='Premier-League-Scraper',
    version='1.0',
    description='A tool to scrape the season statistics of any club from the premier league.',
    url='https://github.com/asadiceccarelli/Data-Collection-Pipeline',
    author='Asadi Ceccarelli',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'boto3',
        'botocore',
        'brotlipy',
        'certifi',
        'cffi',
        'cryptography',
        'greenlet',
        'idna',
        'jmespath',
        'numpy',
        'pandas',
        'pip',
        'psycopg2',
        'psycopg2-binary',
        'pycparser',
        'pyOpenSSL',
        'PySocks',
        'python-dateutil',
        'pytz',
        's3transfer',
        'selenium',
        'setuptools',
        'six',
        'SQLAlchemy',
        'urllib3',
        'uuid',
        'wget',
        'wheel'
    ]
)