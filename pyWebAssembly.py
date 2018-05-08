#!/usr/bin/env python


"""
TODO:
 - validator
   - chapter 3 infrastructure is mostly done, need to finish spec_validate_instrstar(), then will test and debug
   - chapter 7 infrastructure is mostly done, almost ready to test and debug
 - execution
   - eager to start this
 - error handling in chapter 5: binary parser
   - if idx>len(raw) or idx<0 and access raw[idx], will get "index out of range" error, but should handle this and return an error code

"""







###############
# 2 STRUCTURE #
###############


# 2.2.3 FLOATING-POINT

N_to_signif={32:23,64:52}
signif_to_N={val:key for key,val in N_to_signif.items()}

def spec_signif(N):
  if N in N_to_signif:
    return N_to_signif[N]
  else:
    return None

def spec_signif_inv(signif):
  if signif in signif_to_N:
    return signif_to_N[signif]
  else:
    return None

N_to_expon={32:8,64:11}
expon_to_N={val:key for key,val in N_to_expon.items()}

def spec_expon(N):
  if N in N_to_expon:
    return N_to_expon[N]
  else:
    return None

def spec_expon_inv(expon):
  if expon in expon_to_N:
    return expon_to_N[expon]
  else:
    return None









################
################
# 3 VALIDATION #
################
################


###########
# 3.2 TYPES
###########

# 3.2.1 LIMITS

def spec_validate_limits(limits):
  if limits["max"] != "None" and m>n:
    return -1
  return limits

# 3.2.2 FUNCTION TYPES

def spec_validate_functype(ft):
  if len(ft[1])>1:
    return -1
  return ft

# 3.2.3 TABLE TYPES

def spec_validate_tabletype(tt):
  limits, elemtype = tt
  ret = spec_validate_limit(limits)
  if ret == -1:
    return -1
  return tt

# 3.2.4 MEMORY TYPES

def spec_validate_memtype(limits):
  return spec_validate_limits(limits)

# 3.2.5 GLOBAL TYPES

def spec_validate_globaltype(globaltype):
  return globaltype


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
  if len(C["locals"]) <= x:
    return -1
  t = C["locals"][x]
  return [],[t] 

def spec_validate_set_local(C,x):
  if len(C["locals"]) <= x: return -1
  t = C.["locals"][x]
  return [t],[]

def spec_validate_tee_local(C,x):
  if len(C["locals"]) <= x: return -1
  t = C["locals"][x]
  return [t],[t]

def spec_validate_get_global(C,x):
  if len(C["globals"]) <= x: return -1
  mut,t = C.globals[x]
  return [],[t]

def spec_validate_set_global(C,x):
  if len(C["globals"]) <= x: return -1
  mut,t = C.globals[x]
  if mut!="var": return -1
  return [t],[]


# 3.3.4 MEMORY INSTRUCTIONS

def spec_validate_t_load(C,t,memarg):
  if len(C["mems"])<1: return -1
  tval = int(t[1:2]) # invariant: t has form: letter digit digit  eg i32
  if 2**memarg.align>tval//8: return -1
  return ["i32"],[t]

def spec_validate_tloadNsx(C,t,N,memarg):
  if len(C["mems"])<1: return -1
  if 2**memarg.align>N//8: return -1
  return ["i32"],[t]

def spec_validate_tstore(C,t,memarg):
  if len(C["mems"])<1: return -1
  tval = int(t[1:2]) # invariant: t has form: letter digit digit  eg i32
  if 2**memarg.align>tval//8: return -1
  return ["i32",t],[]

def spec_validate_tstoreN(C,t,N,memarg):
  if len(C["mems"])<1: return -1
  if 2**memarg.align>N//8: return -1
  return ["i32",t],[]

def spec_validate_memorysize(C):
  if len(C["mems"])<1: return -1
  return [],["i32"]

def spec_validate_memorygrow(C):
  if len(C["mems"])<1: return -1
  return ["i32"],["i32"]


# 3.3.5 CONTROL INSTRUCTIONS

def spec_validate_nop():
  return [].[]

def spec_validate_uneachable():
  return ["t1*"],["t2*"]

def spec_validate_block(C,tq,instrstar):
  C["labels"].append([tq] if tq else [])
  type_ = spec_validate_instrstar(C,instrstar)  
  C["labels"].pop()
  if type_ != ([],[tq] if tq else []): return -1
  return type_

def spec_validate_loop(C,tq,instrstar):
  C["labels"].append([])
  type_ = spec_validate_instrstar(C,instrstar)  
  C["labels"].pop()
  if type_ != ([],[tq] if tq else []): return -1
  return type_

def spec_validate_if(C,tq,instrstar1,instrstar2):
  C["labels"].append([tq] if tq else [])
  type_ = spec_validate_instrstar(C,instrstar1)  
  if type_ != ([],[tq] if tq else []): return -1
  type_ = spec_validate_instrstar(C,instrstar2)  
  if type_ != ([],[tq] if tq else []): return -1
  C["labels"].pop()
  return ["i32"],[tq] if tq else []

def spec_validate_br(C,l):
  if len(C["labels"]) <= l: return -1
  tq_in_brackets = C["labels"][l]
  return ["t1*"] + tq_in_brackets, ["t2*"]
  
def spec_validate_br_if(C,l):
  if len(C["labels"]) <= l: return -1
  tq_in_brackets = C["labels"][l]
  return tq_in_brackets + ["i32"], tq_in_brackets

def spec_validate_br_table(C,lstar,lN):
  if len(C["labels"]) <= lN: return -1
  tq_in_brackets = C["labels"][lN]
  for li in lstar:
    if len(C["labels"]) <= li: return -1
    if C["labels"][li] != tq_in_brackets: return -1
  return ["t1*"] + tq_in_brackes + ["i32"], ["t2*"]

def spec_validate_return(C):
  if C["return"] == None: return -1
  tq_in_brackets = C["return"]
  return ["t1*"] + tq_in_brackes + ["i32"], ["t2*"]

def spec_validate_call(C,x):
  if len(C["funcs"]) <= x: return -1
  return C.["funcs"][x]

def spec_validate_call_indirect(C,x):
  if C["tables"]==None or len(C["tables"]) < 1: return -1
  limits,elemtype = C["tables"][0]
  if elemtype != "anyfunc": return -1
  if C["types"]==None or len(C["types"]) <= x: return -1
  return C["types"][x][0]+["i32"],C["types"][x][1]


# 3.3.6 INSTRUCTION SEQUENCES

def spec_validate_instrstar(C,instrstar):
  #get instr and immediate
  #special case if block, loop, or if, then loop with recursive call
  #return whatever validation returns, and maybe opds and ctrls
  if instrstar == []: return ["t*"],["t*"]
  operandstack = []
  for instr in instrstar:
    opcode = instr[0]
    if opcode not in opcodes_text2binary: return -1
    immediates=None
    if len(instr[0]>1)
      immediates = instr[0][1:]
    # numeric instructions
    if opcode[4:] in {"const"}:
      type_ = spec_validate_t_const(opcode[:3])
    elif opcode[4:] in {'clz','ctz','popcnt','abs','neg','sqrt','ceil','floor','trunc','nearest'}:
      type_ = spec_validate_t_unop(opcode[:3])
    elif opcode[4:] in {'add','sub','mul',  'div_u','div_s','rem_u','rem_s','and','or','xor','shl','shr_u','shr_s','rotl','rotr',  'div','min','max','copysign'}:
      type_ = sspec_validate_t_binop(opcode[:3])
    elif opcode[4:] in {'eqz'}:
      type_ = spec_validate_t_testop(opcode[:3])
    elif opcode[4:] in {'eq','ne',  'lt_u','lt_s','gt_u','gt_s','le_u','le_s','ge_u','ge_s',  'lt','gt','le','ge' }:
      type_ = spec_validate_t_relop([opcode[:3]])
    elif opcode[4:] in {'wrap','extend_u','extend_s','trunc_u','trunc_s','convert_u','convert_s','demote','promote','reinterpret'}:
      type_ = spec_validate_t2_cvtop_t1(opcode[-3:],opcode[:3])
    # parametric instructions
    elif opcode in {'drop'}:
      type_ = spec_validate_drop()
    elif opcode in {'select'}:
      type_ = spec_validate_select()
    # variable instructions
    elif opcode[-5:] == "local":
      if opcode[:3] == "get":
        type_ = spec_validate_get_local(C,immediates)
      elif opcode[:3] == "set":
        type_ = spec_validate_set_local(C,immediates)
      elif opcode[:3] == "tee":
        type_ = spec_validate_tee_local(C,immediates)
    elif opcode[-5:] == "global":
      if opcode[:3] == "get":
        type_ = spec_validate_get_global(C,immediates)
      elif opcode[:3] == "set":
        type_ = spec_validate_set_global(C,immediates)
    # memory instructions
    elif opcode[4:8] == "load":
      if opcode[4:] == "load":
        type_ = spec_validate_t_load(C,opcode[:3],immediates)
      else:
        N,sx = opcode[9:].split(_)
        N=int(N)
        type_ = spec_validate_tloadNsx(C,opcode[:3],N,immediates)
    elif opcode[4:9] == "store":
      if opcode[4:] == "store":
        type_ = spec_validate_tstore(C,opcode[:3],immediates)
      else:
        type_ = spec_validate_tstoreN(C,opcode[:3],int(opcode[10:]),immediates)
    elif opcode == "memory.size":
      type_ = spec_validate_memorysize(C)
    elif opcode == "memory.grow":
      type_ = spec_validate_memorygrow(C)
    # control instructions
    elif opcode == "nop":
      type_ = spec_validate_nop()
    elif opcode == "unreachable":
      type_ = spec_validate_uneachable()
    elif opcode == "block":
      type_ = spec_validate_block(C,immediate,instr[2]) #TODO: check index
    elif opcode == "loop":
      type_ = spec_validate_loop(C,immediate,instr[2]) #TODO: check index
    elif opcode == "if":
      type_ = spec_validate_if(C,immeidate,instr[2],[] if len(instr)<4 else instr[3]) #TODO: check indices
    elif opcode == "br":
      type_ = spec_validate_br(C,immediates)
    elif opcode == "br_if":
      type_ = spec_validate_br_if(C,immediates)
    elif opcode == "br_table":
      type_ = spec_validate_br_table(C,immediates[0],immediates[1]) #TODO check indices
    elif opcode == "return":
      type_ = spec_validate_return(C)
    elif opcode == "call":
      type_ = spec_validate_call(C,immeidates)
    elif opcode == "call_indirect":
      type_ = spec_validate_call_indirect(C,immediates)
    # handle type_ wrt current operand stack, TODO: FINISH THIS to support stack-polymorphism
    for t in reversed(type_[0]):
      if operandstack[-1] != t:
        return -1
      del operandstack[-1]
    for t in type_[0]:
      operandstack.append(t)
  return operandstack


# 3.3.7 EXPRESSIONS

def spec_validate_expr(C,expr):
  type_ = spec_validate_instrstrar(C,expr[:-1])
  if expr[-1] != ['end']:
    return -1
  return type_

