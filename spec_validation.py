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

import spec_structure as structure
import spec_binary_format as binary_format

debug = 0

################
################
# 3 VALIDATION #
################
################

# Chapter 3 defines validation rules over the abstract syntax. These rules constrain the syntax, but provide properties such as type-safety.


###########
# 3.2 TYPES
###########

# 3.2.1 LIMITS

def spec_validate_limit(limits,k):
  if debug: print("spec_validate_limit()")
  n=limits["min"]
  m=limits["max"]
  if n>k: raise Exception("invalid")
  if m != None and (m>k or m<n): raise Exception("invalid")
  return k

# 3.2.2 FUNCTION TYPES

def spec_validate_functype(ft):
  if debug: print("spec_validate_functype()")
  if len(ft[1])>1: raise Exception("invalid")
  return ft

# 3.2.3 TABLE TYPES

def spec_validate_tabletype(tt):
  if debug: print("spec_validate_tabletype()")
  limits, elemtype = tt
  spec_validate_limit(limits,2**32)
  return tt

# 3.2.4 MEMORY TYPES

def spec_validate_memtype(limits):
  if debug: print("spec_validate_memtype()")
  spec_validate_limit(limits,2**16)
  return limits

# 3.2.5 GLOBAL TYPES

def spec_validate_globaltype(globaltype):
  if debug: print("spec_validate_globaltype()")
  return globaltype #TODO: always valid, maybe should check whether mut and valtype are both ok


##################
# 3.3 INSTRUCTIONS
##################

# 3.3.1 NUMERIC INSTRUCTIONS

def spec_validate_t_const(t):
  return [],[t]

def spec_validate_t_unop(t):
  return [t],[t]

def spec_validate_t_binop(t):
  return [t,t],[t]

def spec_validate_t_testop(t):
  return [t],['i32']

def spec_validate_t_relop(t):
  return [t, t],['i32']

def spec_validate_t2_cvtop_t1(t1,t2):
  return [t1],[t2]


# 3.3.2  PARAMETRIC INSTRUCTIONS

def spec_validate_drop():
  return ["t"], []

def spec_validate_select():
  return ["t", "t", "i32"],["t"]

# 3.3.3 VARIABLE INSTRUCTIONS

def spec_validate_get_local(C,x):
  if len(C["locals"]) <= x: raise Exception("invalid")
  t = C["locals"][x]
  return [],[t] 

def spec_validate_set_local(C,x):
  if len(C["locals"]) <= x: raise Exception("invalid")
  t = C["locals"][x]
  return [t],[]

def spec_validate_tee_local(C,x):
  if len(C["locals"]) <= x: raise Exception("invalid")
  t = C["locals"][x]
  return [t],[t]

def spec_validate_get_global(C,x):
  if len(C["globals"]) <= x: raise Exception("invalid")
  mut,t = C.globals[x]
  return [],[t]

def spec_validate_set_global(C,x):
  if len(C["globals"]) <= x: raise Exception("invalid")
  mut,t = C.globals[x]
  if mut!="var": raise Exception("invalid")
  return [t],[]


# 3.3.4 MEMORY INSTRUCTIONS

def spec_validate_t_load(C,t,memarg):
  if len(C["mems"])<1: raise Exception("invalid")
  tval = int(t[1:2]) # invariant: t has form: letter digit digit  eg i32
  if 2**memarg["align"]>tval//8: raise Exception("invalid")
  return ["i32"],[t]

def spec_validate_tloadNsx(C,t,N,memarg):
  if len(C["mems"])<1: raise Exception("invalid")
  if 2**memarg["align"]>N//8: raise Exception("invalid")
  return ["i32"],[t]

def spec_validate_tstore(C,t,memarg):
  if len(C["mems"])<1: raise Exception("invalid")
  tval = int(t[1:2]) # invariant: t has form: letter digit digit  eg i32
  if 2**memarg["align"]>tval//8: raise Exception("invalid")
  return ["i32",t],[]

def spec_validate_tstoreN(C,t,N,memarg):
  if len(C["mems"])<1: raise Exception("invalid")
  if 2**memarg["align"]>N//8: raise Exception("invalid")
  return ["i32",t],[]

def spec_validate_memorysize(C):
  if len(C["mems"])<1: raise Exception("invalid")
  return [],["i32"]

def spec_validate_memorygrow(C):
  if len(C["mems"])<1: raise Exception("invalid")
  return ["i32"],["i32"]


# 3.3.5 CONTROL INSTRUCTIONS

def spec_validate_nop():
  return [],[]

def spec_validate_uneachable():
  return ["t1*"],["t2*"]

def spec_validate_block(C,tq,instrstar):
  if debug: print("spec_validate_block()")
  C["labels"].append([tq] if tq else [])
  type_ = spec_validate_instrstar(C,instrstar)  
  C["labels"].pop()
  if type_ != ([],[tq] if tq else []): raise Exception("invalid")
  return type_

def spec_validate_loop(C,tq,instrstar):
  if debug: print("spec_validate_loop()")
  C["labels"].append([])
  type_ = spec_validate_instrstar(C,instrstar)  
  C["labels"].pop()
  if type_ != ([],[tq] if tq else []): raise Exception("invalid")
  return type_

