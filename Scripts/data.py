import json

import clean



import argparse

# Create the parser
parser = argparse.ArgumentParser(description="A script that handles -size and -type arguments.")

# Define the arguments with their default values
parser.add_argument('-file', type=str, default='hate.json', help="location of the hate or non-hate file (default: hate.json)")
parser.add_argument('-type', type=str, default='hate', choices=['hate', 'nonhate'], help="Type of data (default: 'hate').")
parser.add_argument('-stats', type=str, default='global', help="Choose either global or inter gender metrics")

# Parse the arguments
args = parser.parse_args()

fP = args.file
data = {}
import os

dataO = open(fP,"r+")
data = json.loads("".join(dataO.readlines()))
dataO.close()

gender = {"en_US_AriaNeural" : "female", "en_US_ChristopherNeural" : "male", "vits/p225" : "female", "vits/p229" : "male", "ST5/bdl" : "male",  "ST5/clb" : "female", "edge/en_US_AriaNeural" : "female", "edge/en_US_ChristopherNeural" : "male", "human/male" : "male", "human/female" : "female"}


from collections import Counter

def get_char_differences(list1, list2):
    # Count character frequencies
    counter1 = Counter(''.join(list1))
    counter2 = Counter(''.join(list2))

    # All characters from both lists
    all_chars = set(counter1) | set(counter2)

    # Compute differences and drop those with no difference
    diffs = {
        char: abs(counter1.get(char, 0) - counter2.get(char, 0))
        for char in all_chars
        if counter1.get(char, 0) != counter2.get(char, 0)
    }

    # Sort by most different
    sorted_diffs = sorted(diffs.items(), key=lambda x: x[1], reverse=True)
    return sorted_diffs

# Example usage
list1 = []
list2 = []
listbase = []

def only_period_vs_comma(text1, text2):
    if len(text1) != len(text2):
        return False  # Can't be a simple punctuation swap if lengths differ

    diffs = [(c1, c2) for c1, c2 in zip(text1, text2) if c1 != c2]
    
    # Check if all differences are just period ↔ comma
    return all((c1, c2) in {('.', ','), (',', '.')} for c1, c2 in diffs)

symbols = [".",",","?","!"]

def endClean(text):
	if(len(text) > 0):
		if(text[-1] in symbols):
			return text[0:-1]
	return text

def comma_period_swap_only(text1, text2):
    if len(text1) != len(text2):
        return False, []

    swaps = []
    other_diffs = []

    for i, (c1, c2) in enumerate(zip(text1, text2)):
        if c1 != c2:
            if (c1, c2) in {(',', '.'), ('.', ',')}:
                swaps.append((i, c1, c2))
            else:
                other_diffs.append((i, c1, c2))

    # Return True only if all differences are comma/period swaps
    return len(other_diffs) == 0, swaps

import re
import inflect

# Create an inflect engine
p = inflect.engine()

def numbers_to_words(text):
    def replace_number(match):
        number = match.group(0)
        return p.number_to_words(int(number))
    
    # Match standalone numbers (not decimals or parts of words)
    return re.sub(r'\b\d+\b', replace_number, text)

showRaw = False

if(args.stats.lower() == "global"):
	returnGlobal = True
else:
	returnGlobal = False

showInfo = False


import numpy as np

def calculate_wer(reference, hypothesis):
	ref_words = reference.split()
	hyp_words = hypothesis.split()
	# Counting the number of substitutions, deletions, and insertions
	substitutions = sum(1 for ref, hyp in zip(ref_words, hyp_words) if ref != hyp)
	deletions = len(ref_words) - len(hyp_words)
	insertions = len(hyp_words) - len(ref_words)
	# Total number of words in the reference text
	total_words = len(ref_words)
	# Calculating the Word Error Rate (WER)
	wer = (substitutions + deletions + insertions) / total_words
	return wer

