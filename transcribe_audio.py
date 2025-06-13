import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import whisper

# Record audio from the microphone
def record_audio(filename="output.wav", duration=30, fs=16000):
    print(f"Recording for {duration} seconds...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    wav.write(filename, fs, audio)
    print(f"Audio saved to {filename}")
    return filename

# Transcribe audio using Whisper
def transcribe_audio_file(filename):
    print(f"Transcribing {filename}...")
    model = whisper.load_model("base")
    result = model.transcribe(filename)
    print("Transcription complete.")
    return result["text"]
