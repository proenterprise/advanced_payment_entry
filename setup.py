# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in advanced_payment_entry/__init__.py
from advanced_payment_entry import __version__ as version

setup(
	name='advanced_payment_entry',
	version=version,
	description='Automatic allocation of payment entries',
	author='Proenterprise Ventures',
	author_email='contact@goelite.in',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
