import streamlit as st
import sounddevice as sd
import numpy as np
import requests
import wave
import tempfile
'''
sounddevice → Records audio from your microphone.
numpy → Handles the recorded audio data as a NumPy array.
requests → Sends audio data to Deepgram's API for transcription.
wave → Saves the recorded audio as a WAV file.
tempfile → Creates a temporary file to store the recorded audio.
'''

import os
from dotenv import load_dotenv

DEEPGRAM_API_KEY = ""

# Function to record audio
def record_audio(duration=5, sample_rate=44100):
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype=np.int16)
    sd.wait()
    return audio_data, sample_rate
'''
Breakdown:
duration=5 → Records for 5 seconds.
sample_rate=44100 → Audio is sampled at 44.1 kHz, which is CD-quality.
sd.rec(...) → Uses sounddevice to start recording:
int(duration * sample_rate) → Calculates the total number of audio samples.
channels=1 → Uses mono recording (single channel).
dtype=np.int16 → Stores audio in 16-bit integer format.
sd.wait() → Waits until recording is finished.
Returns → The recorded audio data and sample rate.
'''

# Function to save audio
def save_audio(audio_data, sample_rate):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        with wave.open(temp_file.name, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data.tobytes())
        return temp_file.name
    
'''
Breakdown:
Creates a temporary file to save the recorded audio.
wave.open(temp_file.name, "wb") → Opens the file in write-binary (wb) mode.
WAV file settings:
setnchannels(1) → Mono audio (1 channel).
setsampwidth(2) → 16-bit samples (2 bytes per sample).
setframerate(sample_rate) → Uses the same sample rate as recording.
writeframes(audio_data.tobytes()) → Converts the NumPy array to bytes and writes it to the file.
Returns → The file path of the saved audio file.
'''   

# Function to send to Deepgram
def transcribe_audio(audio_path):
    url = "https://api.deepgram.com/v1/listen"
    headers = {"Authorization": f"Token {DEEPGRAM_API_KEY}", "Content-Type": "audio/wav"}
    
    with open(audio_path, "rb") as audio_file:
        response = requests.post(url, headers=headers, data=audio_file)
    
    result = response.json()
    return result["results"]["channels"][0]["alternatives"][0]["transcript"]
'''
Breakdown:
Defines Deepgram API URL → https://api.deepgram.com/v1/listen.
Sets HTTP Headers:
"Authorization": f"Token {DEEPGRAM_API_KEY}" → Passes the API key for authentication.
"Content-Type": "audio/wav" → Tells Deepgram the audio format.
Opens the saved WAV file in read-binary (rb) mode.
Sends a POST request with the audio file to Deepgram's API.
Gets JSON response with the transcription result.
Extracts & returns the transcript from the JSON response.
'''

# Streamlit UI
st.title("🎙️ Speech-to-Text with Deepgram")
st.write("Click 'Record & Transcribe' to capture and convert speech to text.")

if st.button("Record & Transcribe"):
    st.write("Recording...")
    audio_data, sample_rate = record_audio()
    audio_path = save_audio(audio_data, sample_rate)
    
    st.write("Transcribing...")
    transcript = transcribe_audio(audio_path)
    
    st.write(f"📝 Transcribed Text: {transcript}")
