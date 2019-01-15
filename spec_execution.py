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
import spec_validation as validation
import math
import struct

verbose = 0

###############
###############
# 4 EXECUTION #
###############
###############

#Chapter 4 defines execution semantics over the abstract syntax.

##############
# 4.3 NUMERICS
##############

def spec_trunc(q):
  if verbose>=1: print("spec_trunc(",q,")")
  # round towards zero
  # q can be float or rational as tuple (numerator,denominator)
  if type(q)==tuple: #rational
    result = q[0]//q[1] #rounds towards negative infinity
    if result < 0 and q[1]*result != q[0]:
      return result+1
    else:
      return result
  elif type(q)==float:
    #using ftrunc instead
    return int(q) 


# 4.3.1 REPRESENTATIONS

# bits are string of 1s and 0s
# bytes are bytearray (maybe can also read from memoryview)

def spec_bitst(t,c):
  if verbose>=1: print("spec_bitst(",t,c,")")
  N = int(t[1:3])
  if t[0]=='i':
    return spec_bitsiN(N,c)
  elif t[0]=='f':
    return spec_bitsfN(N,c)

def spec_bitst_inv(t,bits):
  if verbose>=1: print("spec_bitst_inv(",t,bits,")")
  N = int(t[1:3])
  if t[0]=='i':
    return spec_bitsiN_inv(N,bits)
  elif t[0]=='f':
    return spec_bitsfN_inv(N,bits)

def spec_bitsiN(N,i):
  if verbose>=1: print("spec_bitsiN(",N,i,")")
  return spec_ibitsN(N,i)

def spec_bitsiN_inv(N,bits):
  if verbose>=1: print("spec_bitsiN_inv(",N,bits,")")
  return spec_ibitsN_inv(N,bits)

def spec_bitsfN(N,z):
  if verbose>=1: print("spec_bitsfN(",N,z,")")
  return spec_fbitsN(N,z)

def spec_bitsfN_inv(N,bits):
  if verbose>=1: print("spec_bitsfN_inv(",N,bits,")")
  return spec_fbitsN_inv(N,bits)


# Integers

def spec_ibitsN(N,i):
  if verbose>=1: print("spec_ibitsN(",N,i,")")
  #print(bin(i)[2:].zfill(N))
  return bin(i)[2:].zfill(N)

def spec_ibitsN_inv(N,bits):
  if verbose>=1: print("spec_ibitsN_inv(",N,bits,")")
  return int(bits,2)


# Floating-Point

def spec_fbitsN(N,z):
  if verbose>=1: print("spec_fbitsN(",N,z,")")
  if N==32:
    z_bytes = struct.pack('>f',z)
  elif N==64:
    z_bytes = struct.pack('>d',z)
  #stryct.pack() gave us bytes, need bits
  bits = ''
  for byte in z_bytes:
    bits += bin( int(byte) ).lstrip('0b').zfill(8)
  return bits

