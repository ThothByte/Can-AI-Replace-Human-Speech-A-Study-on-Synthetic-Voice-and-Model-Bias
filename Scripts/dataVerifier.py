import subprocess

def count_files_in_directory(directory):
	# Run the ls command to list files in the directory, pipe to wc -l to count
	result = subprocess.run(f"ls {directory} | wc -l", shell=True, text=True, capture_output=True)
	# Extract the result and return the number of files
	return int(result.stdout.strip())

print("AUDIO FILE")
o = ["nonhate"]
for x in o:
	edge_male = count_files_in_directory("../audioFiles/"+x+"/edge/en_US_AriaNeural")
	edge_female = count_files_in_directory("../audioFiles/"+x+"/edge/en_US_ChristopherNeural")

	ST5_male = count_files_in_directory("../audioFiles/"+x+"/ST5/bdl")
	ST5_female = count_files_in_directory("../audioFiles/"+x+"/ST5/clb")

	VITS_male = count_files_in_directory("../audioFiles/"+x+"/vits/p229")
	VITS_female = count_files_in_directory("../audioFiles/"+x+"/vits/p225")

	HUMAN_male = count_files_in_directory("../audioFiles/"+x+"/human/male")
	HUMAN_female = count_files_in_directory("../audioFiles/"+x+"/human/female")
	perfect = edge_female == edge_male and ST5_male == ST5_female and VITS_male == VITS_female
	print(f"----{x}----")
	print("EDGE:", edge_female == edge_male, edge_male, edge_female)
	print("ST5:", ST5_male == ST5_female, ST5_male, ST5_female)
	print("VITS:", VITS_male == VITS_female, VITS_male, VITS_female)
	print("HUMAN:", HUMAN_male == HUMAN_female, HUMAN_male, HUMAN_female)
	print("PERFECT:",perfect)
	
dataItems = {}
for x in o:
	if(x not in dataItems):
		dataItems[x] = {}
	edge_female = count_files_in_directory("../audioFilesClean/"+x+"/edge/en_US_AriaNeural")
	edge_male = count_files_in_directory("../audioFilesClean/"+x+"/edge/en_US_ChristopherNeural")
	dataItems[x]["edge"] = {"female" : edge_female, "male" : edge_male}

	ST5_male = count_files_in_directory("../audioFilesClean/"+x+"/ST5/bdl")
	ST5_female = count_files_in_directory("../audioFilesClean/"+x+"/ST5/clb")	
	dataItems[x]["st5"] = {"female" : ST5_female, "male" : ST5_male}

	VITS_male = count_files_in_directory("../audioFilesClean/"+x+"/vits/p229")
	VITS_female = count_files_in_directory("../audioFilesClean/"+x+"/vits/p225")	
	dataItems[x]["vits"] = {"female" : VITS_female, "male" : VITS_male}

	HUMAN_male = count_files_in_directory("../audioFilesClean/"+x+"/human/male")
	HUMAN_female = count_files_in_directory("../audioFilesClean/"+x+"/human/female")
	dataItems[x]["human"] = {"female" : HUMAN_female, "male" : HUMAN_male}

	perfect = edge_female == edge_male and ST5_male == ST5_female and VITS_male == VITS_female
	print(f"----{x}----")
	print("EDGE:", edge_female == edge_male, edge_male, edge_female)
	print("ST5:", ST5_male == ST5_female, ST5_male, ST5_female)
	print("VITS:", VITS_male == VITS_female, VITS_male, VITS_female)
	print("HUMAN:", HUMAN_male == HUMAN_female, HUMAN_male, HUMAN_female)
	print("PERFECT:",perfect)	
	
import os, json
def read_files_with_prefix(directory, prefix):
	contents = []
	for filename in os.listdir(directory):
		if filename.startswith(prefix + '-') and '-error' not in filename:
			filepath = os.path.join(directory, filename)
			if os.path.isfile(filepath):
				with open(filepath, 'r') as file:
					contents.append(file.read())
	contents = "".join(contents)[0:len("".join(contents))-2]
	return json.loads("{" + contents + "}"), directory

types = ["Vosk-giga", "Vosk-small", "deepSearch", "deepSearch-Scorer", "WHISPERX", "WHISPERX-Allign"]
options = o
for option in options:
	print(option)
	problems = []
	p = True
	for t in types:
		problems = []
		f1Lines, d1 = (read_files_with_prefix("../transcript/" + option + "/" + t,"bdl"))
		f2Lines, d2 = (read_files_with_prefix("../transcript/" + option + "/" + t,"clb"))

		if(dataItems[option]["st5"]['female'] != len(f1Lines)):
			problems.append("ST5 Female Dif\n" + str(len(f1Lines)) + " " + str(dataItems[option]["st5"]['female']))
			p = False
			
		if(dataItems[option]["st5"]['male'] != len(f2Lines)):
			problems.append("ST5 Male Dif\n" + str(len(f2Lines)) + " " + str(dataItems[option]["st5"]['male']))
			p = False

		f1Lines, d1 = (read_files_with_prefix("../transcript/" + option + "/" + t,"en_US_AriaNeural"))
		f2Lines, d2 = (read_files_with_prefix("../transcript/" + option + "/" + t,"en_US_ChristopherNeural"))


		if(dataItems[option]["edge"]['female'] != len(f1Lines)):
			problems.append("edge Female Dif\n" + str(len(f1Lines)) + " " + str(dataItems[option]["edge"]['female']))
			p = False
			
		if(dataItems[option]["edge"]['male'] != len(f2Lines)):
			problems.append("edge Male Dif\n" + str(len(f2Lines)) + " " + str(dataItems[option]["edge"]['male']))
			p = False

		f1Lines, d1 = (read_files_with_prefix("../transcript/" + option + "/" + t,"p225"))
		f2Lines, d2 = (read_files_with_prefix("../transcript/" + option + "/" + t,"p229"))

		if(dataItems[option]["vits"]['female'] != len(f1Lines)):
			problems.append("vits Female Dif\n" + str(len(f1Lines)) + " " + str(dataItems[option]["vits"]['female']))
			p = False
			
		if(dataItems[option]["vits"]['male'] != len(f2Lines)):
			problems.append("vits Male Dif\n" + str(len(f2Lines)) + " " + str(dataItems[option]["vits"]['male']))
			p = False	

		f1Lines, d1 = (read_files_with_prefix("../transcript/" + option + "/" + t,"female"))
		f2Lines, d2 = (read_files_with_prefix("../transcript/" + option + "/" + t,"male"))

		if(dataItems[option]["human"]['female'] != len(f1Lines)):
			problems.append("Human Female Dif\n" + str(len(f1Lines)) + " " + str(dataItems[option]["human"]['female']))
			p = False
			
		if(dataItems[option]["human"]['male'] != len(f2Lines)):
			problems.append("Human Male Dif\n" + str(len(f2Lines)) + " " + str(dataItems[option]["human"]['male']))
			p = False	

		if(len(problems) > 0):
			print("TYPE:" ,t, "\nOption:",option)
		for x in problems:
			print(x)
		print("\n\n")


