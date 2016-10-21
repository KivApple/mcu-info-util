import os
from mcu_info_util.toolchain import Toolchain
from mcu_info_util.utils import find_program
from mcu_info_util.device_tree import DeviceTree
from pkg_resources import resource_filename
from . import linker_script
from mcu_info_util.svd_utils import generate_header


class ToolchainARM(Toolchain):
    def find_compiler(self):
        compiler = find_program("arm-none-eabi-gcc")
        if compiler:
            return compiler
        try:
            try:
                import winreg
            except:
                import _winreg as winreg
            reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
            key = winreg.OpenKey(reg, r"Software\ARM\GNU Tools for ARM Embedded Processors")
            val = winreg.QueryValueEx(key, "InstallFolder")
            val = val[0] if isinstance(val, tuple) else val
            compiler = os.path.join(val, "bin", "arm-none-eabi-gcc.exe")
            if os.path.isfile(compiler):
                return compiler
        except:
            pass
        return ""

    def get_flags(self, mcu):
        device_tree = DeviceTree()
        device_tree.load(resource_filename("mcu_info_util", "data/devices.data"))
        entry = device_tree.find(mcu)
        compiler_options = entry.get_options() if entry else []
        return compiler_options

    def generate_header(self, mcu, filename=None):
        return generate_header(mcu, filename)

    def generate_linker_script(self, mcu, filename=None):
        return linker_script.generate(self.get_flags(mcu), filename)
