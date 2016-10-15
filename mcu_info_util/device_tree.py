import re


class DeviceTree:
    def __init__(self):
        self.devices = []

    def load(self, file_name):
        with open(file_name, 'r') as file:
            for line in file:
                if len(line) == 0:
                    continue
                if line[0] == '#':
                    continue
                line = line.strip()
                parts = line.split(' ')
                if len(parts) < 2:
                    continue
                name = parts[0]
                parent = parts[1]
                if parent == 'END':
                    parent = ''
                self.devices.append(DeviceTreeEntry(self, name, parent, parts[2:]))

    def find(self, name):
        if name.startswith('AT91SAM'):
            name = name[4:]
        for entry in self.devices:
            pattern = entry.name.replace('?', '.').replace('*', '.*')
            if re.compile(pattern, re.IGNORECASE).match(name):
                return entry
        return None


class DeviceTreeEntry:
    def __init__(self, tree, name, parent, options):
        self.tree = tree
        self.name = name
        self.parent = parent
        self.options = options

    def get_options(self, enable_libopencm3 = False, only_defines = False):
        options = self.options
        if self.parent:
            parent = self.tree.find(self.parent)
            if parent:
                options = options + parent.get_options(enable_libopencm3=enable_libopencm3, only_defines=only_defines)
        final_options = []
        for option in options:
            if option[0] == '-':
                if only_defines and (not option.startswith('-D')):
                    continue
                if (not enable_libopencm3) and option.startswith('-lopencm3_'):
                    continue
            else:
                option = '-D_' + option
            if option.startswith('-D'):
                try:
                    i = option.index('=')
                    if i > 0:
                        defName = option[0:i]
                        defValue = option[(i + 1):]
                        if re.match(r'[0-9]+K', defValue):
                            defValue = int(defValue[:-1]) * 1024
                        elif re.match(r'[0-9]+M', defValue):
                            defValue = int(defValue[:-1]) * 1024 * 1024
                        option = defName + '=' + str(defValue)
                except:
                    pass
            final_options.append(option)
        return final_options