def spec_validate_if(C,tq,instrstar1,instrstar2):
  if debug: print("spec_validate_if()")
  C["labels"].append([tq] if tq else [])
  type_ = spec_validate_instrstar(C,instrstar1)  
  if type_ != ([],[tq] if tq else []): raise Exception("invalid")
  type_ = spec_validate_instrstar(C,instrstar2)  
  if type_ != ([],[tq] if tq else []): raise Exception("invalid")
  C["labels"].pop()
  return ["i32"],[tq] if tq else []

def spec_validate_br(C,l):
  if debug: print("spec_validate_br()")
  if len(C["labels"]) <= l: raise Exception("invalid")
  tq_in_brackets = C["labels"][l]
  return ["t1*"] + tq_in_brackets, ["t2*"]
  
def spec_validate_br_if(C,l):
  if debug: print("spec_validate_br_if()")
  if len(C["labels"]) <= l: raise Exception("invalid")
  tq_in_brackets = C["labels"][l]
  return tq_in_brackets + ["i32"], tq_in_brackets

def spec_validate_br_table(C,lstar,lN):
  if debug: print("spec_validate_br_table()")
  if len(C["labels"]) <= lN: raise Exception("invalid")
  tq_in_brackets = C["labels"][lN]
  for li in lstar:
    if len(C["labels"]) <= li: raise Exception("invalid")
    if C["labels"][li] != tq_in_brackets: raise Exception("invalid")
  return ["t1*"] + tq_in_brackes + ["i32"], ["t2*"]

def spec_validate_return(C):
  if debug: print("spec_validate_return()")
  if C["return"] == None: raise Exception("invalid")
  tq_in_brackets = C["return"]
  return ["t1*"] + tq_in_brackes + ["i32"], ["t2*"]

def spec_validate_call(C,x):
  if debug: print("spec_validate_call()")
  if len(C["funcs"]) <= x: raise Exception("invalid")
  return C["funcs"][x]

def spec_validate_call_indirect(C,x):
  if debug: print("spec_validate_call_indirect()")
  if C["tables"]==None or len(C["tables"]) < 1: raise Exception("invalid")
  limits,elemtype = C["tables"][0]
  if elemtype != "anyfunc": raise Exception("invalid")
  if C["types"]==None or len(C["types"]) <= x: raise Exception("invalid")
  return C["types"][x][0]+["i32"],C["types"][x][1]


# 3.3.6 INSTRUCTION SEQUENCES

# We use the algorithm in the appendix for validating instruction sequences

# 3.3.7 EXPRESSIONS

def spec_validate_expr(C,expr):
  if debug: print("spec_validate_expr()")
  opd_stack = []
  ctrl_stack = []
  iterate_through_expression_and_validate_each_opcode(expr,C,opd_stack,ctrl_stack) # call to the algorithm in the appendix
  if len(opd_stack)>1: raise Exception("invalid")
  else: return opd_stack

def spec_validate_const_instr(C,instr):
  if debug: print("spec_validate_const_instr()")
  if instr[0] not in {"i32.const","i64.const","f32.const","f64.const","get_global"}: raise Exception("invalid")
  if instr[0] == "get_global" and C["globals"][instr[1]][0] != "const": raise Exception("invalid")
  return "const"

def spec_validate_const_expr(C,expr):
  if debug: print("spec_validate_const_expr()")
  #expr is in AST form
  stack = []
  for e in expr[:-1]:
    spec_validate_const_instr(C,e)
  if expr[-1][0] != "end": raise Exception("invalid")
  return "const"


#############
# 3.4 MODULES
#############

# 3.4.1 FUNCTIONS

def spec_validate_func(C,func,raw=None):
  if debug: print("spec_validate_func()")
  x = func["type"]
  if len(C["types"])<=x: raise Exception("invalid")
  t1 = C["types"][x][0]
  t2 = C["types"][x][1]
  C["locals"] = t1 + func["locals"]
  C["labels"] = t2
  C["return"] = t2
  # validate body using algorithm in appendix
  instrstar = [["block",t2,func["body"]]] # spec didn't nest func body in a block, but algorithm in appendix gives errors otherwise
  ft = spec_validate_expr(C,instrstar)
  #clear out function-specific things
  C["locals"] = []
  C["labels"] = []
  C["return"] = []
  return ft


# 3.4.2 TABLES

def spec_validate_table(table):
  if debug: print("spec_validate_table()")
  return spec_validate_tabletype(table["type"])


# 3.4.3 MEMORIES

def spec_validate_mem(mem):
  if debug: print("spec_validate_mem()")
  ret = spec_validate_memtype(mem["type"])
  if mem["type"]["min"]>65536: raise Exception("invalid")
  if mem["type"]["max"] and mem["type"]["max"]>65536: raise Exception("invalid")
  return ret


# 3.4.4 GLOBALS

def spec_validate_global(C,global_):
  if debug: print("spec_validate_global()")
  #print("spec_validate_global(",C,global_,")")
  spec_validate_globaltype(global_["type"])
  # validate expr, but wrap it in a block first since empty control stack gives errors
  # but first wrap in block with appropriate return type
  instrstar = [["block",global_["type"][1],global_["init"]]]
  ret = spec_validate_expr(C,instrstar)
  if ret != [global_["type"][1]]: raise Exception("invalid")
  ret = spec_validate_const_expr(C,global_["init"])
  return global_["type"]


