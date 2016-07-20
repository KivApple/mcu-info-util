import argparse
import os

from mcu_info_util import linker_script
from mcu_info_util.device_tree import DeviceTree
from mcu_info_util.svd import load_svd_for_mcu

def main():
	parser = argparse.ArgumentParser(description='MCU info util')
	parser.add_argument('--mcu', help='specify MCU model (e. g. STM32F407VG)')
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
		device_tree = DeviceTree(metadata_dir + '/devices.data')
		entry = device_tree.find(args.mcu)
		compiler_options = entry.get_options(enable_libopencm3=args.enable_libopencm3)
		if args.print_flags:
			compiler_options_str = ' '.join(compiler_options)
			print(compiler_options_str)
		if args.linker_script:
			linker_script.generate(args.linker_script, compiler_options)
		if args.header:
			svd = load_svd_for_mcu(metadata_dir + '/SVD', args.mcu)
			if svd:
				svd.generate_header(args.header, use_defines=args.use_defines)
	else:
		parser.print_help()

if __name__ == "__main__":
	main()
