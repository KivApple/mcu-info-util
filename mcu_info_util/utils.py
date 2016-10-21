import os


def find_program(program, paths = None):
    fpath, fname = os.path.split(program)
    if fpath:
        if os.path.isfile(program):
            return program
    else:
        if paths is None:
            paths = os.environ['PATH'].split(os.pathsep)
        for path in paths:
            path = path.strip('"')
            program_file = os.path.join(path, program)
            if os.path.isfile(program_file):
                return program_file
            program_file += '.exe'
            if os.path.isfile(program_file):
                return program_file
    return None
