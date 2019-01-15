#!/usr/bin/env python3

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



# Some helper functions to parse a .wasm file and invoke a function

def instantiate_wasm_invoke_start(filename):
  file_ = open(filename, 'rb')
  if not file_: return "error, could not open "+filename
  bytestar = memoryview(file_.read())
  if not bytestar: return "error, could not read "+filename
  module = wasm.decode_module(bytestar)	#get module as abstract syntax
  #print("module",module)
  if not module: return "error, could not decode "+filename
  store = wasm.init_store()		#do this once for each VM instance
  externvalstar = []			#imports, hopefully none
  store,moduleinst,ret = wasm.instantiate_module(store,module,externvalstar)
  if moduleinst == "error": return "error, module could not be instantiated"
  return ret
   

def instantiate_wasm_invoke_func(filename,funcname,args):
  file_ = open(filename, 'rb')
  if not file_: return "error, could not open "+filename
  bytestar = memoryview(file_.read())
  if not bytestar: return "error, could not read "+filename
  module = wasm.decode_module(bytestar)	#get module as abstract syntax
  #print("module",module)
  if not module: return "error, could not decode "+filename
  store = wasm.init_store()		#do this once for each VM instance
  externvalstar = []			#imports, hopefully none
  store,moduleinst,ret = wasm.instantiate_module(store,module,externvalstar)
  if moduleinst == "error": return "error, module could not be instantiated"
  #print("moduleinst",moduleinst)
  externval = wasm.get_export(moduleinst, funcname)
  if not externval or externval[0]!="func": return "error, "+funcname+" is not a function export of the module"
  #print("externval",externval)
  funcaddr = externval[1]
  valstar = [["i32.const",int(arg)] for arg in args]
  #print("valstar",valstar)
  store,ret = wasm.invoke_func(store,funcaddr,valstar)
  if ret=="trap": return "error, invokation resulted in a trap"
  #print("ret",ret)
  if type(ret)==list and len(ret)>0:
    ret = ret[0]
  return ret




if __name__ == "__main__":
  import sys
  if len(sys.argv) < 2 or sys.argv[1][-5:] != ".wasm":
    print("Help:")
    print("python3 pywebassembly.py <filename>.wasm funcname arg1 arg2 etc")
    print("where funcname is an exported function of the module, followed by its arguments")
    print("if funcname and args aren't present, we invoke the start function")
    exit(-1)
  filename = sys.argv[1]
  ret = None
  if len(sys.argv)==2:
    ret = instantiate_wasm_invoke_start(filename)
  elif len(sys.argv)>2:
    funcname = sys.argv[2]
    args = sys.argv[3:]
    ret = instantiate_wasm_invoke_func(filename,funcname,args)
  print(ret)

