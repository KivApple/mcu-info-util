import os
from mcu_info_util.toolchain import Toolchain
from mcu_info_util.utils import find_program


class ToolchainAVR(Toolchain):
    def find_compiler(self):
        compiler = find_program("avr-gcc")
        if compiler:
            return compiler
        try:
            try:
                import winreg
            except:
                import _winreg as winreg
            reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
            key = winreg.OpenKey(reg, r"Software\WinAVR")
            i = 0
            while True:
                val = winreg.EnumValue(key, i)
                if len(val) < 3:
                    continue
                val = val[1]
                compiler = os.path.join(val, "bin", "avr-gcc.exe")
                if os.path.isfile(compiler):
                    return compiler
                i += 1
        except:
            pass
        return ""

    def get_flags(self, mcu):
        return ["-mmcu=%s" % mcu.lower()]
