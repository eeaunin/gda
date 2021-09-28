#!/usr/bin/env python3
"""
Script for converting the output of decomposition_gc_skew_repeats_sliding_window.py to bedgraph format
"""

import general_purpose_functions as gpf
import argparse
import pandas as pd
import sys

def is_float(value):
    """
    https://stackoverflow.com/questions/736043/checking-if-a-string-can-be-converted-to-float-in-python
    """
    try:
        float(value)
        return True
    except ValueError:
        return False


def main(in_path, out_folder, fasta_path):
    fasta_basename = fasta_path.split("/")[-1]
    fasta_basename = fasta_basename.split(".")[0]

    gpf.run_system_command("mkdir -p " + out_folder)

    df = pd.read_csv(in_path, sep="\t", dtype=str)

    query_variables = list(df.columns.values.tolist())
    query_variables = query_variables[3:len(query_variables)]

    for query_variable in query_variables:
        out_path = out_folder + "/" + fasta_basename + "_" + query_variable + ".bedgraph"
        out_file = open(out_path, "w")
        header_line = "track type=bedGraph name=\"{}\" description=\"{}\" visibility=full color=0,0,255 altColor=0,100,200 priority=20".format(query_variable, query_variable)
        out_file.write(header_line + "\n")
        for row_tuple in df.iterrows():
            df_row = row_tuple[1]
            query_variable_value = df_row[query_variable]
            if is_float(query_variable_value):
                out_line = " ".join([df_row["scaffold"].split()[0], df_row["start_pos"], df_row["end_pos"], df_row[query_variable]])
                out_file.write(out_line + "\n")
            else:
                sys.stderr.write("Non-numeric value encountered (" + query_variable + "): " + str(df_row) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("in_path", type=str, help="Path to the output file of decomposition_gc_skew_repeats_sliding_window.py")
    parser.add_argument("out_folder", type=str, help="Path to folder for output files")
    parser.add_argument("fasta_path", type=str, help="Path to assembly FASTA file")
    args = parser.parse_args()
    main(args.in_path, args.out_folder, args.fasta_path)