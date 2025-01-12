pip install pipwin
pipwin install pyaudio
import streamlit as st
import pyaudio
import wave
import threading
import time
from datetime import datetime
import os

class AudioRecorder:
    def _init_(self):
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.recording = False
        self.frames = []
        self.audio = pyaudio.PyAudio()

    def start_recording(self):
        self.recording = True
        self.frames = []
        threading.Thread(target=self._record).start()

    def stop_recording(self):
        self.recording = False

    def _record(self):
        stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )

        while self.recording:
            data = stream.read(self.CHUNK)
            self.frames.append(data)

        stream.stop_stream()
        stream.close()

    def save_recording(self, filename):
        # Ensure the recordings directory exists
        os.makedirs("recordings", exist_ok=True)
        
        # Create the full file path
        filepath = os.path.join("recordings", filename)
        
        wf = wave.open(filepath, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        return filepath

def main():
    st.title("Audio Recorder")

    # Initialize session state for recorder
    if 'recorder' not in st.session_state:
        st.session_state.recorder = AudioRecorder()
    if 'recording_status' not in st.session_state:
        st.session_state.recording_status = False
    if 'recorded_files' not in st.session_state:
        st.session_state.recorded_files = []

    # Create columns for buttons
    col1, col2 = st.columns(2)

    # Recording controls
    with col1:
        if st.button("Start Recording"):
            if not st.session_state.recording_status:
                st.session_state.recorder.start_recording()
                st.session_state.recording_status = True
                st.error("🔴 Recording in progress...")

    with col2:
        if st.button("Stop Recording"):
            if st.session_state.recording_status:
                st.session_state.recorder.stop_recording()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"recording_{timestamp}.wav"
                filepath = st.session_state.recorder.save_recording(filename)
                st.session_state.recorded_files.append(filepath)
                st.session_state.recording_status = False
                st.success(f"Recording saved as {filename}")

    # Display recording status
    if st.session_state.recording_status:
        st.markdown("### Recording Status")
        status_placeholder = st.empty()
        while st.session_state.recording_status:
            status_placeholder.write("Recording... Duration: {:.2f} seconds".format(
                len(st.session_state.recorder.frames) * st.session_state.recorder.CHUNK / 
                st.session_state.recorder.RATE
            ))
            time.sleep(0.1)

    # Display recorded files
    if st.session_state.recorded_files:
        st.markdown("### Recorded Files")
        for file in st.session_state.recorded_files:
            filename = os.path.basename(file)
            col1, col2 = st.columns([3, 1])
            with col1:
                st.audio(file)
            with col2:
                st.write(filename)

if __name__ == "_main_":
    main()
