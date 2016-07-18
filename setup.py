import os
from setuptools import setup

setup(
	name='mcu-info-util',
	version='0.1',
	author='Ivan Kolesnikov',
	author_email='kiv.apple@gmail.com',
	url='https://github.com/KivApple/mcu-info-util',
	packages=['mcu_info_util'],
	entry_points={
		'console_scripts': [
			'mcu-info-util = mcu_info_util.__main__:main'
		]
	},
	data_files=[
		(d, [os.path.join(d, f) for f in files]) for d, folders, files in os.walk('share')
	]
)
