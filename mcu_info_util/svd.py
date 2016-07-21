import os, re, xml.etree.ElementTree

def load_svd_for_mcu(base_dir, mcu):
	mcu = mcu.upper()
	for sub_dir in os.listdir(base_dir):
		for file in os.listdir(base_dir + '/' + sub_dir):
			if file.endswith('.svd'):
				pattern = file[:-4].upper().replace('X', '.')
				if re.compile(pattern).match(mcu):
					file_name = base_dir + '/' + sub_dir + '/' + file
					return SVD(file_name)
	if mcu.startswith('AT91SAM'):
		return load_svd_for_mcu(base_dir, 'AT' + mcu[4:])
	return None

class SVD:
	def __init__(self, file_name):
		self.file_name = file_name
		tree = xml.etree.ElementTree.parse(file_name)
		root = tree.getroot()
		periphList = root.find('peripherals')
		self.periphList = []
		for periph in periphList.iter('peripheral'):
			self.periphList.append(Peripheral(self, periph))

	def generate_header(self, file_name, use_defines = False):
		f = open(file_name, 'w')
		include_guard = '__%s__' % (os.path.basename(file_name).replace('.', '_').upper())
		f.write('#ifndef %s\n' % (include_guard))
		f.write('#define %s\n' % (include_guard))
		f.write('\n')
		f.write('#include <stdint.h>\n')
		f.write('\n')
		f.write('#ifndef ISR\n')
		f.write('#ifdef __cplusplus\n')
		f.write('#define ISR(name) extern "C" void name(void)\n')
		f.write('#else\n')
		f.write('#define ISR(name) void name(void)\n')
		f.write('#endif\n')
		f.write('#endif\n')
		f.write('\n')
		f.write('#ifndef PACKED\n')
		f.write('#define PACKED __attribute__((packed))\n')
		f.write('#endif\n')
		f.write('\n')
		f.write('#ifndef bit\n')
		f.write('#define bit(i) (1 << (i))\n')
		f.write('#endif\n')
		f.write('\n')
		interrupts_names = []
		interrupts = {}
		max_interrupt_index = -1
		for periph in self.periphList:
			already_packed = True
			for reg in periph.regs:
				if (reg.offset % (reg.size / 8)) != 0:
					already_packed = False
					break
			f.write('/* %s: %s */\n' % (periph.name, periph.desc))
			f.write('\n')
			f.write('#ifndef %s_BASE\n' % (periph.name))
			f.write('\n')
			if already_packed:
				f.write('typedef struct %s_regs_t {\n' % (periph.name))
			else:
				f.write('typedef struct PACKED %s_regs_t {\n' % (periph.name))
			fields = {}
			max_offset = 0
			for reg in periph.regs:
				if reg.offset in fields:
					if isinstance(fields[reg.offset], list):
						fields[reg.offset].append(reg)
					else:
						fields[reg.offset] = [fields[reg.offset], reg]
				else:
					fields[reg.offset] = reg
					if reg.offset > max_offset:
						max_offset = reg.offset
			offset = 0
			reserved_index = 1
			reserved_count = 0
			while offset <= max_offset:
				if offset in fields:
					if reserved_count > 0:
						f.write('\tuint8_t RESERVED_%s[%s];\n' % (reserved_index, reserved_count))
						reserved_index += 1
						reserved_count = 0
					if isinstance(fields[offset], list):
						f.write('\tunion {\n')
						max_size = 0
						for reg in fields[offset]:
							if reg.dim > 1:
								f.write('\t\tuint%s_t %s[%s]; /* %s */\n' % (reg.size, reg.name, reg.dim, reg.desc))
							else:
								f.write('\t\tuint%s_t %s; /* %s */\n' % (reg.size, reg.name, reg.desc))
							size = reg.size * reg.dim
							if size > max_size:
								max_size = size
						f.write('\t};\n')
						offset += max_size / 8
					else:
						reg = fields[offset]
						if reg.dim > 1:
							f.write('\tuint%s_t %s[%s]; /* %s */\n' % (reg.size, reg.name, reg.dim, reg.desc))
						else:
							f.write('\tuint%s_t %s; /* %s */\n' % (reg.size, reg.name, reg.desc))
						offset += (reg.size * reg.dim) / 8
				else:
					reserved_count += 1
					offset += 1
			f.write('} %s_regs_t;\n' % (periph.name))
			f.write('\n')
			f.write('#define %s_BASE %s\n' % (periph.name, periph.baseAddress.lower()))
			f.write('\n')
			f.write('static volatile %s_regs_t* const %s_regs = (volatile %s_regs_t*)%s_BASE;\n' %
					(periph.name, periph.name, periph.name, periph.name))
			f.write('\n')
			for interrupt in periph.interrupts:
				if interrupt.name in interrupts_names:
					f.write('/* ')
				if use_defines:
					f.write('#define %s_IRQ %s' % (interrupt.name, interrupt.index))
				else:
					f.write('static const uint8_t %s_IRQ = %s;' % (interrupt.name, interrupt.index))
				if interrupt.name in interrupts_names:
					f.write(' */')
				f.write('\n\n')
				interrupts[interrupt.index] = interrupt
				if interrupt.index > max_interrupt_index:
					max_interrupt_index = interrupt.index
				interrupts_names.append(interrupt.name)
			for reg in periph.regs:
				f.write('/* %s_%s: %s */\n' % (periph.name, reg.name, reg.desc))
				if use_defines:
					f.write('#define %s_%s ((volatile uint%s_t*)(%s_BASE + %s)) \n' %
							(periph.name, reg.name, reg.size, periph.name, reg.offset))
				else:
					f.write('static volatile uint%s_t* const %s_%s = ((volatile uint%s_t*)(%s_BASE + %s));\n' %
							(reg.size, periph.name, reg.name, reg.size, periph.name, reg.offset))
				f.write('\n')
				for field in reg.fields:
					if field.size == reg.size:
						continue
					f.write('/* %s_%s_%s: %s */\n' % (periph.name, reg.name, field.name, field.desc))
					if field.size == 1:
						if use_defines:
							f.write('#define %s_%s_%s bit(%s)\n' %
									(periph.name, reg.name, field.name, field.offset))
						else:
							f.write('static const uint%s_t %s_%s_%s = bit(%s);\n' %
									(reg.size, periph.name, reg.name, field.name, field.offset))
					else:
						if use_defines:
							f.write('#define %s_%s_%s_OFFSET %s\n' %
									(periph.name, reg.name, field.name, field.offset))
							f.write('#define %s_%s_%s_LENGTH %s\n' %
									(periph.name, reg.name, field.name, field.size))
							f.write('#define %s_%s_%s_MASK %s\n' %
									(periph.name, reg.name, field.name,
									 hex(((2 ** field.size) - 1) << field.offset)))
						else:
							f.write('static const uint8_t %s_%s_%s_OFFSET = %s;\n' %
									(periph.name, reg.name, field.name, field.offset))
							f.write('static const uint8_t %s_%s_%s_LENGTH = %s;\n' %
									(periph.name, reg.name, field.name, field.size))
							f.write('static const uint%s_t %s_%s_%s_MASK = %s;\n' %
									(reg.size, periph.name, reg.name, field.name, hex(((2 ** field.size) - 1) << field.offset)))
				f.write('\n')
			if os.path.basename(self.file_name).upper().startswith('STM32'):
				if periph.name == 'RCC':
					f.write('typedef enum STM32RCCPeriph {\n')
					for reg in periph.regs:
						if reg.name.endswith('ENR'):
							for field in reg.fields:
								if field.name.endswith('EN'):
									f.write('\tRCC_%s_%s = (%s << 5) | %s,\n' %
											(reg.name[:-3], field.name[:-2], hex(reg.offset), field.offset))
					f.write('} STM32RCCPeriph;\n')
					f.write('\n')
			f.write('#endif\n')
			f.write('\n')
		f.write('#ifdef DEFINE_IRQ_HANDLERS\n')
		f.write('\n')
		interrupt_index = 0
		while interrupt_index < max_interrupt_index:
			if interrupt_index in interrupts:
				interrupt = interrupts[interrupt_index]
				f.write('#pragma weak %s_vect=empty_handler\n' % (interrupt.name))
				f.write('ISR(%s_vect);\n' % (interrupt.name))
			interrupt_index += 1
		f.write('\n')
		f.write('#define IRQ_HANDLERS \\\n')
		interrupt_index = 0
		while interrupt_index < max_interrupt_index:
			if interrupt_index in interrupts:
				f.write('\t%s_vect,\\\n' % (interrupts[interrupt_index].name))
			else:
				f.write('\t0,\\\n')
			interrupt_index += 1
		f.write('\t0\n')
		f.write('\n')
		f.write('#endif\n')
		f.write('\n')
		f.write('#endif\n')
		f.close()


