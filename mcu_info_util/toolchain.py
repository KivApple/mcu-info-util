import os


class Toolchain:
    MCU_TYPES = {
        "stm32": "arm",
        "atsam": "arm",
        "at91sam": "arm",
        "atmega": "avr",
        "attiny": "avr",
        "msp430": "msp430"
    }

    @classmethod
    def mcu_type(cls, mcu):
        for prefix in cls.MCU_TYPES:
            if mcu.startswith(prefix):
                return cls.MCU_TYPES[prefix]
        return "unknown"

    @classmethod
    def find_toolchain(cls, mcu):
        type = cls.mcu_type(mcu)
        if type == "arm":
            from mcu_info_util.toolchain_arm import ToolchainARM
            return ToolchainARM()
        if type == "avr":
            from mcu_info_util.toolchain_avr import ToolchainAVR
            return ToolchainAVR()
        if type == "msp430":
            from mcu_info_util.toolchain_msp430 import ToolchainMSP430
            return ToolchainMSP430()
        return None

    def find_compiler(self):
        return ""

    def find_prefix(self):
        compiler = self.find_compiler()
        if compiler.endswith("gcc"):
            return compiler[0:-3]
        return os.path.dirname(compiler) + '/'

    def get_flags(self, mcu):
        return []

    def generate_header(self, mcu, filename=None):
        return False

    def generate_linker_script(self, mcu, filename=None):
        return False