# 3.4.5 ELEMENT SEGMENT

def spec_validate_elem(C,elem):
  if debug: print("spec_validate_elem()")
  x = elem["table"]
  if "tables" not in C or len(C["tables"])<=x: raise Exception("invalid")
  tabletype = C["tables"][x]
  limits = tabletype[0]
  elemtype = tabletype[1]
  if elemtype != "anyfunc": raise Exception("invalid")
  # first wrap in block with appropriate return type
  instrstar = [["block","i32",elem["offset"]]]
  ret = spec_validate_expr(C,instrstar)
  if ret != ["i32"]: raise Exception("invalid")
  spec_validate_const_expr(C,elem["offset"])
  for y in elem["init"]:
    if len(C["funcs"])<=y: raise Exception("invalid")
  return 0


# 3.4.6 DATA SEGMENTS

def spec_validate_data(C,data):
  if debug: print("spec_validate_data()")
  x = data["data"]
  if len(C["mems"])<=x: raise Exception("invalid")
  instrstar = [["block","i32",data["offset"]]]
  ret = spec_validate_expr(C,instrstar)
  if ret != ["i32"]: raise Exception("invalid")
  spec_validate_const_expr(C,data["offset"])
  return 0


# 3.4.7 START FUNCTION

def spec_validate_start(C,start):
  if debug: print("spec_validate_start()")
  x = start["func"]
  if len(C["funcs"])<=x: raise Exception("invalid")
  if C["funcs"][x] != [[],[]]: raise Exception("invalid")
  return 0
  

# 3.4.8 EXPORTS

def spec_validate_export(C,export):
  if debug: print("spec_validate_export()")
  return spec_validate_exportdesc(C,export["desc"])
  
def spec_validate_exportdesc(C,exportdesc):
  if debug: print("spec_validate_exportdesc()")
  #print("C",C)
  #print("exportdesc",exportdesc)
  x = exportdesc[1]
  if exportdesc[0]=="func":
    if len(C["funcs"])<=x: raise Exception("invalid")
    return ["func",C["funcs"][x]]
  elif exportdesc[0]=="table":
    if len(C["tables"])<=x: raise Exception("invalid")
    return ["table",C["tables"][x]]
  elif exportdesc[0]=="mem":
    if len(C["mems"])<=x: raise Exception("invalid")
    return ["mem",C["mems"][x]]
  elif exportdesc[0]=="global":
    #print("global")
    #print(len(C["globals"]),x)
    if len(C["globals"])<=x: raise Exception("invalid")
    mut,t = C["globals"][x]
    #print(mut)
    #if mut != "const": raise Exception("invalid") #TODO: this was in the spec, but tests fail linking.wast: $Mg exports a mutable global, seems not to parse in wabt
    return ["global",C["globals"][x]]
  else: raise Exception("invalid")
  

# 3.4.9 IMPORTS

def spec_validate_import(C,import_):
  if debug: print("spec_validate_import()")
  return spec_validate_importdesc(C,import_["desc"])
  
def spec_validate_importdesc(C,importdesc):
  if debug: print("spec_validate_importdesc()")
  if importdesc[0]=="func":
    x = importdesc[1]
    if len(C["funcs"])<=x: raise Exception("invalid")
    return ["func",C["types"][x]]
  elif importdesc[0]=="table":
    tabletype = importdesc[1]
    spec_validate_tabletype(tabletype)
    return ["table",tabletype]
  elif importdesc[0]=="mem":
    memtype = importdesc[1]
    spec_validate_memtype(memtype)
    return ["mem",memtype]
  elif importdesc[0]=="global":
    globaltype = importdesc[1]
    spec_validate_globaltype(globaltype)
    #if globaltype[0] != "const": raise Exception("invalid") #TODO: this was in the spec, but tests fail linking.wast: $Mg exports a mutable global, seems not to parse in wabt
    return ["global",globaltype]
  else: raise Exception("invalid")



# 3.4.10 MODULE

