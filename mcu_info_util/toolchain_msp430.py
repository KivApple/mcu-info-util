from mcu_info_util.toolchain import Toolchain
from mcu_info_util.utils import find_program


class ToolchainMSP430(Toolchain):
    def find_compiler(self):
        compiler = find_program("msp430-elf-gcc")
        if compiler:
            return compiler
        return ""

    def get_flags(self, mcu):
        return ["-mmcu=%s" % mcu.lower()]
