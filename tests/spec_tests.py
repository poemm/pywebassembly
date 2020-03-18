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



import os
import sys
sys.path.append('..')  #since pywebassembly.py is in parent dir
#import pywebassembly_runtime_loop_works as pywebassembly
#import pywebassembly
import pywebassembly as wasm
#import pywebassembly
import spec_binary_format as binary_format
import spec_execution as execution

import json
import struct #for decoding floats
import math


verbose = 1




###################################################################
# module "spectest" with host functions which are imported by tests
###################################################################

def instantiate_spectest_module(store):
  def spectest__print_i32(store,arg):
    if verbose>1: print(arg)
    return store,[]
  def spectest__print_i64(store,arg):
    if verbose>1: print(arg)
    return store,[]
  def spectest__print_f32(store,arg):
    if verbose>1: print(arg)
    return store,[]
  def spectest__print_f64(store,arg):
    if verbose>1: print(arg)
    return store,[]
  def spectest__print_i32_f32(store,arg):
    if verbose>1: print(arg)
    return store,[]
  def spectest__print_f64_f64(store,arg):
    if verbose>1: print(arg)
    return store,[]
  def spectest__print(store,arg):
    if verbose>1: print(arg)
    return store,[]
  wasm.alloc_func(store, [["i32"],[]], spectest__print_i32)
  wasm.alloc_func(store, [["i64"],[]], spectest__print_i64)
  wasm.alloc_func(store, [["f32"],[]], spectest__print_f32)
  wasm.alloc_func(store, [["f64"],[]], spectest__print_f64)
  wasm.alloc_func(store, [["i32","f32"],[]], spectest__print_i32_f32)
  wasm.alloc_func(store, [["f64","f64"],[]], spectest__print_f64_f64)
  wasm.alloc_func(store, [[],[]], spectest__print)
  wasm.alloc_mem(store, {"min":1,"max":2})	#min:1,max:2 required by import.wast:
  wasm.alloc_global(store, ["const", "i32"], 666)	#666 required by import.wast
  wasm.alloc_global(store, ["const", "f32"], 0.0)
  wasm.alloc_global(store, ["const", "f64"], 0.0)
  wasm.alloc_table(store, [{"min":10,"max":20}, "anyfunc"])  #max was 30, changed to 20 for import.wast
  moduleinst = {"types":[[["i32"],[]],
                          [["i64"],[]],
                          [["i32"],[]],
                          [["f64"],[]],
                          [["i32","f32"],[]],
                          [["f64","f64"],[]],
                          [[],[]],
                         ],
                 "funcaddrs":[0,1,2,3,4,5,6],
                 "tableaddrs":[0],
                 "memaddrs":[0],
                 "globaladdrs":[0,1,2],
                 "exports":[{"name":"print_i32","value":["func",0]},
                            {"name":"print_i64","value":["func",1]},
                            {"name":"print_f32","value":["func",2]},
                            {"name":"print_f64","value":["func",3]},
                            {"name":"print_i32_f32","value":["func",4]},
                            {"name":"print_f64_f64","value":["func",5]},
                            {"name":"print","value":["func",6]},
                            {"name":"memory","value":["mem",0]},
                            {"name":"global_i32","value":["global",0]},
                            {"name":"global_f32","value":["global",1]},
                            {"name":"global_f64","value":["global",2]},
                            {"name":"table","value":["table",0]}
                           ]
                }
  return moduleinst