def spec_validate_const_instr(C,instr):
  if e[0] not in {"i32.const","i64.const","f32.const","f64.const","get_global"}:
    return -1
  if e[0] == "get_global" and C.globals[e[1]][0] != "const":
    return -1
  return "const"

def spec_validate_const_expr(C,expr):
  #expr is in AST form
  for e in expr[:-1]:
    if spec_validate_const_instr(C,e) == -1:
      return -1
  if expr[-1] != "end":
    return -1
  return 0


#############
# 3.4 MODULES
#############

# 3.4.1 FUNCTIONS

def spec_validate_func(C,func,raw=None):
  x = func["type"]
  if len(C.types)<=x: return -1
  t1 = C.types[x][0]
  t2 = C.types[x][1]
  C["locals"] = t1 + func["locals"]
  C["labels"] = t2
  C["return"] = t2
  if len(func["body"])==3: #since func["body"] is has form (locals,expr), but we added the form (locals,expr_bytecode_address,size)
    if raw:
      ft = spec_validate_expr_bytecode(func["expr"],C,raw)
    else:
      return -1
  else
    ft = spec_validate_expr(func["expr"],C)
  C["locals"] = None
  C["labels"] = None
  C["return"] = None
  return ft


# 3.4.2 TABLES

def spec_validate_table(table)
  return spec_validate_tabletype(table["type"])


# 3.4.3 MEMORIES

def spec_validate_mem(mem):
  return spec_validate_memtype(mem["type"])


# 3.4.4 GLOBALS

def spec_validate_global(C,global_):
  if spec_validate_globaltype(global_["type"])
  valid = spec_validate_const_ezpression(global_["init"])
  if valid == -1: return -1
  return 0


# 3.4.5 ELEMENT SEGMENT

def spec_validate_elem(C,elem):
  x = elem["table"]
  if "tables" not in C or len(C["tables"])<=x: return -1
  tabletype = C.tables[x]
  limits = tabletype[0]
  elemtype = tabletype[1]
  if elemtype != "anyfunc": return -1
  if spec_validate_expr(elem["offset"],C) != ["i32"]: return -1
  if spec_validate_const_ezpression(C,elem["offset"]) == -1: return -1
  for y in elem["init"]:
    if len(C.funcs)<=y: return -1
  return 0


# 3.4.6 DATA SEGMENTS

def spec_validate_data(C,data):
  x = data["data"]
  if len(C.mems)<=x: return -1
  if spec_validate_expr(data["offset"],C) != ["i32"]: return -1
  if spec_validate_const_ezpression(C,data["offset"]) == -1: return -1
  return 0


# 3.4.7 START FUNCTION

def spec_validate_start(C,start):
  x = start["funcs"]
  if len(C.funcs)<=x: return -1
  if C.funcs[x] != ([].[]): return -1
  return 0
  

# 3.4.8 EXPORTS

def spec_validate_export(C,export):
  return spec_validate_exportdesc(C,export["desc"])
  
def spec_validate_exportdesc(c,exportdesc):
  x = exportdesc[1]
  if exportdesc[0]=="func":
    if len(C["funcs"])<=x: return -1
    return "func",C["funcs"][x]
  elif exportdesc[0]=="table":
    if len(C["tables"])<=x: return -1
    return "table",C["tables"][x]
  elif exportdesc[0]=="mem":
    if len(C["mems"])<=x: return -1
    return "mem",C["mems"][x]
  elif exportdesc[0]=="global":
    if len(C["globals"])<=x: return -1
    mut,t = C["globals"][x]
    if mut != "const": return -1
    return "global",C["globals"][x]
  else: return -1
  

# 3.4.9 IMPORTS

def spec_validate_import(C,import_):
  return spec_validate_importdesc(C,import_["desc"])
  
def spec_validate_importdesc(c,importdesc):
  if importdesc[0]=="func":
    x = importdesc[1]
    if len(C["funcs"])<=x: return -1,-1
    return "func",C["types"][x]
  elif importdesc[0]=="table":
    tabletype = importdesc[1]
    if spec_validate_tabletype(tabletype) == -1: return -1,-1
    return "table",tabletype
  elif importdesc[0]=="mem":
    memtype = importdesc[1]
    if spec_validate_memtype(memtype) == -1: return -1,-1
    return "mem",memtype
  elif importdesc[0]=="global":
    globaltype = importdesc[1]
    if spec_validate_globaltype(globaltype) == -1: return -1,-1
    if globaltype[0] != "const": return -1,-1
    mut,t = C["globals"][x]
    if mut != "const": return -1,-1
    return "global",globaltype
  else: return -1



# 3.4.10 MODULES

 def spec_validate_module(mod,bytecode=None)
  # bytecode is the module in raw bytecode, used when functions store code as a bytearray (which is faster to validate), otherwise code is in abstract syntax form
  # mod is the module to validate
  # let _tstar be the concatenation of ...
  ftstar = [func["type"] for func in mod["funcs"]]
  ttstar = [table["type"] for table in mod["tables"]]
  mtstar = [mem["type"] for mem in mod["mems"]]
  gtstar = [global_["type"] for global_ in mod["globals"]]
  itstar = []
  for import_ in mod["imports"]:
    if import_["desc"][0] == "func":
      itstar.append( ["func",mod["types"][import_["desc"][1]]] )
    else
      itstar.append( import_["desc"] )
  etstar = []
  for export in mod["exports"]:
    if export["desc"][0] == "func":
      itstar.append( ["func",mod["types"][export["desc"][1]]] )
    elif export["desc"][0] == "table":
      itstar.append( ["table",mod["tables"][export["desc"][1]]]["type"] )
    elif export["desc"][0] == "mem":
      itstar.append( ["mem",mod["mems"][export["desc"][1]]]["type"] )
    elif export["desc"][0] == "global":
      itstar.append( ["global",mod["globals"][export["desc"][1]]]["type"] )
  # let i_tstar be the concatenation of imports of each type
  iftstar = [it for it in itstar if it["type"]=="func"]
  ittstar = [it for it in itstar if it["type"]=="table"]
  imtstar = [it for it in itstar if it["type"]=="mem"]
  igtstar = [it for it in itstar if it["type"]=="global"]
  # let C and Cprime be contexts
  C = {"types":		mod["types"],
       "funcs":		iftstar + ftstar
       "tables":	ittstar + ttstar
       "mems":		imtstar + mtstar
       "globals":	igtstar + gtstar
       "locals":	None,
       "labels":	None,
       "return":	None }
  Cprime = {
       "types":		None,
       "funcs":		None,
       "tables":	None,
       "mems":		None,
       "globals":	igtstar,
       "locals":	None,
       "labels":	None,
       "returns":	None }
  # under the context C or Cprime, validate each section
  for type_ in mod["types"]:
    valid = spec_validate_functype(C,type_)
    if valid == -1: return -1
  for i,func in enumerate(mod["funcs"]):
    ft = spec_validate_func(C, func, bytecode)
    if ft == -1 or ft != ftstar[i]: return -1
  for i,table in enumerate(mod["tables"]):
    tt = spec_validate_table(table)
    if tt == -1 or tt != ttstar[i]: return -1
  for i,mem in enumerate(mod["mems"]):
    mt = spec_validate_mem(mem)
    if mt == -1 or mt != mtstar[i]: return -1
  for i,global_ in enumerate(mod["globals"]):
    gt = spec_validate_global(Cprime,global_)
    if gt == -1 or gt != gtstar[i]: return -1
  for elem in mod["elem"]:
    valid = spec_validate_elem(C,elem)
    if valid == -1: return -1
  for data in mod["data"]:
    valid = spec_validate_data(C,data)
    if valid == -1: return -1
  if mod["start"]:
    valid = spec_validate_start(C,mod["start"])
    if valid == -1: return -1
  for i,import_ in enumerate(mod["imports"]):
    it = spec_validate_import(C,import_)
    if valid == -1 or it != itstar[i]: return -1
  for i,export in enumerate(mod["exports"]):
    et = spec_validate_export(C,export)
    if valid == -1 or et != etstar[i]: return -1
  # export names must be unique
  exportnames = set()
  for export in mod["exports"]:
    if export["name"] in exportnames: return -1
     exportnames.add(export["name"])
  # tables and mems have at most one each
  if len(C["tables"])>1: return -1
  if len(C["mems"])>1: return -1
  return [itstar, etstar]









###############
###############
# 4 EXECUTION #
###############
###############


##############
# 4.3 NUMERICS
##############

# 4.3.1 REPRESENTATIONS

#TODO: check if this is correct; note little-endian; 
#floating-point values are encoded directly by their IEEE 754-2008 bit pattern in little endian byte order
def spec_bytes_fN_inv(bstar,N):
  bitstring=""
  for by in bstar:
    bitstring += bin(by)[2:].rjust(8, '0')
  signstring='+' if bitstring[0]=='1' else '-'
  M=spec_signif(N)
  E=spec_expon(N)
  e=bitstring[1:E+1]
  m=bitstring[E+1:]
  if e=='1'*E:
    if m=='0'*M:
      return signstring+"inf"
    else:
      return signstring+"nan("+string(int(m,2))+")"
  elif e=='0'*E:
    return signstring+'0.'+str(int(m,2))
  else:
    return signstring+"1."+str(int(m,2))+"e"+str(int(e,2)-(2**(E-1)-1))



# 4.3.2 INTEGER OPERATIONS

def spec_signediN(N,i):
  if 0<=i<2**(N-1):
    return i
  elif 2**(N-1)<=i<2**N:
    return i-2**N
  else:
    return None

def spec_signed_iN_inv(N,i):
  if 0<=i<2**(N-1):
    return i
  elif -1*(2**(N-1))<=i<0:
    return i+2**N
  else:
    return None







###################
###################
# 5 BINARY FORMAT #
###################
###################

