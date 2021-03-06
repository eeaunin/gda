#!/usr/bin/env python3
"""
Script for converting coverage data (based on SAMtools depth) to bedgraph format. Output (STDOUT): a bedgraph file with mean coverage of fixed length chunks of scaffolds
"""
# MIT License
# 
# Copyright (c) 2020-2021 Genome Research Ltd.
# 
# Author: Eerik Aunin (ea10@sanger.ac.uk)
# 
# This file is a part of the Genome Decomposition Analysis (GDA) pipeline.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
import general_purpose_functions as gpf
import numpy as np


def process_buffer(buffer_array, buffer_array_index, buffer_array_start_window):
    """
    Finds the average coverage in the data for one window
    """
    split_buffer_array_start_window = buffer_array_start_window.split()
    buffer_array_start_coord = int(split_buffer_array_start_window[1]) - 1
    buffer_array_end_coord = buffer_array_start_coord + buffer_array_index
    buffer_array_scaff = split_buffer_array_start_window[0]
    buffer_array = buffer_array[0:buffer_array_index]
    window_mean_coverage = np.mean(buffer_array)
    out_line = buffer_array_scaff + " " + str(buffer_array_start_coord) + " " + str(buffer_array_end_coord) + " " + str(window_mean_coverage)
    print(out_line)


def main(samtools_depth_path, header_title, chunk_size):
    bedgraph_header = 'track type=bedGraph name="' + header_title + '" description="' + header_title + '" visibility=full color=0,0,255 altColor=0,100,200 priority=20'
    print(bedgraph_header)

    in_data = gpf.ll(samtools_depth_path)
    buffer_array = np.zeros(chunk_size)
    buffer_array_index = 0
    previous_scaff_name = None
    buffer_array_start_window = None
    for line in in_data:
        split_line = line.split()
        scaff_name = split_line[0]
        if scaff_name != previous_scaff_name and previous_scaff_name is not None:
            process_buffer(buffer_array, buffer_array_index, buffer_array_start_window)
            buffer_array_index = 0
        samtools_depth_value = int(line.split()[2])
        if buffer_array_index == 0:
            buffer_array_start_window = line
        buffer_array[buffer_array_index] = samtools_depth_value
        buffer_array_index += 1
        if buffer_array_index == chunk_size:
            process_buffer(buffer_array, buffer_array_index, buffer_array_start_window)
            buffer_array = np.zeros(chunk_size)
            buffer_array_index = 0
        previous_scaff_name = scaff_name
    if buffer_array_index > 0:
        process_buffer(buffer_array, buffer_array_index, buffer_array_start_window)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("samtools_depth_path", type=str, help="Path to SAMtools depth file")
    parser.add_argument("header_title", type=str, help="Title for bedgraph file header")
    parser.add_argument("--chunk_size", type=int, help="Chunk size (sliding window step size) in base pairs. Default: 5000", default=5000)
    args = parser.parse_args()
    main(args.samtools_depth_path, args.header_title, args.chunk_size)
