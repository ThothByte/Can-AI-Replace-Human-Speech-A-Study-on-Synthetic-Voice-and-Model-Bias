import asyncio
import os
import threading
import time
import json
import re
import clean
from threading import Lock
import logging
import os

chunkWorkers = 4
logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s [%(name)s] %(message)s",
)

class Center:
	def __init__(self, f= "nonPointer"):
		self.lock = Lock()
		self.baseF = f

	def train(self, ttsModel, dataset):
		print("TRAINING DATASET", len(dataset))
		c = 0
		error = 0
		sError = 0
		name = ttsModel.name
		error_dir = "../error/"
		os.makedirs(error_dir, exist_ok=True)

		
		print("STARTING", name)
		time.sleep(1)
		start_time = time.time()  # Track the overall start time
		last_time = start_time   # Track the last iteration's time
		total_length = len(dataset)	

		for idx, data_point in enumerate(dataset):
			try:
				out = ttsModel.speak(data_point["text"], data_point["id"])
				if out != -1:
					# Write to file with thread-safe locking
					with self.lock:
						with open(os.path.join(error_dir, f"{name}.log"), "a") as f:
							f.write(json.dumps(data_point) + "\n")
					error += 1
			except Exception as e:
				sError += 1
				print(f"[{name}] Error: {e}")

			c += 1


			# Display progress and ETA
			if idx % 2 == 0 or c == len(dataset):  # Reduce print frequency			
				# Calculate elapsed time and ETA
				current_time = time.time()
				elapsed_time = current_time - start_time
				avg_time_per_iter = elapsed_time / c if c != 0 else 0
				remaining_iters = total_length - c
				eta = avg_time_per_iter * remaining_iters
				eta_minutes = int(eta // 60)
				eta_seconds = int(eta % 60)
				progress = f"[{name}] Progress: {c}/{len(dataset)} | Errors: {error} | Skipped: {sError} | ETA: {eta_minutes:02d}:{eta_seconds:02d}    "
				logging.info(progress)
		
	
	async def trainA(self, ttsModel, dataset):
		print("TRAINING DATASET", len(dataset))
		c = 0
		error = 0
		sError = 0
		name = ttsModel.name
		error_dir = "../error/"
		os.makedirs(error_dir, exist_ok=True)

		
		print("STARTING", name)
		time.sleep(1)
		start_time = time.time()  # Track the overall start time
		last_time = start_time   # Track the last iteration's time
		total_length = len(dataset)	

		for idx, data_point in enumerate(dataset):
			try:
				out = await ttsModel.speak(data_point["text"], data_point["id"])
				if out != -1:
					# Write to file with thread-safe locking
					with self.lock:
						with open(os.path.join(error_dir, f"{name}.log"), "a") as f:
							f.write(json.dumps(data_point) + "\n")
					error += 1
			except Exception as e:
				sError += 1
				print(f"[{name}] Error: {e}")

			c += 1


			# Display progress and ETA
			if idx % 2 == 0 or c == len(dataset):  # Reduce print frequency			
				# Calculate elapsed time and ETA
				current_time = time.time()
				elapsed_time = current_time - start_time
				avg_time_per_iter = elapsed_time / c if c != 0 else 0
				remaining_iters = total_length - c
				eta = avg_time_per_iter * remaining_iters
				eta_minutes = int(eta // 60)
				eta_seconds = int(eta % 60)
				progress = f"[{name}] Progress: {c}/{len(dataset)} | Errors: {error} | Skipped: {sError} | ETA: {eta_minutes:02d}:{eta_seconds:02d}    "
				logging.info(progress)
		


	def setFolder(self, folder = "nonPointer"):
		self.baseF = folder

	def transcribe(self, sttModel, dataset, voice, page):	
		print("STARTING",sttModel.name)		
		c = 0	
		tt = 0
		error = 0 
		try:
			if not os.path.exists("../transcript/"+self.baseF+"/" + sttModel.name):
				os.makedirs("../transcript/"+self.baseF+"/" + sttModel.name )
		except Exception as e:
			pass
		fileP = "../transcript/"+self.baseF+"/" + sttModel.name + "/" + str(voice) + "-" + str(page) + ".json"
		print(fileP)
		response = {}
		if(os.path.isfile(fileP)):
			f = open(fileP, "r")
			response = "{" + "".join(f.readlines())[0:len("".join(f.readlines()))-2] + "}"
			f.close()
			response = json.loads(response)			
		else:
			f = open(fileP, "w+")
			f.close()
		time.sleep(1)

		fe = open("../transcript/"+self.baseF+"/" + sttModel.name + "/" + str(voice) + "-" + str(page) + "-error.json", "a+")	
		textWrite = ""
		for data in dataset:
			try:
				data["location"] = data["location"].replace("\\","/")
				data["voice"] = data["voice"].replace("../audioFilesClean/","")
				if(data["id"] not in response):
					out = sttModel.transcribe(data["location"])
					if(out != -1):
						
						c += 1	
						item = {}
						item[data["id"]] = {"text": out, "voice" : data["voice"].replace("../audioFilesClean/",""), "id" : data["id"], "location" : data["location"]}
						textWrite += '"' + data["id"] + '" : ' + json.dumps({"text": out, "voice" : data["voice"], "id" : data["id"], "location" : data["location"]}) + ",\n"
					else:
						error += 1	
						fe.write(json.dumps(data) + "\n")
				else:					
					c += 1	
			except Exception as e:
				print(e)
			print(c, len(dataset), error, round(c/len(dataset) * 100,2), round(error/len(dataset) * 100,2),end="\r")
			tt += 1
			if(tt % 10 == 0 or tt == len(dataset)):
				f = open(fileP, "a+")
				f.write(textWrite)
				f.close()
				textWrite = ""	
		
		fe.close()

data = []
datasetLoc = "../datasets/"
fP = datasetLoc
datasetName = "CommonVoice"


import argparse

# Create the parser
parser = argparse.ArgumentParser(description="The main script to create or transcribe audio")

# Define the arguments with their default values
parser.add_argument('-file', type=str, default='hate.json', help="location of the hate or non-hate file (default: hate.json)")
parser.add_argument('-type', type=str, default='hate', choices=['hate', 'nonhate'], help="Type of data (default: 'hate').")
parser.add_argument('-method', type=str, default='create', choices=['create', 'transcribe'], help="Type of method you want to run (default: create)")
parser.add_argument('-model', type=str, default='WhisperX', help="Which model should be used for TTS or STT")

# Parse the arguments
args = parser.parse_args()




f = open(args.file, "r")
dataRaw = json.loads("".join(f.readlines()))
f.close()

print(f"[LOADED DATASET] {args.file} contains {len(dataRaw)} points")


for x in dataRaw:
	text = x["text"]
	id = x["id"]
	data.append({'text' : text, 'id' : id})

def listToSmaller(data, chunk, chunkOf):
	chunkSize = len(data)
	if(chunkSize * (chunkOf + 1) > len(data)):
		print(len(data), len(data[chunkSize * chunkOf : ]))
		data = data[chunkSize * chunkOf : ]
	else:	
		print(len(data), len(data[chunkSize * chunkOf : chunkSize * (chunkOf + 1)]))
		print(chunkSize * chunkOf, chunkSize * (chunkOf + 1))
		data = data[chunkSize * chunkOf : chunkSize * (chunkOf + 1)]
	return data

#runner = Center()

def split_data_dynamically(data, num_workers):
    chunk_size = len(data) // num_workers  # Integer division to get chunk size

    # Create chunks
    dataloads = [data[i * chunk_size:(i + 1) * chunk_size] for i in range(num_workers)]

    # If there's any remainder, add it to the last chunk
    remainder = len(data) % num_workers
    if remainder:
        dataloads[-1].extend(data[-remainder:])  # Add remainder to the last chunk

    return dataloads

def main():
	import TTSMan
	chunk = 9
	dlen = len(data) // chunk
	runner = Center()
	runner2 = Center()
	print("RUNNING ON CHUNK:",chunk)
	print("DATASET LEN:",len(data))
	print("CHUNK SIZE:", dlen)
	print("START [SPEAK] > ")

	data_splits = [
		data[0: dlen],
		data[dlen * 1 : dlen * 2],
		data[dlen * 2 : dlen * 3],
		data[dlen * 3 : dlen * 4],

		data[dlen * 4 : dlen * 5],
		data[dlen * 5 : dlen * 6],
		data[dlen * 6 : dlen * 7],
		data[dlen * 7 : dlen * 8],

		data[dlen * 8 :],
	]
	if(args.model.lower() == "vits"):
		tts1 = TTSMan.TTSGlobal("tts_models/en/vctk/vits",voiceName="p225")
		tts2 = TTSMan.TTSGlobal("tts_models/en/vctk/vits",voiceName="p229")
	else:
		tts1 = TTSMan.ST5("bdl")
		tts2 = TTSMan.ST5("clb")
	t1 = threading.Thread(target=runner.train, args=(tts1, data_splits[0],))
	t2 = threading.Thread(target=runner.train, args=(tts1, data_splits[1],))
	t3 = threading.Thread(target=runner.train, args=(tts1, data_splits[2],))
	t4 = threading.Thread(target=runner.train, args=(tts1, data_splits[3],))
	t5 = threading.Thread(target=runner.train, args=(tts1, data_splits[4],))
	t6 = threading.Thread(target=runner.train, args=(tts1, data_splits[5],))
	t7 = threading.Thread(target=runner.train, args=(tts1, data_splits[6],))
	t8 = threading.Thread(target=runner.train, args=(tts1, data_splits[7],))
	t9 = threading.Thread(target=runner.train, args=(tts1, data_splits[8],))

	t1.start()
	t2.start()
	t3.start()
	t4.start()
	t5.start()
	t6.start()
	t7.start()
	t8.start()
	t9.start()
	
	t1.join()
	t2.join()
	t3.join()
	t4.join()
	t5.join()
	t6.join()
	t7.join()
	t8.join()
	t9.join()

	t_2_1 = threading.Thread(target=runner2.train, args=(tts2, data_splits[0],))
	t_2_2 = threading.Thread(target=runner2.train, args=(tts2, data_splits[1],))
	t_2_3 = threading.Thread(target=runner2.train, args=(tts2, data_splits[2],))
	t_2_4 = threading.Thread(target=runner2.train, args=(tts2, data_splits[3],))
	t_2_5 = threading.Thread(target=runner2.train, args=(tts2, data_splits[4],))
	t_2_6 = threading.Thread(target=runner2.train, args=(tts2, data_splits[5],))
	t_2_7 = threading.Thread(target=runner2.train, args=(tts2, data_splits[6],))
	t_2_8 = threading.Thread(target=runner2.train, args=(tts2, data_splits[7],))
	t_2_9 = threading.Thread(target=runner2.train, args=(tts2, data_splits[8],))

	t_2_1.start()
	t_2_2.start()
	t_2_3.start()
	t_2_4.start()
	t_2_5.start()
	t_2_6.start()
	t_2_7.start()
	t_2_8.start()
	t_2_9.start()

	t_2_1.join()
	t_2_2.join()
	t_2_3.join()
	t_2_4.join()
	t_2_5.join()
	t_2_6.join()
	t_2_7.join()
	t_2_8.join()
	t_2_9.join()
	
async def mainA():
	import TTSMan
	chunk = 6
	dlen = len(data) // chunk
	print("DATASET SIZE:", len(data))
	print("RUNNING ON CHUNK:",chunk)
	print("CHUNK SIZE:", dlen)
	
	data_splits = [
		data[0: dlen],
		data[dlen * 1: dlen * 2],
		data[dlen * 2:dlen * 3],
		data[dlen * 3:dlen * 4],
		data[dlen * 4:dlen * 5],
		data[dlen * 5:]
	]

	# Create TTS model instances
	tts_aria = TTSMan.Edge("en-US-AriaNeural")
	tts_chris = TTSMan.Edge("en-US-ChristopherNeural")


	
	# Create runner instances
	aria_runner = Center()
	chris_runner = Center()

	# Create 4 tasks for each voice using the same runner
	tasks = [
		# Aria voice
		aria_runner.trainA(tts_aria, chunk) for chunk in data_splits
	] + [
		# Christopher voice
		chris_runner.trainA(tts_chris, chunk) for chunk in data_splits
	]

	# Run all tasks in parallel
	await asyncio.gather(*tasks)
	exit()


def getAudioClips(folder):
	data = []
	print("GETTING FILES")
	for root, dirs, files in os.walk(folder):
		for filename in files:
			file_path = os.path.join(root, filename)
			if os.path.isfile(file_path):
				data.append({"location": file_path.replace("\\\\","/"), "voice" : root.split("\\")[-1], "id" : filename.replace(".txt","").replace(".mp3","").replace(".wav","")})
	return data

def getTranscript(voice, data, chunkOf,w1, rr):
	print("STARTING TRANSCRIPT")	
	if(chunkOf != -1):
		data = data[chunkOf]#"Vosk-small", "vosk-model-small-en-us-0.15")
	time.sleep(1)
	#w1 = STTMan.ESPNet()
	#w1 = STTMan.Vosk("Vosk-small", "vosk-model-small-en-us-0.15")
	#w1 = STTMan.Vosk("Vosk-giga", "vosk-model-en-us-0.42-gigaspeech")
	#t1 = threading.Thread(target=runner.transcribe, args=(w1, data,"en_US_AriaNeural",))
	rr.transcribe(w1, data, voice, chunkOf)
	#print("DONE?")
	#t1.start()


def transcriptMan(fP, voice, f, model):
	print(f)
	if(model.lower() == "whisperx"):		
		import whisperx
		w1 = STTMan.WhisperXC()
	elif(model.lower() == "vosk-small"):
		from vosk import Model, KaldiRecognizer
		w1 = STTMan.Vosk("Vosk-small", "vosk-model-small-en-us-0.15")
	elif(model.lower() == "vosk-giga"):
		from vosk import Model, KaldiRecognizer
		w1 = STTMan.Vosk("Vosk-giga", "vosk-model-en-us-0.42-gigaspeech")
	elif(model.lower() == "deepspeech"):
		import deepspeech
		w1 = STTMan.DeepSearch(False)
	elif(model.lower() == "deepspeech-scorer"):
		import deepspeech
		w1 = STTMan.DeepSearch(True)


	data = getAudioClips(fP)
	chunk = 6
	dlen = len(data) // chunk
	runner = Center(f)

	print("RUNNING ON CHUNK:",chunk)
	print("DATASET LEN:",len(data))
	print("CHUNK SIZE:", dlen)
	print("LOC:",fP)
	print("START [TRANSCRIPT] [" + voice + "] [" + w1.name + "] > ")

	data_splits = [
		data[0:dlen],
		data[dlen:dlen*2],
		data[dlen*2:dlen*3],
		data[dlen*3:dlen*4],
		data[dlen*4:dlen*5],
		data[dlen*5:]
	]

	t1 = threading.Thread(target=getTranscript, args=(voice,data_splits,0,w1,runner,))
	t1.start()

	t2 = threading.Thread(target=getTranscript, args=(voice,data_splits,1,w1,runner,))
	t2.start()

	t3 = threading.Thread(target=getTranscript, args=(voice,data_splits,2,w1,runner,))
	t3.start()

	t4 = threading.Thread(target=getTranscript, args=(voice,data_splits,3,w1,runner,))
	t4.start()

	t5 = threading.Thread(target=getTranscript, args=(voice,data_splits,4,w1,runner,))
	t5.start()
	
	t6 = threading.Thread(target=getTranscript, args=(voice,data_splits,5,w1,runner,))
	t6.start()

	t1.join()
	t2.join()
	t3.join()
	t4.join()
	t5.join()
	t6.join()

def startTranscript():
	
	options = [args.type]

	model = args.model

	for o in options:
		print(o)
		transcriptMan("../audioFilesClean/" + str(o) + "/ST5/bdl", "bdl", o, model)
		transcriptMan("../audioFilesClean/" + str(o) + "/ST5/clb", "clb", o, model)

		transcriptMan("../audioFilesClean/" + str(o) + "/vits/p225", "p225", o, model)
		transcriptMan("../audioFilesClean/" + str(o) + "/vits/p229", "p229", o, model)
		
		transcriptMan("../audioFilesClean/" + str(o) + "/edge/en_US_ChristopherNeural", "en_US_ChristopherNeural", o, model)
		transcriptMan("../audioFilesClean/" + str(o) + "/edge/en_US_AriaNeural", "en_US_AriaNeural", o, model)

		transcriptMan("../audioFilesClean/" + str(o) + "/human/male", "male", o, model)
		transcriptMan("../audioFilesClean/" + str(o) + "/human/female", "female", o, model)


if(args.method == "create"):
	import TTSMan
	TTSMan.setBaseFolder(args.type)
	if(args.model.lower() == "edge-tts"):
		asyncio.run(mainA())
	else:
		main()
else:	
	import STTMan 
	startTranscript()
	
	


