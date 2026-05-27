import pandas as pd
import pyarrow.parquet as pq
from tqdm.auto import tqdm

def read_parquet_in_batches_with_progress(file_path, batch_size):
    """
    Read a Parquet file in fixed-size row batches with a progress bar and per-chunk logging.

    Args:
        file_path (str): Path to the Parquet file.
        batch_size (int): Number of rows per batch.

    Returns:
        pd.DataFrame: Combined DataFrame after processing all batches.
    """
    # Open the Parquet file
    parquet_file = pq.ParquetFile(file_path)
    
    # Total number of rows in the file
    total_rows = parquet_file.metadata.num_rows
    
    # Initialize a list to store DataFrame chunks
    all_chunks = []
    
    # Initialize the progress bar
    with tqdm(total=total_rows, desc="Processing Batches", unit="rows") as pbar:
        # Enumerate batches for logging
        for batch_number, batch in enumerate(parquet_file.iter_batches(batch_size=batch_size), start=1):
            # Convert the batch to a Pandas DataFrame
            df_batch = batch.to_pandas()
            
            # Simulate processing (add custom logic here if necessary)
            all_chunks.append(df_batch)
            
            # Update the progress bar
            pbar.update(len(df_batch))
            
            # Print per-chunk information
            print(f"Processed Chunk {batch_number}: {len(df_batch)} rows")
    
    # Combine all chunks into a single DataFrame
    combined_df = pd.concat(all_chunks, ignore_index=True)
    
    return combined_df

# EXAMPLE USAGE
if __name__ == "__main__":
    file_path = "Data/2.Processed/ModellingData/P1_all.parquet"
    batch_size = 100_000  # Define your desired chunk size
    
    df = read_parquet_in_batches_with_progress(file_path, batch_size)
    
    print(f"\nFinal DataFrame with {len(df)} rows:")
    df.head()

