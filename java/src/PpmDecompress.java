/* 
 * Reference arithmetic coding
 * Copyright (c) Project Nayuki
 * 
 * https://www.nayuki.io/page/reference-arithmetic-coding
 * https://github.com/nayuki/Reference-arithmetic-coding
 */

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.Arrays;


/**
 * Decompression application using prediction by partial matching (PPM) with arithmetic coding.
 * <p>Usage: java PpmDecompress InputFile OutputFile</p>
 * <p>This decompresses files generated by the "PpmCompress" application.</p>
 */
public final class PpmDecompress {
	
	// Must be at least -1 and match PpmDecompress. Warning: Exponential memory usage at O(257^n).
	private static final int MODEL_ORDER = 3;
	
	
	public static void main(String[] args) throws IOException {
		// Handle command line arguments
		if (args.length != 2) {
			System.err.println("Usage: java PpmDecompress InputFile OutputFile");
			System.exit(1);
			return;
		}
		File inputFile  = new File(args[0]);
		File outputFile = new File(args[1]);
		
		// Perform file decompression
		try (BitInputStream in = new BitInputStream(new BufferedInputStream(new FileInputStream(inputFile)))) {
			try (OutputStream out = new BufferedOutputStream(new FileOutputStream(outputFile))) {
				decompress(in, out);
			}
		}
	}
	
	
	// To allow unit testing, this method is package-private instead of private.
	static void decompress(BitInputStream in, OutputStream out) throws IOException {
		// Set up encoder and model
		ArithmeticDecoder dec = new ArithmeticDecoder(in);
		PpmModel model = new PpmModel(MODEL_ORDER, 257, 256);
		int[] history = new int[0];
		
		while (true) {
			int symbol = decodeSymbol(dec, model, history);
			if (symbol == 256)  // EOF symbol
				break;
			out.write(symbol);
			model.incrementContexts(history, symbol);
			
			// Append current symbol or shift back by one
			if (model.modelOrder >= 1) {
				if (history.length < model.modelOrder)
					history = Arrays.copyOf(history, history.length + 1);
				else
					System.arraycopy(history, 1, history, 0, history.length - 1);
				history[history.length - 1] = symbol;
			}
		}
	}
	
	
	private static int decodeSymbol(ArithmeticDecoder dec, PpmModel model, int[] history) throws IOException {
		outer:
		for (int order = Math.min(history.length, model.modelOrder); order >= 0; order--) {
			PpmModel.Context ctx = model.rootContext;
			for (int i = history.length - order; i < history.length; i++) {
				if (ctx.subcontexts == null)
					throw new AssertionError();
				ctx = ctx.subcontexts[history[i]];
				if (ctx == null)
					continue outer;
			}
			int symbol = dec.read(ctx.frequencies);
			if (symbol < 256)
				return symbol;
			// Else the context escape symbol was encountered, so continue decrementing the order
		}
		// Logic for order = -1
		return dec.read(model.orderMinus1Freqs);
	}
	
}