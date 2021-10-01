#!/usr/bin/env python3
"""
Script for counting kmer frequencies in a FASTA file using a sliding window
Output: bedgraph files for the counts of kmers in every sliding window step across the scaffolds in the input FASTA file
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
import kcounter


def kmer_likelihood(kmer_seq, nucleotide_likelihoods):
    """
    Calculates the likelihood of observing the kmer by chance, given the nucleotide composition of the sequence
    """
    likelihood = 1
    for nt in kmer_seq:
        likelihood = likelihood * nucleotide_likelihoods[nt]
    likelihood = likelihood * 2
    return likelihood


def main(fasta_path, chunk_size, kmer_size):
    fasta_data = gpf.read_fasta_in_chunks(fasta_path)

    feature_title = "kmer_deviation_kmer_size_" + str(kmer_size)
    bedgraph_header = 'track type=bedGraph name="' + feature_title + '" description="' + feature_title + '" visibility=full color=0,0,255 altColor=0,100,200 priority=20'
    print(bedgraph_header)

    for header, seq in fasta_data:
        seq = seq.upper()
        seq_chunks = gpf.string_to_chunks(seq, chunk_size)
        header = header.split()[0]
        for counter, seq_chunk in enumerate(seq_chunks):
            seq_chunk_len = len(seq_chunk)

            g_count = seq_chunk.count("G")
            c_count = seq_chunk.count("C")
            a_count = seq_chunk.count("A")
            t_count = seq_chunk.count("T")

            nucleotide_counts_sum = g_count + c_count + a_count + t_count

            if seq_chunk_len > 3 and nucleotide_counts_sum > 0:
                nucleotides_dict = kcounter.count_kmers(seq_chunk, kmer_size, canonical_kmers=True)

                nucleotides_dict["scaff"] = header
                nucleotides_dict["seq_chunk_len"] = seq_chunk_len
                start_pos = counter * chunk_size
                nucleotides_dict["start_pos"] = start_pos
                nucleotides_dict["end_pos"] = start_pos + seq_chunk_len

                seq_chunk_gc_ratio = (g_count + c_count) / nucleotide_counts_sum
                nucleotide_likelihoods = {"A": (1 - seq_chunk_gc_ratio) / 2, "T": (1 - seq_chunk_gc_ratio) / 2, "G": seq_chunk_gc_ratio / 2, "C": seq_chunk_gc_ratio / 2}

                kmer_counts = [nucleotides_dict[n] for n in nucleotides_dict.keys() if str(n) not in ("scaff", "start_pos", "end_pos", "seq_chunk_len")]
                kmer_counts_sum = sum(kmer_counts)

                kmer_likelihoods_sum = 0
                kmer_expected_counts_sum = 0
                kmer_deviation_sum = 0

                for item in nucleotides_dict.keys():
                    item = str(item)
                    if item not in ("scaff", "start_pos", "end_pos", "seq_chunk_len"):
                        kmer_likelihood_value = kmer_likelihood(item, nucleotide_likelihoods)
                        kmer_expected_count = kmer_likelihood_value * kmer_counts_sum
                        obs_expected_diff = abs(nucleotides_dict[item] - kmer_expected_count)
                        kmer_likelihoods_sum += kmer_likelihood_value
                        kmer_expected_counts_sum += kmer_expected_count
                        kmer_deviation_sum += obs_expected_diff
                print("{} {} {} {}".format(header, str(start_pos), str(start_pos + seq_chunk_len), str(kmer_deviation_sum)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fasta_path", type=str, help="Path to assembly FASTA file")
    parser.add_argument("--chunk_size", type=int, help="Chunk size (sliding window step size) in base pairs. Default: 5000", default=5000)
    parser.add_argument("--kmer_size", type=int, help="kmer size. Default: 3", default=3)
    args = parser.parse_args()
    main(args.fasta_path, args.chunk_size, args.kmer_size)




