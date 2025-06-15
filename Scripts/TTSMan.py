import asyncio
import logging
import sys
import os
from contextlib import redirect_stdout
import torch
import soundfile as sf
from datasets import load_dataset
baseFolder = ""

def setBaseFolder(o):
	global baseFolder
	baseFolder = "../audioFiles/" + str(o)

def setFolder(folder):
	baseFolder = folder

class Edge:
	def __init__(self,voice="en-US-ChristopherNeural"):
		self.name = "edge_" + voice
		self.voice = voice

	async def speak(self, text, out, folder = "edge"):
		import edge_tts
		try:
			out = out.replace(".txt","")
			
			if not os.path.exists(baseFolder + "/edge"):
				os.makedirs(baseFolder + "/edge")
			if not os.path.exists(baseFolder + "/edge/" + self.voice.replace("-","_")):
				os.makedirs(baseFolder + "/edge/" + self.voice.replace("-","_"))

			endPath = baseFolder + "/edge/" + self.voice.replace("-","_") + "/" + str(out) + ".wav"
			if not os.path.exists(endPath):
				communicate = edge_tts.Communicate(
					text=text,
					voice=self.voice, 
					rate="+0%"                  
				)
				await communicate.save(endPath)
			return -1
		except Exception as e:
			return out

class TTSGlobal:
	def __init__(self, voice="tts_models/en/vctk/vits", voiceName = "", folder="vits"):
		from TTS.api import TTS
		
		logging.getLogger("TTS").setLevel(logging.ERROR)
		
		# Optional: Suppress other libraries too
		logging.getLogger("numba").setLevel(logging.WARNING)
		logging.getLogger("tensorflow").setLevel(logging.ERROR)
		self.tts = TTS(model_name=voice)
		self.folderOut = voice.split("/")[len(voice.split("/")) - 1]
		self.voice = voice.split("/")[len(voice.split("/")) - 1]
		if(voiceName != ""):
			self.voice = voiceName
		self.name = "vits_" + self.voice
		

	def speak(self, text, out, ):		
		try:
			out = out.replace(".txt","").replace(".mp3","").replace(".wav","")
			if not os.path.exists(baseFolder + "/"+str(self.folderOut)):
				os.makedirs(baseFolder + "/"+str(self.folderOut))
			
			if not os.path.exists(baseFolder + "/"+str(self.folderOut) + "/" + self.voice.replace("-","_")):
				os.makedirs(baseFolder + "/"+str(self.folderOut) + "/"  + self.voice.replace("-","_"))

			endPath = baseFolder + "/"+str(self.folderOut) + "/"  + self.voice.replace("-","_") + "/" + str(out) + ".wav"
			if not os.path.exists(endPath):
				with open(os.devnull, 'w') as fnull:
					with redirect_stdout(fnull):
						self.tts.tts_to_file(
							text=text, 
							file_path=endPath,
							speaker=self.voice
						)
			return -1
		except Exception as e:
			return out


#from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
#import torchaudio
class ST5:
	def __init__(self, voice: str = "bdl"):
		from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
		# Load models
		self.voice = voice
		self.name = "ST5_" + voice
		self.processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
		self.model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
		self.vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

		# Load speaker embeddings dataset
		dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")

		# Extract speaker IDs from 'filename' field
		speaker_ids = [item["filename"].split("_")[2] for item in dataset]

		if voice not in speaker_ids:
			raise ValueError(f"Voice '{voice}' not found. Available voices: {sorted(set(speaker_ids))}")

		index = speaker_ids.index(voice)
		self.embedding = torch.tensor(dataset[index]["xvector"]).unsqueeze(0)

	def speak(self, text: str, out: str = "output.wav", folder="ST5"):
		try:
			out = out.replace(".txt","")
			if not os.path.exists(baseFolder + "/"+str(folder)):
				os.makedirs(baseFolder + "/"+str(folder))
			
			if not os.path.exists(baseFolder + "/"+str(folder) + "/" + self.voice.replace("-","_")):
				os.makedirs(baseFolder + "/"+str(folder) + "/"  + self.voice.replace("-","_"))

			endPath = baseFolder + "/" + str(folder) + "/"  + self.voice.replace("-","_") + "/" + str(out) + ".wav"
			if not os.path.exists(endPath):
				inputs = self.processor(text=text, return_tensors="pt")
				speech = self.model.generate_speech(inputs["input_ids"], self.embedding, vocoder=self.vocoder)
				torchaudio.save(endPath, speech.unsqueeze(0), 16000)
			return -1
		except Exception as e:
			print(e)
			return out