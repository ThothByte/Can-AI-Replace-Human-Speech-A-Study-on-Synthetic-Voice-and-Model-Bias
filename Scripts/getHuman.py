import json
import os
import shutil
from tqdm import tqdm  # Progress bar


import argparse

# Create the parser
parser = argparse.ArgumentParser(description="Script to get the human voice dataset")

# Define the arguments with their default values
parser.add_argument('-file', type=str, default='hate.json', help="Location of the hate or non-hate file (default: hate.json)")
parser.add_argument('-human', type=str, default='../datasets/cv-corpus-21.0-2025-03-14/en/clips/', help="Location of where the human data is stored (default ../datasets/cv-corpus-21.0-2025-03-14/en/clips/)")
parser.add_argument('-type', type=str, default='hate', choices=['hate', 'nonhate'], help="Type of data (default: 'hate').")

# Parse the arguments
args = parser.parse_args()


file = args.file
basePath = args.human
outFile = "../audioFiles/"

def copyFiles(filePath, type):
    male_dir = os.path.join(outFile, type, "male")
    female_dir = os.path.join(outFile, type, "female")

    # Create folders if they don't exist
    os.makedirs(male_dir, exist_ok=True)
    os.makedirs(female_dir, exist_ok=True)
    with open(filePath, "r") as f:
        items = json.load(f)  # No need to manually join lines

    # Wrap with tqdm for progress bar
    for x in tqdm(items, desc=f"Copying files for type '{type}'"):
        if(x["male"] != None):
            shutil.copy(basePath + x["male"], outFile + type + "/human/male/" + x["id"] + ".mp3")
        if(x["female"] != None):
            shutil.copy(basePath + x["female"], outFile + type + "/human/female/" + x["id"] + ".mp3")

# Call the function with correct arguments
copyFiles(file, args.type)
