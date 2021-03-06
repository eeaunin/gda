#!/usr/bin/env python3
"""
Script for converting tRNAscan output BED file to GFF3 format
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

import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
import general_purpose_functions as gpf
import genome_decomp_pipeline_shared_functions
from genome_decomp_pipeline_shared_functions import print_gff_header_based_on_fasta


def main(fasta_path, bed_file_path):
    print_gff_header_based_on_fasta(fasta_path)
    bed_file_data = gpf.l(bed_file_path)

    for line in bed_file_data:
        split_line = line.split()
        scaff = split_line[0]
        feature_start = str(int(split_line[1]) + 1)
        feature_end = split_line[2]
        id = split_line[3]
        score = split_line[4]
        strand = split_line[5]
        out_line = "\t".join((scaff, "tRNAscan", "tRNA", feature_start, feature_end, score, strand, ".", "ID=" + id))
        print(out_line)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fasta_path", type=str, help="Path to assembly FASTA file")
    parser.add_argument("bed_file_path", type=str, help="Path to tRNAscan output BED file")
    args = parser.parse_args()
    main(args.fasta_path, args.bed_file_path)