def spec_validate_module(mod):
  if debug: print("spec_validate_module()")
  # mod is the module to validate
  ftstar = []
  for func in mod["funcs"]:
    if len(mod["types"]) <= func["type"]: raise Exception("invalid") # this was not explicit in spec, how about other *tstar
    ftstar += [mod["types"][func["type"]]]
  ttstar = [ table["type"] for table in mod["tables"] ]
  mtstar = [ mem["type"] for mem in mod["mems"] ]
  gtstar = [ global_["type"] for global_ in mod["globals"] ]
  itstar = []
  for import_ in mod["imports"]:
    if import_["desc"][0] == "func":
      if len(mod["types"])<=import_["desc"][1]: raise Exception("invalid") # this was not explicit in spec
      itstar.append( ["func",mod["types"][import_["desc"][1]]] )
    else:
      itstar.append( import_["desc"] )
  # let i_tstar be the concatenation of imports of each type
  iftstar = structure.spec_funcs(itstar) #[it[1] for it in itstar if it[0]=="func"]
  ittstar = structure.spec_tables(itstar) #[it[1] for it in itstar if it[0]=="table"]
  imtstar = structure.spec_mems(itstar) #[it[1] for it in itstar if it[0]=="mem"]
  igtstar = structure.spec_globals(itstar) #[it[1] for it in itstar if it[0]=="global"]
  # let C and Cprime be contexts
  C = {"types":		mod["types"],
       "funcs":		iftstar + ftstar,
       "tables":	ittstar + ttstar,
       "mems":		imtstar + mtstar,
       "globals":	igtstar + gtstar,
       "locals":	[],
       "labels":	[],
       "return":	[] }
  #print("C",C)
  Cprime = {
       "types":		[],
       "funcs":		[],
       "tables":	[],
       "mems":		[],
       "globals":	igtstar,
       "locals":	[],
       "labels":	[],
       "returns":	[] }
  # et* is needed later, here is a good place to do it
  etstar = []
  for export in mod["exports"]:
    if export["desc"][0] == "func":
      if len(C["funcs"])<=export["desc"][1]: raise Exception("invalid") # this was not explicit in spec
      etstar.append( [ "func",C["funcs"][export["desc"][1]] ] )
    elif export["desc"][0] == "table":
      if len(C["tables"])<=export["desc"][1]: raise Exception("invalid") # this was not explicit in spec
      etstar.append( ["table",C["tables"][export["desc"][1]]] )
    elif export["desc"][0] == "mem":
      if len(C["mems"])<=export["desc"][1]: raise Exception("invalid") # this was not explicit in spec
      etstar.append( ["mem",C["mems"][export["desc"][1]]] )
    elif export["desc"][0] == "global":
      if len(C["globals"])<=export["desc"][1]: raise Exception("invalid") # this was not explicit in spec
      etstar.append( ["global",C["globals"][export["desc"][1]]] )
  # under the context C
  for functypei in mod["types"]:
    spec_validate_functype(functypei)
  for i,func in enumerate(mod["funcs"]):
    ft = spec_validate_func(C, func)
    if ft != ftstar[i][1]: raise Exception("invalid")
  for i,table in enumerate(mod["tables"]):
    tt = spec_validate_table(table)
    if tt != ttstar[i]: raise Exception("invalid")
  for i,mem in enumerate(mod["mems"]):
    mt = spec_validate_mem(mem)
    if mt != mtstar[i]: raise Exception("invalid")
  for i,global_ in enumerate(mod["globals"]):
    gt = spec_validate_global(Cprime,global_)
    if gt != gtstar[i]: raise Exception("invalid")
  for elem in mod["elem"]:
    spec_validate_elem(C,elem)
  for data in mod["data"]:
    spec_validate_data(C,data)
  if mod["start"]:
    spec_validate_start(C,mod["start"])
  for i,import_ in enumerate(mod["imports"]):
    it = spec_validate_import(C,import_)
    if it != itstar[i]: raise Exception("invalid")
  #print("ok9")
  #print("mod[\"exports\"]",mod["exports"])
  for i,export in enumerate(mod["exports"]):
    et = spec_validate_export(C,export)
    #print("ok9.5")
    if et != etstar[i]: raise Exception("invalid")
  #print("ok10")
  if len(C["tables"])>1: raise Exception("invalid")
  if len(C["mems"])>1: raise Exception("invalid")
  # export names must be unique
  exportnames = set()
  for export in mod["exports"]:
    if export["name"] in exportnames: raise Exception("invalid")
    exportnames.add(export["name"])
  return [itstar, etstar]





##########################
# 7.3 VALIDATION ALGORITHM
##########################

# 7.3.1 DATA STRUCTURES

# Conventions:
#   the spec makes opds and ctrls global variables, but we pass them around as arguments
#   the control stack is a python list, which allows fast appending but not prepending. So the spec's index 0 corresponds to python list idx -1, and eg spec idx 3 corresponds to our python list idx -1-3 ie -4
#   the spec offers two ways to keep track of labels, using C.labels in ch 3 or a control stack in the appendix. Here we use the appendix method

def spec_push_opd(opds,type_):
  opds.append(type_)

def spec_pop_opd(opds,ctrls):
  # check if underflows current block, and returns one type
  # but if underflows and unreachable, which can happen if unconditional branch, when stack is typed polymorphically, operands are still pushed and popped to check if code after unreachable is valid, polymorphic stack can't underflow
  if len(opds) == ctrls[-1]["height"] and ctrls[-1]["unreachable"]:
    return "Unknown"
  if len(opds) == ctrls[-1]["height"]: raise Exception("invalid") #error
  if len(opds) == 0: raise Exception("invalid") #error, not in spec
  to_return = opds[-1]
  del opds[-1]
  return to_return

def spec_pop_opd_expect(opds,ctrls,expect):
  actual = spec_pop_opd(opds,ctrls)
  if actual == -1:  raise Exception("invalid") #error
  # in case one is unknown, the more specific one is returned
  if actual == "Unknown":
    return expect
  if expect == "Unknown":
    return actual
  if actual != expect: raise Exception("invalid") #error
  return actual

def spec_push_opds(opds,ctrls,types):
  for t in types:
    spec_push_opd(opds,t)
  return 0

def spec_pop_opds_expect(opds,ctrls,types):
  if types:
    for t in reversed(types):
      r = spec_pop_opd_expect(opds,ctrls,t)
    return r
  else:
    return None

