from setuptools import setup

setup(
    name='CFM Discord Bot',
    version='0.1.0',
    author='Jugal Bilimoria',
    description="A Discord Bot which helps track assignments for the CFM Program",
    url='https://github.com/JugalBili/Python-CFM-Discord-Bot',
    license='license.txt',
    long_description=open('README.md').read(),
    install_requires=[
        "discord.py==1.5.1"
        "mysql-connector-python==8.0.22"
        "python-dotenv==0.15.0"
        "tabulate==0.8.7"
    ],
    python_requires='>=3.6',
)