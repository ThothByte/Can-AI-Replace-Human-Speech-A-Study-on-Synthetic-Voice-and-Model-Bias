from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import json
import os


def read_files_with_prefix(directory, prefix):
	contents = []
	for filename in os.listdir(directory):
		if filename.startswith(prefix + '-') and '-error' not in filename:
			filepath = os.path.join(directory, filename)
			if os.path.isfile(filepath):  # Ensure it's a file
				with open(filepath, 'r') as file:
					contents.append(file.read())
	contents = "".join(contents)[0:len("".join(contents))-2]
	return json.loads("{" + contents + "}"), directory

from detoxify import Detoxify
from tqdm import tqdm
import json
import os

def load_checkpoint(checkpoint_path):
    if os.path.exists(checkpoint_path):
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_checkpoint(results_dict, checkpoint_path):
    with open(checkpoint_path, 'w', encoding='utf-8') as f:
        json.dump(results_dict, f, ensure_ascii=False, indent=2)

def analyze_texts(data_dict, checkpoint_path, hateO = False):
	results = load_checkpoint(checkpoint_path)
	print("LOADED CHECKPOINT")
	processed_ids = set(results.keys())
	neededSize = len(data_dict)
	c = 0


	items_to_process = [
		item for key, item in data_dict.items()
		if key not in results
	]

	model = Detoxify('original')

	averageScore = 0
	for item in tqdm(items_to_process): 
		text = item["text"]
		scores = model.predict(text)
		hate_score = round(float(scores.get("toxicity", 0.0)),4)
		label = "hate" if hate_score >= 0.8 else "not_hate"
		hh = False
		if(hate_score >= 0.8):
			hh = True
		item["hate"] = hh
		item["hate_score"] = hate_score
		results[item["id"]] = item
		averageScore += hate_score
		
		if len(results) % 200 == 0:
			save_checkpoint(results, checkpoint_path)

	for x in results:
		averageScore += results[x]["hate_score"]
		if(results[x]["hate"] == hateO):
			c += 1
	save_checkpoint(results, checkpoint_path)
	#print(averageScore, averageScore / neededSize)
	#exit()
	return results, c, neededSize, c == neededSize, averageScore / neededSize

def getStats(f1, checkPoint, hate):
	#print(len(f1))
	checkpoint_file = checkPoint
	labeled_results, c, ns, g, averageScore = analyze_texts(f1, checkpoint_file, hate)
	#print(c,ns,g)
	return labeled_results, c, ns, g, round(c / ns,4), averageScore



import argparse

# Create the parser
parser = argparse.ArgumentParser(description="Transcribe all transcripts and classify if the detoxify score has changed")

# Define the arguments with their default values
parser.add_argument('-type', type=str, default='hate', choices=['hate', 'nonhate'], help="Type of data (default: 'hate').")

# Parse the arguments
args = parser.parse_args()


types = [args.type]
options = ["en_US_AriaNeural", "en_US_ChristopherNeural", "p225", "p229", "clb", "bdl", "male", "female"]
STTM = ["deepSearch", "deepSearch-Scorer", "WHISPERX", "WHISPERX-Allign", "Vosk-small", "Vosk-giga"]


outText = ""
outText2 = ""
for t in types:
	print(t)
	for s in STTM:
		allC = 0
		allT = 0
		
		correctRatio = 0
		totalRatio = 0

		averageScoreT = 0

		print(s)
		items = []
		os.makedirs("../textClassificationOut/" + str(t) + "/" + str(s), exist_ok=True)
		for o in options:
			try:
				path = "../transcript/" + str(t) + "/" + str(s)
				outPath = "../textClassificationOut/" + str(t) + "/" + str(s) + "/" + str(o) + ".json"
				f1, d1 = read_files_with_prefix(path, o)
				print("LOADED DATA")
				if(args.type.lower() == "hate"):
					labeled_results, c, ns, g, total, averageScore = getStats(f1, outPath, True)
				else:
					labeled_results, c, ns, g, total, averageScore = getStats(f1, outPath, False)
				print("GOT STATS")
				averageScoreT += averageScore
				correctRatio += round(c / ns,4) 
				totalRatio += 1
				if(g == True):
					allC += 1
				allT += 1
				f = open(outPath, "w+")
				f.write(json.dumps(labeled_results).replace('}, "','},\n "'))
				f.close()
				items.append([s,o.replace("en_US_AriaNeural","Aria").replace("en_US_ChristopherNeural","Christopher"), str(round(round(correctRatio / totalRatio ,4) * 100,4)), str(round(averageScore,4))])
				outText2 += s + " & " + o + " & " + str(round(round(correctRatio / totalRatio ,4) * 100,4)) + " & " + str(round(averageScore,4)) + "\\\\ \n"
			except Exception as e:
				print("ERROR",t, o, e)
				pass
		for i in range(0, len(items),2):
			if("Aria" in items[i][1]):
				outText += items[i][0] + " (" + items[i][1] + " / " + items[i+1][1] + ") & " + items[i][2] + " / " + items[i+1][2] + " & " + items[i][3] + " / " + items[i+1][3] + "\\\\ \n"
			else:
				outText += items[i][0] + " (" + items[i+1][1] + " / " + items[i][1] + ") & " + items[i+1][2] + " / " + items[i][2] + " & " + items[i+1][3] + " / " + items[i][3] + "\\\\ \n"

		print(s, "&", c, "&", ns, " & ", round(round(correctRatio / totalRatio ,4) * 100,4), " & ", round(averageScoreT / len(options), 4))
		outText += s + " & " + str(c) + " & " + str(ns) + " & " + str(round(round(correctRatio / totalRatio ,4) * 100,4)) + " & " + str(round(averageScoreT / len(options), 4)) + "\\\\ \n"
print(allC, allT, allC / allT)
print(outText)
print(outText2)