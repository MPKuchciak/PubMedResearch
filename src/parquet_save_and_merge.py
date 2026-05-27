import os
import pandas as pd
from tqdm import tqdm

def save_and_merge_in_batches(
    df: pd.DataFrame,
    batch_size: int,
    output_folder: str,
    final_filename: str = "final_merged.parquet",
    temp_batch_prefix: str = "temp_batch_"
):
    """
    Splits 'df' into multiple batches (size = batch_size), writes each batch to a Parquet file,
    then merges them into one final Parquet, with a progress bar showing how many batches are done.

    Steps:
    ------
    1) Creates subfolder 'temp_batches' in output_folder for batch files.
    2) For each chunk of rows:
       - Writes it to 'temp_batch_X.parquet'
       - Increments a progress bar
    3) Reads & merges all batch files into 'final_filename', then removes them.

    Returns:
    --------
    str -> path to the final merged Parquet file.
    """

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Subfolder for temporary batch files
    temp_folder = os.path.join(output_folder, "temp_batches")
    os.makedirs(temp_folder, exist_ok=True)

    total_rows = len(df)
    batch_count = (total_rows + batch_size - 1) // batch_size
    print(f"Splitting DataFrame of {total_rows} rows into {batch_count} batches (size={batch_size}).")

    temp_files = []
    current_row = 0
    batch_index = 1

    # -- 1) SAVE IN MULTIPLE BATCHES WITH A PROGRESS BAR FOR THE BATCHES --
    with tqdm(total=batch_count, desc="Saving Batches", unit="batch") as pbar:
        while current_row < total_rows:
            end_row = min(current_row + batch_size, total_rows)
            df_batch = df.iloc[current_row:end_row]

            temp_file_name = f"{temp_batch_prefix}{batch_index}.parquet"
            temp_file_path = os.path.join(temp_folder, temp_file_name)

            # Write the chunk (one shot for each batch)
            df_batch.to_parquet(temp_file_path, index=False, compression="snappy")

            temp_files.append(temp_file_path)

            # Update progress bar
            pbar.update(1)

            # Optional: Print log
            print(f"  -> Batch {batch_index} rows [{current_row}:{end_row}] saved to {temp_file_path}")

            current_row = end_row
            batch_index += 1

    # -- 2) MERGE ALL BATCH FILES INTO A SINGLE PARQUET --
    final_file_path = os.path.join(output_folder, final_filename)
    print(f"\nMerging {len(temp_files)} batch files into {final_file_path}...")

    merged_parts = []
    # Another progress bar for reading merges (optional)
    with tqdm(total=len(temp_files), desc="Merging Batches", unit="file") as pbar_merge:
        for file_path in temp_files:
            merged_parts.append(pd.read_parquet(file_path))
            pbar_merge.update(1)

    df_merged = pd.concat(merged_parts, ignore_index=True)
    df_merged.to_parquet(final_file_path, index=False, compression="snappy")
    print(f"Final merged DataFrame saved as: {final_file_path}\n")

    # -- 3) CLEAN UP TEMPORARY FILES --
    for path in temp_files:
        os.remove(path)
    os.rmdir(temp_folder)

    print("Temporary batch files removed. All done!")
    return final_file_path

# ---------------------------
# EXAMPLE USAGE
# ---------------------------
if __name__ == "__main__":

    folder_path = "Data/2.Processed/ModellingData"
    final_file = "P4_final_merged.parquet"
    batch_size = 100_000  # e.g. if you want ~10 batches

    result_path = save_and_merge_in_batches(
        df=df_final,
        batch_size=batch_size,
        output_folder=folder_path,
        final_filename=final_file,
        temp_batch_prefix="temp_batch_"
    )

    print(f"All done. Merged file at: {result_path}")