import concurrent.futures
import glob
import hashlib
import os

import click
import pandas as pd

NUM_THREADS = 20

def get_file_stats(file_path):
    """Get the size of the file in bytes. Compute the MD5 checksum of the file"""
    with open(file_path, "rb") as f:
        file_data = f.read()
    md5sum =  hashlib.md5(file_data).hexdigest()
    return os.path.getsize(file_path), md5sum


@click.command()
@click.option("--results_dir")
@click.option("--output_file")
def main(results_dir, output_file):
    combined_stats = []
    all_files = []
    pred_pattern = os.path.join(results_dir, "*", "*", "Predictions", "abc_predictions_*")
    peak_pattern = os.path.join(results_dir, "*", "*", "Peaks", "abc_predictions_*")
    # all_files += glob.glob(pred_pattern)
    all_files += glob.glob(peak_pattern)
    print(f"Computing stats for {len(all_files)} files")
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = {
            executor.submit(get_file_stats, file): os.path.basename(file)
            for file in all_files
        }

        for future in concurrent.futures.as_completed(futures.keys()):
            file = futures[future]
            file_size, md5sum = future.result()
            combined_stats.append({"file": file, "md5sum": md5sum, "file_size": file_size})

    pd.DataFrame(combined_stats).to_csv(output_file, sep='\t', header=False, index=False)

if __name__ == "__main__":
    main()