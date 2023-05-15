from cffi import FFI
from os.path import dirname, join

file_dir = dirname(__file__)
ffi_dir = join(file_dir, 'ada-url')

ffi_builder = FFI()
ffi_builder.set_source(
    '_ada_wrapper',
    '# include "ada_c.h"',
    include_dirs=[ffi_dir],
    extra_objects=[join(ffi_dir, 'ada.o')],
)

cdef_lines = []
with open(join(ffi_dir, 'ada_c.h'), 'rt') as f:
    for line in f:
        if not line.startswith('#'):
            cdef_lines.append(line)
ffi_builder.cdef(''.join(cdef_lines))

if __name__ == '__main__':
    ffi_builder.compile(tmpdir=file_dir, verbose=True)
