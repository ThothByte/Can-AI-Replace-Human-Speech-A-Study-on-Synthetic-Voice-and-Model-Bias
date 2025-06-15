import os
import subprocess
from pathlib import Path
from multiprocessing import Pool
from tqdm import tqdm

# Configuration
num_workers = 12  # Adjust to your CPU cores

input_dir = "../audioFiles/Broken"
output_dir = "../audioFilesClean/Broken"
def convert_to_wav(input_path):
    output_path = Path(output_dir) / (input_path.stem + ".wav")

    if output_path.exists():
        return input_path  # Mark as done even if skipped

    try:
        subprocess.run([
            "ffmpeg", "-y",
            "-i", str(input_path),
            "-ar", "16000",
            "-ac", "1",
            "-f", "wav",
            str(output_path)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Failed to convert {input_path}: {e}")
    return input_path

def main(dirF):
    global output_dir
    global input_dir
    input_dir = "../audioFiles/" + dirF
    output_dir = "../audioFilesClean/" + dirF 
    input_path = Path(input_dir)
    os.makedirs(output_dir, exist_ok=True)

    audio_files = list(input_path.rglob("*.*"))
    print(f"Found {len(audio_files)} audio files to convert...")

    with Pool(num_workers) as pool:
        for _ in tqdm(pool.imap_unordered(convert_to_wav, audio_files), total=len(audio_files)):
            pass

    print("Batch conversion complete.")


if __name__ == "__main__":
    print("----HATE----")
    main("hate/human/male")
    main("hate/human/female")

    main("hate/vits/p229")
    main("hate/vits/p225")

    main("hate/ST5/bdl")
    main("hate/ST5/clb-new")
    

    main("hate/edge/en_US_AriaNeural")
    main("hate/edge/en_US_ChristopherNeural")
    print("----NON HATE----")
    
    main("nonhate/human/male")
    main("nonhate/human/female")
    
    main("nonhate/vits/p229")
    main("nonhate/vits/p225")

    main("nonhate/ST5/bdl")
    main("nonhate/ST5/clb")
    
    main("nonhate/edge/en_US_AriaNeural")
    main("nonhate/edge/en_US_ChristopherNeural")

