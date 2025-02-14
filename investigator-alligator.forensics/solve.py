# File: solve.py
# Author: Julián Casaburi
# Date: January 6, 2024
# Description: This is a script to solve the challenge "Investigator Alligator (Iris CTF 2024 - Forensics)".

import gzip
import shutil
import os
import re
from scapy.all import *
import subprocess
import random
import requests
from tqdm import tqdm

RESOURCE_PRIMARY_URL = "https://cdn.2024.irisc.tf/investigator-alligator.gz"
RESOURCE_BACKUP_URL = "https://shawndxyz.sjc1.vultrobjects.com/ctf/2024.irisctf/investigator-alligator.gz"

input_file = "./resource/investigator-alligator.gz"
output_dir = "./solve"
output_file = os.path.join(output_dir, "investigator-alligator")
extracted_path = os.path.join(output_dir, "extracted-files")
capture_to_extract = "root/capture/network"
memdump_to_extract = "root/LiME/src/sample.mem"
encrypted_file_to_extract = "home/stephen/encrypted.img"
encrypted_file_path = os.path.join(extracted_path, "encrypted.img")
decrypted_file_path = os.path.join(output_dir, "decrypted.img")
decrypted_files_path = os.path.join(output_dir, "decrypted")
super_duper_important_info_path = "data/super_duper_important_info.png"
flag_file_path = os.path.join(output_dir, "flag_part2.txt")

def write_flag_to_file(flag, flag_file_path):
    with open(flag_file_path, 'w') as flag_file:
        flag_file.write(flag)
    print(f'[+] Flag written to {os.path.abspath(flag_file_path)}')