# this module called "wast" is used by import.wast to test for assert_unlinkable
def instantiate_test_module(store):
  def test__func(store,arg):
    pass
  def test__func_i32(store,arg):
    pass
  def test__func_f32(store,arg):
    pass
  def test__func__i32(store,arg):
    pass
  def test__func__f32(store,arg):
    pass
  def test__func_i32_i32(store,arg):
    pass
  def test__func_i64_i64(store,arg):
    pass
  wasm.alloc_func(store, [[],[]], test__func)
  wasm.alloc_func(store, [["i32"],[]], test__func_i32)
  wasm.alloc_func(store, [["f32"],[]], test__func_f32)
  wasm.alloc_func(store, [[],["i32"]], test__func__i32)
  wasm.alloc_func(store, [[],["f32"]], test__func__f32)
  wasm.alloc_func(store, [["i32"],["i32"]], test__func_i32_i32)
  wasm.alloc_func(store, [["i64"],["i64"]], test__func_i64_i64)
  wasm.alloc_mem(store, {"min":1,"max":None})	
  wasm.alloc_global(store, ["const", "i32"], 666)
  wasm.alloc_global(store, ["const", "f32"], 0.0)
  wasm.alloc_table(store, [{"min":10,"max":None}, "anyfunc"])
  moduleinst = {"types":[[["i32"],[]],
                         [["f32"],[]],
                         [[],["i32"]],
                         [[],["f32"]],
                         [["i32"],["i32"]],
                         [["i64"],["i64"]]
                        ],
                "funcaddrs":[0,1,2,3,4,5,6],
                "tableaddrs":[0],
                "memaddrs":[0],
                "globaladdrs":[0,1],
                "exports":[{"name":"func","value":["func",0]},
                           {"name":"func_i32","value":["func",1]},
                           {"name":"func_f32","value":["func",2]},
                           {"name":"func__i32","value":["func",3]},
                           {"name":"func__f32","value":["func",4]},
                           {"name":"func__i32_i32","value":["func",5]},
                           {"name":"func__i64_i64","value":["func",6]},
                           {"name":"memory-2-inf","value":["mem",0]},
                           {"name":"global-i32","value":["global",0]},
                           {"name":"global-f32","value":["global",1]},
                           {"name":"table-10-inf","value":["table",0]}
                          ]
               }
  return moduleinst



######################################################
# Tests require instantiating modules from .wasm files
######################################################

def instantiate_module_from_wasm_file(test,filename,store,registered_modules):
  if verbose>2: print("instantiate_module_from_wasm_file(",filename,")")
  if filename[-5:]!=".wasm":
    if verbose>1: print("we don't yet support .wast or .wat text format files")
    return store,None
  moduleinst = None
  with open(filename, 'rb') as f:
    #memoryview doesn't make copy, bytearray may require copy
    wasmbytes = memoryview(f.read())
    module = wasm.decode_module(wasmbytes)
    if module=="malformed": return None,"malformed"
    #validate
    ret = wasm.validate_module(module)
    if type(ret)==str and ret[:14]=="error: invalid":
      return None,"invalid"
    #imports preparation
    externvalstar = []
    #print("module",filename,module)
    for import_ in module["imports"]:
      if import_["module"] not in registered_modules: return store,"unlinkable"	#error: module name doesn't exist
      importmoduleinst = registered_modules[import_["module"]]
      externval = None
      for export in importmoduleinst["exports"]:
        if export["name"] == import_["name"]:
          externval = export["value"]
      if externval == None: return store,"unlinkable"	#error: export name doesn't exist
      if externval[0] != import_["desc"][0]: return store,"unlinkable"	#error: import type (func, table, mem, globa) doesn't match
      externvalstar += [externval]
    store,moduleinst,ret = wasm.instantiate_module(store,module,externvalstar)
    if moduleinst=="error":
      return store,ret #ret is the actual error, eg "unlinkable"
  return store,moduleinst



