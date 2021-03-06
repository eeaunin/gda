#!/usr/bin/env python3
"""
Script for running wgsim to generate simulated reads, mapping these reads and finding their coverage
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

import general_purpose_functions as gpf
import argparse

def get_assembly_size(assembly_path):
    """
    Input: path to assembly FASTA file
    Output: assembly size (bp)
    """
    assembly_data = gpf.read_fasta_in_chunks(assembly_path)
    assembly_size = 0
    for fasta_tuple in assembly_data:
        seq = fasta_tuple[1]
        assembly_size += len(seq)
    return assembly_size


def main(fasta_path, wgsim_folder, pipeline_output_folder, chunk_size, threads, target_coverage):

    assembly_size = get_assembly_size(fasta_path)

    number_of_read_pairs = (assembly_size * target_coverage) / (150 * 2)

    fasta_basename = fasta_path.split("/")[-1]
    fasta_basename = fasta_basename.split(".")[0]

    reads_1_path = wgsim_folder + "/{}_wgsim_reads1.fq".format(fasta_basename)
    reads_2_path = wgsim_folder + "/{}_wgsim_reads2.fq".format(fasta_basename)
    wgsim_stdout_path = wgsim_folder + "/{}_wgsim_stdout.txt".format(fasta_basename)

    gpf.run_system_command("mkdir -p " + wgsim_folder)
    wgsim_command = "wgsim -S 1 -e 0 -N {} -1 150 -2 150 -r 0 -R 0 -X 0 -h -d 500 {} {} {} > {}".format(number_of_read_pairs, fasta_path, reads_1_path, reads_2_path, wgsim_stdout_path)
    gpf.run_system_command(wgsim_command)

    gzip_command1 = "gzip " + reads_1_path
    gzip_command2 = "gzip " + reads_2_path
    gzipped_reads_1_path = reads_1_path + ".gz"
    gzipped_reads_2_path = reads_2_path + ".gz"
    gpf.run_system_command(gzip_command1)
    gpf.run_system_command(gzip_command2)

    sam_file_path = wgsim_folder + "/{}_wgsim_reads_minimap2.sam".format(fasta_basename)

    minimap2_command = "minimap2 -ax sr -t {} {} {} {} > {}".format(str(threads), fasta_path, gzipped_reads_1_path, gzipped_reads_2_path, sam_file_path)
    gpf.run_system_command(minimap2_command)

    sort_sam_command = "sam_to_sorted_indexed_bam.py {} {}".format(sam_file_path, threads)
    gpf.run_system_command(sort_sam_command)

    sorted_bam_file_path = wgsim_folder + "/{}_wgsim_reads_minimap2_sorted.bam".format(fasta_basename)
    sorted_filtered_bam_file_path = wgsim_folder + "/{}_wgsim_reads_minimap2_sorted_filtered.bam".format(fasta_basename)

    filter_bam_by_mapq_command = "samtools view -bq 60 -@ {} {} > {}".format(threads, sorted_bam_file_path, sorted_filtered_bam_file_path)
    gpf.run_system_command(filter_bam_by_mapq_command)

    remove_sorted_bam_command = "rm " + sorted_bam_file_path
    gpf.run_system_command(remove_sorted_bam_command)

    samtools_depth_path = wgsim_folder + "/{}_wgsim_reads_minimap2_samtools_depth.txt".format(fasta_basename)

    samtools_depth_command = "samtools depth -aa {} --reference {} > {}".format(sorted_filtered_bam_file_path, fasta_path, samtools_depth_path)
    gpf.run_system_command(samtools_depth_command)

    samtools_depth_bedgraph_path = pipeline_output_folder + "/{}_wgsim_minimap2_coverage.bedgraph".format(fasta_basename)
    depth_to_bedgraph_command = "samtools_depth_to_bedgraph.py {} wgsim_depth_minimap2 --chunk_size {} > {}".format(samtools_depth_path, chunk_size, samtools_depth_bedgraph_path)
    gpf.run_system_command(depth_to_bedgraph_command)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fasta_path", type=str, help="Path to input FASTA file")
    parser.add_argument("wgsim_folder", type=str, help="Folder for running the mapping of simulated reads")
    parser.add_argument("pipeline_output_folder", type=str, help="Folder for outputting the bedgraph file")
    parser.add_argument("--chunk_size", type=int, help="Genome chunk size (bp) for generating the bedgraph file using sliding window (default: 5000)", default=5000)
    parser.add_argument("--threads", type=int, help="Number of threads (default: 1)", default=1)
    parser.add_argument("--target_coverage", type=int, help="Average coverage of simulated reads (default: 10)", default=10)
    args = parser.parse_args()
    main(args.fasta_path, args.wgsim_folder, args.pipeline_output_folder, args.chunk_size, args.threads, args.target_coverage)
