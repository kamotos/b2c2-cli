from setuptools import setup, find_packages

setup(
    name='b2c2',
    version='0.1',
    py_modules=['cli'],
    packages=find_packages(),
    include_package_data=True,
    install_requires="\n".split(open('requirements.txt', 'r').read()),
    entry_points='''
        [console_scripts]
        b2c2-cli=b2c2.cli:cli
    ''',
)