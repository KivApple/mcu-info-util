import os
from re import match, sub
from datetime import datetime
from pkg_resources import resource_listdir
from cmsis_svd.parser import SVDParser
from functools import reduce


def find_for_mcu(mcu):
    mcu = mcu.lower()
    vendors = resource_listdir("cmsis_svd", "data")
    for vendor in vendors:
        fnames = resource_listdir("cmsis_svd", "data/%s" % vendor)
        for fname in fnames:
            filename = fname.lower()
            if not filename.endswith(".svd"):
                continue
            filename = filename[:-4]
            if mcu.startswith(filename):
                return vendor, fname
        for fname in fnames:
            filename = fname.lower()
            if not filename.endswith(".svd"):
                continue
            filename = "^%s.*" % filename[:-4].replace('x', '.')
            if match(filename, mcu):
                return vendor, fname
    return None, None


def load_svd_for_mcu(mcu):
    vendor, filename = find_for_mcu(mcu)
    if (vendor is None) or (filename is None):
        return None
    return SVDParser.for_packaged_svd(vendor, filename).get_device()
    #parser = SVDParser.for_mcu(mcu)
    #if parser is None:
    #    return None
    #return parser.get_device()


GENERATED_FILE_HEADER = """/* This file generated at %s by mcu-info-util from SVD description. */
"""

def generate_header(mcu, filename=None):
    svd = load_svd_for_mcu(mcu)
    if not svd:
        return False
    if not filename:
        return True
    f = open(filename, "w")
    f.write(GENERATED_FILE_HEADER % datetime.now().strftime('%x %X'))
    include_guard = "__%s__" % (os.path.basename(filename).replace('.', '_').upper())
    f.write("#ifndef %s\n" % (include_guard))
    f.write("#define %s\n" % (include_guard))
    f.write("\n")
    f.write("#include <stdint.h>\n")
    f.write("\n")
    for periph in svd.peripherals:
        f.write("#define %s_BASE %s\n" % (periph.name, hex(periph.base_address)))
    f.write("\n")
    for periph in svd.peripherals:
        f.write("/* %s: %s */\n" % (periph.name, periph.description))
        f.write("\n")
        f.write("typedef struct %s_regs_t {\n" % periph.name)
        regs = []
        for reg in periph.registers:
            regs.append([reg.address_offset, sub(r"[\[\]]", "", reg.name), reg.size])
        regs.sort()
        _regs = regs
        regs = []
        for reg in _regs:
            if len(regs) and (regs[-1][0] == reg[0]):
                assert regs[-1][2] == reg[2]
                if isinstance(regs[-1][1], str):
                    regs[-1][1] = [regs[-1][1]]
                regs[-1][1] += [reg[1]]
            else:
                regs.append(reg)
        reseved_index = 0
        offset = 0
        for reg in regs:
            skip_count = reg[0] - offset
            assert skip_count >= 0, "%s_%s %s %s %s" % (periph.name, reg[1], offset, reg[0], regs)
            if skip_count:
                f.write("\tuint8_t RESERVED_%s[%s];\n" % (reseved_index, skip_count))
                reseved_index += 1
                offset += skip_count
            item_size = (reg[2] + 7) // 8
            if isinstance(reg[1], str):
                f.write("\tuint%s_t %s;\n" % (item_size * 8, reg[1]))
            else:
                f.write("\tunion {\n")
                for name in reg[1]:
                    f.write("\t\tuint%s_t %s;\n" % (item_size * 8, name))
                f.write("\t};\n")
            offset += item_size
        f.write("} %s_regs_t;\n" % periph.name)
        f.write("\n")
        f.write("#define %s_regs ((volatile %s_regs_t*)%s_BASE)\n" % (periph.name, periph.name, periph.name))
        f.write("\n")
        for interrupt in periph.interrupts:
            f.write("#define %s_IRQ %s\n" % (interrupt.name, interrupt.value))
        f.write("\n")
        for reg in periph.registers:
            f.write("/* %s_%s: %s */\n" % (periph.name, sub(r"[\[\]]", "", reg.name), reg.description))
            f.write("#define %s_%s (*((volatile uint%s_t*)(%s_BASE + %s)))\n" %
                    (periph.name, sub(r"[\[\]]", "", reg.name), reg.size, periph.name, reg.address_offset))
            f.write("\n")
            for field in reg.fields:
                f.write("/* %s_%s_%s: %s */\n" % (periph.name, sub(r"[\[\]]", "", reg.name), field.name, field.description))
                if field.bit_width == 1:
                    f.write("#define %s_%s_%s (1 << %s)\n" % (periph.name, sub(r"[\[\]]", "", reg.name),
                                                              field.name, field.bit_offset))
                else:
                    f.write("#define %s_%s_%s_OFFSET %s\n" % (periph.name, sub(r"[\[\]]", "", reg.name),
                                                              field.name, field.bit_offset))
                    f.write("#define %s_%s_%s_WIDTH %s\n" % (periph.name, sub(r"[\[\]]", "", reg.name),
                                                             field.name, field.bit_width))
                    f.write("#define %s_%s_%s_MASK %s\n" %
                            (periph.name, sub(r"[\[\]]", "", reg.name), field.name,
                             hex(((2 ** field.bit_width) - 1) << field.bit_offset)))
            f.write("\n")
        f.write("\n")
    interrupts = []
    for periph in svd.peripherals:
        for interrupt in periph.interrupts:
            interrupts.append([interrupt.value, interrupt.name])
    interrupts.sort()
    _interrupts = interrupts
    interrupts = []
    for interrupt in _interrupts:
        if len(interrupts) and (interrupts[-1][0] == interrupt[0]):
            continue
        else:
            interrupts.append(interrupt)
    f.write("#ifndef ISR\n")
    f.write("#ifdef __cplusplus\n")
    f.write("#define ISR(name) extern \"C\" void name(void)\n")
    f.write("#else\n")
    f.write("#define ISR(name) void name(void)\n")
    f.write("#endif\n")
    f.write("#endif\n")
    f.write("\n")
    f.write("ISR(empty_handler);\n")
    for interrupt in interrupts:
        f.write("ISR(%s_handler);\n" % interrupt[1])
    f.write("\n")
    f.write("#ifdef DEFINE_IRQ_HANDLERS\n")
    f.write("\n")
    f.write("ISR(empty_handler) {}\n")
    f.write("\n")
    for interrupt in interrupts:
        f.write("#pragma weak %s_handler=empty_handler\n" % interrupt[1])
    f.write("\n")
    f.write("#define IRQ_HANDLERS \\\n")
    index = 0
    for interrupt in interrupts:
        skip_count = interrupt[0] - index
        assert skip_count >= 0
        while skip_count > 0:
            f.write("\t0,\\\n")
            skip_count -= 1
            index += 1
        f.write("\t%s_handler,\\\n" % interrupt[1])
        index += 1
    f.write("\t0\n")
    f.write("\n")
    f.write("#endif\n")
    f.write("\n")
    f.write("#endif\n")
    f.close()
    return True
