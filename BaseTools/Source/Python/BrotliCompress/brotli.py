## @file
# Command line interface for BrotliCompress tool
# for compression/decompression using the Brotli algorithm.
#
# Copyright (c) 2022, Intel Corporation. All rights reserved.<BR>
# SPDX-License-Identifier: BSD-2-Clause-Patent
##

import sys
import _brotli
import os
import argparse

# The library version
__version__ = _brotli.__version__

# The Compressor object
Compressor = _brotli.Compressor

# Brotli defaults
BROTLI_DEFAULT_LGWIN = 22
BROTLI_MIN_WINDOW_BITS = 10
BROTLI_MAX_WINDOW_BITS = 24
BROTLI_WINDOW_GAP = 16
BROTLI_DEFAULT_LGBLOCK = 0
BROTLI_DEFAULT_QUALITY = 9
DECODE_HEADER_SIZE = 0x10

def calc_lgwin(datalen):
    lgwin = BROTLI_MIN_WINDOW_BITS
    max_backward_limit = lambda w: (1 << w) - BROTLI_WINDOW_GAP

    while (max_backward_limit(lgwin) < datalen and
            lgwin < BROTLI_MAX_WINDOW_BITS):
        lgwin += 1
    return lgwin

def compress(data, quality=BROTLI_DEFAULT_QUALITY, lgwin=BROTLI_DEFAULT_LGWIN,
             lgblock=BROTLI_DEFAULT_LGBLOCK, mode=_brotli.MODE_GENERIC,
             backward=False):
    compressor = _brotli.Compressor(mode=mode, quality=quality, lgwin=lgwin,
                                    lgblock=lgblock)
    output = compressor.process(data) + compressor.finish()

    if backward:
        input_len_arr = int.to_bytes(len(data), DECODE_HEADER_SIZE, 'little')
        output = input_len_arr + output
    return output

def decompress(data):
    try:
        return _brotli.decompress(data)
    except _brotli.error as e:
        # Backward compatibility: try to extract the extra header
        if len(data) > DECODE_HEADER_SIZE:
            data = data[DECODE_HEADER_SIZE:len(data)]
            return _brotli.decompress(data)
        else:
            raise e

def setup_parser():
    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        description='''
        Compression/decompression tool using the Brotli algorithm.
        ''')

    parser.add_argument(
    '-v',
    '--version',
    action='version',
    version=__version__)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-e',
        '--compress',
        action='store_true',
        help='Compress input file'
    )
    group.add_argument(
        '-d',
        '--decompress',
        action='store_true',
        help='Decompress input file'
    )

    parser.add_argument(
        'infile',
        metavar='input_file',
        type=str,
        help='Input file'
    )
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        help='Output file',
        required=True
    )

    parser.add_argument(
        '-q',
        '--quality',
        type=int,
        choices=range(0, 12),
        default=BROTLI_DEFAULT_QUALITY,
        metavar='QUALITY',
        help='Compression Level (0-11)'
    )
    # TODO remove as not used?
    parser.add_argument(
        '-g',
        '--gap',
        type=int,
        choices=range(1, 17),
        default=1,
        metavar='GAP',
        help='Scratch memory gap level (1-16)'
    )

    parser.add_argument(
        '-lw',
        '--lgwin',
        type=int,
        choices=range(10, 25),
        metavar='LGWIN',
        help='Base 2 logarithm of the sliding window size (10-24). '
        'Default is based on the input file size'
    )
    parser.add_argument(
        '-lb',
        '--lgblock',
        type=int,
        choices=[0] + list(range(16, 25)),
        default=0,
        metavar='LGBLOCK',
        help='Base 2 logarithm of the maximum input block size. '
        'Values: 0, 16-24. Default is 0 that means that the value '
        'will be based on the quality'
    )

    parser.add_argument(
        '-b',
        '--backward',
        action='store_true',
        default=False,
        help='Compress with an extra header to match '
        'the previous Tianocore Brotli version'
    )

    return parser

def main(args=None):
    parser = setup_parser()
    options = parser.parse_args(args=args)
    if not os.path.isfile(options.infile):
        parser.error(f'File {options.infile} not found')
    with open(options.infile, 'rb') as infile:
        data = infile.read()

    outfile = open(options.output, 'wb')

    try:
        if options.compress:
            if options.lgwin == None:
                options.lgwin = calc_lgwin(len(data))
            data = compress(data, options.quality, lgwin=options.lgwin,
                            lgblock=options.lgblock, backward=options.backward)
        else:
            data = decompress(data)
    except _brotli.error as e:
        parser.exit(1, f'brotli error: {e}: {options.infile}')

    outfile.write(data)
    outfile.close()

if __name__ == '__main__':
    main()