class Peripheral:
	def __init__(self, svd, node):
		self.name = node.find('name').text
		self.baseAddress = node.find('baseAddress').text
		reg_list = node.find('registers')
		self.regs = []
		if reg_list is not None:
			for reg in reg_list.iter('register'):
				self.regs.append(PeripheralRegister(reg))
		self.interrupts = []
		for interrupt in node.iter('interrupt'):
			self.interrupts.append(PeripheralInterrupt(interrupt))
		if 'derivedFrom' in node.attrib:
			parentName = node.attrib['derivedFrom']
			for periph in svd.periphList:
				if periph.name == parentName:
					self.desc = periph.desc
					for reg in periph.regs:
						self.regs.append(reg)
		else:
			self.desc = node.find('description').text
		regNames = []
		for reg in self.regs:
			regNames.append(reg.name)
		prefix = os.path.commonprefix(regNames)
		for reg in self.regs:
			newName = reg.name[len(prefix):]
			if (len(newName) > 0) and (newName[0].isalpha() or newName[0] == '_'):
				reg.name = newName


class PeripheralRegister:
	def __init__(self, node):
		self.name = node.find('name').text
		self.desc = node.find('description').text
		self.offset = int(node.find('addressOffset').text, 0)
		self.size = int(node.find('size').text, 0)
		self.fields = []
		field_list = node.find('fields')
		if field_list is not None:
			for field in field_list.iter('field'):
				self.fields.append(PeripheralRegisterField(field))
		if node.find('dim') is not None:
			self.dim = int(node.find('dim').text, 0)
			self.name = self.name.replace('[%s]', '')
		else:
			self.dim = 1


class PeripheralRegisterField:
	def __init__(self, node):
		self.name = node.find('name').text
		if node.find('description') is not None:
			self.desc = node.find('description').text
		else:
			self.desc = ''
		self.offset = int(node.find('bitOffset').text, 0)
		self.size = int(node.find('bitWidth').text, 0)


class PeripheralInterrupt:
	def __init__(self, node):
		self.name = node.find('name').text.replace('_IRQ', '')
		self.index = int(node.find('value').text, 0)

