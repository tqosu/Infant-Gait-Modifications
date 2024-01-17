import os


import os
import shutil
import concurrent.futures
import argparse


parser = argparse.ArgumentParser(description="Description of your script")

# Add command-line arguments
parser.add_argument('--input', type=str, help='Source')
parser.add_argument('--output', type=str, help='Target')
# Parse the command-line arguments
args = parser.parse_args()

path = args.input

def extract_and_move(file_path):
    # Extract 'Sxx' from the filename
    filename = os.path.basename(file_path)
    extracted_value = filename.split('_')[2]

    # Create the destination folder path
    dest_folder =  args.output+'/'+extracted_value
    # print(dest_folder)

    # Check if the destination folder exists, and create it if not
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    # Move the file to the destination folder
    src,tgt=os.path.join(path, filename),os.path.join(dest_folder, filename)
    print(src,tgt)
    shutil.move(src,tgt)

def process_files_in_parallel():
    file_list = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    # Number of parallel workers (adjust as needed)
    num_workers = min(len(file_list), 4)

    # Use ThreadPoolExecutor for parallel execution
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Submit tasks for each file path
        futures = [executor.submit(extract_and_move, file_path) for file_path in file_list]

        # Wait for all tasks to complete
        concurrent.futures.wait(futures)

if __name__ == "__main__":
    process_files_in_parallel()