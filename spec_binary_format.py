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

import spec_execution as execution

verbose = 0

###################
###################
# 5 BINARY FORMAT #
###################
###################

#Chapter 5 defines a binary syntax over the abstract syntax. The implementation is a recursive-descent parser which takes a `.wasm` file and builds an abstract syntax tree out of nested Python lists and dicts. Also implemented are inverses (up to a canonical form) which write an abstract syntax tree back to a `.wasm` file.

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
0x3c:'i64.store8',		# memarg
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
0xbf:'f64.reinterpret/i64'
}

# key-value pairs of text opcodes and their binary reperesentation
opcodes_text2binary = {}
for opcode in opcodes_binary2text:
  opcodes_text2binary[opcodes_binary2text[opcode]]=opcode


# 5.1.3 VECTORS

def spec_binary_vec(raw,idx,B):
  if verbose: print("spec_binary_vec(",idx,")")
  idx,n=spec_binary_uN(raw,idx,32)
  xn = []
  for i in range(n):
    idx,x = B(raw,idx)
    xn+=[x]
  return idx,xn

def spec_binary_vec_inv(mynode,myfunc):
  n_bytes=spec_binary_uN_inv(len(mynode),32) 
  xn_bytes=bytearray()
  for x in mynode:
    xn_bytes+=myfunc(x)
  return n_bytes+xn_bytes 


############
# 5.2 VALUES
############

# 5.2.1 BYTES

def spec_binary_byte(raw,idx):
  if verbose: print("spec_binary_byte(",idx,")")
  if len(raw)<=idx: raise Exception("malformed")
  return idx+1,raw[idx]

def spec_binary_byte_inv(node):
  return bytearray([node])

# 5.2.2 INTEGERS

#unsigned
def spec_binary_uN(raw,idx,N):
  if verbose: print("spec_binary_uN(",idx,N,")")
  idx,n=spec_binary_byte(raw,idx)
  if n<2**7 and n<2**N:
    return idx,n
  elif n>=2**7 and N>7:
    idx,m=spec_binary_uN(raw,idx,N-7)
    return idx, (2**7)*m+(n-2**7)
  else:
    raise Exception("malformed")

