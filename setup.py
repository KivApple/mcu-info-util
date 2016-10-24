#!/usr/bin/env python
import os, sys
from setuptools import setup


base_dir = os.path.dirname(__file__)
package_dir = os.path.join(base_dir, 'mcu_info_util')
data_files = []
for root, dirs, files in os.walk(os.path.join(package_dir, 'data')):
    data_files += [os.path.join(root, file) for file in files]
package_data_files = [os.path.relpath(data_file, package_dir) for data_file in data_files]
data_files = []
for fname in ('rules.mk', 'toolchain.cmake'):
    fullname = os.path.join(base_dir, 'misc', fname)
    if os.path.isfile(fullname):
        data_files.append(fullname)


setup(
    name='mcu-info-util',
    version='0.4',
    author='Ivan Kolesnikov',
    author_email='kiv.apple@gmail.com',
    url='https://github.com/KivApple/mcu-info-util',
    download_url='https://github.com/KivApple/mcu-info-util/archive/v0.4.tar.gz',
    packages=['mcu_info_util'],
    package_dir={'mcu_info_util': 'mcu_info_util'},
    package_data={'mcu_info_util': package_data_files},
    data_files=[('share/mcu-info-util', data_files)],
    entry_points={
        'console_scripts': [
            'mcu-info-util = mcu_info_util.__main__:main'
        ]
    },
    install_requires=[
        'six',
        'cmsis-svd'
    ],
    description='Small utility that allows you to find embedded toolchain for specified MCU, compiler flags and generate linker script and header files (for ARM MCUs)'
)
