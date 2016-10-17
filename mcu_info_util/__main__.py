import argparse
import os

from . import linker_script
from .svd import load_svd_for_mcu
from .find_compiler import find_toolchain_prefix, find_compiler, find_compiler_options


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
    parser.add_argument('--use-defines', help='use #define instead of static const', action='store_true')
    parser.add_argument('--enable-libopencm3', help='enable linking with libopencm3 library (if supported for target MCU)',
                        action='store_true')
    parser.add_argument('--metadata-dir', help='specify metadata directory')
    args = parser.parse_args()

    if args.metadata_dir:
        metadata_dir = args.metadata_dir
    else:
        metadata_dir = os.path.join(os.path.dirname(__file__), 'metadata')

    if args.mcu:
        toolchain_prefix = find_toolchain_prefix(args.mcu, metadata_dir, args)
        compiler_executable = find_compiler(args.mcu, metadata_dir, args)
        compiler_options = find_compiler_options(args.mcu, metadata_dir, args)
        if args.find_compiler:
            print(compiler_executable)
        if args.find_prefix:
            print(toolchain_prefix)
        if args.print_flags:
            compiler_options_str = ' '.join(compiler_options)
            print(compiler_options_str)
        if args.linker_script:
            linker_script.generate(args.linker_script, compiler_options)
        if args.header:
            svd = load_svd_for_mcu(metadata_dir + '/SVD', args.mcu)
            if args.header != '?':
                if svd:
                    svd.generate_header(args.header, use_defines=args.use_defines)
            else:
                print("yes" if svd else "no")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
