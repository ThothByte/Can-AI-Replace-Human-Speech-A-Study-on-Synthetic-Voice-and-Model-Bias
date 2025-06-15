import os
import wave
import json

#import whisperx
class WhisperXC:
	model = None
	def __init__(self, allignText = False):
		try:
			self.allignText = allignText
			self.name = "WHISPERX"
			self.device = "cpu"
			self.batch_size = 16 # reduce if low on GPU mem
			compute_type = "int8" # change to "int8" if low on GPU mem (may reduce accuracy)
			if(allignText == True):
				self.name = "WHISPERX-Allign"
			# 1. Transcribe with original whisper (batched)
			self.model = whisperx.load_model("base", self.device, compute_type=compute_type, language="en")
		except Exception as e:
			print(e)

	def createModel(self):
		if(self.model == None):
			self.name = "WHISPERX"
			self.device = "cpu"
			self.batch_size = 16 # reduce if low on GPU mem
			compute_type = "int8" # change to "int8" if low on GPU mem (may reduce accuracy)
			self.model = whisperx.load_model("base", self.device, compute_type=compute_type, language="en")

	def transcribe(self,audio_file):
		try:
			audio = whisperx.load_audio(audio_file)
			result = self.model.transcribe(audio, batch_size=self.batch_size)
			if(self.allignText == True):
				model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=self.device)
				result = whisperx.align(result["segments"], model_a, metadata, audio, self.device, return_char_alignments=False)
			transcribed_text = ""
			for segment in result["segments"]:
				transcribed_text += segment["text"] + " "  

			return transcribed_text.strip()
		except Exception as e:
			print(e)
			return -1


#from vosk import Model, KaldiRecognizer
class Vosk:
	
	def __init__(self, name = "Vosk-small", model = "vosk-model-small-en-us-0.15"):
		from vosk import Model, KaldiRecognizer
		#vosk-model-en-us-0.42-gigaspeech
		#Vosk-giga vosk-model-en-us-0.42-gigaspeech
		self.name = name
		self.model = Model("../models/" + model)  # Path to your model

	def transcribe(self, file_path):
		file_path = file_path
		#print(file_path)
		wf = wave.open(file_path, "rb")
		rec = KaldiRecognizer(self.model, wf.getframerate())
		rec.SetWords(True)
		results = []
		while True:
			data = wf.readframes(4000)
			if not data:
				break
			if rec.AcceptWaveform(data):
				results.append(json.loads(rec.Result()))
		results.append(json.loads(rec.FinalResult()))

		transcript = " ".join([r.get("text", "") for r in results])
		return transcript
	
import wave
import numpy as np

class DeepSpeech:
	def __init__(self, scorer = False):
		# Load model
		self.name = "deepSpeech"
		model_file_path = '../datasets/Moz/deepspeech-0.9.3-models.pbmm'
		self.model = deepspeech.Model(model_file_path)
		if(scorer == True):
			scorer_file_path = '../datasets/Moz/deepspeech-0.9.3-models.scorer'
			self.name = "deepSpeech-Scorer"
			self.model.enableExternalScorer(scorer_file_path)

	def transcribe(self, file_path):
		try:
			# Load audio file
			with wave.open(file_path, 'rb') as wf:
				frames = wf.getnframes()
				buffer = wf.readframes(frames)
				audio = np.frombuffer(buffer, dtype=np.int16)

			# Transcribe
			text = self.model.stt(audio)
			return text
		
		except Exception as e:
			print(e)
			return -1
