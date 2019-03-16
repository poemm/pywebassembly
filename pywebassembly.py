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

import spec_binary_format as binary_format
import spec_validation as validation
import spec_execution as execution


###############
# 7.1 EMBEDDING
###############

# THE FOLLOWING IS THE OFFICIAL API TO WEBASSEMBLY

# 7.1.1 STORE

def init_store():
  return {"funcs":[], "mems":[], "tables":[], "globals":[]}

# 7.1.2 MODULES

def decode_module(bytestar):
  try:
    mod = binary_format.spec_binary_module(bytestar)
  except:
    return "malformed"
  return mod

# this function is not in the spec. It is the inverse of the above function, useful in the examples.
def encode_module(mod):
  return binary_format.spec_binary_module_inv(mod)
  
def parse_module(codepointstar):
  # text parser not implemented yet
  return -1

def validate_module(module):
  #print("validate_module()")
  try:
    validation.spec_validate_module(module)
  except Exception as e:
    return "error: invalid"
  return None

def instantiate_module(store,module,externvalstar):
  # we deviate from the spec by also returning the return value
  try:
    ret = execution.spec_instantiate(store,module,externvalstar)
  except Exception as e:
    return store,"error",e.args[0]
  store,F,startret = ret
  modinst = F["module"]
  return store, modinst, startret

def module_imports(module):
  try: validation.spec_validate_module(mod)
  except: return "error: invalid"
  externtypestar, extertypeprimestar = ret
  importstar = module["imports"]
  if len(importstar) != len(externtypestar): return "error: wrong import length"
  result = []
  for i in range(len(importstar)):
    importi = importstar[i]
    externtypei = externtypestar[i]
    resutli = [immporti["module"],importi["name"],externtypei] 
    result += resulti
  return result

def module_exports(module):
  try: ret = validation.spec_validate_module(mod)
  except: return "error: invalid"
  externtypestar, extertypeprimestar = ret
  exportstar = module["exports"]
  assert len(exportstar) == len(externtypeprimestar)
  result = []
  for i in range(len(importstar)):
    exporti = exportstar[i]
    externtypeprimei = externtypeprimestar[i]
    resutli = [exporti["name"],externtypeprimei] 
    result += resulti
  return result


# 7.1.3 EXPORTS

def get_export(moduleinst, name):
  # assume valid so all export names are unique
  for exportinsti in moduleinst["exports"]:
    if name == exportinsti["name"]:
      return exportinsti["value"]
  return "error"

# 7.1.4 FUNCTIONS

def alloc_func(store, functype, hostfunc):
  store, funcaddr = execution.spec_allochostfunc(store,functype,hostfunc)
  return store, funcaddr

def type_func(store,funcaddr):
  if len(store["funcs"]) <= funcaddr: return "error"
  functype = store["funcs"][funcaddr]
  return functype

def invoke_func(store,funcaddr,valstar):
  try: 
    ret = execution.spec_invoke(store,funcaddr,valstar)
  except Exception as e:
    return store,e.args[0]
  return store,ret
  
# 7.1.4 TABLES

def alloc_table(store, tabletype):
  store,tableaddr = execution.spec_alloctable(store,tabletype)
  return store,tableaddr

def type_table(store,tableaddr):
  if len(store["tables"]) <= tableaddr: return "error"
  tableinst = store["tables"][tableaddr]
  max_ = tableinst["max"]
  min_ = len(tableinst["elem"]) #TODO: is this min OK?
  tabletype = [{"min":min_, "max":max_}, "anyfunc"]
  return tabletype

def read_table(store,tableaddr,i):
  if len(store["tables"]) < tableaddr: return "error"
  if type(i)!=int or i < 0: return "error"
  ti = store["tables"][tableaddr]
  if i >= len(ti["elem"]): return "error"
  return ti["elem"][i]

def write_table(store,tableaddr,i,funcaddr):
  if len(store["tables"]) <= tableaddr: return "error"
  if type(i)!=int or i < 0: return "error"
  ti = store["tables"][tableaddr]
  if i >= len(ti["elem"]): return "error"
  ti["elem"][i] = funcaddr
  return store

def size_table(store, tableaddr):
  if len(store["tables"]) <= tableaddr: return "error"
  return len(store["tables"][tableaddr]["elem"])

def grow_table(store, tableaddr, n):
  if len(store["tables"]) <= tableaddr: return "error"
  if type(n)!=int or n < 0: return "error"
  try: execution.spec_growtable(store["tabless"][tableaddr],n)
  except: return "error"
  #store["tables"][tableaddr]["elem"] += [{"elem":[], "max":None} for i in range(n)]  # see spec \S 4.2.7 Table Instances for discussion on uninitialized table elements.
  return store

# 7.1.6 MEMORIES

def alloc_mem(store, memtype):
  store, memaddr = execution.spec_allocmem(store,memtype)
  return store, memaddr

def type_mem(store, memaddr):
  if len(store["mems"]) <= memaddr: return "error"
  meminst = store["mems"][memaddr]
  max_ = meminst["max"]
  min_ = len(meminst["data"])//65536  #page size = 64 Ki = 65536 #TODO: is this min OK?
  return {"min":min_, "max":max_}

def read_mem(store, memaddr, i):
  if len(store["mems"]) <= memaddr: return "error"
  if type(i)!=int or i < 0: return "error"
  mi = store["mems"][memaddr]
  if i >= len(mi["data"]): return "error"
  return mi["data"][i]

def write_mem(store,memaddr,i,byte):
  if len(store["mems"]) <= memaddr: return "error"
  if type(i)!=int or i < 0: return "error"
  mi = store["mems"][memaddr]
  if i >= len(mi["data"]): return "error"
  mi["data"][i] = byte
  return store

def size_mem(store,memaddr):
  if len(store["mems"]) <= memaddr: return "error"
  return len(store["mems"][memaddr])//65536  #page size = 64 Ki = 65536

def grow_mem(store,memaddr,n):
  if len(store["mems"]) <= memaddr: return "error"
  if type(n)!=int or n < 0: return "error"
  try: execution.spec_growmem(store["mems"][memaddr],n)
  except: return "error"
  return store

# 7.1.7 GLOBALS
  
def alloc_global(store,globaltype,val):
  try:
    store,globaladdr = execution.spec_allocglobal(store,globaltype,val)
  except:
     return store,"error"
  return store,globaladdr

def type_global(store, globaladdr):
  if len(store["globals"]) <= globaladdr: return "error"
  globalinst = store["globals"][globaladdr]
  mut = globalinst["mut"]
  valtype = globalinst["value"][0]
  return [mut, valtype]

def read_global(store, globaladdr):
  if len(store["globals"]) <= globaladdr: return "error"
  gi = store["globals"][globaladdr]
  return gi["value"]
  
# arg must look like ["i32.const",5]
def write_global(store,globaladdr,val):
  if len(store["globals"]) <= globaladdr: return "error"
  #TODO: type check; handle val without type
  gi = store["globals"][globaladdr]
  if gi["mut"] != "var": return "error"
  gi["value"] = val
  return store
  