# key-value pairs of binary opcodes and their text reperesentation
opcodes_binary2text = {
0x00:'unreachable',
0x01:'nop',
0x02:'block',			# blocktype in* end		# begin block
0x03:'loop',			# blocktype in* end		# begin block
0x04:'if',			# blocktype in1* else? end	# begin block
0x05:'else',			# in2*				# end block & begin block
0x0b:'end',							# end block
0x0c:'br',			# labelidx			# branch
0x0d:'br_if',			# labelidx			# branch
0x0e:'br_table',		# labelidx* labelidx		# branch
0x0f:'return',							# end outermost block
0x10:'call',			# funcidx			# branch
0x11:'call_indirect',		# typeidx 0x00			# branch

0x1a:'drop',
0x1b:'select',

0x20:'get_local',		# localidx
0x21:'set_local',		# localidx
0x22:'tee_local',		# localidx
0x23:'get_global',		# globalidx
0x24:'set_global',		# globalidx

0x28:'i32.load',		# memarg
0x29:'i64.load',		# memarg
0x2a:'f32.load',		# memarg
0x2b:'f64.load',		# memarg
0x2c:'i32.load8_s',		# memarg
0x2d:'i32.load8_u',		# memarg
0x2e:'i32.load16_s',		# memarg
0x2f:'i32.load16_u',		# memarg
0x30:'i64.load8_s',		# memarg
0x31:'i64.load8_u',		# memarg
0x32:'i64.load16_s',		# memarg
0x33:'i64.load16_u',		# memarg
0x34:'i64.load32_s',		# memarg
0x35:'i64.load32_u',		# memarg
0x36:'i32.store',		# memarg
0x37:'i64.store',		# memarg
0x38:'f32.store',		# memarg
0x39:'f64.store',		# memarg
0x3a:'i32.store8',		# memarg
0x3b:'i32.store16',		# memarg
0x3c:'i64.store8',,		# memarg
0x3d:'i64.store16',		# memarg
0x3e:'i64.store32',		# memarg
0x3f:'memory.size',
0x40:'memory.grow',

0x41:'i32.const',		# i32
0x42:'i64.const',		# i64
0x43:'f32.const',		# f32
0x44:'f64.const',		# f64

0x45:'i32.eqz',
0x46:'i32.eq',
0x47:'i32.ne',
0x48:'i32.lt_s',
0x49:'i32.lt_u',
0x4a:'i32.gt_s',
0x4b:'i32.gt_u',
0x4c:'i32.le_s',
0x4d:'i32.le_u',
0x4e:'i32.ge_s',
0x4f:'i32.ge_u',

0x50:'i64.eqz',
0x51:'i64.eq',
0x52:'i64.ne',
0x53:'i64.lt_s',
0x54:'i64.lt_u',
0x55:'i64.gt_s',
0x56:'i64.gt_u',
0x57:'i64.le_s',
0x58:'i64.le_u',
0x59:'i64.ge_s',
0x5a:'i64.ge_u',

0x5b:'f32.eq',
0x5c:'f32.ne',
0x5d:'f32.lt',
0x5e:'f32.gt',
0x5f:'f32.le',
0x60:'f32.ge',

0x61:'f64.eq',
0x62:'f64.ne',
0x63:'f64.lt',
0x64:'f64.gt',
0x65:'f64.le',
0x66:'f64.ge',

0x67:'i32.clz',
0x68:'i32.ctz',
0x69:'i32.popcnt',
0x6a:'i32.add',
0x6b:'i32.sub',
0x6c:'i32.mul',
0x6d:'i32.div_s',
0x6e:'i32.div_u',
0x6f:'i32.rem_s',
0x70:'i32.rem_u',
0x71:'i32.and',
0x72:'i32.or',
0x73:'i32.xor',
0x74:'i32.shl',
0x75:'i32.shr_s',
0x76:'i32.shr_u',
0x77:'i32.rotl',
0x78:'i32.rotr',

0x79:'i64.clz',
0x7a:'i64.ctz',
0x7b:'i64.popcnt',
0x7c:'i64.add',
0x7d:'i64.sub',
0x7e:'i64.mul',
0x7f:'i64.div_s',
0x80:'i64.div_u',
0x81:'i64.rem_s',
0x82:'i64.rem_u',
0x83:'i64.and',
0x84:'i64.or',
0x85:'i64.xor',
0x86:'i64.shl',
0x87:'i64.shr_s',
0x88:'i64.shr_u',
0x89:'i64.rotl',
0x8a:'i64.rotr',

0x8b:'f32.abs',
0x8c:'f32.neg',
0x8d:'f32.ceil',
0x8e:'f32.floor',
0x8f:'f32.trunc',
0x90:'f32.nearest',
0x91:'f32.sqrt',
0x92:'f32.add',
0x93:'f32.sub',
0x94:'f32.mul',
0x95:'f32.div',
0x96:'f32.min',
0x97:'f32.max',
0x98:'f32.copysign',

0x99:'f64.abs',
0x9a:'f64.neg',
0x9b:'f64.ceil',
0x9c:'f64.floor',
0x9d:'f64.trunc',
0x9e:'f64.nearest',
0x9f:'f64.sqrt',
0xa0:'f64.add',
0xa1:'f64.sub',
0xa2:'f64.mul',
0xa3:'f64.div',
0xa4:'f64.min',
0xa5:'f64.max',
0xa6:'f64.copysign',

0xa7:'i32.wrap/i64',
0xa8:'i32.trunc_s/f32',
0xa9:'i32.trunc_u/f32',
0xaa:'i32.trunc_s/f64',
0xab:'i32.trunc_u/f64',
0xac:'i64.extend_s/i32',
0xad:'i64.extend_u/i32',
0xae:'i64.trunc_s/f32',
0xaf:'i64.trunc_u/f32',
0xb0:'i64.trunc_s/f64',
0xb1:'i64.trunc_u/f64',
0xb2:'f32.convert_s/i32',
0xb3:'f32.convert_u/i32',
0xb4:'f32.convert_s/i64',
0xb5:'f32.convert_u/i64',
0xb6:'f32.demote/f64',
0xb7:'f64.convert_s/i32',
0xb8:'f64.convert_u/i32',
0xb9:'f64.convert_s/i64',
0xba:'f64.convert_u/i64',
0xbb:'f64.promote/f32',
0xbc:'i32.reinterpret/f32',
0xbd:'i64.reinterpret/f64',
0xbe:'f32.reinterpret/i32',
0xbf:'f64.reinterpret/i64',
}

# key-value pairs of text opcodes and their binary reperesentation
opcodes_text2binary = {}
for opcode inopcodes_binary2text:
  opcodes_text2binary[opcodes_binary2text[opcode]]=opcode


# 5.1.3 VECTORS

def spec_vec(raw,idx,B):
  idx,n=spec_uN(raw,idx,32)
  xn = []
  for i in range(n):
    idx,x = B(raw,idx)
    xn+=[x]
  return idx,xn

def spec_vec_inv(mynode,myfunc):
  n_bytes=spec_uN_inv(len(mynode),32) 
  xn_bytes=bytearray()
  for x in mynode:
    xn_bytes+=myfunc(x)
  return n_bytes+xn_bytes 


############
# 5.2 VALUES
############

# 5.2.1 BYTES

def spec_byte(raw,idx):
  return idx+1,raw[idx]

def spec_byte_inv(node):
  return bytearray([node])

# 5.2.2 INTEGERS
#TODO: check things on pg 87

#unsigned
def spec_uN(raw,idx,N):
  idx,n=spec_byte(raw,idx)
  if n<2**7 and n<2**N:
    return idx,n
  elif n>=2**7 and N>7:
    idx,m=spec_uN(raw,idx,N-7)
    return idx, (2**7)*m+(n-2**7)
  else:
    return idx,None #error

