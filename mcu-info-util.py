import os, argparse
from device_tree import DeviceTree
import linker_script
from svd import load_svd_for_mcu

parser = argparse.ArgumentParser(description='MCU info util')
parser.add_argument('--mcu', help='Specify MCU model (e. g. STM32F407VG)')
parser.add_argument('--linker-script', help='Specify output file name for linker script')
parser.add_argument('--header', help='Specify output file name for header')
parser.add_argument('--enable-libopencm3', help='Enable linking with libopencm3 library (if supported for target MCU)',
					action='store_true')
parser.add_argument('--metadata-dir', help='Specify metadata directory')
args = parser.parse_args()

if args.metadata_dir:
	metadata_dir = args.metadata_dir
else:
	metadata_dir = os.path.dirname(__file__) + '/metadata'

if args.mcu:
	device_tree = DeviceTree(metadata_dir + '/devices.data')
	entry = device_tree.find(args.mcu)
	compiler_options = entry.get_options(enable_libopencm3=args.enable_libopencm3)
	compiler_options_str = ' '.join(compiler_options)
	print(compiler_options_str)
	if args.linker_script:
		linker_script.generate(args.linker_script, compiler_options)
	if args.header:
		svd = load_svd_for_mcu(metadata_dir + '/SVD', args.mcu)
		if svd:
			svd.generate_header(args.header)
else:
	parser.print_help()
