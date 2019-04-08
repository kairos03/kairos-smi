from setuptools import setup, find_packages

setup(
    name='kairos-smi',
    version='0.1.0',
    url='https://github.com/kairos03/kairos-smi',
    license='MIT',
    author='Eunseop Shin',
    author_email='kairos9603@gmail.com',
    description='Multi-server GPU monotoring tools',
    packages=find_packages(exclude=['tests', 'config.json']),
    long_description=open('README.md').read(),
    zip_safe=False,
    setup_requires=['nose>=1.0'],
    test_suite='nose.collector'
)