########################################################################################
# helper function to convert int to float, since wast2json prints floats encoded as ints
# used for to parse argument and return values in <test>.json files
########################################################################################
def int2float(N,int_):
  #return wasm.spec_reinterprett1t2("i"+str(N),'f'+str(N),int_)
  #print("int2float(",N,int_,")")
  bits = bin(int_).lstrip('0b').zfill(N)
  #print(bits)
  bytes_ = bytearray()
  for i in range(len(bits)//8):
    bytes_ += bytearray( [int(bits[8*i:8*(i+1)],2)] )
  if N==32:
    value = struct.unpack('!f',bytes_)[0]
  if N==64:
    value = struct.unpack('!d',bytes_)[0]
  return value



###################################################
# extra test opcodes, see list here: https://github.com/WebAssembly/spec/blob/master/interpreter/README.md#scripts
###################################################


# module opcode

#dir_ = "./"
def test_opcode_module(test,store,modules,registered_modules):
  if verbose>2: print("test_opcode_module()")
  moduleinst=None
  if "filename" in test:
    store,moduleinst = instantiate_module_from_wasm_file(test,dir_+test["filename"],store,registered_modules)
    #print("test_opcode_module()",moduleinst)
    if moduleinst=="malformed": return store,"malformed"
    if moduleinst=="invalid": return store,"invalid"
    if moduleinst=="uninstantiable": return store,"uninstantiable"
    if moduleinst and "name" in test:
      modules[test["name"]] = moduleinst
  if verbose>1 and moduleinst==None: print("could not instantiate")
  return store,moduleinst


# register opcode

def test_opcode_register(test,store,modules,registered_modules,moduleinst):
  if "name" in test:
    registered_modules[test["as"]] = modules[test["name"]]
  else:
    registered_modules[test["as"]] = moduleinst


#assertion opcodes  `assert_<blah>`

def test_opcode_assertion(test,store,modules,registered_modules,moduleinst):
  if "filename" in test and test["type"] in {"assert_return","assert_trap"}: #second part temporary
    store,moduleinst = test_opcode_module(test,store,modules,registered_modules)
  ret = None
  if test["type"] == "assert_return":
    ret = test_opcode_assert_return(test,store,modules,registered_modules,moduleinst)
  elif test["type"] == "assert_return_canonical_nan":
    ret = test_opcode_assert_return_canonical_nan(test,store,modules,registered_modules,moduleinst)
  elif test["type"] == "assert_return_arithmetic_nan":
    ret = test_opcode_assert_return_arithmetic_nan(test,store,modules,registered_modules,moduleinst)
  elif test["type"] == "assert_trap":
    ret = test_opcode_assert_trap(test,store,modules,registered_modules,moduleinst)
  elif test["type"] == "assert_malformed":
    ret = test_opcode_assert_malformed(test,store,modules,registered_modules,moduleinst)
  elif test["type"] == "assert_invalid":
    ret = test_opcode_assert_invalid(test,store,modules,registered_modules,moduleinst)
  elif test["type"] == "assert_unlinkable":
    ret = test_opcode_assert_unlinkable(test,store,modules,registered_modules,moduleinst)
  elif test["type"] == "assert_uninstantiable":
    ret = test_opcode_assert_uninstantiable(test,store,modules,registered_modules,moduleinst)
  elif test["type"] == "assert_exhaustion":
    ret = test_opcode_assert_exhaustion(test,store,modules,registered_modules,moduleinst)
  else:
    print("assertion not yet implemented!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ",test["type"])
  if verbose>1: print(ret)
  return ret

def test_opcode_assert_return(test,store,modules,registered_modules,moduleinst):
  if verbose>1: print("test_opcode_assert_return")
  ret = test_opcode_action(test,store,modules,registered_modules,moduleinst)
  if verbose>2: print("results:",ret)
  if ret == "trap":
    if verbose>1: print("FAILURE trap")
    return "failure!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  #print("test[\"expected\"]",test["expected"])
  if len(ret) != len(test["expected"]):
    print("ret=",ret,len(ret),"   test[\"expected\"]", test["expected"], len(test["expected"]))
    if verbose>1: print("FAILURE different number of expected and returned values")
    return "failure!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  if len(ret)==0 and len(test["expected"]) == 0:
    return "success"
  for i in range(len(ret)):
    #print(test["expected"][i]["value"])
    if test["expected"][i]["value"] in {'nan:canonical', 'nan:arithmetic'}:
      expected_val = 4286578688 # = int("11111111100000000000000000000000",2)
    else:
      expected_val = int(test["expected"][i]["value"])
    expected_type = test["expected"][i]["type"]
    if expected_type in {'i32','i64'}:
      if verbose>1: print("expected: ",expected_val,"   actual: ",ret[i])
      if ret[i] != expected_val:
        return "failure!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    elif expected_type in {'f32','f64'}:
      N = int(expected_type[1:])
      exp = int2float(N,expected_val)
      if verbose>1: print("expected: ",exp,"   actual: ",ret[i])
      if execution.spec_fsign(ret[i]) != execution.spec_fsign(exp):
         return "failure!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
      elif math.isnan(ret[i]) and math.isnan(exp):
         return "success"
      elif math.isinf(ret[i]) and math.isinf(exp):
         return "success"
      elif math.isnan(ret[i]) or math.isnan(exp) or math.isinf(ret[i]) or math.isinf(exp):
         return "failure!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
      retabs = execution.spec_fabsN(N,ret[i])
      expabs = execution.spec_fabsN(N,exp)
      #print("abs:",expabs,retabs)
      if retabs*1.01 < expabs or retabs*0.99 > expabs:
         return "failure!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  return "success"

def test_opcode_assert_return_canonical_nan(test,store,modules,registered_modules,moduleinst):
  #TODO
  return "unimplemented"

def test_opcode_assert_return_arithmetic_nan(test,store,modules,registered_modules,moduleinst):
  #TODO
  return "unimplemented"

def test_opcode_assert_trap(test,store,modules,registered_modules,moduleinst):
  if "action" in test:
    ret = test_opcode_action(test,store,modules,registered_modules,moduleinst)
  elif "module" in test:
    _,ret = test_opcode_module(test,store,modules,registered_modules)
  if ret=="trap":
    if verbose>=2: print("assert_trap SUCCESS")
    return "success"
  else:
    if verbose>=1: print("assert_trap FAILURE")
    return "failure!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"

def test_opcode_assert_exhaustion(test,store,modules,registered_modules,moduleinst):
  if "action" in test:
    ret = test_opcode_action(test,store,modules,registered_modules,moduleinst)
  elif "module" in test:
    _,ret = test_opcode_module(test,store,modules,registered_modules)
  if ret=="exhaustion":
    if verbose>=2: print("assert_exhaustion SUCCESS")
    return "success"
  else:
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    if verbose>=1: print("assert_exhaustion FAILURE")
    return "failure!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"

def test_opcode_assert_malformed(test,store,modules,registered_modules,moduleinst):
  if test["module_type"] != "binary":
    return "unimplemented"
  if "filename" in test: # TODO: delete this and do in caller
    store,moduleinst = test_opcode_module(test,store,modules,registered_modules)
    if moduleinst == "malformed":
      return "success"
  return "failure!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"

def test_opcode_assert_invalid(test,store,modules,registered_modules,moduleinst):
  if test["module_type"] != "binary":
    return "unimplemented"
  if "filename" in test: # TODO: delete this and do in caller
    store,moduleinst = test_opcode_module(test,store,modules,registered_modules)
    if moduleinst == "invalid":
      #print("SUCCESS invalid")
      return "success"
  print("FAILURE invalid !!!!!!!!!")
  return "failure!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"

def test_opcode_assert_unlinkable(test,store,modules,registered_modules,moduleinst):
  if "filename" in test: # TODO: delete this and do in caller
    store,moduleinst = test_opcode_module(test,store,modules,registered_modules)
  if moduleinst == "unlinkable":
    #print("SUCCESS UNLINKABLE")
    return "success"
  else:
    #print("FAILURE UNLINKABLE")
    return "failure!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"

def test_opcode_assert_uninstantiable(test,store,modules,registered_modules,moduleinst):
  if "filename" in test: # TODO: delete this and do in caller
    store,moduleinst = test_opcode_module(test,store,modules,registered_modules)
  if moduleinst == "uninstantiable":
    return "success"
  else:
    return "failure!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"


# action opcodes `get` and `invoke`

def test_opcode_action(test,store,modules,registered_modules,moduleinst):
  if test["action"]["type"] == "invoke":
    return test_opcode_action_invoke(test,store,modules,registered_modules,moduleinst)
  elif test["action"]["type"] == "get":
    return test_opcode_action_get(test,store,modules,registered_modules,moduleinst)

def test_opcode_action_invoke(test,store,modules,registered_modules,moduleinst):
  if verbose>1: print(test["action"]["field"])
  if "module" in test["action"]:
    moduleinst = modules[test["action"]["module"]]
  #get function name, which could include unicode bytes like \u001b which must be converted to unicode string
  funcname = test["action"]["field"]
  funcname_with_codepoints_translated = ""
  idx=0
  utf8_bytes = binary_format.spec_binary_name_inv(funcname)
  _,funcname = binary_format.spec_binary_name(utf8_bytes,0)
  #get function address
  funcaddr = None
  for export in moduleinst["exports"]:
    if export["name"] == funcname:
      funcaddr = export["value"][1]
  if verbose>2: print("funcaddr",funcaddr)
  #get args
  args = []
  float_flag = 0
  for idx in range(len(test["action"]["args"])):
    type_ = test["action"]["args"][idx]["type"]
    value = test["action"]["args"][idx]["value"]
    value = int(value)	#wabt outputs integers (even floats are encoded as ints)
    if type_ in {"f32","f64"}:
      if verbose>1: print("found float arg so skipping")
      float_flag = 1 #this is a hack to avoid floating point until implemented
      value = int2float(int(type_[1:]),value)
    args+=[ [type_+".const",value] ]
  #invoke func
  ret = []
  #if not float_flag:
  _,ret = wasm.invoke_func(store,funcaddr,args)
  #else:
  #  num_tests_tried-=1
  return ret

def test_opcode_action_get(test,store,modules,registered_modules,moduleinst):
  if "module" in test["action"]:
    moduleinst = modules[test["action"]["module"]]
  exports = moduleinst["exports"]
  #this is naive, since test["expected"] is a list, should iterate over each one, but maybe OK since there is only one test["action"]
  for export in exports:
    if export["name"] == test["action"]["field"]:
      globaladdr = export["value"][1]
      value = store["globals"][globaladdr]["value"][1]
      return [value]





################################################
# Loop over each test in a <test>.json test file
################################################

def run_test_file(jsonfilename):
  d = None
  with open(jsonfilename) as f:
    d = json.load(f)
  if d==None: return -1
  if "source_filename" not in d:
    print("this may not be a valid wabt test file")
    return -1
  if verbose>-1: print("\nrunning tests in "+d["source_filename"])
  tests = d["commands"]
  modules = { }		#all moduleinst's indexed by their names, used to call funcs and resolve exports
  registered_modules={}	#all moduleinst's which can be imported from, indexed by their registered name
  store = wasm.init_store()	#done once and lasts for lifetime of this abstract machine
  modules["spectest"] = instantiate_spectest_module(store)	#module "spectest" is imported from by many tests
  modules["test"] = instantiate_test_module(store)	#module "test" is imported from by many tests
  registered_modules["spectest"] = modules["spectest"]	#register module "spectest" to be import-able
  registered_modules["test"] = modules["test"]		#register module "test" to be import-able
  moduleinst = None
  num_tests_passed = 0
  num_tests_tried = 0
  for idx,test in enumerate(tests):	#iterate over tests in this file
    if verbose>1: print("\ntest #",idx, test["type"])
    if test["type"] == "module":		#module
      store,moduleinst = test_opcode_module(test,store,modules,registered_modules)
      num_tests_tried += 1
      if moduleinst: num_tests_passed+=1
    elif test["type"] == "register":		#register
      test_opcode_register(test,store,modules,registered_modules,moduleinst)
      num_tests_tried += 1
      num_tests_passed+=1
    elif test["type"] == "action":		#action
      test_opcode_action(test,store,modules,registered_modules,moduleinst)
      num_tests_tried += 1
      num_tests_passed+=1
    elif test["type"][:7] == "assert_":		#assertion
      ret = test_opcode_assertion(test,store,modules,registered_modules,moduleinst)
      if ret in {"success","failure!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"}:
        num_tests_tried += 1
      if ret=="success":
        num_tests_passed += 1
    else:
      print("test not yet implemented!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ", test["type"])
  if verbose>-1: print("Passed",num_tests_passed,"out of",num_tests_tried,"tests")  #"(actually, there are ",len(tests),"total tests, some test opcodes not implemented yet)")
  if verbose>-1: 
   if num_tests_passed!=num_tests_tried:
     print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")






if __name__ == "__main__":
  if "-h" in sys.argv or "--help" in sys.argv or len(sys.argv)<=1:
    if verbose>1: print("arguments should be list of json files filename.json")
    if verbose>1: print("or a directory means run on every json in directory")
  #get .json filename(s)
  filenames = []
  for arg in sys.argv[1:]:
    if os.path.isdir(arg):
      if arg[-1]!='/':
        arg=arg+'/'
      #get each json filename in dir
      for filename in os.listdir(arg):
        if filename[-5:] != ".json": continue
        filenames+=[arg+filename]
    elif arg[-5:]==".json":
      filenames+=[arg]
  #run test on each filename
  for filename in filenames:
    #print(filename)
    global dir_
    dir_,file_ = os.path.split(filename)
    if dir_=='/':
      dir_ = './'
    if dir_[-1]!='/':
      dir_+='/'
    res = run_test_file(dir_+file_)