def spec_ctrl_frame(label_types, end_types, height, unreachable):
  #args are:
  #   label_types: type of the branch's label, to type-check branches
  #   end_types: result type of the branch, currently Wasm spec allows at most one return value
  #   height: height of opd_stack at start of block, to check that operands do not underflow current block
  #   unreachable: whether remainder of block is unreachable, to handle stack-polymorphic typing after branches
  return {"label_types":label_types, "end_types":end_types, "height":height, "unreachable":unreachable}

def spec_push_ctrl(opds,ctrls,label,out):
  frame = {"label_types":label,"end_types":out,"height":len(opds),"unreachable":False}
  ctrls.append(frame)

def spec_pop_ctrl(opds,ctrls):
  if len(ctrls)<1:  raise Exception("invalid") #error
  frame = ctrls[-1]
  #verify opd stack has right types to exit block, and pops them
  #print("frame[\"end_types\"]",frame["end_types"])
  r = spec_pop_opds_expect(opds,ctrls,frame["end_types"])
  if r==-1:  raise Exception("invalid") #error
  #make shure stack is back to original height
  if len(opds) != frame["height"]:  raise Exception("invalid") #error
  del ctrls[-1]
  return frame["end_types"]

# extra underscore since spec_unreachable() is used in chapter 4
def spec_unreachable_(opds, ctrls):
  # purge from operand stack, allows stack-polymorphic logic in pop_opd() take effect
  del opds[ ctrls[-1]["height"]: ]
  ctrls[-1]["unreachable"] = True



# 7.3.2 VALIDATION OF OPCODE SEQUENCES

