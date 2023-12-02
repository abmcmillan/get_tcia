import argparse
import json
import pathlib
import requests
import shutil
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm

def parse_manifest(file_path: pathlib.Path) -> dict:
    """
    Parses the manifest file and returns a dictionary with keys and their corresponding multi-line values.

    Args:
    file_path (pathlib.Path): The path to the manifest file.

    Returns:
    dict: A dictionary where each key is a line key from the file and the value is a list of associated lines.
    """
    manifest_data = {}
    current_key = None
    with file_path.open() as file:
        for line in file:
            line = line.strip()
            if '=' in line:
                current_key, _, value = line.partition('=')
                current_key = current_key.strip()
                manifest_data[current_key] = [value.strip()] if value else []
            elif current_key and line:
                manifest_data[current_key].append(line)
    return manifest_data

def download_series(series_id: str, dest_file: pathlib.Path, max_retries: int) -> pathlib.Path:
    """
    Downloads a series from the TCIA endpoint with retry mechanism.

    Args:
    series_id (str): The series ID to download.
    dest_file (pathlib.Path): The destination file path.
    download_server_url (str): The download server URL.
    max_retries (int): Maximum number of retries for the download.

    Returns:
    pathlib.Path: The path to the downloaded file.
    """
    DOWNLOAD_SERVER_URL = 'https://services.cancerimagingarchive.net/services/v3/TCIA/query/getImage'
    
    retry_count = 0
    while retry_count <= max_retries:
        try:
            # Check if the file already exists
            if dest_file.exists():
                return dest_file

            # Prepare the request
            response = requests.get(DOWNLOAD_SERVER_URL, params={"SeriesInstanceUID": series_id}, stream=True)
            response.raise_for_status()

            # Check if the file is a ZIP file
            metadata = json.loads(response.headers.get("metadata", "{}"))
            filetype = metadata.get("Result", {}).get("Type", [""])[0]
            if filetype != "ZIP":
                raise ValueError(f"Invalid series ID {series_id}. Expected a ZIP file.")

            # Write the file to disk
            with dest_file.open("wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)

            #print(f"Series {series_id} downloaded at {dest_file}")
            return dest_file

        except Exception as e:
            print(f"Error downloading series {series_id}: {e}")
            retry_count += 1

            if retry_count > max_retries:
                print(f"Failed to download series {series_id} after {max_retries} retries.")
                break

            print(f"Retrying {retry_count}/{max_retries}...")
            time.sleep(1)  # Sleep for a short time before retrying

    return dest_file

def download_from_manifest(manifest_path:str, output_base_path:str, njobs:int=1):
    '''
    Download images from the TCIA website using a manifest file.
    
    Args:
    manifest_path (str): The path to the manifest file.
    output_base_path (str): The base path to download the images.
    njobs (int): The number of concurrent connections.
    
    Returns:
    None
    '''
    # Create the destination folder
    manifest_path = pathlib.Path(manifest_path)
    destination_folder = pathlib.Path(output_base_path) / manifest_path.name
    destination_folder.mkdir(exist_ok=True, parents=True)

    if not manifest_path.is_file():
        raise ValueError(f"{manifest_path} does not exist or is not a file")

    # Copy the manifest file to the destination folder
    shutil.copy(manifest_path, destination_folder)
    
    # Parse the manifest file
    print( f'Parsing manifest file {manifest_path}.')
    manifest_data = parse_manifest(manifest_path)
    series_ids_to_download = manifest_data.get('ListOfSeriesToDownload', [])
    no_of_retries = int(manifest_data.get('noOfrRetry', 0)[0])

    # Download all of the series with a thread pool
    print( f'Downloading {len(series_ids_to_download)} series to {destination_folder}.' )
    with ProcessPoolExecutor(max_workers=njobs) as executor:
        futures = {executor.submit(download_series, series_id, destination_folder / f"{series_id}.zip", no_of_retries): series_id for series_id in series_ids_to_download}

        for future in tqdm(as_completed(futures), total=len(futures), desc="Downloading"):
           future.result()
    
    print( 'Done.' )

if __name__ == '__main__':
    # Parse the command-line arguments
    parser = argparse.ArgumentParser(description="Download images from the TCIA website")
    parser.add_argument("-m","-manifest", help="The manifest file", required=True)
    parser.add_argument("-o","-output_folder", help="The folder to download the images", required=True)
    parser.add_argument("--njobs", type=int, default=5, help="Number of concurrent connections")
    args = parser.parse_args()

    # Run the main function
    download_from_manifest(args.m, args.o, args.njobs)