def remove_non_unicode_chars(input_str):
    # Use a regular expression to match only Unicode characters
    unicode_pattern = re.compile('[^\x00-\x7F]+')
    
    # Replace non-Unicode characters with an empty string
    cleaned_str = unicode_pattern.sub('', input_str)
    
    return cleaned_str

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Check if the resource already exists
resource_available = True  # Track resource availability
if not os.path.exists(input_file):
    resource_available = False
    # If the file doesn't exist, download it
    try:
        # Create the 'resource' directory if it doesn't exist
        os.makedirs(os.path.dirname(input_file), exist_ok=True)
        
        # Download the file from the primary URL
        print(f"[+] Downloading file {input_file} from {RESOURCE_PRIMARY_URL}")
        response = requests.get(RESOURCE_PRIMARY_URL, stream=True)
        total_size = int(response.headers.get('content-length', 0))

        # Download the file with tqdm for progress bar
        with open(input_file, "wb") as file, tqdm(
            desc="Downloading",
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                bar.update(len(data))
                file.write(data)
        
        resource_available = True
        print(f"[+] File downloaded to {input_file}")
    except requests.exceptions.RequestException as primary_err:
        print(f"[-] Failed to download the file from the primary URL: {primary_err}")

        # If the primary URL download fails, try the backup URL
        try:
            print(f"[+] Downloading file {input_file} from backup URL: {RESOURCE_BACKUP_URL}")
            response = requests.get(RESOURCE_BACKUP_URL, stream=True)

            # NoSuchBucket
            if 'application/gzip' not in response.headers['Content-Type']:
                raise ValueError("URL does not point to a file")

            total_size = int(response.headers.get('content-length', 0))

            # Download the file with tqdm for progress bar
            with open(input_file, "wb") as file, tqdm(
                desc="Downloading",
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for data in response.iter_content(chunk_size=1024):
                    bar.update(len(data))
                    file.write(data)

            resource_available = True
            print(f"[+] File downloaded to {input_file} (from backup URL)")
        except (requests.exceptions.RequestException, ValueError) as backup_err:
            print(f"[-] Failed to download the file from the backup URL: {backup_err}")
    except Exception as e:
        print(f"[-] Failed to download the file: {e}")
else:
    print(f"[+] The file {input_file} already exists. Skipping download")

if not resource_available:
    print(f'[-] Resource {input_file} not available. Exiting.')
    exit(1)

if not os.path.exists(output_file):
    try:
        print(f'[+] Extracting file {input_file} to {output_file}')
        with gzip.open(input_file, 'rb') as f_in, open(output_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
        print(f"[+] File '{input_file}' has been successfully extracted to '{output_file}'.")
    except Exception as e:
        print(f"[-] Error during extraction: {e}")
else:
    print(f'[+] {output_file} file already exists. Skipping decompression.')

# Run the 7z command to extract files
command = ["7z", "e", "-aos", output_file, capture_to_extract, f"-o{extracted_path}"]

try:
    # Extract pcap
    print(f"[+] Extracting file", command[4])
    subprocess.run(command, check=True)
    print("[+] Extraction successful.")
    print()

    # Extract LiMe dump
    command[4] = memdump_to_extract
    print(f"[+] Extracting file", command[4])
    subprocess.run(command, check=True)
    print("[+] Extraction successful.")
    print()

    # Extract encrypted.img
    command[4] = encrypted_file_to_extract
    print(f"[+] Extracting file", command[4])
    subprocess.run(command, check=True)
    print("[+] Extraction successful.")
    print()

except subprocess.CalledProcessError as e:
    print(f"[-] Extraction failed with error code {e.returncode}: {e}")

def extract_tcp_data(file_path, port=9281):
    packets = rdpcap(file_path)  # Read pcap file

    # Choose a specific packet (e.g., the first packet)
    selected_packet = packets[6513]

    # Check if the selected packet has a TCP layer
    if TCP in selected_packet:
        # Access the TCP layer
        tcp_layer = selected_packet[TCP]

        # Check if there is payload data
        if Raw in tcp_layer:
            # Access the payload data
            tcp_data = tcp_layer[Raw].load

            # Display the TCP data
            tcp_data = tcp_data.decode('utf-8')
            print("[+] TCP Data:", tcp_data)

            return tcp_data
        else:
            print("[-] No TCP payload data in the selected packet.")
    else:
        print("[-] The selected packet does not have a TCP layer.")

# pcap
print()
file_path = os.path.join(extracted_path, "network")
print(f'[+] Processing {file_path}')
extracted_data = extract_tcp_data(file_path)
print()

print(f'[+] Decrypting {encrypted_file_path}')

random.seed(extracted_data.strip())
with open(encrypted_file_path, "rb") as f:
	data = f.read()
stream = random.randbytes(len(data))
decrypted = bytearray()
for i in range(len(data)):
	decrypted.append(data[i] ^ stream[i])
with open(decrypted_file_path, "wb") as f:
	f.write(decrypted)
    
try:
    # Extract decrypted.img
    command[3] = decrypted_file_path
    command[4] = super_duper_important_info_path
    command[5] = f"-o{decrypted_files_path}"
    print(f"[+] Extracting file", command[3])
    subprocess.run(command, check=True)
    print("[+] Extraction successful.")
    print()

    #Flag part 1/2:
    # Open the file and iterate through lines
    with open(os.path.join(extracted_path, "sample.mem"), 'r', encoding='ISO-8859-15') as file:
        for line_number, line in enumerate(file, start=1):
            if "ctive_ty" in line:
                flag_part2 = remove_non_unicode_chars(line)
                print(f'[+] Flag part 2/2: {flag_part2}')
                # Write flag to file
                write_flag_to_file(flag_part2, flag_file_path)
                break
        else:
            print("No lines containing 'ctive_ty' found.")

    #Flag part 2/2:
    print()
    print(f'[+] View the image {os.path.join(decrypted_file_path, "super_duper_important_info.png")} to get the flag (part 1/2)')

except subprocess.CalledProcessError as e:
    print(f"[-] Extraction failed with error code {e.returncode}: {e}")