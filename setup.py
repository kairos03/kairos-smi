from setuptools import setup, find_packages

setup(
    name='ksmi',
    version='0.1.5',
    url='https://github.com/kairos03/kairos-smi',
    license='MIT',
    author='Eunseop Shin',
    author_email='kairos9603@gmail.com',
    description='Multi-server GPU monotoring tools',
    packages=find_packages(exclude=['tests', 'config.json']),
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    zip_safe=False,
    setup_requires=['nose>=1.0'],
    test_suite='nose.collector',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)