# TCIA Image Downloader

This simple Python script is designed to download images from the TCIA (The Cancer Imaging Archive) website using a specified manifest file. It supports downloading multiple series concurrently and includes a retry mechanism for robustness.
-Alan McMillan

## Features
- Download images based on series IDs listed in a manifest file.
- Handle multiple downloads concurrently.
- Retry mechanism for handling download failures.
- Can be run from the command line or imported as a function in other Python scripts.

## Usage
### As a Command Line Tool

To use this script from the command line, you need to provide the path to the manifest file and the output folder where the images will be saved. Optionally, you can specify the number of concurrent download jobs.

```bash
python tcia_downloader.py -m <path_to_manifest_file> -o <output_folder_path> --njobs <number_of_concurrent_jobs>
```

### As a Function in Python

You can also use the download_from_manifest function in other Python scripts. The function requires the path to the manifest file, the output base path, and the number of jobs (optional).

```python
from tcia_downloader import download_from_manifest

download_from_manifest('path_to_manifest.txt', 'path_to_output_folder', njobs=5)
```

## Acknowledgements
This project is based on ```tcia.py``` from the TCIA Downloader project (https://github.com/lescientifik/tcia_downloader), licensed under Apache 2.0. We thank the original authors for their work which served as a foundation for this code.

## Requirements
 - Python 3.x
 - Requests library
 - Tqdm library for progress bar

## Installation

Ensure you have Python installed, and then install the required libraries:

```bash
pip install requests tqdm
```

## License

This project is licensed under the Apache 2.0 License. See the LICENSE file for more details.