# validate a single opcode based on current context C, operand stack opds, and control stack ctrls
def spec_validate_opcode(C,opds,ctrls,opcode,immediates):
  #print("spec_validate_opcode(",C,"   ",opds,"   ",ctrls,"   ",opcode,"   ",immediates,")")
  # C is the context
  # opds is the operand stack
  # ctrls is the control stack
  opcode_binary = binary_format.opcodes_text2binary[opcode]
  if 0x00<=opcode_binary<=0x11:			# CONTROL INSTRUCTIONS
    if opcode_binary==0x00:			# unreachable 
      spec_unreachable_(opds,ctrls)
    elif opcode_binary==0x01:			# nop
      pass
    elif opcode_binary<=0x04:			# block, loop, if
      rt = immediates
      if rt!=[] and type(rt)!=list: rt=[rt]  #TODO: clean this up, works but ugly
      if opcode_binary==0x02:			# block
        spec_push_ctrl(opds,ctrls,rt,rt)
      elif opcode_binary==0x03:			# loop
        spec_push_ctrl(opds,ctrls,[],rt)
      else:					# if
        spec_pop_opd_expect(opds,ctrls,"i32")
        spec_push_ctrl(opds,ctrls,rt,rt)
    elif opcode_binary==0x05:			# else
      results = spec_pop_ctrl(opds,ctrls)
      if results!=[] and type(results)!=list: results=[results]
      spec_push_ctrl(opds,ctrls,results,results)
    elif opcode_binary==0x0b:			# end
      results = spec_pop_ctrl(opds,ctrls)
      spec_push_opds(opds,ctrls,results)
    elif opcode_binary==0x0c:			# br
      n = immediates
      if n==None: raise Exception("invalid")
      if len(ctrls) <= n:  raise Exception("invalid")
      spec_pop_opds_expect(opds,ctrls,ctrls[-1-n]["label_types"])
      spec_unreachable_(opds,ctrls)
    elif opcode_binary==0x0d:			# br_if
      n = immediates
      if n==None: raise Exception("invalid")
      if len(ctrls) <= n: raise Exception("invalid")
      spec_pop_opd_expect(opds,ctrls,"i32")
      spec_pop_opds_expect(opds,ctrls,ctrls[-1-n]["label_types"]) 
      spec_push_opds(opds,ctrls,ctrls[-1-n]["label_types"])
    elif opcode_binary==0x0e:			# br_table
      nstar = immediates[0]
      m = immediates[1]
      if len(ctrls)<=m: raise Exception("invalid")
      for n in nstar:
        if len(ctrls)<=n or ctrls[-1-n]["label_types"] != ctrls[-1-m]["label_types"]: raise Exception("invalid")
      spec_pop_opd_expect(opds,ctrls,"i32")
      spec_pop_opds_expect(opds,ctrls,ctrls[-1-m]["label_types"])
      spec_unreachable_(opds,ctrls)
    elif opcode_binary==0x0f:			# return
      if "return" not in C: raise Exception("invalid")
      t = C["return"]
      spec_pop_opds_expect(opds,ctrls,t)
      spec_unreachable_(opds,ctrls)
    elif opcode_binary==0x10:			# call
      x = immediates
      if ("funcs" not in C) or len(C["funcs"])<=x: raise Exception("invalid")
      spec_pop_opds_expect(opds,ctrls,C["funcs"][x][0])
      spec_push_opds(opds,ctrls,C["funcs"][x][1])
    elif opcode_binary==0x11:			# call_indirect
      x = immediates
      if ("tables" not in C) or len(C["tables"])==0: raise Exception("invalid")
      if C["tables"][0][1] != "anyfunc": raise Exception("invalid")
      if len(C["types"])<=x: raise Exception("invalid")
      spec_pop_opd_expect(opds,ctrls,"i32")
      spec_pop_opds_expect(opds,ctrls,C["types"][x][0])
      spec_push_opds(opds,ctrls,C["types"][x][1])
  elif 0x1a<=opcode_binary<=0x1b:		# PARAMETRIC INSTRUCTIONS
    if opcode_binary==0x1a:			# drop
      spec_pop_opd(opds,ctrls)
    elif opcode_binary==0x1b:			# select
      spec_pop_opd_expect(opds,ctrls,"i32")
      t1 = spec_pop_opd(opds,ctrls)
      t2 = spec_pop_opd_expect(opds,ctrls,t1)
      spec_push_opd(opds,t2)
  elif 0x20<=opcode_binary<=0x24:		# VARIABLE INSTRUCTIONS
    if opcode_binary==0x20:			# get_local
      x = immediates
      if len(C["locals"])<=x: raise Exception("invalid")
      if C["locals"][x]=="i32": spec_push_opd(opds,"i32")
      elif C["locals"][x]=="i64": spec_push_opd(opds,"i64")
      elif C["locals"][x]=="f32": spec_push_opd(opds,"f32")
      elif C["locals"][x]=="f64": spec_push_opd(opds,"f64")
      else: raise Exception("invalid")
    if opcode_binary==0x21:			# set_local
      x = immediates
      if len(C["locals"])<=x: raise Exception("invalid")
      if C["locals"][x]=="i32": ret = spec_pop_opd_expect(opds,ctrls,"i32")
      elif C["locals"][x]=="i64": ret = spec_pop_opd_expect(opds,ctrls,"i64")
      elif C["locals"][x]=="f32": ret = spec_pop_opd_expect(opds,ctrls,"f32")
      elif C["locals"][x]=="f64": ret = spec_pop_opd_expect(opds,ctrls,"f64")
      else: raise Exception("invalid")
    if opcode_binary==0x22:			# tee_local
      x = immediates
      if len(C["locals"])<=x: raise Exception("invalid")
      if C["locals"][x]=="i32":
        spec_pop_opd_expect(opds,ctrls,"i32")
        spec_push_opd(opds,"i32")
      elif C["locals"][x]=="i64":
        spec_pop_opd_expect(opds,ctrls,"i64")
        spec_push_opd(opds,"i64")
      elif C["locals"][x]=="f32":
        spec_pop_opd_expect(opds,ctrls,"f32")
        spec_push_opd(opds,"f32")
      elif C["locals"][x]=="f64":
        spec_pop_opd_expect(opds,ctrls,"f64")
        spec_push_opd(opds,"f64")
      else: raise Exception("invalid")
    if opcode_binary==0x23:			# get_global
      x = immediates
      if len(C["globals"])<=x: raise Exception("invalid")
      if C["globals"][x][1]=="i32": spec_push_opd(opds,"i32")
      elif C["globals"][x][1]=="i64": spec_push_opd(opds,"i64")
      elif C["globals"][x][1]=="f32": spec_push_opd(opds,"f32")
      elif C["globals"][x][1]=="f64": spec_push_opd(opds,"f64")
      else: raise Exception("invalid")
    if opcode_binary==0x24:			# set_global
      x = immediates
      if len(C["globals"])<=x: raise Exception("invalid")
      if C["globals"][x][0] != "var": raise Exception("invalid")
      if C["globals"][x][1]=="i32": ret = spec_pop_opd_expect(opds,ctrls,"i32")
      elif C["globals"][x][1]=="i64": ret = spec_pop_opd_expect(opds,ctrls,"i64")
      elif C["globals"][x][1]=="f32": ret = spec_pop_opd_expect(opds,ctrls,"f32")
      elif C["globals"][x][1]=="f64": ret = spec_pop_opd_expect(opds,ctrls,"f64")
      else: raise Exception("invalid")
  elif 0x28<=opcode_binary<=0x40:		# MEMORY INSTRUCTIONS
    if "mems" not in C or len(C["mems"])==0: raise Exception("invalid")
    if opcode_binary<=0x35:
      memarg = immediates
      if opcode_binary==0x28:			# i32.load
        N=32; t="i32"
      elif opcode_binary==0x29:			# i64.load
        N=64; t="i64"
      elif opcode_binary==0x2a:			# f32.load
        N=32; t="f32"
      elif opcode_binary==0x2b:			# f64.load
        N=64; t="f64"
      elif opcode_binary <= 0x2d:		# i32.load8_s, i32.load8_u
        N=8; t="i32"
      elif opcode_binary <= 0x2f:		# i32.load16_s, i32.load16_u
        N=16; t="i32"
      elif opcode_binary <= 0x31:		# i64.load8_s, i64.load8_u
        N=8; t="i64"
      elif opcode_binary <= 0x33:		# i64.load16_s, i64.load16_u
        N=16; t="i64"
      elif opcode_binary <= 0x35:		# i64.load32_s, i64.load32_u
        N=32; t="i64"
      if 2**memarg["align"]>N//8: raise Exception("invalid")
      spec_pop_opd_expect(opds,ctrls,"i32")
      spec_push_opd(opds,t)
    elif opcode_binary<=0x3e:
      memarg = immediates
      if opcode_binary==0x36:			# i32.store
        N=32; t="i32"
      elif opcode_binary==0x37:			# i64.store
        N=64; t="i64"
      elif opcode_binary==0x38:			# f32.store
        N=32; t="f32"
      elif opcode_binary==0x39:			# f64.store
        N=64; t="f64"
      elif opcode_binary==0x3a:			# i32.store8
        N=8; t="i32"
      elif opcode_binary==0x3b:			# i32.store16
        N=16; t="i32"
      elif opcode_binary==0x3c:			# i64.store8
        N=8; t="i64"
      elif opcode_binary==0x3d:			# i64.store16
        N=16; t="i64"
      elif opcode_binary==0x3e:			# i64.store32
        N=32; t="i64"
      if 2**memarg["align"]>N//8: raise Exception("invalid")
      spec_pop_opd_expect(opds,ctrls,t)
      spec_pop_opd_expect(opds,ctrls,"i32")
    elif opcode_binary==0x3f:			# memory.size
      spec_push_opd(opds,"i32")
    elif opcode_binary==0x40:			# memory.grow
      spec_pop_opd_expect(opds,ctrls,"i32")
      spec_push_opd(opds,"i32")
  elif 0x41<=opcode_binary<=0xbf:		# NUMERIC INSTRUCTIONS
    if opcode_binary<=0x44:
      if opcode_binary == 0x41:			# i32.const
        spec_push_opd(opds,"i32")
      elif opcode_binary == 0x42:		# i64.const
        spec_push_opd(opds,"i64")
      elif opcode_binary == 0x43:		# f32.const
        spec_push_opd(opds,"f32")
      else:					# f64.const
        spec_push_opd(opds,"f64")
    elif opcode_binary<=0x4f:
      if opcode_binary==0x45:			# i32.eqz
        spec_pop_opd_expect(opds,ctrls,"i32")
        spec_push_opd(opds,"i32")
      else:					# i32.eq, i32.ne, i32.lt_s, i32.lt_u, i32.gt_s, i32.gt_u, i32.le_s, i32.le_u, i32.ge_s, i32.ge_u
        spec_pop_opd_expect(opds,ctrls,"i32")
        spec_pop_opd_expect(opds,ctrls,"i32")
        spec_push_opd(opds,"i32")
    elif opcode_binary<=0x5a:
      if opcode_binary==0x50:			# i64.eqz
        spec_pop_opd_expect(opds,ctrls,"i64")
        spec_push_opd(opds,"i32")
      else:					# i64.eq, i64.ne, i64.lt_s, i64.lt_u, i64.gt_s, i64.gt_u, i64.le_s, i64.le_u, i64.ge_s, i64.ge_u
        spec_pop_opd_expect(opds,ctrls,"i64")
        spec_pop_opd_expect(opds,ctrls,"i64")
        spec_push_opd(opds,"i32")
    elif opcode_binary<=0x60:			# f32.eq, f32.ne, f32.lt, f32.gt, f32.le, f32.ge
      spec_pop_opd_expect(opds,ctrls,"f32")
      spec_pop_opd_expect(opds,ctrls,"f32")
      spec_push_opd(opds,"i32")
    elif opcode_binary<=0x66:			# f64.eq, f64.ne, f64.lt, f64.gt, f64.le, f64.ge
      spec_pop_opd_expect(opds,ctrls,"f64")
      spec_pop_opd_expect(opds,ctrls,"f64")
      spec_push_opd(opds,"i32")
    elif opcode_binary<=0x78:
      if opcode_binary<=0x69:			# i32.clz, i32.ctz, i32.popcnt
        spec_pop_opd_expect(opds,ctrls,"i32")
        spec_push_opd(opds,"i32")
      else:					# i32.add, i32.sub, i32.mul, i32.div_s, i32.div_u, i32.rem_s, i32.rem_u, i32.and, i32.or, i32.xor, i32.shl, i32.shr_s, i32.shr_u, i32.rotl, i32.rotr
        spec_pop_opd_expect(opds,ctrls,"i32")
        spec_pop_opd_expect(opds,ctrls,"i32")
        spec_push_opd(opds,"i32")
    elif opcode_binary<=0x8a:
      if opcode_binary<=0x7b:			# i64.clz, i64.ctz, i64.popcnt
        spec_pop_opd_expect(opds,ctrls,"i64")
        spec_push_opd(opds,"i64")
      else:					# i64.add, i64.sub, i64.mul, i64.div_s, i64.div_u, i64.rem_s, i64.rem_u, i64.and, i64.or, i64.xor, i64.shl, i64.shr_s, i64.shr_u, i64.rotl, i64.rotr
        spec_pop_opd_expect(opds,ctrls,"i64")
        spec_pop_opd_expect(opds,ctrls,"i64")
        spec_push_opd(opds,"i64")
    elif opcode_binary<=0x98:
      if opcode_binary<=0x91:			# f32.abs, f32.neg, f32.ceil, f32.floor, f32.trunc, f32.nearest, f32.sqrt,
        spec_pop_opd_expect(opds,ctrls,"f32")
        spec_push_opd(opds,"f32")
      else:					# f32.add, f32.sub, f32.mul, f32.div, f32.min, f32.max, f32.copysign
        spec_pop_opd_expect(opds,ctrls,"f32")
        spec_pop_opd_expect(opds,ctrls,"f32")
        spec_push_opd(opds,"f32")
    elif opcode_binary<=0xa6:
      if opcode_binary<=0x9f:			# f64.abs, f64.neg, f64.ceil, f64.floor, f64.trunc, f64.nearest, f64.sqrt,
        spec_pop_opd_expect(opds,ctrls,"f64")
        spec_push_opd(opds,"f64")
      else:					# f64.add, f64.sub, f64.mul, f64.div, f64.min, f64.max, f64.copysign
        spec_pop_opd_expect(opds,ctrls,"f64")
        spec_pop_opd_expect(opds,ctrls,"f64")
        spec_push_opd(opds,"f64")
    elif opcode_binary<=0xbf:
      if opcode_binary==0xa7:			# i32.wrap/i64
        spec_pop_opd_expect(opds,ctrls,"i64")
        spec_push_opd(opds,"i32")
      elif opcode_binary<=0xa9:			# i32.trunc_s/f32, i32.trunc_u/f32
        spec_pop_opd_expect(opds,ctrls,"f32")
        spec_push_opd(opds,"i32")
      elif opcode_binary<=0xab:			# i32.trunc_s/f64, i32.trunc_u/f64
        spec_pop_opd_expect(opds,ctrls,"f64")
        spec_push_opd(opds,"i32")
      elif opcode_binary<=0xad:			# i64.extend_s/i32, i64.extend_u/i32
        spec_pop_opd_expect(opds,ctrls,"i32")
        spec_push_opd(opds,"i64")
      elif opcode_binary<=0xaf:			# i64.trunc_s/f32, i64.trunc_u/f32
        spec_pop_opd_expect(opds,ctrls,"f32")
        spec_push_opd(opds,"i64")
      elif opcode_binary<=0xb1:			# i64.trunc_s/f64, i64.trunc_u/f64
        spec_pop_opd_expect(opds,ctrls,"f64")
        spec_push_opd(opds,"i64")
      elif opcode_binary<=0xb3:			# f32.convert_s/i32, f32.convert_u/i32
        spec_pop_opd_expect(opds,ctrls,"i32")
        spec_push_opd(opds,"f32")
      elif opcode_binary<=0xb5:			# f32.convert_s/i64, f32.convert_u/i64
        spec_pop_opd_expect(opds,ctrls,"i64")
        spec_push_opd(opds,"f32")
      elif opcode_binary<=0xb6:			# f32.demote/f64
        spec_pop_opd_expect(opds,ctrls,"f64")
        spec_push_opd(opds,"f32")
      elif opcode_binary<=0xb8:			# f64.convert_s/i32, f64.convert_u/i32
        spec_pop_opd_expect(opds,ctrls,"i32")
        spec_push_opd(opds,"f64")
      elif opcode_binary<=0xba:			# f64.convert_s/i64, f64.convert_u/i64
        spec_pop_opd_expect(opds,ctrls,"i64")
        spec_push_opd(opds,"f64")
      elif opcode_binary==0xbb:			# f64.promote/f32
        spec_pop_opd_expect(opds,ctrls,"f32")
        spec_push_opd(opds,"f64")
      elif opcode_binary==0xbc:			# i32.reinterpret/f32
        spec_pop_opd_expect(opds,ctrls,"f32")
        spec_push_opd(opds,"i32")
      elif opcode_binary==0xbd:			# i64.reinterpret/f64
        spec_pop_opd_expect(opds,ctrls,"f64")
        spec_push_opd(opds,"i64")
      elif opcode_binary==0xbe:			# f32.reinterpret/i32
        spec_pop_opd_expect(opds,ctrls,"i32")
        spec_push_opd(opds,"f32")
      else:					# f64.reinterpret/i64
        spec_pop_opd_expect(opds,ctrls,"i64")
        spec_push_opd(opds,"f64")
    else: raise Exception("invalid") #error, opcode not in the correct ranges
  return 0 #success, valid so far
 

# args when called the first time:  
def iterate_through_expression_and_validate_each_opcode(expression,Context,opds,ctrls):
  #print("iterate_through_expression_and_validate_each_opcode()")
  for node in expression:
    if type(node[0])!=str: raise Exception("invalid") #error
    opcode = node[0]
    #get immediate
    immediate=None
    if node[0] in {"br","br_if","block","loop","if","call","call_indirect","get_local", "set_local", "tee_local","get_global", "set_global","i32.const","i64.const","f32.const","f64.const"} or node[0][3:8] in {".load",".stor"}:
      immediate = node[1]
    elif node[0] == "br_table":
      immediate = [node[1],node[2]]
    #print(opcode,immediate)
    #validate
    spec_validate_opcode(Context,opds,ctrls,opcode,immediate)
    #recurse for block, loop, if
    if node[0] in {"block","loop","if"}:
      iterate_through_expression_and_validate_each_opcode(node[2],Context,opds,ctrls)
      if len(node)==4: #if with else
        iterate_through_expression_and_validate_each_opcode(node[3],Context,opds,ctrls)
  return 0

  
  
  

