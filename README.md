# Can-AI-Replace-Human-Speech: A Study on Synthetic Voice and Model Bias

This repository contains the dataset and code used in the paper **"Can AI Replace Human Speech?"**. The project explores synthetic voice generation and model bias.

## How to Use

Follow the steps below to generate, process, and analyze data.

### 1. Create the Data

To generate the dataset, run the following command for **hate** speech:

```bash
python3 main.py -type hate -file ../dataset/hate.json -method create -model edge-tts
```
You can change the model to one of the following:

    edge-tts

    vits

    speecht5

For non-hate speech, simply change the -type to nonhate and point to the nonhate data file:
```bash
python3 main.py -type nonhate -file ../dataset/nonhate.json -method create -model edge-tts
```
2. Convert MP3 to WAV

Once the data is created, convert all MP3 files to WAV format by running:
```bash
python3 mp3towav.py
```

3. Transcribe the Data

Now, transcribe the audio files. For hate speech, run:
```bash
python3 main.py -type hate -file ../dataset/hate.json -method transcribe -model vosk-small
```

You can change the transcription model to one of the following:

    whisperx

    vosk-small

    vosk-giga

    deepspeech

    deepspeech-scorer

For non-hate speech, replace -type hate with -type nonhate and point to the nonhate data file.
4. Verify the Data

To ensure all files were created correctly, run:
```bash
python3 dataVerifier.py
```
5. Generate Metrics

To generate metrics for hate speech, run:
```bash
python3 data.py -type hate -file ../dataset/hate.json
```
For non-hate speech, change -type hate to -type nonhate and point to the nonhate data file.
