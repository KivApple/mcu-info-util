from mcu_info_util.toolchain import Toolchain
import unittest


class TestAsLibrary(unittest.TestCase):
    def test_genheader(self):
        toolchain = Toolchain.find_toolchain("stm32f103c8t6")
        self.assertNotEqual(toolchain, None)
        self.assertTrue(toolchain.generate_header("stm32f103c8t6"))

    def test_genlinkerscript(self):
        toolchain = Toolchain.find_toolchain("stm32f103c8t6")
        self.assertNotEqual(toolchain, None)
        self.assertTrue(toolchain.generate_linker_script("stm32f103c8t6"))

    def test_getflags(self):
        toolchain = Toolchain.find_toolchain("stm32f103c8t6")
        self.assertNotEqual(toolchain, None)
        self.assertTrue(len(toolchain.get_flags("stm32f103c8t6")) > 0)
