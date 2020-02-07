import setuptools

setuptools.setup(
    name='texercise',
    version='0.0.1',
    author='Rasmus Laurvig Haugaard',
    author_email='rasmus.l.haugaard@gmail.com',
    description='command line interface for exercises at TEK, SDU',
    url='https://github.com/RasmusHaugaard/texercise-cli',
    scripts=[
        'bin/texercise',
    ],
    packages=setuptools.find_packages(),
    install_requires=[
        'request',
    ],

)
