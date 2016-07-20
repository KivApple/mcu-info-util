#!/usr/bin/env python
import os
from setuptools import setup

setup(
	name='mcu-info-util',
	version='0.1',
	author='Ivan Kolesnikov',
	author_email='kiv.apple@gmail.com',
	url='https://github.com/KivApple/mcu-info-util',
	packages=['mcu_info_util'],
	package_dir={'mcu_info_util': 'mcu_info_util'},
	package_data={'mcu_info_util': ['metadata/*', 'metadata/*/*', 'metadata/*/*/*', 'metadata/*/*/*/*']},
	entry_points={
		'console_scripts': [
			'mcu-info-util = mcu_info_util.__main__:main'
		]
	},
	install_requires=[
		'six'
	]
)
