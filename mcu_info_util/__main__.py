import argparse, os, sys
from mcu_info_util.toolchain import Toolchain


def main():
    parser = argparse.ArgumentParser(description='MCU info util')
    parser.add_argument('--mcu', help='specify MCU model (e. g. STM32F407VG)')
    parser.add_argument('--find-compiler', help='search target MCU toolchain and print path to the compiler executable',
                        action='store_true')
    parser.add_argument('--find-prefix', help='search target MCU binutils prefix', action='store_true')
    parser.add_argument('--print-flags', help='print required compiler and linker flags for target MCU',
                        action='store_true')
    parser.add_argument('--linker-script', help='specify output file name for the linker script')
    parser.add_argument('--header', help='specify output file name for the C/C++ header')
    parser.add_argument('--build-scripts-dir', help='print mcu-info-util build scripts directory', action='store_true')
    args = parser.parse_args()

    if args.build_scripts_dir:
        paths = (
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'misc'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'share', 'mcu-info-util'),
            os.path.join(sys.prefix, 'share', 'mcu-info-util')
        )
        for path in paths:
            if os.path.isfile(os.path.join(path, 'rules.mk')):
                print(path)
                break
    elif args.mcu:
        mcu = args.mcu.lower()
        toolchain = Toolchain.find_toolchain(mcu)
        if toolchain is None:
            print("Failed to detect toolchain required for MCU %s" % mcu)
            return
        toolchain_prefix = toolchain.find_prefix()
        compiler_executable = toolchain.find_compiler()
        compiler_options = toolchain.get_flags(mcu)
        if args.find_compiler:
            print(compiler_executable)
        if args.find_prefix:
            print(toolchain_prefix)
        if args.print_flags:
            compiler_options_str = ' '.join(compiler_options)
            print(compiler_options_str)
        if args.linker_script:
            if args.linker_script == "?":
                print("yes" if toolchain.generate_linker_script(mcu) else "no")
            else:
                toolchain.generate_linker_script(mcu, args.linker_script)
        if args.header:
            if args.header == "?":
                print("yes" if toolchain.generate_header(mcu) else "no")
            else:
                toolchain.generate_header(mcu, args.header)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