def compare(f1Lines, f2Lines):
	global showRaw
	global returnGlobal
	baseLen = 0
	f1Len = 0
	f2Len = 0


	d = 0
	c = 0
	f = 0
	m = 0
	t = 0

	averageLenDif1 = 0
	averageLenDif1NonAbs = 0
	averageWER1 = 0
	c1B = 0
	f1B = 0
	d1B = 0

	c1BR = 0
	f1BR = 0
	
	averageLenDifINTER = 0
	averageLenDifINTERNonAbs = 0
	averageWERINTER = 0


	averageLenDif2 = 0
	averageLenDif2NonAbs = 0
	averageWER2 = 0
	c2B = 0
	f2B = 0
	d2B = 0
	t2B = 0

	c2BR = 0
	f2BR = 0

	d12 = 0

	averageLenDif12 = 0
	options = []
	for x in f1Lines:
		options.append(f1Lines[x]["voice"].replace("./out/","").replace("../audioFilesClean/","").replace("nonhate/","").replace("hate/",""))
		break
		
	for x in f2Lines:
		options.append(f2Lines[x]["voice"].replace("./out/","").replace("../audioFilesClean/","").replace("nonhate/","").replace("hate/",""))
		break
	print("\nRunning on",options)
	if(len(options) != 2):
		return []
	dif = []
	for x in data:
		#print(x)
		id = x["id"]
		if(id in f2Lines and id in f1Lines):
			t += 1
			f1Raw = numbers_to_words(f1Lines[id]["text"]).lower()
			f1Text = endClean(clean.clean(f1Raw))
			
			f2Raw = numbers_to_words(f2Lines[id]["text"]).lower()
			f2Text = endClean(clean.clean(f2Raw))
			
			f1Len += len(f1Text)
			f2Len += len(f2Text)

			baseText = endClean(clean.clean(numbers_to_words(x["text"]).lower()))
			baseLen += len(baseText)
			listbase.append(baseText)


			list1.append(f1Text)
			list2.append(f2Text)



			result, details = comma_period_swap_only(f1Text, f2Text)
			if(result == True and len(details) > 0):
				d += 1
			


			if(f1Text == f2Text):
				c += 1
			else:
				dif.append([f1Text,f2Text])
				f += 1
				averageLenDifINTER += abs(len(f1Text) - len(f2Text))
				averageLenDifINTERNonAbs += (len(f1Text) - len(f2Text))

			if(f1Text == baseText):
				c1B += 1
			else:
				f1B += 1
				averageLenDif1 += abs(len(f1Text) - len(baseText))
				averageLenDif1NonAbs += (len(f1Text) - len(baseText))
				#print(baseText)
				#print(f1Text)
				#print(calculate_wer(baseText, f1Text))
				#exit()
				#print(f2Text)
				#print(baseText) 
				#print(f2Text == baseText)
			
			averageWER1 += calculate_wer(baseText, f1Text) 
			averageWER2 += calculate_wer(baseText, f2Text)	
			if(f1Text != ""):
				averageWERINTER += calculate_wer(f1Text, f2Text)
				
			if(f1Raw == baseText):
				c1BR += 1
			else:
				f1BR += 1
			
			if(f2Raw == baseText):
				c2BR += 1
			else:
				f2BR += 1

			if(f2Text == baseText):
				c2B += 1
			else:
				f2B += 1
				averageLenDif2 += abs(len(f2Text) - len(baseText))
				averageLenDif2NonAbs += (len(f2Text) - len(baseText))

			if(f2Text != baseText or f1Text != baseText):
				if(f2Text != f1Text):
					d12 += 1 
					averageLenDif12 += abs(len(f2Text) - len(f1Text))
			t2B += 1

			result, details = comma_period_swap_only(f1Text, baseText)
			if(result == True and len(details) > 0):
				d1B += 1
				
			result, details = comma_period_swap_only(f2Text, baseText)
			if(result == True and len(details) > 0):
				d2B += 1
		else:
			m += 1
	if(len(options) == 1):
		for x in f1Lines:
			print(f1Lines[x]["voice"])
			break
		print(len(f1Lines))
		print(len(f2Lines))
		for x in f2Lines:
			print(f2Lines[x]["voice"])
			break

	if(showInfo == True):
		print(options[0],"VS",options[1])
		print("Correct", c, "Incorrect",f, "Missing", m, "Total", t)
		print("Correct / Total:", str(round(c/t*100,2)) + "%", "\nIncorrect / Total:" , str(round(f/t*100,2)) + "%", "\nMissing / Total:", str(round(m/t*100,2)) + "%")
		print("Voice Ending Rate D/T", str(round(d/t*100,2)) + "%", d)
		print()

		print(gender[options[0]], options[0], "VS BASE")
		print(t)
		print(c1B, f1B, c1B+f1B, t2B)
		if(c1B == 0):
			print("Correct / Total: 0%")
		else:
			print("Correct / Total:", str(round(c1B/t2B*100,2)) + "%")
		if(f1B == 0):
			print("Incorrect / Total: 0%")
		else:
			print("Incorrect / Total:", str(round(f1B/t2B*100,2)) + "%")
		print("Voice Ending Rate d1B/T", str(round(d1B/t2B*100,2)) + "%", d1B)
		print("averageLenDif1Abs", str(round(averageLenDif1/t2B,4)), averageLenDif1)
		print("averageLenDif1NonAbs", str(round(averageLenDif1NonAbs/t2B,4)), averageLenDif1NonAbs)
		print()


	if(showRaw == True):
		print(gender[options[0]], options[0], "RAW VS BASE")
		print(c1BR, f1BR, c1BR+f1BR, t2B, "\nCorrect / Total:", str(round(c1BR/t2B*100,2)) + "%")
		print("RAW VS CLEAN",str(round((c1BR/t2B - c1B/t2B)*100,2)) + "%")
		print("Incorrect / Total:", str(round(f1BR/t2B*100,2)) + "%")
		print()
	
	if(showInfo == True):
		print(gender[options[1]], options[1], "VS BASE")
		print(c2B, f2B, c2B+f2B, t2B, "\nCorrect / Total:", str(round(c2B/t2B*100,2)) + "%", "\nIncorrect / Total:", str(round(f2B/t2B*100,2)) + "%")
		print("Voice Ending Rate d2B/T", str(round(d2B/t2B*100,2)) + "%", d2B)
		print("averageLenDif2", str(round(averageLenDif2/t2B,4)), averageLenDif2)
		print("averageLenDif2NonAbs", str(round(averageLenDif2NonAbs/t2B,4)), averageLenDif2NonAbs)
		print()


	if(showRaw == True):
		print(gender[options[1]], options[1], "RAW VS BASE")
		print(c2BR, f2BR, c2BR+f2BR, t2B, "\nCorrect / Total:", str(round(c2BR/t2B*100,2)) + "%")
		print("RAW VS CLEAN",str(round((c2BR/t2B - c2B/t2B)*100,2)) + "%")
		print("Incorrect / Total:", str(round(f2BR/t2B*100,2)) + "%")
		print()


	if(showInfo == True):
		print(baseLen/len(f1Lines), f1Len/len(f1Lines), f2Len/len(f1Lines))

		if(round(c1B/t2B*100,2) > round(c2B/t2B*100,2)):
			print(gender[options[0]], options[0],"LEADING BY", str(abs(round((c1B/t2B - c2B/t2B) * 100,2))) + "%")
		else:	
			print(gender[options[1]], options[1],"LEADING BY", str(abs(round((c1B/t2B - c2B/t2B) * 100,2))) + "%")

	#averageDif = abs(round((averageLenDif1/t2B - averageLenDif2/t2B),4))
	#if(round(averageLenDif1/t2B,4) > round(averageLenDif2/t2B,4)):
	#	print(gender[options[0]], options[0],"HAS HIGHER ERROR RATE", str(averageDif), "CHARS")
	#else:	
	#	print(gender[options[1]], options[1],"HAS HIGHER ERROR RATE", str(averageDif), "CHARS")
	if(len(f1Lines) > 0):
		f1DifVB = round(abs(baseLen/len(f1Lines) - f1Len/len(f1Lines)),4)
	else:
		f1DifVB = 0

	if(len(f2Lines) > 0):
		f2DifVB = round(abs(baseLen/len(f2Lines) - f2Len/len(f2Lines)),4)
	else:
		f2DifVB = 0

	print("BASE VS",options[0],gender[options[0]], f1DifVB)
	print("BASE VS",options[1],gender[options[1]], f2DifVB)
	print("BASE VS AVERAGE", round((f1DifVB + f2DifVB) / 2,4))

	if(f1DifVB > f2DifVB):
		print(gender[options[0]], options[0],"HAS HIGHER ERROR RATE OVER GLOBAL", str(f1DifVB), "CHARS")
	else:		
		print(gender[options[1]], options[1],"HAS HIGHER ERROR RATE OVER GLOBAL", str(f2DifVB), "CHARS")
	dd = []
	if(returnGlobal == True):
		#stats1 = options[0].replace("_","\\_").upper() + " & " + gender[options[0]]+ " & " + str(round(c1B/t2B*100,2))+ " & " + str(round(averageLenDif1/t2B,4)) + " & " + str(round(averageLenDif1NonAbs/t2B,4)) + " & " + str(round(averageWER1 / t2B * 100,2)) + "\\\\"
		#stats2 = options[1].replace("_","\\_").upper() + " & " + gender[options[1]]+ " & " + str(round(c2B/t2B*100,2))+ " & " + str(round(averageLenDif2/t2B,4)) + " & " + str(round(averageLenDif2NonAbs/t2B,4)) + " & " + str(round(averageWER2 / t2B * 100,2)) + "\\\\"
		cc1 = round(c1B/t2B*100,2)
		cc2 = round(c2B/t2B*100,2)


		stats1 = options[0].split("/")[0].upper() + " (" + (options[0].split("/")[1].replace("EN_US_","").replace("_","\\_").replace("EN\\_US\\_","").upper() + " / " + options[1].split("/")[1].replace("EN_US_","").replace("_","\\_").replace("EN\\_US\\_","").upper()) + ") & " + str(round(c1B/t2B*100,2)) + " / " + str(round(c2B/t2B*100,2)) + " & " + str(round(averageLenDif1/t2B,4)) + " / " + str(round(averageLenDif2/t2B,4)) + " & " + str(round(averageLenDif1NonAbs/t2B,4)) + " / " + str(round(averageLenDif2NonAbs/t2B,4)) + " & " + str(round(averageWER1 / t2B * 100,2)) + " / " + str(round(averageWER2 / t2B * 100,2)) + " & " + str(round(cc1 - cc2,3))
		dd.append(stats1)
		#dd.append(stats2)
	if(returnGlobal == False):
		stats1 = options[0].split("/")[0].replace("_","\\_").upper() + " & " + str(round(c/t*100,2)) + " & " + str(round(averageLenDifINTER/t2B,4)) + " & " + str(round(averageLenDifINTERNonAbs/t2B,4)) + " & " + str(round(averageWERINTER / t2B * 100,2)) + "\\"
		#stats2 = options[1].replace("_","\\_") + " & " + gender[options[1]]+ " & " + str(round(c2B/t2B*100,2))+ " & " + str(round(averageLenDif2/t2B,4)) + " & " + str(round(averageLenDif2NonAbs/t2B,4)) + " & " + str(round(averageWER2 / t2B * 100,2)) + "\\\\"
		
		dd.append(stats1)
	
	print(averageWER1 / t2B)
	print(averageWER2 / t2B)
	return list(dd)

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





