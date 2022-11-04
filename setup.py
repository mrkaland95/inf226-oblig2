from setuptools import setup

setup(
   name='tinydiscord',
   version='1.0',
   description='Compulsory assignment - Web server.',
   author='',
   packages=['tinydiscord'],
   install_requires=['flask', 'flask_login', 'apsw', 'flask_wtf', 'wtforms', 'bcrypt']
)