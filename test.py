# 
# Compression application using adaptive arithmetic coding
# 
# Usage: python adaptive-arithmetic-compress.py InputFile OutputFile
# Then use the corresponding adaptive-arithmetic-decompress.py application to recreate the original input file.
# Note that the application starts with a flat frequency table of 257 symbols (all set to a frequency of 1),
# and updates it after each byte encoded. The corresponding decompressor program also starts with a flat
# frequency table and updates it after each byte decoded. It is by design that the compressor and
# decompressor have synchronized states, so that the data can be decompressed properly.
# 
# Copyright (c) Project Nayuki
# 
# https://www.nayuki.io/page/reference-arithmetic-coding
# https://github.com/nayuki/Reference-arithmetic-coding
# 

import contextlib, sys
import arithmeticcoding
import numpy as np
python3 = sys.version_info.major >= 3


# Command line main application function.
def main(binfile):
	#inp = np.random.randint(5,size=[10])
	#inp.tolist()
	inp = [1,1,1,1,1,1,1,1,1,1]	
	with contextlib.closing(arithmeticcoding.BitOutputStream(open(binfile, "wb"))) as bitout:
		compress(inp, bitout)
	
	# Perform file decompression
	with open(binfile, "rb") as bitsfile:
		bitin = arithmeticcoding.BitInputStream(bitsfile)
		out = decompress(bitin)
	
	bpp = 1.0*-np.log(0.1)/np.log(2.0) + 9.0*-np.log(0.1)/np.log(2.0)+1.0*-np.log(0.3)/np.log(2.0)
	print bpp/8.0,"bytes"

	print inp,out

def pmf_quantization(pmf,precision=16):
	pmf = [int(i*(2**16)) for i in pmf]
	return pmf
		
def compress(inp, bitout):

	pmf = [0.2, 0.1, 0.3, 0.2, 0.2]
	pmf_new = [0.2, 0.1, 0.1, 0.3, 0.3]
	pmf = pmf_quantization(pmf)
	pmf_new = pmf_quantization(pmf_new)

	freqs = arithmeticcoding.ContextFrequencyTable(pmf)
	#freqs = arithmeticcoding.SimpleFrequencyTable(initfreqs)
	enc = arithmeticcoding.ArithmeticEncoder(32, bitout)
	for symbol in inp:
		# Read and encode one byte
		enc.write(freqs, symbol)
		freqs.increment(pmf_new)
	enc.write(freqs, 4)  # EOF
	enc.finish()  # Flush remaining code bits

def decompress(bitin):

	pmf = [0.2, 0.1, 0.3, 0.2, 0.2]
	pmf_new = [0.2, 0.1, 0.1, 0.3, 0.3]
	pmf = pmf_quantization(pmf)
	pmf_new = pmf_quantization(pmf_new)

	freqs = arithmeticcoding.ContextFrequencyTable(pmf)
	dec = arithmeticcoding.ArithmeticDecoder(32, bitin)
	out = []
	while True:
		# Decode and write one byte
		symbol = dec.read(freqs)
		if symbol == 4:  # EOF symbol
			break
		#out.append(bytes((symbol,)) if python3 else chr(symbol))
		out.append(symbol)
		freqs.increment(pmf_new)
	return out

# Main launcher
if __name__ == "__main__":
	#main(sys.argv[1 : ])
	main("test.bin")