def spec_binary_uN_inv(k,N):
  #print("spec_binary_uN_inv(",k,N,")")
  if k<2**7 and k<2**N:
    return bytearray([k])
  elif k>=2**7 and N>7:
    return bytearray([k%(2**7)+2**7])+spec_binary_uN_inv(k//(2**7),N-7)
  else:
    raise Exception("malformed")

#signed
def spec_binary_sN(raw,idx,N):
  if verbose: print("spec_binary_sN(",idx,N,")")
  n=int(raw[idx])
  idx+=1
  if n<2**6 and n<2**(N-1):
    return idx,n
  elif 2**6<=n<2**7 and n>=2**7-2**(N-1):
    return idx,n-2**7
  elif n>=2**7 and N>7:
    idx,m=spec_binary_sN(raw,idx,N-7)
    return idx,2**7*m+(n-2**7)
  else:
    raise Exception("malformed")

def spec_binary_sN_inv(k,N):
  if 0<=k<2**6 and k<2**N:
    return bytearray([k])
  elif 2**6<=k+2**7<2**7: # and k+2**7>=2**7-2**(N-1):
    return bytearray([k+2**7])
  elif (k>=2**6 or k<2**6) and N>7: #(k<0 and k+2**7>=2**6)) and N>7:
    return bytearray([k%(2**7)+2**7])+spec_binary_sN_inv((k//(2**7)),N-7)
  else:
    raise Exception("malformed")

#uninterpretted integers
def spec_binary_iN(raw,idx,N):
  if verbose: print("spec_binary_iN(",idx,N,")")
  idx,n=spec_binary_sN(raw,idx,N)
  i = execution.spec_signediN_inv(N,n)
  #i = spec_signediN_inv(N,n)
  return idx, i

def spec_binary_iN_inv(i,N):
  return spec_binary_sN_inv(execution.spec_signediN(N,i),N)
  #return spec_binary_sN_inv(spec_signediN(N,i),N)



# 5.2.3 FLOATING-POINT

#fN::= b*:byte^{N/8} => bytes_{fN}^{-1}(b*)
def spec_binary_fN(raw,idx,N):
  if verbose: print("spec_binary_fN(",idx,N,")")
  bstar = bytearray([])
  for i in range(N//8):
    bstar+= bytearray([raw[idx]])
    idx+=1
  return idx, execution.spec_bytest_inv("f"+str(N),bstar) #bytearray(bstar)
  #return idx, spec_bytest_inv("f"+str(N),bstar) #bytearray(bstar)

def spec_binary_fN_inv(node,N):
  return execution.spec_bytest("f"+str(N),node)
  #return spec_bytest("f"+str(N),node)

  

# 5.2.4 NAMES

#name as UTF-8 codepoints
def spec_binary_name(raw,idx):
  if verbose: print("spec_binary_name(",idx,")")
  #print("spec_binary_name()")
  idx,bstar = spec_binary_vec(raw,idx,spec_binary_byte)
  #print("bstar",bstar)
  nametxt=""
  try:
    nametxt=bytearray(bstar).decode()
  except:
    raise Exception("malformed")
  return idx,nametxt
  #rest is unused, for finding inverse of utf8(name)=b*, keep since want to correct spec doc
  bstaridx=0
  lenbstar = len(bstar)
  name=[]
  while bstaridx<lenbstar:
    if bstaridx>=len(bstar): raise Exception("malformed")
    b1=bstar[bstaridx]
    bstaridx+=1
    if b1<0x80:
      name+=[b1]
      continue
    if bstaridx>=len(bstar): raise Exception("malformed")
    b2=bstar[bstaridx]
    if b2>>6 != 0b01: raise Exception("malformed")
    bstaridx+=1
    c=(2**6)*(b1-0xc0) + (b2-0x80)
    #c_check = 2**6*(b1-192) + (b2-128)
    if 0x80<=c<0x800:
      name+=[c]
      continue
    if bstaridx>=len(bstar): raise Exception("malformed")
    b3=bstar[bstaridx]
    if b2>>5 != 0b011: raise Exception("malformed")
    bstaridx+=1
    c=(2**12)*(b1-0xe0) + (2**6)*(b2-0x80) + (b3-0x80)
    if 0x800<=c<0x10000 and (b2>>6 == 0b01):
      name+=[c]
      continue
    if bstaridx>=len(bstar):raise Exception("malformed")
    b4=bstar[bstaridx]
    if b2>>4 != 0b0111: raise Exception("malformed")
    bstaridx+=1
    c=2**18*(b1-0xf0) + 2**12*(b2-0x80) + 2**6*(b3-0x80) + (b4-0x80)
    if 0x10000<=c<0x110000:
      name+=[c]
    else:
      #print("malformed character")
      raise Exception("malformed")
  #convert each codepoint to utf8 character
  #print("utf8 name",name, len(name), name=="")
  nametxt = ""
  for c in name:
    #print(str(chr(c)))
    #print(c)
    nametxt+=chr(c)
  #print("utf8 nametext",nametxt, len(nametxt), nametxt=="")
  return idx,nametxt

def spec_binary_name_inv(chars):
  name_bytes=bytearray()
  for c in chars:
    c = ord(c)
    if c<0x80:
      name_bytes += bytes([c])
    elif 0x80<=c<0x800:
      name_bytes += bytes([(c>>6)+0xc0,(c&0b111111)+0x80])
    elif 0x800<=c<0x10000:
      name_bytes += bytes([(c>>12)+0xe0,((c>>6)&0b111111)+0x80,(c&0b111111)+0x80])
    elif 0x10000<=c<0x110000:
      name_bytes += bytes([(c>>18)+0xf0,((c>>12)&0b111111)+0x80,((c>>6)&0b111111)+0x80,(c&0b111111)+0x80])
    else:
      return None #error
  return bytearray([len(name_bytes)])+name_bytes


###########
# 5.3 TYPES
###########

# 5.3.1 VALUE TYPES

valtype2bin={"i32":0x7f,"i64":0x7e,"f32":0x7d,"f64":0x7c}
bin2valtype={val:key for key,val in valtype2bin.items()}

def spec_binary_valtype(raw,idx):
  if verbose: print("spec_binary_valtype(",idx,")")
  if idx>=len(raw): raise Exception("malformed")
  if raw[idx] in bin2valtype:
    return idx+1,bin2valtype[raw[idx]]
  else:
    raise Exception("malformed")

def spec_binary_valtype_inv(node):
  #print("spec_binary_valtype_inv(",node,")")
  if node in valtype2bin:
    return bytearray([valtype2bin[node]])
  else:
    return bytearray([]) #error

# 5.3.2 RESULT TYPES

def spec_binary_blocktype(raw,idx):
  if verbose: print("spec_binary_blocktype(",idx,")")
  if raw[idx]==0x40:
    return idx+1,[]
  idx,t=spec_binary_valtype(raw,idx)
  return idx, t

def spec_binary_blocktype_inv(node):
  #print("spec_binary_blocktype_inv(",node,")")
  if node==[]:
    return bytearray([0x40])
  else:
    return spec_binary_valtype_inv(node)


# 5.3.3 FUNCTION TYPES

def spec_binary_functype(raw,idx):
  if verbose: print("spec_binary_functype(",idx,")")
  if raw[idx]!=0x60: raise Exception("malformed")
  idx+=1
  idx,t1star=spec_binary_vec(raw,idx,spec_binary_valtype)
  idx,t2star=spec_binary_vec(raw,idx,spec_binary_valtype)
  return idx,[t1star,t2star]

def spec_binary_functype_inv(node):
  return bytearray([0x60])+spec_binary_vec_inv(node[0],spec_binary_valtype_inv)+spec_binary_vec_inv(node[1],spec_binary_valtype_inv)


# 5.3.4 LIMITS

def spec_binary_limits(raw,idx):
  if verbose: print("spec_binary_limits(",idx,")")
  if raw[idx]==0x00:
    idx,n = spec_binary_uN(raw,idx+1,32)
    return idx,{"min":n,"max":None}
  elif raw[idx]==0x01:
    idx,n = spec_binary_uN(raw,idx+1,32)
    idx,m = spec_binary_uN(raw,idx,32)
    return idx,{"min":n,"max":m}
  else:
    return idx,None #error
    
def spec_binary_limits_inv(node):
  if node["max"]==None:
    return bytearray([0x00])+spec_binary_uN_inv(node["min"],32)
  else:
    return bytearray([0x01])+spec_binary_uN_inv(node["min"],32)+spec_binary_uN_inv(node["max"],32)

  
# 5.3.5 MEMORY TYPES

def spec_binary_memtype(raw,idx):
  if verbose: print("spec_binary_memtype(",idx,")")
  return spec_binary_limits(raw,idx)

def spec_binary_memtype_inv(node):
  return spec_binary_limits_inv(node)


# 5.3.6 TABLE TYPES

def spec_binary_tabletype(raw,idx):
  if verbose: print("spec_binary_tabletype(",idx,")")
  idx,et = spec_binary_elemtype(raw,idx)
  idx,lim = spec_binary_limits(raw,idx)
  return idx,[lim,et]

def spec_binary_elemtype(raw,idx):
  if verbose: print("spec_binary_elemtype(",idx,")")
  if raw[idx]==0x70:
    return idx+1,"anyfunc"
  else:
    raise Exception("malformed")

def spec_binary_tabletype_inv(node):
  return spec_binary_elemtype_inv(node[1])+spec_binary_limits_inv(node[0])

def spec_binary_elemtype_inv(node):
  return bytearray([0x70])


# 5.3.7 GLOBAL TYPES

def spec_binary_globaltype(raw,idx):
  if verbose: print("spec_binary_globaltype(",idx,")")
  idx,t = spec_binary_valtype(raw,idx)
  idx,m = spec_binary_mut(raw,idx)
  return idx,[m,t]

def spec_binary_mut(raw,idx):
  if verbose: print("spec_binary_mut(",idx,")")
  if raw[idx]==0x00:
    return idx+1,"const"
  elif raw[idx]==0x01:
    return idx+1,"var"
  else:
    raise Exception("malformed")

def spec_binary_globaltype_inv(node):
  return spec_binary_valtype_inv(node[1])+spec_binary_mut_inv(node[0])

def spec_binary_mut_inv(node):
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

def spec_binary_memarg(raw,idx):
  if verbose: print("spec_binary_memarg(",idx,")")
  idx,a=spec_binary_uN(raw,idx,32)
  idx,o=spec_binary_uN(raw,idx,32)
  return idx,{"align":a,"offset":o}

def spec_binary_memarg_inv(node):
  return spec_binary_uN_inv(node["align"],32) + spec_binary_uN_inv(node["offset"],32)

def spec_binary_instr(raw,idx):
  if verbose: print("spec_binary_instr(",idx,")")
  if raw[idx] not in opcodes_binary2text:
    return idx, None #error
  instr_binary = raw[idx]
  instr_text = opcodes_binary2text[instr_binary]
  idx+=1
  if instr_text in {"block","loop","if"}:      #block, loop, if
    idx,rt=spec_binary_blocktype(raw,idx)
    instar=[]
    if instr_text=="if":
      instar2=[]
      while raw[idx] not in {0x05,0x0b}:
        idx,ins=spec_binary_instr(raw,idx)
        instar+=[ins]
      if raw[idx]==0x05: #if with else
        idx+=1
        while raw[idx] != 0x0b:
          idx,ins=spec_binary_instr(raw,idx)
          instar2+=[ins]
        #return idx+1, ["if",rt,instar+[["else"]],instar2+[["end"]]] #+[["end"]]
      return idx+1, ["if",rt,instar+[["else"]],instar2+[["end"]]] #+[["end"]]
      #return idx+1, ["if",rt,instar+[["end"]]] #+[["end"]]
    else: 
      while raw[idx]!=0x0b:
        idx,ins=spec_binary_instr(raw,idx)
        instar+=[ins]
      return idx+1, [instr_text,rt,instar+[["end"]]] #+[["end"]]
  elif instr_text in {"br","br_if"}:           # br, br_if
    idx,l = spec_binary_labelidx(raw,idx)
    return idx, [instr_text,l]
  elif instr_text == "br_table":               # br_table
    idx,lstar=spec_binary_vec(raw,idx,spec_binary_labelidx)
    idx,lN=spec_binary_labelidx(raw,idx)
    return idx, ["br_table",lstar,lN]
  elif instr_text in {"call","call_indirect"}: # call, call_indirect
    if instr_text=="call":
      idx,x=spec_binary_funcidx(raw,idx)
    if instr_text=="call_indirect":
      idx,x=spec_binary_typeidx(raw,idx)
      if raw[idx]!=0x00: raise Exception("malformed")
      idx+=1
    return idx, [instr_text,x]
  elif 0x20<=instr_binary<=0x22:               # get_local, etc
    idx,x=spec_binary_localidx(raw,idx)
    return idx, [instr_text,x]
  elif 0x23<=instr_binary<=0x24:               # get_global, etc
    idx,x=spec_binary_globalidx(raw,idx)
    return idx, [instr_text,x]
  elif 0x28<=instr_binary<=0x3e:               # i32.load, i64.store, etc
    idx,m = spec_binary_memarg(raw,idx)
    return idx, [instr_text,m]
  elif 0x3f<=instr_binary<=0x40:               # current_memory, grow_memory
    if raw[idx]!=0x00: raise Exception("malformed")
    return idx+1, [instr_text,]
  elif 0x41<=instr_binary<=0x42:               # i32.const, etc
    n=0
    if instr_text=="i32.const":
      idx,n = spec_binary_iN(raw,idx,32)
    if instr_text=="i64.const":
      idx,n = spec_binary_iN(raw,idx,64)
    return idx, [instr_text,n]
  elif 0x43<=instr_binary<=0x44:               # f32.const, etc
    z=0
    if instr_text=="f32.const":
      if len(raw)<=idx+4: raise Exception("malformed")
      idx,z = spec_binary_fN(raw,idx,32)
    if instr_text=="f64.const":
      if len(raw)<=idx+8: raise Exception("malformed")
      idx,z = spec_binary_fN(raw,idx,64)
    return idx, [instr_text,z]
  else:
    #otherwise no immediate
    return idx, [instr_text,]


def spec_binary_instr_inv(node):
  instr_bytes = bytearray()
  #print("spec_binary_instr_inv(",node,")")
  if type(node[0])==str:
    instr_bytes+=bytearray([opcodes_text2binary[node[0]]])
  #the rest is for immediates
  if node[0] in {"block","loop","if"}:         #block, loop, if
    instr_bytes+=spec_binary_blocktype_inv(node[1])
    instar_bytes=bytearray()
    for n in node[2][:-1]:
      instar_bytes+=spec_binary_instr_inv(n)
    if len(node)==4: #if with else
      instar_bytes+=bytearray([0x05])
      for n in node[3][:-1]:
        instar_bytes+=spec_binary_instr_inv(n)
    instar_bytes+=bytes([0x0b])
    instr_bytes+=instar_bytes
  elif node[0] in {"br","br_if"}:              #br, br_if
    instr_bytes+=spec_binary_labelidx_inv(node[1])
  elif node[0] == "br_table":                   #br_table
    instr_bytes+=spec_binary_vec_inv(node[1],spec_binary_labelidx_inv)
    instr_bytes+=spec_binary_labelidx_inv(node[2])
  elif node[0] == "call":                       #call
    instr_bytes+=spec_binary_funcidx_inv(node[1])
  elif node[0] == "call_indirect":              #call_indirect
    instr_bytes+=spec_binary_typeidx_inv(node[1])
    instr_bytes+=bytearray([0x00])
  elif 0x20<=opcodes_text2binary[node[0]]<=0x24:  #get_local, set_local, tee_local
    instr_bytes+=spec_binary_localidx_inv(node[1])
  elif 0x20<=opcodes_text2binary[node[0]]<=0x24:  #get_global, set_global
    instr_bytes+=spec_binary_globalidx_inv(node[1])
  elif 0x28<=opcodes_text2binary[node[0]]<=0x3e:  #i32.load, i32.load8_s, i64.store, etc
    instr_bytes+=spec_binary_memarg_inv(node[1])
  elif 0x3f<=opcodes_text2binary[node[0]]<=0x40:  #memory.size, memory.grow
    instr_bytes+=bytearray([0x00])
  elif node[0]=="i32.const":                    #i32.const
    instr_bytes+=spec_binary_iN_inv(node[1],32)
  elif node[0]=="i64.const":                    #i64.const
    instr_bytes+=spec_binary_iN_inv(node[1],64)
  elif node[0]=="f32.const":                    #i64.const
    instr_bytes+=spec_binary_fN_inv(node[1],32)
  elif node[0]=="f64.const":                    #i64.const
    instr_bytes+=spec_binary_fN_inv(node[1],64)
  return instr_bytes



# 5.4.6 EXPRESSIONS

def spec_binary_expr(raw,idx):
  if verbose: print("spec_binary_expr(",idx,")")
  instar = []
  while raw[idx] != 0x0b:
    idx,ins = spec_binary_instr(raw,idx)
    instar+=[ins]
  if raw[idx] != 0x0b: return idx,None #error
  return idx+1, instar +[['end']]

def spec_binary_expr_inv(node):
  instar_bytes=bytearray()
  for n in node:
    instar_bytes+=spec_binary_instr_inv(n)
  #instar_bytes+=bytes([0x0b])
  return instar_bytes






#############
# 5.5 MODULES
#############

# 5.5.1 INDICES

def spec_binary_typeidx(raw,idx):
  if verbose: print("spec_binary_typeidx(",idx,")")
  idx, x = spec_binary_uN(raw,idx,32)
  return idx,x

def spec_binary_typeidx_inv(node):
  return spec_binary_uN_inv(node,32)

def spec_binary_funcidx(raw,idx):
  if verbose: print("spec_binary_funcidx(",idx,")")
  idx,x = spec_binary_uN(raw,idx,32)
  return idx,x

def spec_binary_funcidx_inv(node):
  return spec_binary_uN_inv(node,32)

def spec_binary_tableidx(raw,idx):
  if verbose: print("spec_binary_tableidx(",idx,")")
  idx,x = spec_binary_uN(raw,idx,32)
  return idx,x

def spec_binary_tableidx_inv(node):
  return spec_binary_uN_inv(node,32)

def spec_binary_memidx(raw,idx):
  if verbose: print("spec_binary_memidx(",idx,")")
  idx,x = spec_binary_uN(raw,idx,32)
  return idx,x

def spec_binary_memidx_inv(node):
  return spec_binary_uN_inv(node,32)

def spec_binary_globalidx(raw,idx):
  if verbose: print("spec_binary_globalidx(",idx,")")
  idx,x = spec_binary_uN(raw,idx,32)
  return idx,x

def spec_binary_globalidx_inv(node):
  return spec_binary_uN_inv(node,32)

def spec_binary_localidx(raw,idx):
  if verbose: print("spec_binary_localidx(",idx,")")
  idx,x = spec_binary_uN(raw,idx,32)
  return idx,x

def spec_binary_localidx_inv(node):
  return spec_binary_uN_inv(node,32)

def spec_binary_labelidx(raw,idx):
  if verbose: print("spec_binary_labelidx(",idx,")")
  idx,l = spec_binary_uN(raw,idx,32)
  return idx,l

def spec_binary_labelidx_inv(node):
  return spec_binary_uN_inv(node,32)


# 5.5.2 SECTIONS

def spec_binary_sectionN(raw,idx,N,B,skip):
  if verbose: print("spec_binary_sectionN(",idx,")")
  if idx>=len(raw):
    return idx,[] #already at end
  if raw[idx]!=N:
    return idx, []  #this sec not included
  idx+=1
  idx,size = spec_binary_uN(raw,idx,32)
  idx_plus_size = idx+size
  if skip:
    return idx+size,[]
  if N==0: # custom section
    idx, ret = B(raw,idx,idx+size)
  elif N==8: # start section
    idx, ret = B(raw,idx)
  else:
    idx,ret = spec_binary_vec(raw,idx,B)
  if idx != idx_plus_size: raise Exception("malformed")
  return idx,ret

def spec_binary_sectionN_inv(cont,Binv,N):
  if cont==None or cont==[]:
    return bytearray([])
  N_bytes=bytearray([N])
  cont_bytes=bytearray()
  if N==8: #startsec
    cont_bytes=Binv(cont)
  else:
    cont_bytes=spec_binary_vec_inv(cont,Binv)
  size_bytes=spec_binary_uN_inv(len(cont_bytes),32) 
  return N_bytes+size_bytes+cont_bytes


# 5.5.3 CUSTOM SECTION

def spec_binary_customsec(raw,idx,skip):
  if verbose: print("spec_binary_customsec(",idx,")")
  customsecstar = []
  idx,customsec = spec_binary_sectionN(raw,idx,0,spec_binary_custom,skip) 
  return idx,customsec

def spec_binary_custom(raw,idx,endidx):
  if verbose: print("spec_binary_custom(",idx,")")
  bytestar=bytearray()
  idx,name = spec_binary_name(raw,idx)
  while idx<endidx:
    idx,byte = spec_binary_byte(raw,idx)
    bytestar+=bytearray([byte])
    if idx!=endidx:
      idx+=1
  return idx,[name,bytestar]

def spec_binary_customsec_inv(node):
  return spec_binary_sectionN_inv(node,spec_binary_custom_inv)
  
def spec_binary_custom_inv(node):
  return spec_binary_name_inv(node[0]) + spec_binary_byte_inv(node[1]) #check this


# 5.5.4 TYPE SECTION

def spec_binary_typesec(raw,idx,skip=0):
  if verbose: print("spec_binary_typesec(",idx,")")
  return spec_binary_sectionN(raw,idx,1,spec_binary_functype,skip)

def spec_binary_typesec_inv(node):
  #print("spec_binary_typesec_inv(",node,")")
  return spec_binary_sectionN_inv(node,spec_binary_functype_inv,1)


# 5.5.5 IMPORT SECTION

def spec_binary_importsec(raw,idx,skip=0):
  if verbose: print("spec_binary_importsec(",idx,")")
  return spec_binary_sectionN(raw,idx,2,spec_binary_import,skip)

def spec_binary_import(raw,idx):
  if verbose: print("spec_binary_import(",idx,")")
  idx,mod = spec_binary_name(raw,idx)
  idx,nm = spec_binary_name(raw,idx)
  idx,d = spec_binary_importdesc(raw,idx)
  return idx,{"module":mod,"name":nm,"desc":d}

def spec_binary_importdesc(raw,idx):
  if verbose: print("spec_binary_importdesc(",idx,")")
  if raw[idx]==0x00:
    idx,x=spec_binary_typeidx(raw,idx+1)
    return idx,["func",x]
  elif raw[idx]==0x01:
    idx,tt=spec_binary_tabletype(raw,idx+1)
    return idx,["table",tt]
  elif raw[idx]==0x02:
    idx,mt=spec_binary_memtype(raw,idx+1)
    return idx,["mem",mt]
  elif raw[idx]==0x03:
    idx,gt=spec_binary_globaltype(raw,idx+1)
    return idx,["global",gt]
  else:
    return idx,None #error

def spec_binary_importsec_inv(node):
  return spec_binary_sectionN_inv(node,spec_binary_import_inv,2)

def spec_binary_import_inv(node):
  return spec_binary_name_inv(node["module"]) + spec_binary_name_inv(node["name"]) + spec_binary_importdesc_inv(node["desc"])

def spec_binary_importdesc_inv(node):
  key=node[0]
  if key=="func":
    return bytearray([0x00]) + spec_binary_typeidx_inv(node[1])
  elif key=="table":
    return bytearray([0x01]) + spec_binary_tabletype_inv(node[1])
  elif key=="mem":
    return bytearray([0x02]) + spec_binary_memtype_inv(node[1])
  elif key=="global":
    return bytearray([0x03]) + spec_binary_globaltype_inv(node[1])
  else:
    return bytearray()
  

# 5.5.6 FUNCTION SECTION

def spec_binary_funcsec(raw,idx,skip=0):
  if verbose: print("spec_binary_funcsec(",idx,")")
  return spec_binary_sectionN(raw,idx,3,spec_binary_typeidx,skip)

def spec_binary_funcsec_inv(node):
  return spec_binary_sectionN_inv(node,spec_binary_typeidx_inv,3)


# 5.5.7 TABLE SECTION

def spec_binary_tablesec(raw,idx,skip=0):
  if verbose: print("spec_binary_tablesec(",idx,")")
  return spec_binary_sectionN(raw,idx,4,spec_binary_table,skip)

def spec_binary_table(raw,idx):
  if verbose: print("spec_binary_table(",idx,")")
  idx,tt=spec_binary_tabletype(raw,idx)
  return idx,{"type":tt}

def spec_binary_tablesec_inv(node):
  return spec_binary_sectionN_inv(node,spec_binary_table_inv,4)
  
def spec_binary_table_inv(node):
  return spec_binary_tabletype_inv(node["type"])


# 5.5.8 MEMORY SECTION

def spec_binary_memsec(raw,idx,skip=0):
  if verbose: print("spec_binary_memsec(",idx,")")
  return spec_binary_sectionN(raw,idx,5,spec_binary_mem,skip)

def spec_binary_mem(raw,idx):
  if verbose: print("spec_binary_mem(",idx,")")
  idx,mt = spec_binary_memtype(raw,idx)
  return idx,{"type":mt}

def spec_binary_memsec_inv(node):
  return spec_binary_sectionN_inv(node,spec_binary_mem_inv,5)
  
def spec_binary_mem_inv(node):
  return spec_binary_memtype_inv(node["type"])


# 5.5.9 GLOBAL SECTION

def spec_binary_globalsec(raw,idx,skip=0):
  if verbose: print("spec_binary_globalsec(",idx,")")
  return spec_binary_sectionN(raw,idx,6,spec_binary_global,skip)

def spec_binary_global(raw,idx):
  if verbose: print("spec_binary_global(",idx,")")
  idx,gt=spec_binary_globaltype(raw,idx)
  idx,e=spec_binary_expr(raw,idx)
  return idx,{"type":gt,"init":e}

def spec_binary_globalsec_inv(node):
  return spec_binary_sectionN_inv(node,spec_binary_global_inv,6)
  
def spec_binary_global_inv(node):
  return spec_binary_globaltype_inv(node["type"]) + spec_binary_expr_inv(node["init"])


# 5.5.10 EXPORT SECTION

def spec_binary_exportsec(raw,idx,skip=0):
  if verbose: print("spec_binary_exportsec(",idx,")")
  return spec_binary_sectionN(raw,idx,7,spec_binary_export,skip)

def spec_binary_export(raw,idx):
  if verbose: print("spec_binary_export(",idx,")")
  idx,nm = spec_binary_name(raw,idx)
  #print("nm",nm)
  idx,d = spec_binary_exportdesc(raw,idx)
  #print("d",d)
  return idx,{"name":nm,"desc":d}

def spec_binary_exportdesc(raw,idx):
  if verbose: print("spec_binary_exportdesc(",idx,")")
  if raw[idx]==0x00:
    idx,x=spec_binary_funcidx(raw,idx+1)
    return idx,["func",x]
  elif raw[idx]==0x01:
    idx,x=spec_binary_tableidx(raw,idx+1)
    return idx,["table",x]
  elif raw[idx]==0x02:
    idx,x=spec_binary_memidx(raw,idx+1)
    return idx,["mem",x]
  elif raw[idx]==0x03:
    idx,x=spec_binary_globalidx(raw,idx+1)
    return idx,["global",x]
  else:
    return idx,None #error

def spec_binary_exportsec_inv(node):
  return spec_binary_sectionN_inv(node,spec_binary_export_inv,7)

def spec_binary_export_inv(node):
  return spec_binary_name_inv(node["name"]) + spec_binary_exportdesc_inv(node["desc"])

def spec_binary_exportdesc_inv(node):
  key=node[0]
  if key=="func":
    return bytearray([0x00]) + spec_binary_funcidx_inv(node[1])
  elif key=="table":
    return bytearray([0x01]) + spec_binary_tableidx_inv(node[1])
  elif key=="mem":
    return bytearray([0x02]) + spec_binary_memidx_inv(node[1])
  elif key=="global":
    return bytearray([0x03]) + spec_binary_globalidx_inv(node[1])
  else:
    return bytearray()


# 5.5.11 START SECTION

def spec_binary_startsec(raw,idx,skip=0):
  if verbose: print("spec_binary_startsec(",idx,")")
  return spec_binary_sectionN(raw,idx,8,spec_binary_start,skip)

def spec_binary_start(raw,idx):
  if verbose: print("spec_binary_start(",idx,")")
  idx,x=spec_binary_funcidx(raw,idx)
  return idx,{"func":x}

def spec_binary_startsec_inv(node):
  if node==[]:
    return bytearray()
  else:
    return spec_binary_sectionN_inv(node,spec_binary_start_inv,8)

def spec_binary_start_inv(node):
  key=list(node.keys())[0]
  if key=="func":
    return spec_binary_funcidx_inv(node[1])
  else:
    return bytearray()


# 5.5.12 ELEMENT SECTION

def spec_binary_elemsec(raw,idx,skip=0):
  if verbose: print("spec_binary_elemsec(",idx,")")
  return spec_binary_sectionN(raw,idx,9,spec_binary_elem,skip)

def spec_binary_elem(raw,idx):
  if verbose: print("spec_binary_elem(",idx,")")
  idx,x=spec_binary_tableidx(raw,idx)
  idx,e=spec_binary_expr(raw,idx)
  idx,ystar=spec_binary_vec(raw,idx,spec_binary_funcidx)
  return idx,{"table":x,"offset":e,"init":ystar}

def spec_binary_elemsec_inv(node):
  return spec_binary_sectionN_inv(node,spec_binary_elem_inv,9)
  
def spec_binary_elem_inv(node):
  return spec_binary_tableidx_inv(node["table"]) + spec_binary_expr_inv(node["offset"]) + spec_binary_vec_inv(node["init"],spec_binary_funcidx_inv)


# 5.5.13 CODE SECTION

def spec_binary_codesec(raw,idx,skip=0):
  if verbose: print("spec_binary_codesec(",idx,")")
  return spec_binary_sectionN(raw,idx,10,spec_binary_code,skip)

def spec_binary_code(raw,idx):
  if verbose: print("spec_binary_code(",idx,")")
  idx,size=spec_binary_uN(raw,idx,32)
  idx_end = idx+size
  idx,code=spec_binary_func(raw,idx)
  if idx_end != idx: raise Exception("malformed")
  if len(code) >= 2**32: raise Exception("malformed")
  return idx,code

def spec_binary_func(raw,idx):
  if verbose: print("spec_binary_func(",idx,")")
  idx,tstarstar=spec_binary_vec(raw,idx,spec_binary_locals)
  idx,e=spec_binary_expr(raw,idx)
  concattstarstar=[t for tstar in tstarstar for t in tstar] 
  if len(concattstarstar) >= 2**32: raise Exception("malformed")
  return idx, [concattstarstar,e]

def spec_binary_locals(raw,idx):
  if verbose: print("spec_binary_locals(",idx,")")
  idx,n=spec_binary_uN(raw,idx,32)
  idx,t=spec_binary_valtype(raw,idx)
  tn=[t]*n
  return idx,tn

def spec_binary_codesec_inv(node):
  return spec_binary_sectionN_inv(node,spec_binary_code_inv,10)
  
def spec_binary_code_inv(node):
  func_bytes = spec_binary_func_inv(node)
  return spec_binary_uN_inv(len(func_bytes),32) + func_bytes

def spec_binary_func_inv(node):
  #group locals into chunks
  locals_ = []
  prev_valtype = ""
  for valtype in node[0]:
    if valtype==prev_valtype:
      locals_[-1][0]+=1
    else:
      locals_ += [[1,valtype]]
      prev_valtype = valtype
  locals_bytes = spec_binary_vec_inv(locals_,spec_binary_locals_inv)
  expr_bytes = spec_binary_expr_inv(node[1])
  return locals_bytes + expr_bytes 

def spec_binary_locals_inv(node):
  return spec_binary_uN_inv(node[0],32) + spec_binary_valtype_inv(node[1])
  

# 5.5.14 DATA SECTION

def spec_binary_datasec(raw,idx,skip=0):
  if verbose: print("spec_binary_datasec(",idx,")")
  return spec_binary_sectionN(raw,idx,11,spec_binary_data,skip)

def spec_binary_data(raw,idx):
  if verbose: print("spec_binary_data(",idx,")")
  idx,x=spec_binary_memidx(raw,idx)
  idx,e=spec_binary_expr(raw,idx)
  idx,bstar=spec_binary_vec(raw,idx,spec_binary_byte)
  return idx, {"data":x,"offset":e,"init":bstar}

def spec_binary_datasec_inv(node):
  return spec_binary_sectionN_inv(node,spec_binary_data_inv,11)
  
def spec_binary_data_inv(node):
  return spec_binary_memidx_inv(node["data"]) + spec_binary_expr_inv(node["offset"]) + spec_binary_vec_inv(node["init"],spec_binary_byte_inv)


# 5.5.15 MODULES

def spec_binary_module(raw):
  if verbose: print("spec_binary_module()")
  idx=0
  magic=[0x00,0x61,0x73,0x6d]
  if magic!=[x for x in raw[idx:idx+4]]: raise Exception("malformed")
  idx+=4
  version=[0x01,0x00,0x00,0x00]
  if version!=[x for x in raw[idx:idx+4]]: raise Exception("malformed")
  idx+=4

  while idx<len(raw) and raw[idx]==0:
    idx,customsec = spec_binary_customsec(raw,idx,0)

  idx,functypestar=spec_binary_typesec(raw,idx,0)
  if verbose: print("functypestar",functypestar)

  while idx<len(raw) and raw[idx]==0:
    idx,customsec = spec_binary_customsec(raw,idx,0)

  idx,importstar=spec_binary_importsec(raw,idx,0)
  if verbose: print("importstar",importstar)

  while idx<len(raw) and raw[idx]==0:
    idx,customsec = spec_binary_customsec(raw,idx,0)

  idx,typeidxn=spec_binary_funcsec(raw,idx,0)
  if verbose: print("typeidxn",typeidxn)

  while idx<len(raw) and raw[idx]==0:
    idx,customsec = spec_binary_customsec(raw,idx,0)

  idx,tablestar=spec_binary_tablesec(raw,idx,0)
  if verbose: print("tablestar",tablestar)

  while idx<len(raw) and raw[idx]==0:
    idx,customsec = spec_binary_customsec(raw,idx,0)

  idx,memstar=spec_binary_memsec(raw,idx,0)
  if verbose: print("memstar",memstar)

  while idx<len(raw) and raw[idx]==0:
    idx,customsec = spec_binary_customsec(raw,idx,0)

  idx,globalstar=spec_binary_globalsec(raw,idx,0)
  if verbose: print("globalstar",globalstar)

  while idx<len(raw) and raw[idx]==0:
    idx,customsec = spec_binary_customsec(raw,idx,0)

  idx,exportstar=spec_binary_exportsec(raw,idx,0)
  if verbose: print("exportstar",exportstar)

  while idx<len(raw) and raw[idx]==0:
    idx,customsec = spec_binary_customsec(raw,idx,0)

  idx,startq=spec_binary_startsec(raw,idx,0)
  if verbose: print("startq",startq)

  while idx<len(raw) and raw[idx]==0:
    idx,customsec = spec_binary_customsec(raw,idx,0)

  idx,elemstar=spec_binary_elemsec(raw,idx,0)
  if verbose: print("elemstar",elemstar)

  while idx<len(raw) and raw[idx]==0:
    idx,customsec = spec_binary_customsec(raw,idx,0)

  idx,coden=spec_binary_codesec(raw,idx,0)
  if verbose: print("coden",coden)

  while idx<len(raw) and raw[idx]==0:
    idx,customsec = spec_binary_customsec(raw,idx,0)

  idx,datastar=spec_binary_datasec(raw,idx,0)
  if verbose: print("datastar",datastar)

  while idx<len(raw) and raw[idx]==0:
    idx,customsec = spec_binary_customsec(raw,idx,0)

  if len(typeidxn)!=len(coden): raise Exception("malformed")

  funcn=[]
  for i in range(len(typeidxn)):
    funcn+=[{"type":typeidxn[i], "locals":coden[i][0], "body":coden[i][1]}]
  mod = {"types":functypestar, "funcs":funcn, "tables":tablestar, "mems":memstar, "globals":globalstar, "elem": elemstar, "data":datastar, "start":startq, "imports":importstar, "exports":exportstar}
  return mod

# this prints a binary to a filename, maybe we should just return the binary
def spec_binary_module_inv(mod):
  #print_sections(mod)
  typesec   = spec_binary_typesec_inv(mod["types"])
  importsec = spec_binary_importsec_inv(mod["imports"])
  funcsec   = spec_binary_funcsec_inv([e["type"] for e in mod["funcs"]])
  tablesec  = spec_binary_tablesec_inv(mod["tables"])
  memsec    = spec_binary_memsec_inv(mod["mems"])
  globalsec = spec_binary_globalsec_inv(mod["globals"])
  exportsec = spec_binary_exportsec_inv(mod["exports"])
  startsec  = spec_binary_startsec_inv(mod["start"])
  elemsec   = spec_binary_elemsec_inv(mod["elem"])
  codesec   = spec_binary_codesec_inv([(f["locals"],f["body"]) for f in mod["funcs"]])
  datasec   = spec_binary_datasec_inv(mod["data"])
  bytestar = bytearray([])
  bytestar += bytearray([0x00,0x61,0x73,0x6d]) #magic
  bytestar += bytearray([0x01,0x00,0x00,0x00]) #version
  bytestar += typesec
  bytestar += importsec
  bytestar += funcsec
  bytestar += tablesec
  bytestar += memsec
  bytestar += globalsec
  bytestar += exportsec
  bytestar += startsec
  bytestar += elemsec
  bytestar += codesec
  bytestar += datasec
  return bytestar