types = [args.type]
options = ["WHISPERX","WHISPERX-Align","Vosk-giga", "Vosk-small", "deepSpeech","deepSpeech-Scorer"]

for t in types:
	total = ""
	for option in options:
		if(returnGlobal == False):
			total += "\multicolumn{5}{c}{\\textbf{STT Model: " + option + "}} \\\\\n"
		else:
			total += "\multicolumn{6}{c}{\\textbf{STT Model: " + option + "}} \\\\\n"
		total += "\midrule\n"
		f1Lines, d1 = (read_files_with_prefix("../transcript/" + str(t) + "/" + option + "/","bdl"))
		f2Lines, d2 = (read_files_with_prefix("../transcript/" + str(t) + "/" + option + "/","clb"))

		print(d1, d2)
		print(len(f1Lines),len(f2Lines))
		a = compare(f2Lines,f1Lines)
		a = list(a)
		print(a)

		f1Lines, d1 = (read_files_with_prefix("../transcript/" + str(t) + "/" + option + "/","en_US_AriaNeural"))
		f2Lines, d2 = (read_files_with_prefix("../transcript/" + str(t) + "/" + option + "/","en_US_ChristopherNeural"))

		b = compare(f1Lines,f2Lines)
		b = list(b)

		f1Lines, d1 = (read_files_with_prefix("../transcript/" + str(t) + "/" + option + "/","p225"))
		f2Lines, d2 = (read_files_with_prefix("../transcript/" + str(t) + "/" + option + "/","p229"))

		c = compare(f1Lines,f2Lines)
		
		f1Lines, d1 = (read_files_with_prefix("../transcript/" + str(t) + "/" + option + "/","female"))
		f2Lines, d2 = (read_files_with_prefix("../transcript/" + str(t) + "/" + option + "/","male"))

		d = compare(f1Lines,f2Lines)
		total += "\t\n".join(a) + "\\\\\n" + "\t\n".join(b) + "\\\\\n" + "\t\n".join(c) + "\\\\\n" + "\t\n".join(d) + "\\\\\n" 
		total += "\midrule\n"

	print(total)

