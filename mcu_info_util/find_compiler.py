import os
from .device_tree import DeviceTree

MCU_TYPES = {
    'stm32': 'arm-none-eabi',
    'atsam': 'arm-none-eabi',
    'at91sam': 'arm-none-eabi',
    'atmega': 'avr',
    'attiny': 'avr'
}


def get_mcu_type(mcu):
    for prefix in MCU_TYPES:
        if mcu.startswith(prefix):
            return MCU_TYPES[prefix]
    return 'unknown'


def find_program(program, paths = None):
    fpath, fname = os.path.split(program)
    if fpath:
        if os.path.isfile(program):
            return program
    else:
        if paths is None:
            paths = os.environ['PATH'].split(os.pathsep)
        for path in paths:
            path = path.strip('"')
            program_file = os.path.join(path, program)
            if os.path.isfile(program_file):
                return program_file
            program_file += '.exe'
            if os.path.isfile(program_file):
                return program_file
    return None


def find_compiler(mcu, metadata_dir, args):
    mcu_type = get_mcu_type(mcu)
    if mcu_type == 'arm-none-eabi':
        return find_compiler_arm_none_eabi()
    elif mcu_type == 'avr':
        return find_compiler_avr()
    return ''


def find_compiler_arm_none_eabi():
    compiler = find_program('arm-none-eabi-gcc')
    if compiler:
        return compiler
    try:
        try:
            import winreg
        except:
            import _winreg as winreg
        reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        key = winreg.OpenKey(reg, r'Software\ARM\GNU Tools for ARM Embedded Processors')
        val = winreg.QueryValueEx(key, 'InstallFolder')
        val = val[0] if isinstance(val, tuple) else val
        compiler = os.path.join(val, 'bin', 'arm-none-eabi-gcc.exe')
        if os.path.isfile(compiler):
            return compiler
    except:
        pass
    return ''


def find_compiler_avr():
    compiler = find_program('avr-gcc')
    if compiler:
        return compiler
    try:
        try:
            import winreg
        except:
            import _winreg as winreg
        reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        key = winreg.OpenKey(reg, r'Software\WinAVR')
        i = 0
        while True:
            val = winreg.EnumValue(key, i)
            if len(val) < 3:
                continue
            val = val[1]
            compiler = os.path.join(val, 'bin', 'avr-gcc.exe')
            if os.path.isfile(compiler):
                return compiler
            i += 1
    except:
        pass
    return ''


def find_compiler_options(mcu, metadata_dir, args):
    mcu_type = get_mcu_type(mcu)
    if mcu_type == 'avr':
        return ['-mmcu=' + mcu]
    device_tree = DeviceTree()
    device_tree.load(metadata_dir + '/devices.data')
    entry = device_tree.find(mcu)
    compiler_options = entry.get_options(enable_libopencm3=args.enable_libopencm3) if entry else []
    return compiler_options
