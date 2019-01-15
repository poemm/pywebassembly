#!/usr/bin/env python
"""
    PyWebAssembly - Implmentation of WebAssembly, and some tools.
    Copyright (C) 2018-2019  Paul Dworzanski

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


import sys
sys.path.append('..')

import pywebassembly as wasm

def export_only_main_and_memory(mod):
  print("\nexports (should be main function and the memory):")
  for export_ in mod["exports"][:]:
    if export_["name"]=="_main":
      export_["name"]="main"
    if export_["name"] not in {"main","memory"}:
      mod["exports"].remove(export_)
  for export_ in mod["exports"][:]:
    print(export_)

def import_only_ethereum_eei(mod):
  print("\nimports (should be only ewasm helper functions):")
  for import_ in mod["imports"]:
    if import_["module"] != "ethereum":
      import_["module"] = "ethereum"
  for import_ in mod["imports"]:
    print(import_)

def parse_wasm_and_clean_up(filename):
  #print("reading ",filename)
  with open(filename, 'rb') as f:
    bytecode = memoryview(f.read())
    mod = wasm.decode_module(bytecode)
    export_only_main_and_memory(mod)
    import_only_ethereum_eei(mod)
    fout = open(filename.rsplit('.',1)[0]+"_ewasmified.wasm", 'wb')
    bytecode_out = wasm.encode_module(mod)
    fout.write(bytecode_out)
    fout.close()


if __name__ == "__main__":
  import sys
  if len(sys.argv)!=2:
    print("Argument should be <filename>.wasm")
  else:
    parse_wasm_and_clean_up(sys.argv[1])

