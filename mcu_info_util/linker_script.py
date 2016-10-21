from six import iteritems


def generate(options, filename=None):
    mem_regions_count = 0
    defines = {}
    for option in options:
        if not option.startswith('-D_'):
            continue
        parts = option.split('=', 1)
        if len(parts) < 2:
            continue
        name = parts[0][3:]
        value = parts[1]
        defines[name] = value
        if name.endswith('_OFF'):
            mem_regions_count += 1
    if mem_regions_count == 0:
        return False
    if filename is None:
        return True
    f = open(filename, 'w')
    f.write('EXTERN(vector_table)\n')
    f.write('ENTRY(reset_handler)\n')
    f.write('\n')
    f.write('MEMORY {\n')
    for k, v in iteritems(defines):
        if k.endswith('_OFF'):
            continue
        offset_key = '%s_OFF' % (k)
        if not (offset_key in defines):
            continue
        offset = defines[offset_key]
        length = v
        if k.startswith('ROM'):
            access = 'rx'
        elif k == 'EEP':
            access = 'r'
        else:
            access = 'rwx'
        f.write('\t%s (%s) : ORIGIN = %s, LENGTH = %s\n' % (k.lower(), access, offset, length))
    f.write('}\n')
    f.write('\n')
    f.write('SECTIONS {\n')
    f.write('\t.text : {\n')
    f.write('\t\t*(.vectors)\n')
    f.write('\t\t*(.text)\n')
    f.write('\t\t. = ALIGN(4);\n')
    f.write('\t\t*(.rodata)\n')
    f.write('\t\t. = ALIGN(4);\n')
    f.write('\t} >rom\n')
    f.write('\t.preinit_array : {\n')
    f.write('\t\t__preinit_array_start = .;\n')
    f.write('\t\tKEEP (*(.preinit_array))\n')
    f.write('\t\t__preinit_array_end = .;\n')
    f.write('\t} >rom\n')
    f.write('\t.init_array : {\n')
    f.write('\t\t__init_array_start = .;\n')
    f.write('\t\tKEEP (*(SORT(.init_array.*)))\n')
    f.write('\t\tKEEP (*(.init_array))\n')
    f.write('\t\t__init_array_end = .;\n')
    f.write('\t} >rom\n')
    f.write('\t.fini_array : {\n')
    f.write('\t\t__fini_array_start = .;\n')
    f.write('\t\tKEEP (*(.fini_array))\n')
    f.write('\t\tKEEP (*(SORT(.fini_array.*)))\n')
    f.write('\t\t__fini_array_end = .;\n')
    f.write('\t} >rom\n')
    f.write('\t.ARM.extab : {\n')
    f.write('\t\t*(.ARM.extab*)\n')
    f.write('\t} >rom\n')
    f.write('\t.ARM.exidx : {\n')
    f.write('\t\t__exidx_start = .;\n')
    f.write('\t\t*(.ARM.exidx*)\n')
    f.write('\t\t__exidx_end = .;\n')
    f.write('\t} >rom\n')
    f.write('\t. = ALIGN(4);\n')
    f.write('\t_etext = .;\n')
    f.write('\t.data : {\n')
    f.write('\t\t_data = .;\n')
    f.write('\t\t*(.data*)\n')
    f.write('\t\t. = ALIGN(4);\n')
    f.write('\t\t_edata = .;\n')
    f.write('\t} >ram AT >rom\n')
    f.write('\t_data_loadaddr = LOADADDR(.data);\n')
    f.write('\t.bss : {\n')
    f.write('\t\t*(.bss*)\n')
    f.write('\t\t*(COMMON)\n')
    f.write('\t\t. = ALIGN(4);\n')
    f.write('\t\t_ebss = .;\n')
    f.write('\t} >ram\n')
    for k, v in iteritems(defines):
        if k.endswith('_OFF'):
            continue
        offset_key = '%s_OFF' % (k)
        if not (offset_key in defines):
            continue
        if k in ('RAM', 'ROM'):
            continue
        name = k.lower()
        f.write('\t.%s : {\n' % (name))
        f.write('\t\t*(.%s*)\n' % (name))
        f.write('\t\t. = ALIGN(4);\n')
        f.write('\t} >%s\n' % (name))
    f.write('\t/DISCARD/ : { *(.eh_frame) }\n')
    f.write('\t. = ALIGN(4);\n')
    f.write('\tend = .;\n')
    f.write('}\n')
    f.write('\n')
    f.write('PROVIDE(_stack = ORIGIN(ram) + LENGTH(ram));\n')
    f.close()
    return True