def spec_uN_inv(k,N):
  #print("spec_uN_inv(",k,N,")")
  if k<2**7 and k<2**N:
    return bytearray([k])
  elif k>=2**7 and N>7:
    return bytearray([k%(2**7)+2**7])+spec_uN_inv(k//(2**7),N-7)
  else:
    return None

def spec_uN_inv_old(n,N):
  if n>2**N:
    return None #error
  mybytes = bytearray()
  while n>2**7:
    m=(n&0b1111111)+2**7
    mybytes.append(m)
    n=n>>7
  mybytes.append(n)
  return mybytes

#signed
def spec_sN(raw,idx,N):
  n=int(raw[idx])
  idx+=1
  if n<2**6 and n<2**(N-1):
    return idx,n
  elif 2**6<=n<2**7 and n>=2**7-2**(N-1):
    return idx,n-2**7
  elif n>=2**7 and N>7:
    idx,m=spec_sN(raw,idx,N-7)
    return idx,2**7*m+(n-2**7)
  else:
    return idx,None #error

def spec_sN_inv(k,N):
  if 0<=k<2**6 and k<2**N:
    return bytearray([k])
  elif 2**6<=k+2**7<2**7: # and k+2**7>=2**7-2**(N-1):
    return bytearray([k+2**7])
  elif (k>=2**6 or k<2**6) and N>7: #(k<0 and k+2**7>=2**6)) and N>7:
    return bytearray([k%(2**7)+2**7])+spec_sN_inv((k//(2**7)),N-7)
  else:
    return None

#uninterpretted integers
def spec_iN(raw,idx,N):
  idx,n=spec_sN(raw,idx,N)
  i = spec_signed_iN_inv(N,n)
  return idx, i

def spec_iN_inv(i,N):
  return spec_sN_inv(spec_signediN(N,i),N)



# 5.2.3 FLOATING-POINT

#fN::= b*:byte^{N/8} => bytes_{fN}^{-1}(b*)
def spec_fN(raw,idx,N):
  bstar = []
  for i in range(N//8):
    bstar+=[raw[idx]]
    idx+=1
  return idx, bytearray(bstar)

def spec_fN_inv(node,N):
  if len(node)==N/8:
    return node
  else:
    return None
  

# 5.2.4 NAMES

#name as UTF-8 codepoints
def spec_name(raw,idx):
  idx,bstar = spec_vec(raw,idx,spec_byte)
  #rest is finding inverse of utf8(name)=b*
  bstaridx=0
  lenbstar = len(bstar)
  name=[]
  while bstaridx<lenbstar:
    b1=bstar[bstaridx]
    bstaridx+=1
    if b1<0x80:
      name+=[b1]
      continue
    b2=bstar[bstaridx]
    bstaridx+=1
    c=2**6*(b1-0xc0) + (b2-0x80)
    if 0x80<=c<0x800:
      name+=[c]
      continue
    b3=bstar[bstaridx]
    bstaridx+=1
    c=2**12*(b1-0xc0) + 2**6*(b2-0x80) + (b3-0x80)
    if 0x800<=c<0x10000:
      name+=[c]
      continue
    b4=bstar[bstaridx+4]
    bstaridx+=1
    c=2**18*(b1-0xc0) + 2**12*(b2-0x80) + 2**6*(b3-0x80) + (b4-0x80)
    if 0x10000<=c<0x110000:
      name+=[c]
    else:
      break  #return idx, None #error
  #convert each codepoint to utf8 character
  nametxt = ""
  for b in name:
    nametxt+=chr(b)
  return idx,nametxt

def spec_name_inv(chars):
  name_bytes=bytearray()
  for c in chars:
    c = ord(c)
    if c<0x80:
      name_bytes += bytes([c])
    elif 0x80<=c<0x800:
      name_bytes += bytes([(c>>6)+0xc0,(c&0b111111)+0x80])
    elif 0x800<=c<0x10000:
      name_bytes += bytes([(c>>12)+0xc0,((c>>6)&0b111111)+0x80,(c&0b111111)+0x80])
    elif 0x10000<=c<0x110000:
      name_bytes += bytes([(c>>18)+0xc0,((c>>12)&0b111111)+0x80,((c>>6)&0b111111)+0x80,(c&0b111111)+0x80])
    else:
      return None #error
  return bytearray([len(name_bytes)])+name_bytes


###########
# 5.3 TYPES
###########

# 5.3.1 VALUE TYPES

valtype2bin={"i32":0x7f,"i64":0x7e,"f32":0x7d,"f64":0x7c}
bin2valtype={val:key for key,val in valtype2bin.items()}

def spec_valtype(raw,idx):
  if raw[idx] in bin2valtype:
    return idx+1,bin2valtype[raw[idx]]
  else:
    return idx,None #error

def spec_valtype_inv(node):
  if node in valtype2bin:
    return bytearray([valtype2bin[node]])
  else:
    return bytearray([]) #error

# 5.3.2 RESULT TYPES

def spec_blocktype(raw,idx):
  if raw[idx]==0x40:
    return idx+1,None
  idx,t=spec_valtype(raw,idx)
  return idx, t

def spec_blocktype_inv(node):
  if node==None:
    return bytearray([0x40])
  else:
    return spec_valtype_inv(node)


# 5.3.3 FUNCTION TYPES

def spec_functype(raw,idx):
  if raw[idx]!=0x60:
    return idx, None #error
  idx+=1
  idx,t1star=spec_vec(raw,idx,spec_valtype)
  idx,t2star=spec_vec(raw,idx,spec_valtype)
  return idx,[t1star,t2star]

def spec_functype_inv(node):
  return bytearray([0x60])+spec_vec_inv(node[0],spec_valtype_inv)+spec_vec_inv(node[1],spec_valtype_inv)


# 5.3.4 LIMITS

def spec_limits(raw,idx):
  if raw[idx]==0x00:
    idx,n = spec_uN(raw,idx+1,32)
    return idx,{"min":n,"max":None}
  elif raw[idx]==0x01:
    idx,n = spec_uN(raw,idx+1,32)
    idx,m = spec_uN(raw,idx,32)
    return idx,{"min":n,"max":m}
  else:
    return idx,None #error
    
def spec_limits_inv(node):
  if node["max"]==None:
    return bytearray([0x00])+spec_uN_inv(node["min"],32)
  else:
    return bytearray([0x01])+spec_uN_inv(node["min"],32)+spec_uN_inv(node["max"],32)

  
# 5.3.5 MEMORY TYPES

def spec_memtype(raw,idx):
  return spec_limits(raw,idx)

def spec_memtype_inv(node):
  return spec_limits_inv(node)


# 5.3.6 TABLE TYPES

def spec_tabletype(raw,idx):
  idx,et = spec_elemtype(raw,idx)
  idx,lim = spec_limits(raw,idx)
  return idx,[lim,et]

def spec_elemtype(raw,idx):
  if raw[idx]==0x70:
    return idx+1,"anyfunc"
  else:
    return idx,None #error

def spec_tabletype_inv(node):
  return spec_elemtype_inv(node[1])+spec_limits_inv(node[0])

def spec_elemtype_inv(node):
  return bytearray([0x70])


# 5.3.7 GLOBAL TYPES

def spec_globaltype(raw,idx):
  idx,t = spec_valtype(raw,idx)
  idx,m = spec_mut(raw,idx)
  return idx,[m,t]

def spec_mut(raw,idx):
  if raw[idx]==0x00:
    return idx+1,"const"
  elif raw[idx]==0x01:
    return idx+1,"var"
  else:
    return idx, None #error

def spec_globaltype_inv(node):
  return spec_valtype_inv(node[1])+spec_mut_inv(node[0])

def spec_mut_inv(node):
  if node=="const":
    return bytearray([0x00])
  elif node=="var":
    return bytearray([0x01])
  else:
    return bytearray([])


##################
# 5.4 INSTRUCTIONS
##################

# 5.4.1-5 VARIOUS INSTRUCTIONS

def spec_memarg(raw,idx):
  idx,a=spec_uN(raw,idx,32)
  idx,o=spec_uN(raw,idx,32)
  return idx,{"align":a,"offset":o}

def spec_memarg_inv(node):
  return spec_uN_inv(node["align"],32) + spec_uN_inv(node["offset"],32)

def spec_instr(raw,idx):
  if raw[idx] not in opcodes_binary2text:
    return idx, None #error
  instr_binary = raw[idx]
  instr_text = opcodes_binary2text[instr_binary]
  idx+=1
  if instr_text in {"block","loop","if"}:      #block, loop, if
    idx,rt=spec_blocktype(raw,idx)
    instar=[]
    if instr_text=="if":
      instar2=[]
      while raw[idx] not in {0x05,0x0b}:
        idx,ins=spec_instr(raw,idx)
        instar+=[ins]
      if raw[idx]==0x05: #if with else
        idx+=1
        while raw[idx] not in {0x0b}:
          idx,ins=spec_instr(raw,idx)
          instar2+=[ins]
        return idx+1, ["if",rt,instar,instar2] #+[("end",)]
      return idx+1, ["if",rt,instar] #+[("end",)]
    else: 
      while raw[idx]!=0x0b:
        idx,ins=spec_instr(raw,idx)
        instar+=[ins]
      return idx+1, [instr_text,rt,instar] #+[("end",)]
  elif instr_text in {"br","br_if"}:           # br, br_if
    idx,l = spec_labelidx(raw,idx)
    return idx, [instr_text,l]
  elif instr_text == "br_table":               # br_table
    idx,lstar=spec_vec(raw,idx,spec_labelidx)
    idx,lN=spec_labelidx(raw,idx)
    return idx, ["br_table",lstar,lN]
  elif instr_text in {"call","call_indirect"}: # call, call_indirect
    if instr_text=="call":
      idx,x=spec_funcidx(raw,idx)
    if instr_text=="call_indirect":
      idx,x=spec_typeidx(raw,idx)
      if raw[idx]!=0x00: return idx,None #error
      idx+=1
    return idx, [instr_text,x]
  elif 0x20<=instr_binary<=0x22:               # get_local, etc
    idx,x=spec_localidx(raw,idx)
    return idx, [instr_text,x]
  elif 0x23<=instr_binary<=0x24:               # get_global, etc
    idx,x=spec_globalidx(raw,idx)
    return idx, [instr_text,x]
  elif 0x28<=instr_binary<=0x3e:               # i32.load, i64.store, etc
    idx,m = spec_memarg(raw,idx)
    return idx, [instr_text,m]
  elif 0x3f<=instr_binary<=0x40:               # current_memory, grow_memory
    if raw[idx]!=0x00: return idx,None #error
    return idx+1, [instr_text,]
  elif 0x41<=instr_binary<=0x42:               # i32.const, etc
    n=0
    if instr_text=="i32.const":
      idx,n = spec_iN(raw,idx,32)
    if instr_text=="i64.const":
      idx,n = spec_iN(raw,idx,64)
    return idx, [instr_text,n]
  elif 0x43<=instr_binary<=0x44:               # f32.const, etc
    z=0
    if instr_text=="f32.const":
      idx,z = spec_fN(raw,idx,32)
    if instr_text=="f64.const":
      idx,z = spec_fN(raw,idx,64)
    return idx, [instr_text,z]
  else:
    #otherwise no immediate
    return idx, [instr_text,]


def spec_instr_inv(node):
  instr_bytes = bytearray()
  #print("spec_instr_inv(",node,")")
  if type(node[0])==str:
    instr_bytes+=bytearray([opcodes_text2binary[node[0]]])
  #the rest is for immediates
  if node[0] in {"block","loop"}:              #block, loop
    instr_bytes+=spec_blocktype_inv(node[1])
    instar_bytes=bytearray()
    for n in node[2]:
      instar_bytes+=spec_instr_inv(n)
    instar_bytes+=bytes([0x0b])
    instr_bytes+=instar_bytes
  elif node[0]=="if":                          #if
    instr_bytes+=spec_blocktype_inv(node[1])
    instar_bytes=bytearray()
    for n in node[2]:
      instar_bytes+=spec_instr_inv(n)
    if len(node)==4: #TODO: test this
      instar_bytes+=bytearray([0x05])
      for n in node[3]:
        instar_bytes+=spec_instr_inv(n)
    instar_bytes+=bytes([0x0b])
    instr_bytes+=instar_bytes
  elif node[0] in {"br","br_if"}:              #br, br_if
    instr_bytes+=spec_labelidx_inv(node[1])
  elif node[0] == "br_table":                   #br_table
    instr_bytes+=spec_vec_inv(node[1],spec_labelidx_inv)
    instr_bytes+=spec_labelidx_inv(node[2])
  elif node[0] == "call":                       #call
    instr_bytes+=spec_funcidx_inv(node[1])
  elif node[0] == "call_indirect":              #call_indirect
    instr_bytes+=spec_typeidx_inv(node[1])
    instr_bytes+=bytearray([0x00])
  elif 0x20<=opcodes_text2binary[node[0]]<=0x24:  #get_local, set_local, tee_local
    instr_bytes+=spec_localidx_inv(node[1])
  elif 0x20<=opcodes_text2binary[node[0]]<=0x24:  #get_global, set_global
    instr_bytes+=spec_globalidx_inv(node[1])
  elif 0x28<=opcodes_text2binary[node[0]]<=0x3e:  #i32.load, i32.load8_s, i64.store, etc
    instr_bytes+=spec_memarg_inv(node[1])
  elif 0x3f<=opcodes_text2binary[node[0]]<=0x40:  #memory.size, memory.grow
    instr_bytes+=bytearray([0x00])
  elif node[0]=="i32.const":                    #i32.const
    instr_bytes+=spec_iN_inv(node[1],32)
  elif node[0]=="i64.const":                    #i64.const
    instr_bytes+=spec_iN_inv(node[1],64)
  elif node[0]=="f32.const":                    #i64.const
    instr_bytes+=spec_fN_inv(node[1],32)
  elif node[0]=="f64.const":                    #i64.const
    instr_bytes+=spec_fN_inv(node[1],64)
  return instr_bytes



# 5.4.6 EXPRESSIONS

def spec_expr(raw,idx):
  instar = []
  while raw[idx] != 0x0b: 
    idx,ins = spec_instr(raw,idx)
    instar+=[ins]
  if raw[idx] != 0x0b: return idx,None #error
  return idx+1, instar #+[('end',)]

def spec_expr_inv(node):
  instar_bytes=bytearray()
  for n in node:
    instar_bytes+=spec_instr_inv(n)
  instar_bytes+=bytes([0x0b])
  return instar_bytes






#############
# 5.5 MODULES
#############

# 5.5.1 INDICES

def spec_typeidx(raw,idx):
  idx, x = spec_uN(raw,idx,32)
  return idx,x

def spec_typeidx_inv(node):
  return spec_uN_inv(node,32)

def spec_funcidx(raw,idx):
  idx,x = spec_uN(raw,idx,32)
  return idx,x

def spec_funcidx_inv(node):
  return spec_uN_inv(node,32)

def spec_tableidx(raw,idx):
  idx,x = spec_uN(raw,idx,32)
  return idx,x

def spec_tableidx_inv(node):
  return spec_uN_inv(node,32)

def spec_memidx(raw,idx):
  idx,x = spec_uN(raw,idx,32)
  return idx,x

def spec_memidx_inv(node):
  return spec_uN_inv(node,32)

def spec_globalidx(raw,idx):
  idx,x = spec_uN(raw,idx,32)
  return idx,x

def spec_globalidx_inv(node):
  return spec_uN_inv(node,32)

def spec_localidx(raw,idx):
  idx,x = spec_uN(raw,idx,32)
  return idx,x

def spec_localidx_inv(node):
  return spec_uN_inv(node,32)

def spec_labelidx(raw,idx):
  idx,l = spec_uN(raw,idx,32)
  return idx,l

def spec_labelidx_inv(node):
  return spec_uN_inv(node,32)



# 5.5.2 SECTIONS

def spec_sectionN(raw,idx,N,B,skip):
  if idx>=len(raw) or raw[idx]!=N:
    return idx, []  #skip since this sec not included
  idx+=1
  idx,size = spec_uN(raw,idx,32)
  if skip:
    return idx+size,[]
  if N!=8: #not start:
    return spec_vec(raw,idx,B)
  else:
    return B(raw,idx)

def spec_sectionN_inv(cont,Binv,N):
  if cont==None or cont==[]:
    return bytearray([])
  N_bytes=bytearray([N])
  cont_bytes=bytearray()
  if N==8: #startsec
    cont_bytes=Binv(cont)
  else:
    cont_bytes=spec_vec_inv(cont,Binv)
  size_bytes=spec_uN_inv(len(cont_bytes),32) 
  return N_bytes+size_bytes+cont_bytes


# 5.5.3 CUSTOM SECTION

def spec_customsec(raw,idx,skip=1):
  idx,size = spec_uN(raw,idx,32)
  endidx = idx+size
  #TODO: not a vec(), so should adjust sectionN()
  return endidx,None #return spec_sectionN(raw,idx,0,spec_custom,skip) 

def spec_custom(raw,idx):
  idx,name = spec_name(raw,idx)
  #TODO: what is stopping condition for bytestar?
  idx,bytestar = spec_byte(raw,idx)
  return name,bytestar

def spec_customsec_inv(node):
  return spec_sectionN_inv(node,spec_custom_inv)
  
def spec_custom_inv(node):
  return spec_name_inv(node[0]) + spec_byte_inv(node[1]) #TODO: check this


# 5.5.4 TYPE SECTION

def spec_typesec(raw,idx,skip=0):
  return spec_sectionN(raw,idx,1,spec_functype,skip)

def spec_typesec_inv(node):
  return spec_sectionN_inv(node,spec_functype_inv,1)


# 5.5.5 IMPORT SECTION

def spec_importsec(raw,idx,skip=0):
  return spec_sectionN(raw,idx,2,spec_import,skip)

def spec_import(raw,idx):
  idx,mod = spec_name(raw,idx)
  idx,nm = spec_name(raw,idx)
  idx,d = spec_importdesc(raw,idx)
  return idx,{"module":mod,"name":nm,"desc":d}

def spec_importdesc(raw,idx):
  if raw[idx]==0x00:
    idx,x=spec_typeidx(raw,idx+1)
    return idx,{"func":x}
  elif raw[idx]==0x01:
    idx,tt=spec_tabletype(raw,idx+1)
    return idx,{"table":tt}
  elif raw[idx]==0x02:
    idx,mt=spec_memtype(raw,idx+1)
    return idx,{"mem":mt}
  elif raw[idx]==0x03:
    idx,gt=spec_globaltype(raw,idx+1)
    return idx,{"global":gt}
  else:
    return idx,None #error

def spec_importsec_inv(node):
  return spec_sectionN_inv(node,spec_import_inv,2)

def spec_import_inv(node):
  return spec_name_inv(node["module"]) + spec_name_inv(node["name"]) + spec_importdesc_inv(node["desc"])

def spec_importdesc_inv(node):
  key=list(node.keys())[0]
  if key=="func":
    return bytearray([0x00]) + spec_typeidx_inv(node[key])
  elif key=="table":
    return bytearray([0x01]) + spec_tabletype_inv(node[key])
  elif key=="mem":
    return bytearray([0x02]) + spec_memtype_inv(node[key])
  elif key=="global":
    return bytearray([0x03]) + spec_globaltype_inv(node[key])
  else:
    return bytearray()
  

# 5.5.6 FUNCTION SECTION

def spec_funcsec(raw,idx,skip=0):
  return spec_sectionN(raw,idx,3,spec_typeidx,skip)

def spec_funcsec_inv(node):
  return spec_sectionN_inv(node,spec_typeidx_inv,3)


# 5.5.7 TABLE SECTION

def spec_tablesec(raw,idx,skip=0):
  return spec_sectionN(raw,idx,4,spec_table,skip)

def spec_table(raw,idx):
  idx,tt=spec_tabletype(raw,idx)
  return idx,{"type":tt}

def spec_tablesec_inv(node):
  return spec_sectionN_inv(node,spec_table_inv,4)
  
def spec_table_inv(node):
  return spec_tabletype_inv(node["type"])


# 5.5.8 MEMORY SECTION

def spec_memsec(raw,idx,skip=0):
  return spec_sectionN(raw,idx,5,spec_mem,skip)

def spec_mem(raw,idx):
  idx,mt = spec_memtype(raw,idx)
  return idx,{"type":mt}

def spec_memsec_inv(node):
  return spec_sectionN_inv(node,spec_mem_inv,5)
  
def spec_mem_inv(node):
  return spec_memtype_inv(node["type"])


# 5.5.9 GLOBAL SECTION

def spec_globalsec(raw,idx,skip=0):
  return spec_sectionN(raw,idx,6,spec_global,skip)

def spec_global(raw,idx):
  idx,gt=spec_globaltype(raw,idx)
  idx,e=spec_expr(raw,idx)
  return idx,{"type":gt,"init":e}

def spec_globalsec_inv(node):
  return spec_sectionN_inv(node,spec_global_inv,6)
  
def spec_global_inv(node):
  return spec_globaltype_inv(node["type"]) + spec_expr_inv(node["init"])


# 5.5.10 EXPORT SECTION

def spec_exportsec(raw,idx,skip=0):
  return spec_sectionN(raw,idx,7,spec_export,skip)

def spec_export(raw,idx):
  idx,nm = spec_name(raw,idx)
  idx,d = spec_exportdesc(raw,idx)
  return idx,{"name":nm,"desc":d}

def spec_exportdesc(raw,idx):
  if raw[idx]==0x00:
    idx,x=spec_funcidx(raw,idx+1)
    return idx,{"func":x}
  elif raw[idx]==0x01:
    idx,x=spec_tableidx(raw,idx+1)
    return idx,{"table":x}
  elif raw[idx]==0x02:
    idx,x=spec_memidx(raw,idx+1)
    return idx,{"mem":x}
  elif raw[idx]==0x03:
    idx,x=spec_globalidx(raw,idx+1)
    return idx,{"global":x}
  else:
    return idx,None #error

def spec_exportsec_inv(node):
  return spec_sectionN_inv(node,spec_export_inv,7)

def spec_export_inv(node):
  return spec_name_inv(node["name"]) + spec_exportdesc_inv(node["desc"])

def spec_exportdesc_inv(node):
  key=list(node.keys())[0]
  if key=="func":
    return bytearray([0x00]) + spec_funcidx_inv(node[key])
  elif key=="table":
    return bytearray([0x01]) + spec_tableidx_inv(node[key])
  elif key=="mem":
    return bytearray([0x02]) + spec_memidx_inv(node[key])
  elif key=="global":
    return bytearray([0x03]) + spec_globalidx_inv(node[key])
  else:
    return bytearray()


# 5.5.11 START SECTION

def spec_startsec(raw,idx,skip=0):
  #TODO: st has ?
  return spec_sectionN(raw,idx,8,spec_start,skip)

def spec_start(raw,idx):
  idx,x=spec_funcidx(raw,idx)
  return idx,{"func":x}

def spec_startsec_inv(node):
  if node==[]:
    return bytearray()
  else:
    return spec_sectionN_inv(node,spec_start_inv,8)

def spec_start_inv(node):
  key=list(node.keys())[0]
  if key=="func":
    return spec_funcidx_inv(node[key])
  else:
    return bytearray()


# 5.5.12 ELEMENT SECTION

def spec_elemsec(raw,idx,skip=0):
  #TODO: typo? on pg 97 seg doesnt have star
  return spec_sectionN(raw,idx,9,spec_elem,skip)

def spec_elem(raw,idx):
  idx,x=spec_tableidx(raw,idx)
  idx,e=spec_expr(raw,idx)
  idx,ystar=spec_vec(raw,idx,spec_funcidx)
  return idx,{"table":x,"offset":e,"init":ystar}

def spec_elemsec_inv(node):
  return spec_sectionN_inv(node,spec_elem_inv,9)
  
def spec_elem_inv(node):
  return spec_tableidx_inv(node["table"]) + spec_expr_inv(node["offset"]) + spec_vec_inv(node["init"],spec_funcidx_inv)


# 5.5.13 CODE SECTION

def spec_codesec(raw,idx,skip=0):
  return spec_sectionN(raw,idx,10,spec_code,skip)

def spec_code(raw,idx):
  idx,size=spec_uN(raw,idx,32)
  idx,code_=spec_func(raw,idx)
  #TODO: check whether size==|code|; note size is only useful for validation and skipping
  return idx,code_

def spec_func(raw,idx):
  idx,tstarstar=spec_vec(raw,idx,spec_locals)
  idx,e=spec_expr(raw,idx)
  #TODO: check |concat((t*)*)|<2^32?
  #TODO: typo: why is return e*?
  concattstarstar=[t for tstar in tstarstar for t in tstar] 
  #return idx, [tstarstar,e]  #not concatenating the t*'s makes it easier for printing
  return idx, [concattstarstar,e]

def spec_locals(raw,idx):
  idx,n=spec_uN(raw,idx,32)
  idx,t=spec_valtype(raw,idx)
  tn=[t]*n
  return idx,tn

# the following three functions do not parse the expression, just take its address and size
# this is useful for validation or execution using bytecode
def codesec_bytecode_address(raw,idx,skip=0):
  return spec_sectionN(raw,idx,10,code_bytecode_address,skip)

def code_bytecode_address(raw,idx):
  idx,size=spec_uN(raw,idx,32)
  idx,code_=func_bytecode_address(raw,idx)
  idx+=size
  #TODO: check whether size==|code|; note size is only useful for validation and skipping
  return idx, code_+(size,)

def func_bytecode_address(raw,idx):
  idx,tstarstar=spec_vec(raw,idx,spec_locals)
  e=idx
  #concattstarstar=[e for t in tstarstar for e in t] #note: I did not concatenate the t*'s, is makes it easier for printing
  return idx, (tstarstar,e)


def spec_codesec_inv(node):
  return spec_sectionN_inv(node,spec_code_inv,10)
  
def spec_code_inv(node):
  func_bytes = spec_func_inv(node)
  return spec_uN_inv(len(func_bytes),32) + func_bytes

def spec_func_inv(node):
  return spec_vec_inv(node[0],spec_locals_inv) + spec_expr_inv(node[1]) 

def spec_locals_inv(node):
  return spec_uN_inv(len(node),32) + (spec_valtype_inv(node[0]) if len(node)>0 else bytearray())
  

# 5.5.14 DATA SECTION

def spec_datasec(raw,idx,skip=0):
  #TODO: typo pg 99 seg doesnt have star
  return spec_sectionN(raw,idx,11,spec_data,skip)

def spec_data(raw,idx):
  idx,x=spec_memidx(raw,idx)
  idx,e=spec_expr(raw,idx)
  idx,bstar=spec_vec(raw,idx,spec_byte)
  return idx, {"data":x,"offset":e,"init":bstar}

def spec_datasec_inv(node):
  return spec_sectionN_inv(node,spec_data_inv,11)
  
def spec_data_inv(node):
  return spec_memidx_inv(node["data"]) + spec_expr_inv(node["offset"]) + spec_vec_inv(node["init"],spec_byte_inv)


# 5.5.15 MODULES

def spec_module(raw):
  idx=0
  magic=[0x00,0x61,0x73,0x6d]
  if magic!=[x for x in raw[idx:idx+4]]:
    return None
  idx+=4
  version=[0x01,0x00,0x00,0x00]
  if version!=[x for x in raw[idx:idx+4]]:
    return None
  idx+=4
  idx,functypestar=spec_typesec(raw,idx,0)
  idx,importstar=spec_importsec(raw,idx,0)
  idx,typeidxn=spec_funcsec(raw,idx,0)
  idx,tablestar=spec_tablesec(raw,idx,0)
  idx,memstar=spec_memsec(raw,idx,0)
  idx,globalstar=spec_globalsec(raw,idx,0)
  idx,exportstar=spec_exportsec(raw,idx,0)
  idx,startq=spec_startsec(raw,idx,0)
  idx,elemstar=spec_elemsec(raw,idx,0)
  idx,coden=spec_codesec(raw,idx,0)
  idx,datastar=spec_datasec(raw,idx,0)
  funcn=[]
  if typeidxn and coden and len(typeidxn)==len(coden):
    for i in range(len(typeidxn)):
      funcn+=[{"type":typeidxn[i], "locals":coden[i][0], "body":coden[i][1]}]
  mod = {"types":functypestar, "funcs":funcn, "tables":tablestar, "mems":memstar, "globals":globalstar, "elem": elemstar, "data":datastar, "start":startq, "imports":importstar, "exports":exportstar}
  return mod

def get_module_with_just_function_code_addresses(raw):
  idx=0
  magic=[0x00,0x61,0x73,0x6d]
  if magic!=[x for x in raw[idx:idx+4]]:
    return None
  idx+=4
  version=[0x01,0x00,0x00,0x00]
  if version!=[x for x in raw[idx:idx+4]]:
    return None
  idx+=4
  idx,functypestar=	spec_typesec(raw,idx,0)
  idx,importstar=	spec_importsec(raw,idx,0)
  idx,typeidxn=		spec_funcsec(raw,idx,0)
  idx,tablestar=	spec_tablesec(raw,idx,0)
  idx,memstar=		spec_memsec(raw,idx,0)
  idx,globalstar=	spec_globalsec(raw,idx,0)
  idx,exportstar=	spec_exportsec(raw,idx,0)
  idx,startq=		spec_startsec(raw,idx,0)
  idx,elemstar=		spec_elemsec(raw,idx,0)
  idx,coden=		codesec_address(raw,idx,0)
  idx,datastar=		spec_datasec(raw,idx,0)
  if not functypestar: return None
  if not importstar: return None
  if not typeidxn: return None
  if not tablestar: return None
  if not memstar: return None
  if not globalstar: return None
  if not exportstar: return None
  if not startq: return None
  if not elemstar: return None
  if not coden: return None
  if not datastar: return None
  if len(typeidxn)!=len(coden): return None
  #build module
  funcn=[]
  for i in range(len(typeidxn)):
    funcn+=[{"type":typeidxn[i], "locals":coden[i][0], "body":coden[i][1]}]
  mod = {"types":functypestar, "funcs":funcn, "tables":tablestar, "mems":memstar, "globals":globalstar, "elem": elemstar, "data":datastar, "start":startq, "imports":importstar, "exports":exportstar}
  return mod

def spec_module_inv_to_file(mod,filename):
  f = open(filename, 'wb')
  magic=bytes([0x00,0x61,0x73,0x6d])
  version=bytes([0x01,0x00,0x00,0x00])
  f.write(magic)
  f.write(version)
  f.write(spec_typesec_inv(mod["types"]))
  f.write(spec_importsec_inv(mod["imports"]))
  f.write(spec_funcsec_inv([e["type"] for e in mod["funcs"]]))
  f.write(spec_tablesec_inv(mod["tables"]))
  f.write(spec_memsec_inv(mod["mems"]))
  f.write(spec_globalsec_inv(mod["globals"]))
  f.write(spec_exportsec_inv(mod["exports"]))
  f.write(spec_startsec_inv(mod["start"]))
  f.write(spec_elemsec_inv(mod["elem"]))
  f.write(spec_codesec_inv([(f["locals"],f["body"]) for f in mod["funcs"]]))
  f.write(spec_datasec_inv(mod["data"]))
  f.close()


















##############
##############
# 7 APPENDIX #
##############
##############



##################################################
# RANDOM EMBEDDING STUFF THAT IS NOT IN THE SPEC #
##################################################

# SCAN OVER BINARY OPCODES AND THEIR IMMEDIATES, USEFUL FOR VALIDATION AND EXECUTION
# note: This code is not defined in the spec, but left to the embedding

def get_brtable_immediates(raw,idx):
  idx,lstar=spec_vec(raw,idx,spec_labelidx)
  idx,lN=spec_labelidx(raw,idx)
  return idx,(lstar,lN)

def get_callindirect_immediates(raw,idx):
  idx,x=spec_typeidx(raw,idx)
  if raw[idx] != 0x00:
    return idx,-1 #error
  idx+=1
  return idx,x

def get_const_immediate(raw,idx):
  if raw[idx] <=0x42:
    if opcode==0x41:			# i32.cosnt
      return spec_iN(raw,idx,32)
    else opcode==0x42:			# i64.const
      return spec_iN(raw,idx,64)
  elif opcode <=0x44:
    if opcode==0x43:			# f32.cosnt
      return spec_fN(raw,idx,32)
    else opcode==0x44:			# f64.const
      return spec_fN(raw,idx,64)
  else
    return idx,-1

# key-value pairs, each opcode with an immediate is pared with the function to get its immediate
opcodes_to_immediates = {
0x02:spec_blocktype,		# block blocktype
0x03:spec_blocktype,		# loop blocktype
0x04:spec_blocktype,		# if blocktype
0x0c:spec_labelidx,		# br labelidx
0x0d:spec_labelidx,		# br_if labelidx
0x0e:get_brtable_immeidates,	# br_table labelidxstar labelidx
0x10:spec_funcidx,		# call funcidx
0x11:get_callindirect_immediates,	# call_indirect typeidx 0x00

0x20:spec_localidx,		# get_local localidx
0x21:spec_localidx,		# set_local localidx
0x22:spec_localidx,		# tee_local localidx
0x23:spec_globalidx,		# get_global globalidx
0x24:spec_globalidx,		# set_global globalidx

0x28:spec_memarg,		# i32.load memarg
0x29:spec_memarg,		# i64.load memarg
0x2a:spec_memarg,		# f32.load memarg
0x2b:spec_memarg,		# f64.load memarg
0x2c:spec_memarg,		# i32.load8_s memarg
0x2d:spec_memarg,		# i32.load8_u memarg
0x2e:spec_memarg,		# i32.load16_s memarg
0x2f:spec_memarg,		# i32.load16_u memarg
0x30:spec_memarg,		# i64.load8_s memarg
0x31:spec_memarg,		# i64.load8_u memarg
0x32:spec_memarg,		# i64.load16_s memarg
0x33:spec_memarg,		# i64.load16_u memarg
0x34:spec_memarg,		# i64.load32_s memarg
0x35:spec_memarg,		# i64.load32_u memarg
0x36:spec_memarg,		# i32.store memarg
0x37:spec_memarg,		# i64.store memarg
0x38:spec_memarg,		# f32.store memarg
0x39:spec_memarg,		# f64.store memarg
0x3a:spec_memarg,		# i32.store8 memarg
0x3b:spec_memarg,		# i32.store16 memarg
0x3c:spec_memarg,		# i64.store8 memarg
0x3d:spec_memarg,		# i64.store16 memarg
0x3e:spec_memarg,		# i64.store32 memarg
0x3f:spec_memarg,		# memory.size memarg
0x40:spec_memarg,		# memory.grow memarg

0x41:get_const_immediate,	# i32.const i32
0x42:get_const_immediate,	# i64.const i64
0x43:get_const_immediate,	# f32.const f32
0x44:get_const_immediate	# f64.const f64
}

# sample code to iterate over raw binary form starting at an opcode, until reach end idx or end opcode
def iterate_over_instructions_until_endidx(raw,idx,endidx,endopcodes):
  while idx<endidx and raw[idx] not in endopcodes:
    opcode = raw[idx]
    if opcode not in opcodes_binary2text: return -1
    immediate=None
    if raw[idx] in opcodes_to_immediates:
      idx,immediate = opcodes_to_immediates[raw[idx]](raw,idx)
      if immediate == -1: return idx,-1
    # do stuff here
  return 0
  
# sample code to iterate over raw binary form starting at an opcode, until reach some end opcode
def iterate_over_instructions_until_endopcode(raw,idx,endopcodes):
  while raw[idx] not in endopcodes:
    opcode = raw[idx]
    if opcode not in opcodes_binary2text: return -1
    immediate=None
    if raw[idx] in opcodes_to_immediates:
      idx,immediate = opcodes_to_immediates[raw[idx]](raw,idx)
      if immediate == -1: return idx,-1
    # do stuff here
  return 0



##########################
# 7.3 VALIDATION ALGORITHM
##########################

# 7.3.1 DATA STRUCTURES

# This is a faster algorithm to validate a function body
# Conventions:
#   the spec makes opds and ctrls global variables, but we pass them as arguments
#   the control stack is a python list, which allows fast appending but not prepending. So the spec's index 0 corresponds to python list idx -1, and eg spec idx 3 corresponds to our python list idx -1-3 ie -4
#   the spec offers two ways to keep track of labels, using C.labels in ch 3 or a control stack in the appendix. Here we use the appendix method

def spec_push_opd(opds,type_):
  opds.append(type_)

def spec_pop_opd(opds,ctrls):
  #check if underflows current block, and returns one type
  #but if underflows and unreachable, which can happen if unconditional branch, when stack is typed polymorphically, operands are still pushed and popped to check if code after unreachable is valid, polymorphic stack can't underflow
  if len(opds) == ctrls[-1].height and ctrls[-1].unreachable:
    return "Unknown"
  if len(opds) == ctrls[-1].height:
    return -1 #error
  to_return = opds[-1]
  del opds[-1]
  return to_return

def spec_pop_opd_expect(opds,expect):
  actual = opds[-1]
  del opds[-1]
  # in case one is unknown, the more specific one is returned
  if actual == "Unknown":
    return expect
  if expect == "Unknown":
    return actual
  if actual != expect:
    return -1
  return actual

def spec_push_opds(opds,types):
  for t in types:
    spec_push_opd_expect(opds,t)

def spec_pop_opds_expect(types):
  for t in reversed(types):
    r = spec_pop_opd_expect(opds,opds,t)
    if r==-1: return -1
  return 0

def spec_ctrl_frame(label_types, end_types, height, unreachable):
  #args are:
  #   label_types: type of the branch's label, to type-check branches
  #   end_types: result type of the branch, currently Wasm spec allows at most one return value
  #   height: height of opd_stack at start of block, to check that operands do not underflow current block
  #   unreachable: whether remainder of block is unreachable, to handle stack-polymorphic typing after branches
  return {"label_types":label_types, "end_types":end_types, "height":height, "unreachable":unreachable}

def spec_push_ctrl(opds,ctrls,label,out):
  frame = {"label_types":label,"end_types":out,"height":opds.size(),"unreachable":False}
  ctrls.append(frame)

def spec_pop_ctrl(opds,ctrls,label,out):
  if len(ctrls)<1:
    return -1
  frame = ctrls[-1]
  del ctrls[-1]
  #verify opd stack has right types to exit block, and pops them
  spec_pop_opds(opds,frame["end_types"])
  #make shure stack is back to original height
  if len(opds) != frame["height"]
    return -1
  return frame["end_types"]

def spec_unreachable(opds, ctrls):
  # purge from operand stack, allows stack-polymorphic logic in pop_opd() take effect
  opds[ctrls[-1].height:]=[]  #TODO: check this
  ctrls[-1].unreachable = True



# 7.3.2 VALIDATION OF OPCODE SEQUENCES

# validate a single opcode based on current Context, operand stack, and control stack
def spec_validate_opcode(C,opds,ctrls,opcode,immediates):
  # C is the context
  # opds is the operand stack
  # ctrls is the control stack
  if 0x00<=opcode<=0x11:		# CONTROL INSTRUCTIONS
    if opcode==0x00:			# unreachable 
      spec_unreachable()
    elif opcode==0x01:			# nop
      pass
    elif opcode<=0x04:			# block, loop, if
      rt = immediates
      if opcode==0x02:			# block
        spec_push_ctrl(rt,rt)
      elif opcode==0x03:		# loop
        spec_push_ctrl(None,rt)
      else:				# if
        if spec_pop_opd_expect(opds,"i32") < 0: return -1
        spec_push_ctrl(rt,rt)
    elif opcode==0x05:			# else
      results = spec_pop_ctrl()
      if results==-1: return -1
      spec_push_ctrl(results)
    elif opcode==0x0b:			# end
      results = spec_pop_ctrl()
      if results==-1: return -1
      spec_push_opds(results)
    elif opcode==0x0c:			# br
      n = immediates
      if n==None: return -1
      if len(ctrls) < n: return -1
      if spec_pop_opd_expect(opds,"i32") < 0: return -1
      if spec_pop_opds(ctrls[-1-n].label_types) < 0: return -1
      spec_unreachable()
    elif opcode==0x0d:			# br_if
      l = immediates
      if l==None: return -1
      if len(ctrls) < l: return -1
      if spec_pop_opds(ctrls[-1-n].label_types) < 0: return -1
      spec_push_opds(ctrls[-1-n].label_types)
    elif opcode==0x0e:			# br_table
      nstar = immediates[0]
      m = immediates[1]
      if len(ctrls)<m: return -1
      for n in nstar:
        if len(ctrls)<n or ctrls[-1-n].label_types !=ctrls[-1-m].label_types: return -1
      if spec_pop_opd_expect(opds,"i32") == -1: return -1
      if spec_pop_opds(ctrls[-1-m].label_types) == -1: return -1
      unreachable()
    elif opcode==0x0f:			# return
      spec_unreachable()
    elif opcode==0x10:			# call
      x = immediates
      if (funcs not in C) or (x not in C.funcs): return -1
      if spec_pop_opds_expect(opds,revesred(C.funcs[x][0])) == -1: return -1
      spec_push_opds(opds,C.funcs[x][1]):
    elif opcode==0x11:			# call_indirect
      x = immediates
      if tables not in C or len(C.tables)==0: return -1
      if C.tables[0][1] != "anyfunc": return -1
      if x not in C.types: return -1
      if spec_pop_opds_expect(opds,revesred(C.types[x][0])) == -1: return -1
      spec_push_opds(opds,C.types[x][1]):
  elif 0x1a<=opcode<=0x1b:		# PARAMETRIC INSTRUCTIONS
    if opcode<=0x1a:			# drop
      if spec_pop_opd(opds,ctrls) == -1: return -1
    if opcode<=0x1b:			# select
      if spec_pop_opd_expect(opds,"i32") == -1: return -1
      t1 = spec_pop_opd(opds,ctrls)
      t2 = spec_pop_opd(opds,ctrls)
      if t1 != t2 or t1 == -1 or t2 == -1: return -1
      spec_push_opd(t1)
  elif 0x20<=opcode<=0x24:		# VARIABLE INSTRUCTIONS
    if opcode==0x20:			# get_local
      x = immediates
      if len(C.locals)<=x: return -1
      if C.locals[x]=="i32": spec_push_opd("i32")
      elif C.locals[x]=="i64": spec_push_opd("i64")
      elif C.locals[x]=="f32": spec_push_opd("f32")
      elif C.locals[x]=="f64": spec_push_opd("f64")
      else: return -1 
    if opcode==0x21:			# set_local
      x = immediates
      if len(C.locals)<=x: return -1
        if C.locals[x]=="i32": ret = spec_pop_opd_expect(opds,"i32")
        elif C.locals[x]=="i64": ret = spec_pop_opd_expect(opds,"i64")
        elif C.locals[x]=="f32": ret = spec_pop_opd_expect(opds,"f32")
        elif C.locals[x]=="f64": ret = spec_pop_opd_expect(opds,"f64")
        else: return -1
      if ret == -1: return -1
    if opcode==0x21:			# tee_local
      x = immediates
      if len(C.locals)<=x: return -1
      if C.locals[x]=="i32":
        if spec_pop_opd_expect(opds,"i32") == -1: return -1
        spec_push_opd("i32")
      elif C.locals[x]=="i64":
        if spec_pop_opd_expect(opds,"i64") == -1: return -1
        spec_push_opd("i64")
      elif C.locals[x]=="f32":
        if spec_pop_opd_expect(opds,"f32") == -1: return -1
        spec_push_opd("f32")
      elif C.locals[x]=="f64":
        if spec_pop_opd_expect(opds,"f64") == -1: return -1
        spec_push_opd("f64")
      else: return -1
    if opcode==0x22:		# get_global
      x = immediates
      if len(C.globals)<=x: return -1
        if C.globals[x]=="i32": spec_push_opd("i32")
        elif C.globals[x]=="i64": spec_push_opd("i64")
        elif C.globals[x]=="f32": spec_push_opd("f32")
        elif C.globals[x]=="f64": spec_push_opd("f64")
        else: return -1 
    if opcode==0x23:		# set_global
      x = immediates
      if len(C.globals)<=x: return -1
      if C.globals[x]=="i32": ret = spec_pop_opd_expect(opds,"i32")
      elif C.globals[x]=="i64": ret = spec_pop_opd_expect(opds,"i64")
      elif C.globals[x]=="f32": ret = spec_pop_opd_expect(opds,"f32")
      elif C.globals[x]=="f64": ret = spec_pop_opd_expect(opds,"f64")
      else: return -1
      if ret == -1: return -1
  elif 0x28<=opcode<=0x40:		# MEMORY INSTRUCTIONS
    if mem not in C or len(C.mems)==0: return -1
    if opcode<=0x35:
      memarg = immedaites
      if opcode==0x28:			# i32.load
        N=32, t="i32"
      elif opcode==0x29:		# i64.load
        N=64, t="i64"
      elif opcode==0x2a:		# f32.load
        N=32, t="f32"
      elif opcode==0x2b:		# f64.load
        N=64, t="f64"
      elif opcode <= 0x2d:		# i32.load8_s, i32.load8_u
        N=8, t="i32"
      elif opcode <= 0x2f:		# i32.load16_s, i32.load16_u
        N=16, t="i32"
      elif opcode <= 0x31:		# i64.load8_s, i64.load8_u
        N=8, t="i64"
      elif opcode <= 0x33:		# i64.load16_s, i64.load16_u
        N=16, t="i64"
      elif opcode <= 0x35:		# i64.load32_s, i64.load32_u
        N=32, t="i64"
      if 2**memarg.align>N//8: return -1
      if spec_pop_opd_expect(opds,"i32") == -1: return -1
      spec_push_opd(t)
    elif opcode<=0x3e:
      memarg = immedaites
      if opcode==0x36:			# i32.store
        N=32, t="i32"
      elif opcode==0x37:		# i64.store
        N=64, t="i64"
      elif opcode==0x38:		# f32.store
        N=32, t="f32"
      elif opcode==0x39:		# f64.store
        N=64, t="f64"
      elif opcode==0x3a:		# i32.store8
        N=8, t="i32"
      elif opcode==0x3b:		# i32.store16
        N=16, t="i32"
      elif opcode==0x3c:		# i64.store8
        N=8, t="i64"
      elif opcode==0x3d:		# i64.store16
        N=16, t="i64"
      elif opcode==0x3f:		# i64.store32
        N=32, t="i64"
      if 2**memarg.align>N//8: return -1
      if spec_pop_opd_expect(opds,t) == -1: return -1
      if spec_pop_opd_expect(opds,"i32") == -1: return -1
    elif opcode==0x3f:			# memory.size
      spec_push_opd("i32")
    elif opcode==0x40:			# memory.grow
      if spec_pop_opd_expect(opds,"i32") == -1: return -1
      spec_push_opd("i32")
  elif 0x41<=opcode<=0xbf:		# NUMERIC INSTRUCTIONS
    if opcode<=0x44:
      if opcode == 0x41:		# i32.const
        if spec_push_opd("i32") == -1: return -1
      elif opcode == 0x42:		# i64.const
        if spec_push_opd("i64") == -1: return -1
      elif opcode == 0x43:		# f32.const
        if spec_push_opd("f32") == -1: return -1
      else:				# f64.const
        if spec_push_opd("f64") == -1: return -1
    elif opcode<=0x4f:
      if opcode==0x45:			# i32.eqz
        ret = spec_pop_opd_expect(opds,"i32")
        if ret == -1: return -1
        spec_push_opd("i32") == -1
      else:				# i32.eq, i32.ne, i32.lt_s, i32.lt_u, i32.gt_s, i32.gt_u, i32.le_s, i32.le_u, i32.ge_s, i32.ge_u
        ret1 = spec_pop_opd_expect(opds,"i32")
        ret2 = spec_pop_opd_expect(opds,"i32")
        spec_push_opd("i32")
        if ret1 == -1 or ret2 == -1: return -1
      idx+=1
    elif opcode<=0x5a:
      if opcode==0x50:			# i64.eqz
        ret1 = spec_pop_opd_expect(opds,"i64")
        ret2 = spec_push_opd("i32")
        if ret1==-1 or ret2==-1: return -1
      else:				# i64.eq, i64.ne, i64.lt_s, i64.lt_u, i64.gt_s, i64.gt_u, i64.le_s, i64.le_u, i64.ge_s, i64.ge_u
        ret1 = spec_pop_opd_expect(opds,"i64")
        ret2 = spec_pop_opd_expect(opds,"i64")
        ret3 = spec_push_opd("i32")
        if ret1==-1 or ret2==-1 or ret3==-1: return -1
      idx+=1
    elif =opcode<=0x60:			# f32.eq, f32.ne, f32.lt, f32.gt, f32.le, f32.ge
      ret1 = spec_pop_opd_expect(opds,"f32")
      ret2 = spec_pop_opd_expect(opds,"f32")
      ret3 = spec_push_opd("i32")
      if ret1==-1 or ret2==-1 or ret3==-1: return -1
      idx+=1
    elif opcode<=0x66:			# f64.eq, f64.ne, f64.lt, f64.gt, f64.le, f64.ge
      idx+=1
      ret1 = spec_pop_opd_expect(opds,"i64")
      ret2 = spec_pop_opd_expect(opds,"i64")
      ret3 = spec_push_opd("i32")
      if ret1==-1 or ret2==-1 or ret3==-1: return -1
      idx+=1
    elif opcode<=0x78:
      if opcode<=0x69:			# i32.clz, i32.ctz, i32.popcnt
        ret1 = spec_pop_opd_expect(opds,"i32")
        ret2 = spec_push_opd("i32")
        if ret1==-1 or ret2==-1: return -1
      else:				# i32.add, i32.sub, i32.mul, i32.div_s, i32.div_u, i32.rem_s, i32.rem_u, i32.and, i32.or, i32.xor, i32.shl, i32.shr_s, i32.shr_u, i32.rotl, i32.rotr
        ret1 = spec_pop_opd_expect(opds,"i32")
        ret2 = spec_pop_opd_expect(opds,"i32")
        ret3 = spec_push_opd("i32")
        if ret1==-1 or ret2==-1 or ret3==-1: return -1
      idx+=1
    elif opcode<=0x8a:
      if opcode<=0x7b:			# i64.clz, i64.ctz, i64.popcnt
        ret1 = spec_pop_opd_expect(opds,"i64")
        ret2 = spec_push_opd("i64")
        if ret1==-1 or ret2==-1: return -1
      else:				# i64.add, i64.sub, i64.mul, i64.div_s, i64.div_u, i64.rem_s, i64.rem_u, i64.and, i64.or, i64.xor, i64.shl, i64.shr_s, i64.shr_u, i64.rotl, i64.rotr
        ret1 = spec_pop_opd_expect(opds,"i64")
        ret2 = spec_pop_opd_expect(opds,"i64")
        ret3 = spec_push_opd("i64")
        if ret1==-1 or ret2==-1 or ret3==-1: return -1
      idx+=1
    elif opcode<=0x98:
      if opcode<=9f:			# f32.abs, f32.neg, f32.ceil, f32.floor, f32.trunc, f32.nearest, f32.sqrt,
        ret1 = spec_pop_opd_expect(opds,"f32")
        ret2 = spec_push_opd("f32")
        if ret1==-1 or ret2==-1: return -1
      else:				# f32.add, f32.sub, f32.mul, f32.div, f32.min, f32.max, f32.copysign
        ret1 = spec_pop_opd_expect(opds,"f32")
        ret2 = spec_pop_opd_expect(opds,"f32")
        ret3 = spec_push_opd("f32")
        if ret1==-1 or ret2==-1 or ret3==-1: return -1
      idx+=1
    elif opcode<=0xa6:
      if opcode<=9f:			# f64.abs, f64.neg, f64.ceil, f64.floor, f64.trunc, f64.nearest, f64.sqrt,
        ret1 = spec_pop_opd_expect(opds,"f32")
        ret2 = spec_push_opd("f32")
        if ret1==-1 or ret2==-1: return -1
      else:				# f64.add, f64.sub, f64.mul, f64.div, f64.min, f64.max, f64.copysign
        ret1 = spec_pop_opd_expect(opds,"f32")
        ret2 = spec_pop_opd_expect(opds,"f32")
        ret3 = spec_push_opd("f32")
        if ret1==-1 or ret2==-1 or ret3==-1: return -1
      idx+=1
    elif opcode<=0xbf:
      if opcode==0xa7:			# i32.wrap/i64
        ret1 = spec_pop_opd_expect(opds,"i64")
        ret2 = spec_push_opd("i32")
        if ret1==-1 or ret2==-1: return -1
      elif opcode<=0xa9:		# i32.trunc_s/f32, i32.trunc_u/f32
        ret1 = spec_pop_opd_expect(opds,"f32")
        ret2 = spec_push_opd("i32")
        if ret1==-1 or ret2==-1: return -1
      elif opcode<=0xab:		# i32.trunc_s/f64, i32.trunc_u/f64
        ret1 = spec_pop_opd_expect(opds,"f64")
        ret2 = spec_push_opd("i32")
        if ret1==-1 or ret2==-1: return -1
      elif opcode<=0xad:		# i64.extend_s/i32, i64.extend_u/i32
        ret1 = spec_pop_opd_expect(opds,"i32")
        ret2 = spec_push_opd("i64")
        if ret1==-1 or ret2==-1: return -1
      elif opcode<=0xaf:		# i64.trunc_s/f32, i64.trunc_u/f32
        ret1 = spec_pop_opd_expect(opds,"f32")
        ret2 = spec_push_opd("i64")
        if ret1==-1 or ret2==-1: return -1
      elif opcode<=0xb1:		# i64.trunc_s/f64, i64.trunc_u/f64
        ret1 = spec_pop_opd_expect(opds,"f64")
        ret2 = spec_push_opd("i64")
        if ret1==-1 or ret2==-1: return -1
      elif opcode<=0xb3:		# f32.convert_s/i32, f32.convert_u/i32
        ret1 = spec_pop_opd_expect(opds,"i32")
        ret2 = spec_push_opd("f32")
        if ret1==-1 or ret2==-1: return -1
      elif opcode<=0xb6:		# f32.convert_s/i64, f32.convert_u/i64, f32.demote/f64
        ret1 = spec_pop_opd_expect(opds,"i64")
        ret2 = spec_push_opd("f32")
        if ret1==-1 or ret2==-1: return -1
      elif opcode<=0xb8:		# f64.convert_s/i32, f64.convert_u/i32
        ret1 = spec_pop_opd_expect(opds,"i32")
        ret2 = spec_push_opd("f64")
        if ret1==-1 or ret2==-1: return -1
      elif opcode<=0xba:		# f64.convert_s/i64, f64.convert_u/i64
        ret1 = spec_pop_opd_expect(opds,"i64")
        ret2 = spec_push_opd("f64")
        if ret1==-1 or ret2==-1: return -1
      elif opcode==0xbb:		# f64.promote/f32
        ret1 = spec_pop_opd_expect(opds,"f32")
        ret2 = spec_push_opd("f64")
        if ret1==-1 or ret2==-1: return -1
      elif opcode==0xbc:		# i32.reinterpret/f32
        ret1 = spec_pop_opd_expect(opds,"f64")
        ret2 = spec_push_opd("i32")
        if ret1==-1 or ret2==-1: return -1
      elif opcode==0xbd:		# i64.reinterpret/f64
        ret1 = spec_pop_opd_expect(opds,"f64")
        ret2 = spec_push_opd("i64")
        if ret1==-1 or ret2==-1: return -1
      elif opcode==0xbe:		# f32.reinterpret/i32
        ret1 = spec_pop_opd_expect(opds,"i32")
        ret2 = spec_push_opd("f32")
        if ret1==-1 or ret2==-1: return -1
      else:				# f64.reinterpret/i64
        ret1 = spec_pop_opd_expect(opds,"i64")
        ret2 = spec_push_opd("f64")
        if ret1==-1 or ret2==-1: return -1
      idx+=1
    else: return -1 #error, opcode not in the correct ranges
  return 0 #success, valid so far


#TODO: REVIEW THIS
def validate_instrstar_up_to_code_size(raw,idx,idx_end,C,opds,ctrls,idx_end):
  while idx < idx_end:
    # get opcode and immediate
    opcode = raw[idx]
    if opcode not in opcodes_binary2text: return idx,-1
    idx+=1
    immediates=None
    # validate individual opcode
    if raw[idx] in opcodes_to_immediates:
      idx,immediate = opcodes_to_immediates[opcode](raw,idx)
      if immediate == -1: return idx,-1
    idx,valid spec_validate(C,opds,ctrls,opcode,immediates)
    if valid == -1: return idx, -1
  return idx,0


#TODO: REVIEW THIS
def validate_expr(raw,idx,C):
  opds = []
  ctrls = C.labels
  while raw[idx] != 0x0b:
    idx,valid = validate_instr(raw,idx,C,opds,ctrls)
    if valid == -1: return idx,-1
  if raw[idx] != 0x0b: return idx,-1
  if len(opds)>1: return idx,-1
  return idx,opds










##########################
# TOOLS FOR PRINTING STUFF
##########################

def print_tree(node,indent=0):
  if type(node)==tuple:
    print(" "*indent+str(node))
  elif type(node) in {list}:
    for e in node:
      print_tree(e,indent+1)
  elif type(node)==dict:
    for e in node:
      print(" "*indent+e)
      print_tree(node[e],indent+1)
  else:
    print(" "*indent+str(node))


def print_tree_expr(node,indent=0):
  if type(node)==tuple:	# an instruction
    if len(node)>2:	# ie node[0] in {"block","if","loop"}:
      print(" "*indent+str((node[0],node[1])))
      print_tree_expr(node[2],indent+1)
      print(" "*indent+"(end)")
    else:
      print(" "*indent+str(node))
  elif type(node)==list:
    for e in node:
      print_tree_expr(e,indent+1)
  elif type(node)==dict:
    for e in node:
      print(" "*indent+e)
      print_tree_expr(node[e],indent+1)
  else:
    print(" "*indent+str(node))


def print_raw_as_hex(raw):
  print("printing whole module:")
  for i in range(len(raw)):
    print(hex(raw[i]),end=" ")
    if (i+1)%10==0:
      print()
  print()






def print_sections(mod):
  print("types:",mod["types"])
  print()
  print("funcs:",mod["funcs"])
  print()
  for f in mod["funcs"]:
    print(f)
    print()
  print("tables",mod["tables"])
  print()
  print("mems",mod["mems"])
  print()
  print("globals",mod["globals"])
  print()
  print("elem",mod["elem"])
  print()
  print("data",mod["data"])
  print()
  print("start",mod["start"])
  print()
  print("imports",mod["imports"])
  print()
  print("exports",mod["exports"])







#####################
# PYWEBASSEMBLY API #
#####################

def parse_wasm(filename):
  with open(filename, 'rb') as f:
    wasm = memoryview(f.read())
    mod = spec_module(wasm)
    #print_tree(mod)
    #print_sections(mod)
    #print_tree(mod["funcs"])
    #print_sections(mod)
    spec_module_inv_to_file(mod,filename.split('.')[0]+"_generated.wasm") 







if __name__ == "__main__":
  import sys
  if len(sys.argv)!=2:
    print("Argument should be <filename>.wasm")
  else:
    parse_wasm(sys.argv[1])
