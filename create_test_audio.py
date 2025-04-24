#!/usr/bin/env python3
"""
Create a simple test audio file (sine wave) for testing the audio-analyzer MCP server.
"""

import numpy as np
from scipy.io import wavfile
import os
from pathlib import Path

def create_sine_wave(freq=440, duration=5, sample_rate=44100):
    """Create a sine wave with the given frequency, duration, and sample rate."""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    sine_wave = 0.5 * np.sin(2 * np.pi * freq * t)
    return sine_wave

def main():
    # Create a simple sine wave
    sample_rate = 44100  # CD quality
    duration = 5  # 5 seconds
    
    # Create a 440 Hz sine wave (A4 note)
    audio_data = create_sine_wave(freq=440, duration=duration, sample_rate=sample_rate)
    
    # Add a second sine wave at 880 Hz (A5 note) to make it more interesting
    audio_data += 0.3 * create_sine_wave(freq=880, duration=duration, sample_rate=sample_rate)
    
    # Normalize to prevent clipping
    audio_data = audio_data / np.max(np.abs(audio_data))
    
    # Convert to 16-bit PCM
    audio_data_16bit = (audio_data * 32767).astype(np.int16)
    
    # Create the output directory if it doesn't exist
    output_dir = Path("sequence_maker/tests/resources")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save as WAV file
    wav_path = output_dir / "test_audio.wav"
    wavfile.write(wav_path, sample_rate, audio_data_16bit)
    print(f"Created WAV file: {wav_path}")
    
    try:
        # Try to save as MP3 if pydub is available
        from pydub import AudioSegment
        mp3_path = output_dir / "test_audio.mp3"
        AudioSegment.from_wav(str(wav_path)).export(str(mp3_path), format="mp3")
        print(f"Created MP3 file: {mp3_path}")
    except ImportError:
        print("pydub not installed, skipping MP3 creation")
        print("To install pydub: pip install pydub")
        print("You may also need to install ffmpeg")

if __name__ == "__main__":
    main()