def spec_fbitsN_inv(N,bits):
  # this is used by reinterpret
  if verbose>=1: print("spec_fbitsN_inv(",N,bits,")")
  #will use struct.unpack() so need bytearray
  bytes_ = bytearray()
  for i in range(len(bits)//8):
    bytes_ += bytearray( [int(bits[8*i:8*(i+1)],2)] )
  if N==32:
    z = struct.unpack('>f',bytes_)[0]
  elif N==64:
    z = struct.unpack('>d',bytes_)[0]
  return z

def spec_fsign(z):
  bytes_ = spec_bytest("f"+str(64),z)
  #print("fsign bytes_",bytes_, [bin(byte).lstrip('0b').zfill(8) for byte in bytes_])
  sign = bytes_[-1] & 0b10000000	#-1 since littleendian
  #print("spec_fsign(",z,")",sign)
  if sign: return 1
  else: return 0
  #z_bytes = struct.pack('d',z)
  #if bin(z_bytes[0]).replace('0b','')[0] == '1':
  #  return 1
  #else:
  #  return 0

# decided to just use struct.pack() and struct.unpack()
# other options to represent floating point numbers:
#   float which is 64-bit, for 32-bit, can truncate significand and exponent after each operation
#   ctypes.c_float and ctypes.c_double 
#   numpy.float32 and numpy.float64


# Storage

def spec_bytest(t,i):
  if verbose>=1: print("spec_bytest(",t,i,")")
  if t[0]=='i':
    bits = spec_bitsiN(int(t[1:3]),i)
  elif t[0]=='f':
    bits = spec_bitsfN(int(t[1:3]),i)
  return spec_littleendian(bits)

def spec_bytest_inv(t,bytes_):
  if verbose>=1: print("spec_bytest_inv(",t,bytes_,")")
  bits = spec_littleendian_inv(bytes_)
  if t[0]=='i':
    return spec_bitsiN_inv(int(t[1:3]),bits)
  elif t[0]=='f':
    return spec_bitsfN_inv(int(t[1:3]),bits)


def spec_bytesiN(N,i):
  if verbose>=1: print("spec_bytesiN(",N,i,")")
  bits = spec_bitsiN(N,i)
  #convert bits to bytes
  bytes_ = bytearray()
  for byteIdx in range(0,len(bits),8):
    bytes_ += bytearray([int(bits[byteIdx:byteIdx+8],2)])
  return bytes_

def spec_bytesiN_inv(N,bytes_):
  if verbose>=1: print("spec_bytesiN_inv(",N,bytes_,")")
  bits=""
  for byte in bytes_:
    bits += spec_ibitsN(8,byte)
  return spec_ibitsN_inv(N,bits)


# TODO: these are unused, but might use when refactor floats to pass NaN significand tests
def spec_bytesfN(N,z):
  if verbose>=1: print("spec_bytesfN(",N,z,")")
  if N==32:
    z_bytes = struct.pack('>f',z)
  elif N==64:
    z_bytes = struct.pack('>d',z)
  return z_bytes
  
def spec_bytesfN_inv(N,bytes_):
  if verbose>=1: print("spec_bytesfN_inv(",N,bytes_,")")
  if N==32:
    z = struct.unpack('>f',bytes_)[0]
  elif N==64:
    z = struct.unpack('>d',bytes_)[0]
  return z


def spec_littleendian(d):
  if verbose>=1: print("spec_littleendian(",d,")")
  #same behavior for both 32 and 64-bit values
  #this assumes len(d) is divisible by 8
  if len(d)==0: return bytearray()
  d18 = d[:8]
  d2Nm8 = d[8:]
  d18_as_int = spec_ibitsN_inv(8,d18)
  return spec_littleendian(d2Nm8) + bytearray([d18_as_int])
  #return bytearray([d18_as_int]) + spec_littleendian(d2Nm8) 

def spec_littleendian_inv(bytes_):
  if verbose>=1: print("spec_littleendian_inv(",bytes_,")")
  #same behavior for both 32 and 64-bit values
  #this assumes len(d) is divisible by 8
  #this converts bytes to bits
  if len(bytes_)==0: return ''
  bits = bin( int(bytes_[-1]) ).lstrip('0b').zfill(8)
  return bits + spec_littleendian_inv( bytes_[:-1] )
  #bits = bin( int(bytes_[0]) ).lstrip('0b').zfill(8)
  #return spec_littleendian_inv( bytes_[1:] ) + bits



# 4.3.2 INTEGER OPERATIONS


#two's comlement
def spec_signediN(N,i):
  if verbose>=1: print("spec_signediN(",N,i,")")
  if 0<=i<2**(N-1):
    return i
  elif 2**(N-1)<=i<2**N:
    return i-2**N
  #alternative 2's comlement
  #  return i - int((i << 1) & 2**N) #https://stackoverflow.com/a/36338336

def spec_signediN_inv(N,i):
  if verbose>=1: print("spec_signediN_inv(",N,i,")")
  if 0<=i<2**(N-1):
    return i
  elif -1*(2**(N-1))<=i<0:
    return i+2**N
  else:
    return None

def spec_iaddN(N,i1,i2):
  if verbose>=1: print("spec_iaddN(",N,i1,i2,")")
  return (i1+i2) % 2**N

def spec_isubN(N,i1,i2):
  if verbose>=1: print("spec_isubN(",N,i1,i2,")")
  return (i1-i2+2**N) % 2**N

def spec_imulN(N,i1,i2):
  if verbose>=1: print("spec_imulN(",N,i1,i2,")")
  return (i1*i2) % 2**N

def spec_idiv_uN(N,i1,i2):
  if verbose>=1: print("spec_idiv_uN(",N,i1,i2,")")
  if i2==0: raise Exception("trap")
  return spec_trunc((i1,i2))

def spec_idiv_sN(N,i1,i2):
  if verbose>=1: print("spec_idiv_sN(",N,i1,i2,")")
  j1 = spec_signediN(N,i1)
  j2 = spec_signediN(N,i2)
  if j2==0: raise Exception("trap")
  #assuming j1 and j2 are N-bit
  if j1//j2 == 2**(N-1): raise Exception("trap")
  return spec_signediN_inv(N,spec_trunc((j1,j2)))

def spec_irem_uN(N,i1,i2):
  if verbose>=1: print("spec_irem_uN(",i1,i2,")")
  if i2==0:raise Exception("trap")
  return i1-i2*spec_trunc((i1,i2))

def spec_irem_sN(N,i1,i2):
  if verbose>=1: print("spec_irem_sN(",N,i1,i2,")")
  j1 = spec_signediN(N,i1)
  j2 = spec_signediN(N,i2)
  if i2==0: raise Exception("trap")
  #print(j1,j2,spec_trunc((j1,j2)))
  return spec_signediN_inv(N,j1-j2*spec_trunc((j1,j2)))
  
def spec_iandN(N,i1,i2):
  if verbose>=1: print("spec_iandN(",N,i1,i2,")")
  return i1 & i2

def spec_iorN(N,i1,i2):
  if verbose>=1: print("spec_iorN(",N,i1,i2,")")
  return i1 | i2

def spec_ixorN(N,i1,i2):
  if verbose>=1: print("spec_ixorN(",N,i1,i2,")")
  return i1 ^ i2
 
def spec_ishlN(N,i1,i2):
  if verbose>=1: print("spec_ishlN(",N,i1,i2,")")
  k = i2 % N
  return (i1 << k) % (2**N)

def spec_ishr_uN(N,i1,i2):
  if verbose>=1: print("spec_ishr_uN(",N,i1,i2,")")
  j2 = i2 % N
  return i1 >> j2
  
def spec_ishr_sN(N,i1,i2):
  if verbose>=1: print("spec_ishr_sN(",N,i1,i2,")")
  #print("spec_ishr_sN(",N,i1,i2,")")
  k = i2 % N
  #print(k)
  d0d1Nmkm1d2k = spec_ibitsN(N,i1)
  d0 = d0d1Nmkm1d2k[0]
  d1Nmkm1 = d0d1Nmkm1d2k[1:N-k]
  #print(d0*k)
  #print(d0*(k+1) + d1Nmkm1)
  return spec_ibitsN_inv(N, d0*(k+1) + d1Nmkm1 )

def spec_irotlN(N,i1,i2):
  if verbose>=1: print("spec_irotlN(",N,i1,i2,")")
  k = i2 % N
  d1kd2Nmk = spec_ibitsN(N,i1)
  d2Nmk = d1kd2Nmk[k:]
  d1k = d1kd2Nmk[:k]
  return spec_ibitsN_inv(N, d2Nmk+d1k )

def spec_irotrN(N,i1,i2):
  if verbose>=1: print("spec_irotrN(",N,i1,i2,")")
  k = i2 % N
  d1Nmkd2k = spec_ibitsN(N,i1)
  d1Nmk = d1Nmkd2k[:N-k]
  d2k = d1Nmkd2k[N-k:]
  return spec_ibitsN_inv(N, d2k+d1Nmk )

def spec_iclzN(N,i):
  if verbose>=1: print("spec_iclzN(",N,i,")")
  k = 0
  for b in spec_ibitsN(N,i):
    if b=='0':
      k+=1
    else:
      break
  return k

def spec_ictzN(N,i):
  if verbose>=1: print("spec_ictzN(",N,i,")")
  k = 0
  for b in reversed(spec_ibitsN(N,i)):
    if b=='0':
      k+=1
    else:
      break
  return k

def spec_ipopcntN(N,i):
  if verbose>=1: print("spec_ipopcntN(",N,i,")")
  k = 0
  for b in spec_ibitsN(N,i):
    if b=='1':
      k+=1
  return k

def spec_ieqzN(N,i):
  if verbose>=1: print("spec_ieqzN(",N,i,")")
  if i==0:
    return 1
  else:
    return 0

def spec_ieqN(N,i1,i2):
  if verbose>=1: print("spec_ieqN(",N,i1,i2,")")
  if i1==i2:
    return 1
  else:
    return 0

def spec_ineN(N,i1,i2):
  if verbose>=1: print("spec_ineN(",N,i1,i2,")")
  if i1!=i2:
    return 1
  else:
    return 0

def spec_ilt_uN(N,i1,i2):
  if verbose>=1: print("spec_ilt_uN(",N,i1,i2,")")
  if i1<i2:
    return 1
  else:
    return 0

def spec_ilt_sN(N,i1,i2):
  if verbose>=1: print("spec_ilt_sN(",N,i1,i2,")")
  j1 = spec_signediN(N,i1)
  j2 = spec_signediN(N,i2)
  if j1<j2:
    return 1
  else:
    return 0

def spec_igt_uN(N,i1,i2):
  if verbose>=1: print("spec_igt_uN(",N,i1,i2,")")
  if i1>i2:
    return 1
  else:
    return 0

def spec_igt_sN(N,i1,i2):
  if verbose>=1: print("spec_igt_sN(",N,i1,i2,")")
  j1 = spec_signediN(N,i1)
  j2 = spec_signediN(N,i2)
  if j1>j2:
    return 1
  else:
    return 0

def spec_ile_uN(N,i1,i2):
  if verbose>=1: print("spec_ile_uN(",N,i2,i1,")")
  if i1<=i2:
    return 1
  else:
    return 0

def spec_ile_sN(N,i1,i2):
  if verbose>=1: print("spec_ile_sN(",N,i1,i2,")")
  j1 = spec_signediN(N,i1)
  j2 = spec_signediN(N,i2)
  if j1<=j2:
    return 1
  else:
    return 0

def spec_ige_uN(N,i1,i2):
  if verbose>=1: print("spec_ige_uN(",N,i1,i2,")")
  if i1>=i2:
    return 1
  else:
    return 0

def spec_ige_sN(N,i1,i2):
  if verbose>=1: print("spec_ige_sN(",N,i1,i2,")")
  j1 = spec_signediN(N,i1)
  j2 = spec_signediN(N,i2)
  if j1>=j2:
    return 1
  else:
    return 0


# 4.3.3 FLOATING-POINT OPERATIONS


def spec_fabsN(N,z):
  if verbose>=1: print("spec_fabsN(",N,z,")")
  #print("spec_fabsN(",N,z,")")
  sign = spec_fsign(z)
  #print(sign)
  if sign == 0:
    return z
  else:
    return spec_fnegN(N,z)

def spec_fnegN(N,z):
  if verbose>=1: print("spec_fnegN(",N,z,")")
  #get bytes and sign
  bytes_ = spec_bytest("f64",z)	#64 since errors if z too bit for 32
  sign = spec_fsign(z)
  if sign == 0:
    bytes_[-1] |= 0b10000000	#-1 since littleendian
  else:
    bytes_[-1] &= 0b01111111	#-1 since littleendian
  z = spec_bytest_inv("f64",bytes_)	#64 since errors if z too bit for 32
  return z

def spec_fceilN(N,z):
  if verbose>=1: print("spec_fceilN(",N,z,")")
  if math.isnan(z):
    return z
  elif math.isinf(z):
    return z
  elif z==0:
    return z
  elif -1.0<z<0.0:
    return -0.0
  else:
    return float(math.ceil(z))

def spec_ffloorN(N,z):
  if verbose>=1: print("spec_ffloorN(",N,z,")")
  if math.isnan(z):
    return z
  elif math.isinf(z):
    return z
  elif z==0:
    return z
  elif 0.0<z<1.0:
    return 0.0
  else:
    return float(math.floor(z))

def spec_ftruncN(N,z):
  if verbose>=1: print("spec_ftruncN(",N,z,")")
  if math.isnan(z):
    return z
  elif math.isinf(z):
    return z
  elif z==0:
    return z
  elif 0.0<z<1.0:
    return 0.0
  elif -1.0<z<0.0:
    return -0.0
  else:
    magnitude = spec_fabsN(N,z)
    floormagnitude = spec_ffloorN(N,magnitude)
    return floormagnitude * (-1 if spec_fsign(z) else 1) 	#math.floor(z)) + spec_fsign(z) 

def spec_fnearestN(N,z):
  if verbose>=1: print("spec_fnearestN(",N,z,")")
  if math.isnan(z):
    return z
  elif math.isinf(z):
    return z
  elif z==0:
    return z
  elif 0.0 < z <= 0.5:
    return 0.0
  elif -0.5 <= z < 0.0:
    return -0.0
  else:
    return float(round(z))

def spec_fsqrtN(N,z):
  if verbose>=1: print("spec_fsqrtN(",N,z,")")
  if math.isnan(z) or (spec_fsign(z)==1 and z!=0):
    return float('nan')
  else:
    return math.sqrt(z)

def spec_faddN(N,z1,z2):
  if verbose>=1: print("spec_faddN(",N,z1,z2,")")
  res = z1+z2
  if N==32:
    res = spec_demoteMN(64,32,res)
  return res

def spec_fsubN(N,z1,z2):
  if verbose>=1: print("spec_fsubN(",N,z1,z2,")")
  res = z1-z2
  #print("z1-z2:",z1-z2)
  if N==32:
    res = spec_demoteMN(64,32,res)
    #print("demoted z1-z2:",res)
  return res

def spec_fmulN(N,z1,z2):
  if verbose>=1: print("spec_fmulN(",N,z1,z2,")")
  res = z1*z2
  if N==32:
    res = spec_demoteMN(64,32,res)
  return res

def spec_fdivN(N,z1,z2):
  if verbose>=1: print("spec_fdivN(",N,z1,z2,")")
  if math.isnan(z1):
    return z1
  elif math.isnan(z2):
    return z2
  elif math.isinf(z1) and math.isinf(z2):
    return float('nan')
  elif z1==0.0 and z2==0.0:
    return float('nan')
  elif z1==0.0 and z2==0.0:
    return float('nan')
  elif math.isinf(z1):
    if spec_fsign(z1) == spec_fsign(z2):
      return float('inf')
    else:
      return -float('inf')
  elif math.isinf(z2):
    if spec_fsign(z1) == spec_fsign(z2):
      return 0.0
    else:
      return -0.0
  elif z1==0:
    if spec_fsign(z1) == spec_fsign(z2):
      return 0.0
    else:
      return -0.0
  elif z2==0:
    if spec_fsign(z1) == spec_fsign(z2):
      return float('inf')
    else:
      return -float('inf')
  else:
    res = z1/z2
    if N==32:
      res = spec_demoteMN(64,32,res)
    return res

def spec_fminN(N,z1,z2):
  if verbose>=1: print("spec_fminN(",N,z1,z2,")")
  if math.isnan(z1):
    return z1
  elif math.isnan(z2):
    return z2
  elif z1==-float('inf') or z2==-float('inf'):
    return -float('inf')
  elif z1 == float('inf'):
    return z2
  elif z2 == float('inf'):
    return z1
  elif z1==z2==0.0:
    if spec_fsign(z1) != spec_fsign(z2):
      return -0.0
    else:
      return z1
  elif z1 <= z2:
    return z1
  else:
    return z2

def spec_fmaxN(N,z1,z2):
  if verbose>=1: print("spec_fmaxN(",N,z1,z2,")")
  if math.isnan(z1):
    return z1
  elif math.isnan(z2):
    return z2
  elif z1==float('inf') or z2==float('inf') :
    return float('inf')
  elif z1 == -float('inf'):
    return z2
  elif z2 == -float('inf'):
    return z1
  elif z1==z2==0.0:
    if spec_fsign(z1) != spec_fsign(z2):
      return 0.0
    else:
      return z1
  elif z1 <= z2:
    return z2
  else:
    return z1

def spec_fcopysignN(N,z1,z2):
  if verbose>=1: print("spec_fcopysignN(",N,z1,z2,")")
  z1sign = spec_fsign(z1)
  z2sign = spec_fsign(z2)
  if z1sign == z2sign:
    return z1
  else:
    z1bytes = spec_bytest("f"+str(N),z1)
    if z1sign == 0:
      z1bytes[-1] |= 0b10000000		#-1 since littleendian
    else:
      z1bytes[-1] &= 0b01111111		#-1 since littleendian
    z1 = spec_bytest_inv("f"+str(N),z1bytes)
    return z1

def spec_feqN(N,z1,z2):
  if verbose>=1: print("spec_feqN(",N,z1,z2,")")
  if z1==z2:
    return 1
  else:
    return 0

def spec_fneN(N,z1,z2):
  if verbose>=1: print("spec_fneN(",N,z1,z2,")")
  if z1 != z2:
    return 1
  else:
    return 0

def spec_fltN(N,z1,z2):
  if verbose>=1: print("spec_fltN(",N,z1,z2,")")
  if math.isnan(z1):
    return 0
  elif math.isnan(z2):
    return 0
  elif spec_bitsfN(N,z1)==spec_bitsfN(N,z2):
    return 0
  elif z1==float('inf'):
    return 0
  elif z1==-float('inf'):
    return 1
  elif z2==float('inf'):
    return 1
  elif z2==-float('inf'):
    return 0
  elif z1==z2==0:
    return 0
  elif z1 < z2:
    return 1
  else:
    return 0

def spec_fgtN(N,z1,z2):
  if verbose>=1: print("spec_fgtN(",N,z1,z2,")")
  if math.isnan(z1):
    return 0
  elif math.isnan(z2):
    return 0
  elif spec_bitsfN(N,z1)==spec_bitsfN(N,z2):
    return 0
  elif z1==float('inf'):
    return 1
  elif z1==-float('inf'):
    return 0
  elif z2==float('inf'):
    return 0
  elif z2==-float('inf'):
    return 1
  elif z1==z2==0:
    return 0
  elif z1 > z2:
    return 1
  else:
    return 0

def spec_fleN(N,z1,z2):
  if verbose>=1: print("spec_fleN(",N,z1,z2,")")
  if math.isnan(z1):
    return 0
  elif math.isnan(z2):
    return 0
  elif spec_bitsfN(N,z1)==spec_bitsfN(N,z2):
    return 1
  elif z1==float('inf'):
    return 0
  elif z1==-float('inf'):
    return 1
  elif z2==float('inf'):
    return 1
  elif z2==-float('inf'):
    return 0
  elif z1==z2==0:
    return 1
  elif z1 <= z2:
    return 1
  else:
    return 0

def spec_fgeN(N,z1,z2):
  if verbose>=1: print("spec_fgeN(",N,z1,z2,")")
  if math.isnan(z1):
    return 0
  elif math.isnan(z2):
    return 0
  elif spec_bitsfN(N,z1)==spec_bitsfN(N,z2):
    return 1
  elif z1==float('inf'):
    return 1
  elif z1==-float('inf'):
    return 0
  elif z2==float('inf'):
    return 0
  elif z2==-float('inf'):
    return 1
  elif z1==z2==0:
    return 1
  elif z1 >= z2:
    return 1
  else:
    return 0



# 4.3.4 CONVERSIONS

def spec_extend_uMN(M,N,i):
  if verbose>=1: print("spec_extend_uMN(",i,")")
  return i

def spec_extend_sMN(M,N,i):
  if verbose>=1: print("spec_extend_sMN(",M,N,i,")")
  #print("spec_extend_sMN(",M,N,i,")")
  j = spec_signediN(M,i)
  return spec_signediN_inv(N,j)

def spec_wrapMN(M,N,i):
  if verbose>=1: print("spec_wrapMN(",M,N,i,")")
  #print("spec_wrapMN(",M,N,i,")")
  return i % (2**N)

def spec_trunc_uMN(M,N,z):
  if verbose>=1: print("spec_trunc_uMN(",M,N,z,")")
  if math.isnan(z) or math.isinf(z): raise Exception("trap")
  ztrunc = spec_ftruncN(M,z) 
  if -1 < ztrunc < 2**N:
    return int(ztrunc)
  else: raise Exception("trap")

def spec_trunc_sMN(M,N,z):
  if verbose>=1: print("spec_trunc_sMN(",M,N,z,")")
  if math.isnan(z) or math.isinf(z): raise Exception("trap")
  ztrunc = spec_ftruncN(M,z) 
  if -(2**(N-1))-1 < ztrunc < 2**(N-1):
    iztrunc = int(ztrunc)
    if iztrunc < 0:
      return spec_signediN_inv(N,iztrunc)
    else:
      return iztrunc
  else:
    raise Exception("trap")

def spec_promoteMN(M,N,z):
  if verbose>=1: print("spec_promoteMN(",M,N,z,")")
  return z

def spec_demoteMN(M,N,z):
  if verbose>=1: print("spec_demoteMN(",M,N,z,")")
  absz = spec_fabsN(N,z)
  #limitN = 2**(2**(structure.spec_expon(N)-1))
  limitN = 2**128 * (1 - 2**-25)	#this FLT_MAX is slightly different than the Wasm spec's 2**127
  if absz >= limitN:
    signz = spec_fsign(z)
    if signz:
      return -float('inf')
    else:
      return float('inf')
  bytes_ = spec_bytest('f32',z)
  z32 = spec_bytest_inv('f32',bytes_)
  return z32

def spec_convert_uMN(M,N,i):
  if verbose>=1: print("spec_convert_uMN(",M,N,i,")")
  limitN = 2**(2**(structure.spec_expon(N)-1))
  if i >= limitN:
    return float('inf')
  return float(i)

def spec_convert_sMN(M,N,i):
  if verbose>=1: print("spec_convert_sMN(",M,N,i,")")
  limitN = 2**(2**(structure.spec_expon(N)-1))
  #print("limitN",limitN)
  if i >= limitN:
    return float('inf')
  if i <= -1*limitN:
    return -float('inf')
  i = spec_signediN(M,i)
  return float(i)

def spec_reinterprett1t2(t1,t2,c):
  if verbose>=1: print("spec_reinterprett1t2(",t1,t2,c,")")
  #print("spec_reinterprett1t2(",t1,t2,c,")")
  bits = spec_bitst(t1,c)
  #print(bits)
  return spec_bitst_inv(t2,bits)


##################
# 4.4 INSTRUCTIONS
##################

# S is the store

# 4.4.1 NUMERIC INSTRUCTIONS

def spec_tconst(config):
  if verbose>=1: print("spec_tconst(",")")
  S = config["S"]
  c = config["instrstar"][config["idx"]][1]
  if verbose>=1: print("spec_tconst(",c,")")
  config["operand_stack"] += [c]
  config["idx"] += 1

def spec_tunop(config):	# t is in {'i32','i64','f32','f64'}
  if verbose>=1: print("spec_tunop(",")")
  S = config["S"]
  instr = config["instrstar"][config["idx"]][0]
  t = instr[0:3]
  op = opcode2exec[instr][1]
  c1 = config["operand_stack"].pop()
  c = op(int(t[1:3]),c1)
  if c == "trap": return c
  config["operand_stack"].append(c)
  config["idx"] += 1

def spec_tbinop(config):
  if verbose>=1: print("spec_tbinop(",")")
  S = config["S"]
  instr = config["instrstar"][config["idx"]][0]
  t = instr[0:3]
  op = opcode2exec[instr][1]
  c2 = config["operand_stack"].pop()
  c1 = config["operand_stack"].pop()
  c = op(int(t[1:3]),c1,c2)
  if c == "trap": return c
  config["operand_stack"].append(c)
  config["idx"] += 1
  
def spec_ttestop(config):
  if verbose>=1: print("spec_ttestop(",")")
  S = config["S"]
  instr = config["instrstar"][config["idx"]][0]
  t = instr[0:3]
  op = opcode2exec[instr][1]
  c1 = config["operand_stack"].pop()
  c = op(int(t[1:3]),c1)
  if c == "trap": return c
  config["operand_stack"].append(c)
  config["idx"] += 1
  
def spec_trelop(config):
  if verbose>=1: print("spec_trelop(",")")
  S = config["S"]
  instr = config["instrstar"][config["idx"]][0]
  t = instr[0:3]
  op = opcode2exec[instr][1]
  c2 = config["operand_stack"].pop()
  c1 = config["operand_stack"].pop()
  c = op(int(t[1:3]),c1,c2)
  if c == "trap": return c
  config["operand_stack"].append(c)
  config["idx"] += 1

def spec_t2cvtopt1(config):
  if verbose>=1: print("spec_t2crtopt1(",")")
  S = config["S"]
  instr = config["instrstar"][config["idx"]][0]
  t2 = instr[0:3]
  t1 = instr[-3:]
  op = opcode2exec[instr][1]
  c1 = config["operand_stack"].pop()
  if instr[4:15] == "reinterpret":
    c2 = op(t1,t2,c1)
  else:
    c2 = op(int(t1[1:]),int(t2[1:]),c1)
  if c2 == "trap": return c2
  config["operand_stack"].append(c2)
  config["idx"] += 1


# 4.4.2 PARAMETRIC INSTRUCTIONS
 
def spec_drop(config):
  if verbose>=1: print("spec_drop(",")")
  S = config["S"]
  config["operand_stack"].pop()
  config["idx"] += 1
  
def spec_select(config):
  if verbose>=1: print("spec_select(",")")
  S = config["S"]
  operand_stack = config["operand_stack"]
  c = operand_stack.pop()
  val1 = operand_stack.pop()
  val2 = operand_stack.pop()
  if not c:
    operand_stack.append(val1)
  else:
    operand_stack.append(val2)
  config["idx"] += 1

# 4.4.3 VARIABLE INSTRUCTIONS

def spec_get_local(config):
  if verbose>=1: print("spec_get_local(",")")
  S = config["S"]
  F = config["F"]
  x = config["instrstar"][config["idx"]][1]
  #print(F)
  #print(F[-1])
  #print(F[-1]["locals"])
  #print(x)
  val = F[-1]["locals"][x]
  config["operand_stack"].append(val)
  config["idx"] += 1

def spec_set_local(config):
  if verbose>=1: print("spec_set_local(",")")
  S = config["S"]
  F = config["F"]
  x = config["instrstar"][config["idx"]][1]
  val = config["operand_stack"].pop()
  F[-1]["locals"][x] = val
  config["idx"] += 1

def spec_tee_local(config):
  if verbose>=1: print("spec_tee_local(",")")
  S = config["S"]
  x = config["instrstar"][config["idx"]][1]
  operand_stack = config["operand_stack"]
  val = operand_stack.pop()
  operand_stack.append(val)
  operand_stack.append(val)
  spec_set_local(config)
  #config["idx"] += 1
  
def spec_get_global(config):
  if verbose>=1: print("spec_get_global(",")")
  S = config["S"]
  F = config["F"]
  #print("F[-1]",F[-1])
  x = config["instrstar"][config["idx"]][1]
  a = F[-1]["module"]["globaladdrs"][x]
  glob = S["globals"][a]
  val = glob["value"][1]	#*** omit the type eg 'i32.const', just get the value, see above for how this is different from the spec
  config["operand_stack"].append(val)
  config["idx"] += 1

def spec_set_global(config):
  if verbose>=1: print("spec_set_global(",")")
  S = config["S"]
  F = config["F"]
  x = config["instrstar"][config["idx"]][1]
  a = F[-1]["module"]["globaladdrs"][x]
  glob = S["globals"][a]
  val = config["operand_stack"].pop()
  glob["value"][1] = val
  config["idx"] += 1


# 4.4.4 MEMORY INSTRUCTIONS

# this is for both t.load and t.loadN_sx
def spec_tload(config):
  if verbose>=1: print("spec_tload(",")")
  S = config["S"]
  F = config["F"]
  instr = config["instrstar"][config["idx"]][0]
  memarg = config["instrstar"][config["idx"]][1]
  t = instr[:3]
  # 3
  a = F[-1]["module"]["memaddrs"][0]
  # 5
  mem = S["mems"][a]
  # 7
  i = config["operand_stack"].pop()
  # 8
  ea = i+memarg["offset"] 
  # 9
  sxflag = False
  if instr[3:] != ".load":  # N is part of the opcode eg i32.load8_s has N=8
    if instr[-1] == "s":
      sxflag = True
    N = int(instr[8:10].strip("_"))
  else:
    N=int(t[1:])
  # 10
  if ea+N//8 > len(mem["data"]): raise Exception("trap")
  # 11
  bstar = mem["data"][ea:ea+N//8]
  # 12
  if sxflag:
    n = spec_bytest_inv(t,bstar)
    c = spec_extend_sMN(N,int(t[1:]),n)
  else:
    c = spec_bytest_inv(t,bstar)
  # 13
  config["operand_stack"].append(c)
  if verbose>=2: print("loaded",c,"from memory locations",ea,"to",ea+N//8)
  config["idx"] += 1

def spec_tstore(config):
  if verbose>=1: print("spec_tstore(",")")
  S = config["S"]
  F = config["F"]
  instr = config["instrstar"][config["idx"]][0]
  memarg = config["instrstar"][config["idx"]][1]
  t = instr[:3]
  # 3
  a = F[-1]["module"]["memaddrs"][0]
  # 5
  mem = S["mems"][a]
  # 7
  c = config["operand_stack"].pop()
  # 9
  i = config["operand_stack"].pop()
  # 10
  ea = i+memarg["offset"]
  # 11
  Nflag = False 
  if instr[3:] != ".store":  # N is part of the instruction, eg i32.store8
    Nflag = True
    N=int(instr[9:])
  else:
    N=int(t[1:])
  # 12
  if ea+N//8 > len(mem["data"]): raise Exception("trap")
  # 13
  if Nflag:
    M=int(t[1:])
    c = spec_wrapMN(M,N,c)
    bstar = spec_bytest(t,c)
  else:
    bstar = spec_bytest(t,c)
  # 15
  mem["data"][ea:ea+N//8] = bstar[:N//8]
  #if verbose>=2: print("stored",[bin(byte).strip('0b').zfill(8) for byte in bstar[:N//8]],"to memory locations",ea,"to",ea+N//8)
  config["idx"] += 1

def spec_memorysize(config):
  if verbose>=1: print("spec_memorysize(",")")
  S = config["S"]
  F = config["F"]
  a = F[-1]["module"]["memaddrs"][0]
  mem = S["mems"][a]
  sz = len(mem["data"])//65536  #page size = 64 Ki = 65536
  config["operand_stack"].append(sz)
  config["idx"] += 1

def spec_memorygrow(config):
  if verbose>=1: print("spec_memorygrow(",")")
  S = config["S"]
  F = config["F"]
  a = F[-1]["module"]["memaddrs"][0]
  mem = S["mems"][a]
  sz = len(mem["data"])//65536  #page size = 64 Ki = 65536
  n = config["operand_stack"].pop()
  spec_growmem(mem,n)
  if sz+n == len(mem["data"])//65536: #success
    config["operand_stack"].append(sz)
  else: 
    config["operand_stack"].append(2**32-1) #put -1 on top of stack
  config["idx"] += 1
    
  
# 4.4.5 CONTROL INSTRUCTIONS


"""
 This implementation deviates from the spec as follows.
   - Three stacks are maintained, operands, control-flow labels, and function-call frames.
     Operand_stack holds only values, control_stack holds only labels. The function-call frames are mainted implicitly in Python function calls -- this will be changed, putting function call frames into the label stack or into their own stack.
   - `config` inculdes store S, frame F, instr_list, idx into this instr_list, operand_stack, and control_stack.
   - Each label L has extra value for height of operand stack when it started, continuation when it is branched to, and end when it's last instruction is called.
"""

def spec_nop(config):
  if verbose>=1: print("spec_nop(",")")
  config["idx"] += 1

def spec_unreachable(config):
  if verbose>=1: print("spec_unreachable(",")")
  raise Exception("trap")


def spec_block(config):
  if verbose>=1: print("spec_block(",")")
  instrstar = config["instrstar"]
  idx = config["idx"]
  operand_stack = config["operand_stack"]
  control_stack = config["control_stack"]
  t = instrstar[idx][1]
  # 1
  if type(t) == str:
    n=1
  elif type(t) == list:
    n=len(t)
  # 2
  continuation = [instrstar,idx+1]
  L = {"arity":n, "height":len(operand_stack), "continuation":continuation, "end":continuation}
  # 3
  spec_enter_block(config,instrstar[idx][2],L)
  #control_stack.append(L)
  #config["instrstar"] = instrstar[idx][2]
  #config["idx"] = 0

def spec_loop(config):
  if verbose>=1: print("spec_loop(",")")
  instrstar = config["instrstar"]
  idx = config["idx"]
  operand_stack = config["operand_stack"]
  control_stack = config["control_stack"]
  # 1
  continuation = [instrstar[idx][2],0]
  end = [instrstar,idx+1]
  L = {"arity":0, "height":len(operand_stack), "continuation":continuation, "end":end, "loop_flag":1}
  # 2
  spec_enter_block(config,instrstar[idx][2],L)
  #control_stack.append(L)
  #config["instrstar"] = instrstar[idx][2]
  #config["idx"] = 0

def spec_if(config):
  if verbose>=1: print("spec_if(",")")
  instrstar = config["instrstar"]
  idx = config["idx"]
  operand_stack = config["operand_stack"]
  control_stack = config["control_stack"]
  # 2
  c = operand_stack.pop()
  # 3
  t = instrstar[idx][1]
  if type(t) == str: n=1
  elif type(t) == list: n=len(t)
  # 4
  continuation = [instrstar,idx+1]
  L = {"arity":n, "height":len(operand_stack), "continuation":continuation, "end":continuation}
  # 5
  if c:
    spec_enter_block(config,instrstar[idx][2],L)
  # 6
  else:
    spec_enter_block(config,instrstar[idx][3],L)

def spec_br(config, l = None):
  if verbose>=1: print("spec_br(",")")
  operand_stack = config["operand_stack"]
  control_stack = config["control_stack"]
  if l == None:
    l = config["instrstar"][config["idx"]][1]
  # 2
  L = control_stack[-1*(l+1)]
  # 3
  n = L["arity"]
  # 5
  valn = []
  if n>0:
    valn = operand_stack[-1*n:]
  # 6
  del operand_stack[ L["height"]: ]
  if "loop_flag" in L: # branching to loop starts at beginning of loop, so don't delete
    if l>0:
      del control_stack[-1*l:]
    config["idx"] = 0
  else:
    del control_stack[-1*(l+1):]
  # 7
  operand_stack += valn
  # 8
  config["instrstar"],config["idx"] = L["continuation"]

def spec_br_if(config):
  if verbose>=1: print("spec_br_if(",")")
  l = config["instrstar"][config["idx"]][1]
  # 2
  c = config["operand_stack"].pop()
  # 3
  if c!=0: spec_br(config,l)
  # 4
  else: config["idx"] += 1

def spec_br_table(config):
  if verbose>=1: print("spec_br_table(",")")
  lstar = config["instrstar"][config["idx"]][1]
  lN = config["instrstar"][config["idx"]][2]
  # 2
  i = config["operand_stack"].pop()
  #print(lstar,lN)
  # 3
  if i < len(lstar):
    li = lstar[i]
    spec_br(config,li)
  # 4
  else:
    spec_br(config,lN)


def spec_return(config):
  if verbose>=1: print("spec_return(",")")
  operand_stack = config["operand_stack"]
  # 1
  F = config["F"][-1]
  # 2
  n = F["arity"]
  # 4
  valn = []
  if n>0:
    valn = operand_stack[-1*n:]
    # 6
    del operand_stack[F["height"]:]
  # 8
  config["F"].pop()
  # 9
  operand_stack += valn
  config["instrstar"], config["idx"], config["control_stack"] = F["continuation"]


def spec_call(config):
  if verbose>=1: print("spec_call(",")")
  operand_stack = config["operand_stack"]
  instr = config["instrstar"][config["idx"]]
  x = instr[1]
  # 1
  F = config["F"][-1]
  # 3
  a = F["module"]["funcaddrs"][x]
  # 4
  ret = spec_invoke_function_address(config,a)
  if ret=="exhaustion": return ret

def spec_call_indirect(config):
  if verbose>=1: print("spec_call_indirect(",")")
  S = config["S"]
  # 1
  F = config["F"][-1]
  # 3
  ta = F["module"]["tableaddrs"][0]
  # 5
  tab = S["tables"][ta]
  # 7
  x = config["instrstar"][config["idx"]][1]
  ftexpect = F["module"]["types"][x]
  # 9
  i = config["operand_stack"].pop()
  # 10
  if len(tab["elem"])<=i: raise Exception("trap")
  # 11
  if tab["elem"][i] == None: raise Exception("trap")
  # 12
  a = tab["elem"][i]
  # 14
  f = S["funcs"][a]
  # 15
  ftactual = f["type"]
  # 16
  if ftexpect != ftactual: raise Exception("trap")
  # 17
  ret = spec_invoke_function_address(config,a)
  if ret=="exhaustion": return ret


# 4.4.6 BLOCKS

def spec_enter_block(config,instrstar,L):
  # 1
  config["control_stack"].append(L)
  # 2
  config["instrstar"] = instrstar
  config["idx"] = 0

# this is unused, just done in spec_expr() since need to check if label stack is empty
def spec_exit_block(config):
  # 4
  L = config["control_stack"].pop()
  # 6
  config["instrstar"],config["idx"] = L["end"]
  


  

# 4.4.7 FUNCTION CALLS

# this is called by spac_call() and spec_call_indirect()
def spec_invoke_function_address(config, a=None):
  if verbose>=1: print("spec_invoke_function_address(",a,")")
  # a is address
  S = config["S"]
  F = config["F"]
  if len(F)>1024: #TODO: this is not part of spec, but this is required to pass tests. Tests pass with limit 10000, maybe more
    return "exhaustion"
  instrstar = config["instrstar"]
  idx = config["idx"]
  operand_stack  = config["operand_stack"]
  control_stack  = config["control_stack"]
  if a==None:
    a=config["instrstar"][config["idx"]][1]
  # 2
  f = S["funcs"][a]
  # 3
  t1n,t2m = f["type"]
  if "code" in f:
    #print("a",a)
    #print("f[code]",f["code"])
    #print("f[type]",f["type"])
    # 5
    tstar = f["code"]["locals"]
    # 6
    instrstarend = f["code"]["body"]
    # 8
    valn = []
    if len(t1n)>0:
      valn = operand_stack[-1*len(t1n):]
      del operand_stack[-1*len(t1n):]
    # 9
    val0star = []
    for t in tstar:
      if t[0]=='i':
        val0star += [0]
      if t[0]=='f':
        val0star += [0.0]
    # 10 & 11
    #print("valn",valn)
    #print("val0star",val0star)
    F += [{ "module": f["module"], "locals": valn+val0star, "arity":len(t2m), "height":len(operand_stack), "continuation":[instrstar, idx+1, control_stack], }]
    # 12
    retval = [] if not t2m else t2m[0]
    blockinstrstarendend = [["block", retval,instrstarend],["end"]]
    config["instrstar"] = blockinstrstarendend
    config["idx"] = 0
    config["control_stack"] = []
    #config_new = {"S":S,"F":F,"instrstar":blockinstrstarendend,"idx":0,"operand_stack":[],"control_stack":[]}
    #ret = spec_expr(config_new)
    #if ret=="trap": return ret
    #operand_stack += config_new["operand_stack"]
    #print("operand_stack after:",operand_stack)
    #config["instrstar"], config["idx"] = F[-1]["continuation"]
    #F.pop()
  elif "hostcode" in f:
    valn = []
    if len(t1n)>0:
      valn = operand_stack[-1*len(t1n):]
      #print("operand_stack",operand_stack)
      del operand_stack[-1*len(t1n):]
    S,ret = f["hostcode"](S,valn)
    if ret=="trap": return ret
    operand_stack+=ret
    config["idx"]+=1


# this is unused for now
# this is called when end of function reached without return or trap aborting it
def spec_return_from_func(config):
  if verbose>=1: print("spec_return_from_func() !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
  # 1
  F = config["F"][-1]
  # 2,3,4,7 not needed since we have separate operand stack
  # 6
  config["F"].pop()
  # 8
  config["instrstar"], config["idx"], config["control_stack"] = F["continuation"]
  #print("config stuff")
  #print(config["instrstar"])
  #print(config["idx"],config["control_stack"])
  


def spec_end(config):
  if verbose>=1: print("spec_end()")
  if len(config["control_stack"])>=1:
    #print("ending block")
    spec_exit_block(config)
  else:
    #print("F:",config["F"][-1])
    if len(config["F"])>=1 and "continuation" in config["F"][-1]: #continuation for case of init elem or data or global 
      #print("ending function")
      spec_return_from_func(config)
    else:
      #print("config[F]",config["F"])
      #print("ending done")
      return "done"
    


# 4.4.8 EXPRESSIONS

#Map each opcode to the function(s) to invoke when it is encountered. For opcodes with two functions, the second function is called by the first function.
opcode2exec = {
"unreachable":	(spec_unreachable,),
"nop":		(spec_nop,),
"block":	(spec_block,),				# blocktype in* end
"loop":		(spec_loop,),				# blocktype in* end
"if":		(spec_if,),				# blocktype in1* else? in2* end
"else":		(spec_end,),				# in2*
"end":		(spec_end,),
"br":		(spec_br,),				# labelidx
"br_if":	(spec_br_if,),				# labelidx
"br_table":	(spec_br_table,),			# labelidx* labelidx
"return":	(spec_return,),
"call":		(spec_call,),				# funcidx
"call_indirect":(spec_call_indirect,),			# typeidx 0x00

"drop":		(spec_drop,),
"select":	(spec_select,),

"get_local":	(spec_get_local,),			# localidx
"set_local":	(spec_set_local,),			# localidx
"tee_local":	(spec_tee_local,),			# localidx
"get_global":	(spec_get_global,),			# globalidx
"set_global":	(spec_set_global,),			# globalidx

"i32.load":	(spec_tload,),				# memarg
"i64.load":	(spec_tload,),				# memarg
"f32.load":	(spec_tload,),				# memarg
"f64.load":	(spec_tload,), 				# memarg
"i32.load8_s":	(spec_tload,), 				# memarg
"i32.load8_u":	(spec_tload,), 				# memarg
"i32.load16_s":	(spec_tload,),				# memarg
"i32.load16_u":	(spec_tload,),				# memarg
"i64.load8_s":	(spec_tload,),				# memarg
"i64.load8_u":	(spec_tload,), 				# memarg
"i64.load16_s":	(spec_tload,), 				# memarg
"i64.load16_u":	(spec_tload,), 				# memarg
"i64.load32_s":	(spec_tload,), 				# memarg
"i64.load32_u":	(spec_tload,), 				# memarg
"i32.store":	(spec_tstore,), 			# memarg
"i64.store":	(spec_tstore,), 			# memarg
"f32.store":	(spec_tstore,), 			# memarg
"f64.store":	(spec_tstore,), 			# memarg
"i32.store8":	(spec_tstore,), 			# memarg
"i32.store16":	(spec_tstore,), 			# memarg
"i64.store8":	(spec_tstore,), 			# memarg
"i64.store16":	(spec_tstore,), 			# memarg
"i64.store32":	(spec_tstore,),				# memarg
"memory.size":	(spec_memorysize,),
"memory.grow":	(spec_memorygrow,),

"i32.const":	(spec_tconst,),				# i32
"i64.const":	(spec_tconst,),				# i64
"f32.const":	(spec_tconst,),				# f32
"f64.const":	(spec_tconst,),				# f64

"i32.eqz":	(spec_ttestop,spec_ieqzN),
"i32.eq":	(spec_trelop,spec_ieqN),
"i32.ne":	(spec_trelop,spec_ineN),
"i32.lt_s":	(spec_trelop,spec_ilt_sN),
"i32.lt_u":	(spec_trelop,spec_ilt_uN),
"i32.gt_s":	(spec_trelop,spec_igt_sN),
"i32.gt_u":	(spec_trelop,spec_igt_uN),
"i32.le_s":	(spec_trelop,spec_ile_sN),
"i32.le_u":	(spec_trelop,spec_ile_uN),
"i32.ge_s":	(spec_trelop,spec_ige_sN),
"i32.ge_u":	(spec_trelop,spec_ige_uN),

"i64.eqz":	(spec_ttestop,spec_ieqzN),
"i64.eq":	(spec_trelop,spec_ieqN),
"i64.ne":	(spec_trelop,spec_ineN),
"i64.lt_s":	(spec_trelop,spec_ilt_sN),
"i64.lt_u":	(spec_trelop,spec_ilt_uN),
"i64.gt_s":	(spec_trelop,spec_igt_sN),
"i64.gt_u":	(spec_trelop,spec_igt_uN),
"i64.le_s":	(spec_trelop,spec_ile_sN),
"i64.le_u":	(spec_trelop,spec_ile_uN),
"i64.ge_s":	(spec_trelop,spec_ige_sN),
"i64.ge_u":	(spec_trelop,spec_ige_uN),

"f32.eq":	(spec_trelop,spec_feqN),
"f32.ne":	(spec_trelop,spec_fneN),
"f32.lt":	(spec_trelop,spec_fltN),
"f32.gt":	(spec_trelop,spec_fgtN),
"f32.le":	(spec_trelop,spec_fleN),
"f32.ge":	(spec_trelop,spec_fgeN),

"f64.eq":	(spec_trelop,spec_feqN),
"f64.ne":	(spec_trelop,spec_fneN),
"f64.lt":	(spec_trelop,spec_fltN),
"f64.gt":	(spec_trelop,spec_fgtN),
"f64.le":	(spec_trelop,spec_fleN),
"f64.ge":	(spec_trelop,spec_fgeN),

"i32.clz":	(spec_tunop,spec_iclzN),
"i32.ctz":	(spec_tunop,spec_ictzN),
"i32.popcnt":	(spec_tunop,spec_ipopcntN),
"i32.add":	(spec_tbinop,spec_iaddN),
"i32.sub":	(spec_tbinop,spec_isubN),
"i32.mul":	(spec_tbinop,spec_imulN),
"i32.div_s":	(spec_tbinop,spec_idiv_sN),
"i32.div_u":	(spec_tbinop,spec_idiv_uN),
"i32.rem_s":	(spec_tbinop,spec_irem_sN),
"i32.rem_u":	(spec_tbinop,spec_irem_uN),
"i32.and":	(spec_tbinop,spec_iandN),
"i32.or":	(spec_tbinop,spec_iorN),
"i32.xor":	(spec_tbinop,spec_ixorN),
"i32.shl":	(spec_tbinop,spec_ishlN),
"i32.shr_s":	(spec_tbinop,spec_ishr_sN),
"i32.shr_u":	(spec_tbinop,spec_ishr_uN),
"i32.rotl":	(spec_tbinop,spec_irotlN),
"i32.rotr":	(spec_tbinop,spec_irotrN),

"i64.clz":	(spec_tunop,spec_iclzN),
"i64.ctz":	(spec_tunop,spec_ictzN),
"i64.popcnt":	(spec_tunop,spec_ipopcntN),
"i64.add":	(spec_tbinop,spec_iaddN),
"i64.sub":	(spec_tbinop,spec_isubN),
"i64.mul":	(spec_tbinop,spec_imulN),
"i64.div_s":	(spec_tbinop,spec_idiv_sN),
"i64.div_u":	(spec_tbinop,spec_idiv_uN),
"i64.rem_s":	(spec_tbinop,spec_irem_sN),
"i64.rem_u":	(spec_tbinop,spec_irem_uN),
"i64.and":	(spec_tbinop,spec_iandN),
"i64.or":	(spec_tbinop,spec_iorN),
"i64.xor":	(spec_tbinop,spec_ixorN),
"i64.shl":	(spec_tbinop,spec_ishlN),
"i64.shr_s":	(spec_tbinop,spec_ishr_sN),
"i64.shr_u":	(spec_tbinop,spec_ishr_uN),
"i64.rotl":	(spec_tbinop,spec_irotlN),
"i64.rotr":	(spec_tbinop,spec_irotrN),

"f32.abs":	(spec_tunop,spec_fabsN),
"f32.neg":	(spec_tunop,spec_fnegN),
"f32.ceil":	(spec_tunop,spec_fceilN),
"f32.floor":	(spec_tunop,spec_ffloorN),
"f32.trunc":	(spec_tunop,spec_ftruncN),
"f32.nearest":	(spec_tunop,spec_fnearestN),
"f32.sqrt":	(spec_tunop,spec_fsqrtN),
"f32.add":	(spec_tbinop,spec_faddN),
"f32.sub":	(spec_tbinop,spec_fsubN),
"f32.mul":	(spec_tbinop,spec_fmulN),
"f32.div":	(spec_tbinop,spec_fdivN),
"f32.min":	(spec_tbinop,spec_fminN),
"f32.max":	(spec_tbinop,spec_fmaxN),
"f32.copysign":	(spec_tbinop,spec_fcopysignN),

"f64.abs":	(spec_tunop,spec_fabsN),
"f64.neg":	(spec_tunop,spec_fnegN),
"f64.ceil":	(spec_tunop,spec_fceilN),
"f64.floor":	(spec_tunop,spec_ffloorN),
"f64.trunc":	(spec_tunop,spec_ftruncN),
"f64.nearest":	(spec_tunop,spec_fnearestN),
"f64.sqrt":	(spec_tunop,spec_fsqrtN),
"f64.add":	(spec_tbinop,spec_faddN),
"f64.sub":	(spec_tbinop,spec_fsubN),
"f64.mul":	(spec_tbinop,spec_fmulN),
"f64.div":	(spec_tbinop,spec_fdivN),
"f64.min":	(spec_tbinop,spec_fminN),
"f64.max":	(spec_tbinop,spec_fmaxN),
"f64.copysign":	(spec_tbinop,spec_fcopysignN),

"i32.wrap/i64":		(spec_t2cvtopt1,spec_wrapMN),
"i32.trunc_s/f32":	(spec_t2cvtopt1,spec_trunc_sMN),
"i32.trunc_u/f32":	(spec_t2cvtopt1,spec_trunc_uMN),
"i32.trunc_s/f64":	(spec_t2cvtopt1,spec_trunc_sMN),
"i32.trunc_u/f64":	(spec_t2cvtopt1,spec_trunc_uMN),
"i64.extend_s/i32":	(spec_t2cvtopt1,spec_extend_sMN),
"i64.extend_u/i32":	(spec_t2cvtopt1,spec_extend_uMN),
"i64.trunc_s/f32":	(spec_t2cvtopt1,spec_trunc_sMN),
"i64.trunc_u/f32":	(spec_t2cvtopt1,spec_trunc_uMN),
"i64.trunc_s/f64":	(spec_t2cvtopt1,spec_trunc_sMN),
"i64.trunc_u/f64":	(spec_t2cvtopt1,spec_trunc_uMN),
"f32.convert_s/i32":	(spec_t2cvtopt1,spec_convert_sMN),
"f32.convert_u/i32":	(spec_t2cvtopt1,spec_convert_uMN),
"f32.convert_s/i64":	(spec_t2cvtopt1,spec_convert_sMN),
"f32.convert_u/i64":	(spec_t2cvtopt1,spec_convert_uMN),
"f32.demote/f64":	(spec_t2cvtopt1,spec_demoteMN),
"f64.convert_s/i32":	(spec_t2cvtopt1,spec_convert_sMN),
"f64.convert_u/i32":	(spec_t2cvtopt1,spec_convert_uMN),
"f64.convert_s/i64":	(spec_t2cvtopt1,spec_convert_sMN),
"f64.convert_u/i64":	(spec_t2cvtopt1,spec_convert_uMN),
"f64.promote/f32":	(spec_t2cvtopt1,spec_promoteMN),
"i32.reinterpret/f32":	(spec_t2cvtopt1,spec_reinterprett1t2),
"i64.reinterpret/f64":	(spec_t2cvtopt1,spec_reinterprett1t2),
"f32.reinterpret/i32":	(spec_t2cvtopt1,spec_reinterprett1t2),
"f64.reinterpret/i64":	(spec_t2cvtopt1,spec_reinterprett1t2),

"invoke":		(spec_invoke_function_address,)
}







# this is the main loop over instr* end
# this is not in the spec
def instrstarend_loop(config):
  if verbose>=1: print("instrstar_loop()")
  while 1:
    instr = config["instrstar"][config["idx"]][0]  # idx<len(instrs) since instrstar[-1]=="end" which changes instrstar
    #print()
    #print(" ",instr)
    #immediate = None if len(config["instrstar"][config["idx"]])==1 else config["instrstar"][config["idx"]][1]
    ret = opcode2exec[instr][0](config)
    #print("  len(F)",len(config["F"]))
    #print("  config[control_stack]",config["control_stack"])
    #print("  config[operand_stack]",config["operand_stack"])
    #print("  config[instrstar]",config["instrstar"])
    #print("  config[idx]",config["idx"])
    if ret: return ret,config["operand_stack"]	#eg "trap" or "done"




# this executes instr* end. This deviates from the spec.
def spec_expr(config):
  if verbose>=1: print("spec_expr(",")")
  #S = config["S"]
  #F = config["F"]
  #operand_stack = config["operand_stack"]
  #control_stack = config["control_stack"]
  #iterate over list of instructions and nested lists of instructions
  #idx = config["idx"]
  #if len(config["instrstar"])==0: return operand_stack
  #print(instrstar)
  config["idx"]=0
  while 1:
    instr = config["instrstar"][config["idx"]][0]  # idx<len(instrs) since instrstar[-1]=="end" which changes instrstar
    #print(instr)
    #immediate = None if len(config["instrstar"][config["idx"]])==1 else config["instrstar"][config["idx"]][1]
    ret = opcode2exec[instr][0](config)
    if ret == "trap": raise Exception("trap")
    if ret == "exhaustion": raise Exception("exhaustion") 
    if ret: return config["operand_stack"]
    #print("locals",F[-1]["locals"])
    if verbose >= 2: print("operand_stack",config["operand_stack"])
    #print("control_stack",len(config["control_stack"]),config["control_stack"])
    #print()
    if verbose >= 4: print("control_stack",config["control_stack"])
  #return "done",config["operand_stack"]





#############
# 4.5 MODULES
#############

# 4.5.1 EXTERNAL TYPING

def spec_external_typing(S,externval):
  if verbose>=1: print("spec_external_typing(",externval,")")
  if "func" == externval[0]:
    a = externval[1]
    if len(S["funcs"])<a: raise Exception("unlinkable")
    funcinst = S["funcs"][a]
    return ["func",funcinst["type"]]
  elif "table" == externval[0]:
    a = externval[1]
    if len(S["tables"])<a: raise Exception("unlinkable")
    tableinst = S["tables"][a]
    return ["table",[{"min":len(tableinst["elem"]),"max":tableinst["max"]},"anyfunc"]]
  elif "mem" == externval[0]:
    a = externval[1]
    if len(S["mems"])<a: raise Exception("unlinkable")
    meminst = S["mems"][a]
    return ["mem",{"min":len(meminst["data"])//65536,"max":meminst["max"]}]  #page size = 64 Ki = 65536
  elif "global" == externval[0]:
    a = externval[1]
    if len(S["globals"])<a: raise Exception("unlinkable")
    globalinst = S["globals"][a]
    return [ "global", [globalinst["mut"],globalinst["value"][0][:3]] ]
  else:
    raise Exception("unlinkable")


# 4.5.2 IMPORT MATCHING

def spec_externtype_matching_limits(limits1,limits2):
  if verbose>=1: print("spec_externtype_matching_limits(",limits1,limits2,")")
  n1 = limits1["min"]
  m1 = limits1["max"]
  n2 = limits2["min"]
  m2 = limits2["max"]
  if n1<n2: raise Exception("unlinkable")
  if m2==None or (m1!=None and m2!=None and m1<=m2): return "<="
  else: raise Exception("unlinkable")

def spec_externtype_matching(externtype1,externtype2):
  if verbose>=1: print("spec_externtype_matching(",externtype1,externtype2,")")
  if "func"==externtype1[0] and "func"==externtype2[0]:
    if externtype1[1] == externtype2[1]:
      return "<="
  elif "table"==externtype1[0] and "table"==externtype2[0]:
    limits1 = externtype1[1][0]
    limits2 = externtype2[1][0]
    spec_externtype_matching_limits(limits1,limits2)
    elemtype1 = externtype1[1][1]
    elemtype2 = externtype2[1][1]
    if elemtype1 == elemtype2:
      return "<="
  elif "mem"==externtype1[0] and "mem"==externtype2[0]:
    limits1 = externtype1[1]
    limits2 = externtype2[1]
    if spec_externtype_matching_limits(limits1,limits2) == "<=":
      return "<="
  elif "global"==externtype1[0] and "global"==externtype2[0]:
    if externtype1[1] == externtype2[1]:
      return "<="
  raise Exception("unlinkable")


# 4.5.3 ALLOCATION

def spec_allocfunc(S,func,moduleinst):
  if verbose>=1: print("spec_allocfunc(",")")
  funcaddr = len(S["funcs"])
  functype = moduleinst["types"][func["type"]]
  funcinst = {"type":functype, "module":moduleinst, "code":func}
  S["funcs"].append(funcinst)
  return S,funcaddr

def spec_allochostfunc(S,functype,hostfunc):
  if verbose>=1: print("spec_allochostfunc(",")")
  funcaddr = len(S["funcs"])
  funcinst = {"type":functype, "hostcode":hostfunc}
  S["funcs"].append(funcinst)
  return S,funcaddr

def spec_alloctable(S,tabletype):
  if verbose>=1: print("spec_alloctable(",")")
  min_ = tabletype[0]["min"]
  max_ = tabletype[0]["max"]
  tableaddr = len(S["tables"])  
  tableinst = {"elem":[None for i in range(min_)], "max":max_}
  S["tables"].append(tableinst)
  return S,tableaddr

def spec_allocmem(S,memtype):
  if verbose>=1: print("spec_allocmem(",")")
  min_ = memtype["min"]
  max_ = memtype["max"]
  memaddr = len(S["mems"])
  meminst = {"data":bytearray(min_*65536), "max":max_}  #page size = 64 Ki = 65536
  S["mems"].append(meminst)
  return S,memaddr

def spec_allocglobal(S,globaltype,val):
  if verbose>=1: print("spec_allocglobal(",")")
  #print("spec_allocglobal(",")")
  #print(globaltype)
  mut = globaltype[0]
  valtype = globaltype[1]
  globaladdr = len(S["globals"])
  globalinst = {"value":[valtype+".const",val], "mut":mut}
  S["globals"].append(globalinst)
  return S,globaladdr
  
def spec_growtable(tableinst,n):
  if verbose>=1: print("spec_growtable(",")")
  len_ = n + len(tableinst["elem"])
  if len_>2**32: return "fail"
  if tablinst["max"]!=None and tableinst["max"] < len_: return "fail" #TODO: what does fail mean? raise Exception("trap")
  tableinst["elem"]+=[None for i in range(n)]
  return tableinst

def spec_growmem(meminst,n):
  if verbose>=1: print("spec_growmem(",")")
  #print("ok",len(meminst["data"]))
  assert len(meminst["data"])%65536 == 0        #ie divisible by page size = 64 Ki = 65536
  len_ = n + len(meminst["data"])//65536
  if len_>2**16: return "fail"
  if (meminst["max"]!=None and meminst["max"] < len_): return "fail"; #TODO: what does fail mean? raise Exception("trap")
  #if len_+len(meminst["data"]) > 2**32: return "fail" # raise Exception("grow mem") #TODO: this is not part of the spec, maybe should be
  #else:
  meminst["data"] += bytearray(n*65536) # each page created with bytearray(65536) which is 0s

  

def spec_allocmodule(S,module,externvalimstar,valstar):  
  if verbose>=1: print("spec_allocmodule(",")")
  moduleinst = {
     "types": module["types"],
     "funcaddrs": None,
     "tableaddrs": None,
     "memaddrs": None,
     "globaladdrs": None,
     "exports": None
    }
  funcaddrstar = [spec_allocfunc(S,func,moduleinst)[1] for func in module["funcs"]]
  tableaddrstar = [spec_alloctable(S,table["type"])[1] for table in module["tables"]]
  memaddrstar = [spec_allocmem(S,mem["type"])[1] for mem in module["mems"]]
  globaladdrstar = [spec_allocglobal(S,global_["type"],valstar[idx])[1] for idx,global_ in enumerate(module["globals"])]
  funcaddrmodstar = structure.spec_funcs(externvalimstar) + funcaddrstar
  tableaddrmodstar = structure.spec_tables(externvalimstar) + tableaddrstar
  memaddrmodstar = structure.spec_mems(externvalimstar) + memaddrstar
  globaladdrmodstar = structure.spec_globals(externvalimstar) + globaladdrstar
  exportinststar = []
  for exporti in module["exports"]:
    if exporti["desc"][0] == "func":
      x = exporti["desc"][1]
      externvali = ["func", funcaddrmodstar[x]]
    elif exporti["desc"][0] == "table":
      x = exporti["desc"][1]
      externvali = ["table", tableaddrmodstar[x]]
    elif exporti["desc"][0] == "mem":
      x = exporti["desc"][1]
      externvali = ["mem", memaddrmodstar[x]]
    elif exporti["desc"][0] == "global":
      x = exporti["desc"][1]
      externvali = ["global", globaladdrmodstar[x]]
    exportinststar += [{"name": exporti["name"], "value": externvali}]
  moduleinst["funcaddrs"] = funcaddrmodstar
  moduleinst["tableaddrs"] = tableaddrmodstar
  moduleinst["memaddrs"] = memaddrmodstar
  moduleinst["globaladdrs"] = globaladdrmodstar
  moduleinst["exports"] = exportinststar
  return S,moduleinst 


def spec_instantiate(S,module,externvaln):
  if verbose>=1: print("spec_instantiate(",")")
  # 1
  # 2
  ret = validation.spec_validate_module(module)
  externtypeimn,externtypeexstar = ret
  # 3
  if len(module["imports"]) != len(externvaln): raise Exception("unlinkable")
  # 4
  for i in range(len(externvaln)):
    externtypei = spec_external_typing(S,externvaln[i])
    spec_externtype_matching(externtypei,externtypeimn[i])
  # 5
  valstar = []
  moduleinstim = {"globaladdrs":[externval[1] for externval in externvaln if "global"==externval[0]]}
  Fim = {"module":moduleinstim, "locals":[], "arity":1, "height":0}
  framestack = []
  framestack += [Fim]
  for globali in module["globals"]:
    config = {"S":S,"F":framestack,"instrstar":globali["init"],"idx":0,"operand_stack":[],"control_stack":[]}
    ret = spec_expr( config )[0]
    valstar += [ ret ]
  framestack.pop()
  # 6
  S,moduleinst = spec_allocmodule(S,module,externvaln,valstar)
  # 7
  F={"module":moduleinst, "locals":[]}
  # 8
  framestack += [F]
  # 9
  tableinst = []
  eo = []
  for elemi in module["elem"]:
    config = {"S":S,"F":framestack,"instrstar":elemi["offset"],"idx":0,"operand_stack":[],"control_stack":[]}
    eovali = spec_expr(config)[0]
    eoi = eovali
    eo+=[eoi]
    tableidxi = elemi["table"]
    tableaddri = moduleinst["tableaddrs"][tableidxi]
    tableinsti = S["tables"][tableaddri]
    tableinst+=[tableinsti]
    #print("eoi",eoi)
    eendi = eoi+len(elemi["init"])
    if eendi > len(tableinsti["elem"]): raise Exception("unlinkable")
  # 10
  meminst = []
  do = []
  for datai in module["data"]:
    config = {"S":S,"F":framestack,"instrstar":datai["offset"],"idx":0,"operand_stack":[],"control_stack":[]}
    dovali = spec_expr(config)[0]
    doi = dovali
    do+=[doi]
    memidxi = datai["data"]
    memaddri = moduleinst["memaddrs"][memidxi]
    meminsti = S["mems"][memaddri]
    meminst += [meminsti]
    dendi = doi+len(datai["init"])
    if dendi > len(meminsti["data"]): raise Exception("unlinkable")
  # 11
  # 12
  framestack.pop()
  # 13
  for i,elemi in enumerate(module["elem"]):
    for j,funcidxij in enumerate(elemi["init"]):
      funcaddrij = moduleinst["funcaddrs"][funcidxij]
      tableinst[i]["elem"][eo[i]+j] = funcaddrij
  # 14
  for i,datai in enumerate(module["data"]):
    for j,bij in enumerate(datai["init"]):
      meminst[i]["data"][do[i]+j] = bij
  # 15
  ret = None
  if module["start"]:
    funcaddr = moduleinst["funcaddrs"][ module["start"]["func"] ]
    ret = spec_invoke(S,funcaddr,[])
  return S,F,ret


    
# 4.5.5 INVOCATION

# valn looks like [["i32.const",3],["i32.const",199], ...]
def spec_invoke(S,funcaddr,valn):
  if verbose>=1: print("spec_invoke(",")")
  # 1
  if len(S["funcs"]) < funcaddr or funcaddr < 0: raise Exception("bad address")
  # 2
  funcinst = S["funcs"][funcaddr]  
  # 5
  t1n,t2m = funcinst["type"]
  # 4
  if len(valn)!=len(t1n): raise Exception("wrong number of arguments")
  # 5
  for ti,vali in zip(t1n,valn):
    if vali[0][:3]!=ti: raise Exception("argument type mismatch")
  # 6
  operand_stack = []
  for ti,vali in zip(t1n,valn):
    arg=vali[1]
    if type(arg)==str:
      if ti[0]=="i": arg = int(arg)
      if ti[0]=="f": arg = float(arg)
    operand_stack += [arg]
  # 7
  valresm=None
  if "code" in funcinst:
    #config = {"S":S,"F":[],"instrstar":funcinst["code"]["body"],"idx":0,"operand_stack":operand_stack,"control_stack":[]}  #TODO: toggle these back when uncomment main loop execution
    #valresm = spec_invoke_function_address(config,funcaddr)  #TODO: toggle these back when uncomment main loop execution 
    config = {"S":S,"F":[],"instrstar":[["invoke",funcaddr],["end",None]],"idx":0,"operand_stack":operand_stack,"control_stack":[]}
    valresm = spec_expr(config) #instrstarend_loop(config)
    #moved this here from bottom
    return valresm
  elif "hostcode" in funcinst:
    S,valresm = funcinst["hostcode"](S,operand_stack)
    #moved this here from bottom
    return valresm
  else: raise Exception("")
  #return valresm  #TODO: toggle these back when uncomment main loop execution


