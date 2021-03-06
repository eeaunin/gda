#!/usr/bin/env python3
"""
Script for running Barrnap for detecting rRNAs
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
import os
import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
import general_purpose_functions as gpf


def main(pipeline_run_folder, assembly_fasta_path, kingdom, threads):
    gene_annotation_folder = pipeline_run_folder + "/gene_annotation"
    gpf.run_system_command("mkdir -p " + gene_annotation_folder)
    barrnap_folder = gene_annotation_folder + "/barrnap"
    gpf.run_system_command("mkdir -p " + barrnap_folder)
    fasta_filename = assembly_fasta_path.split("/")[-1]
    fasta_basename = fasta_filename.split(".")[0]

    temp_fasta_path = barrnap_folder + "/seq_for_barrnap.fa"
    barrnap_gff_path = barrnap_folder + "/" + fasta_basename + "_Barrnap_rRNAs.gff3"

    # A short sequence of ATGC repeated 3 times is added to the start of the FASTA file. This is a workaround for a bug in Barrnap, where the nhmmer component of Barrnap fails to recognise
    #   the input sequence as DNA if does not find A, T, G and C nucleotides all present at the start of the first sequence in the input FASTA file.
    # https://github.com/tseemann/barrnap/issues/54
    barrnap_temp_file_command = "echo '>artificial_sequence_for_barrnap' > {}; echo 'ATGCATGCATGC' | cat - {} >> {}".format(temp_fasta_path, assembly_fasta_path, temp_fasta_path)
    gpf.run_system_command(barrnap_temp_file_command)

    barrnap_command = "barrnap --kingdom {} --threads {} {} > {}".format(kingdom, threads, temp_fasta_path, barrnap_gff_path)
    gpf.run_system_command(barrnap_command)
    os.remove(temp_fasta_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pipeline_run_folder", type=str, help="Folder for running the pipeline")
    parser.add_argument("assembly_fasta_path", type=str, help="Path to input FASTA file")
    parser.add_argument("--kingdom", type=str, help="Super kingdom of the species. Options: 'bac' (bacteria), 'arc' (archaea), 'euk' (eukaryota), 'mito': metazoan mitochondria. Default: 'euk'", choices=["bac", "arc", "euk", "mito"], default="euk")
    parser.add_argument("--threads", type=int, help="Number of threads (default: 1)", default=1)
    args = parser.parse_args()
    main(args.pipeline_run_folder, args.assembly_fasta_path, args.kingdom, args.threads)
