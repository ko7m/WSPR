import numpy as np
from scipy.io.wavfile import write

def generate_ws_signal(ws_symbols, base_freq=1500.0, spacing=1.46, sample_rate=12000, symbol_duration=8192):
    """
    Generate the WSPR audio signal based on the given symbols.
    """
    signal = []
    t = np.arange(symbol_duration) / sample_rate  # Time array for one symbol
    print(t)
    for symbol in ws_symbols:
        freq = base_freq + symbol * spacing
        waveform = np.sin(2 * np.pi * freq * t)
        signal.extend(waveform)
    return np.array(signal)

wspr_symbols = [3,3,0,2,0,0,0,2,3,0,2,2,3,1,3,0,0,2,3,2,0,1,0,1,3,3,1,0,0,2,2,2,2,0,1,0,2,1,0,3,2,0,2,2,0,2,3,0,3,3,2,2,1,1,2,3,2,2,0,3,1,0,1,0,0,0,0,1,1,0,3,0,3,0,1,2,3,2,0,1,0,0,3,0,3,3,0,0,0,3,1,0,1,0,3,2,2,0,1,2,2,2,0,2,1,2,0,1,0,2,3,3,1,2,1,1,2,2,1,3,0,1,0,0,0,1,1,1,2,0,0,0,2,1,0,1,0,0,3,3,0,2,0,2,0,2,0,3,1,2,3,0,3,1,2,2,2,1,1,2,0,2]

# Generate the audio
audio_signal = generate_ws_signal(wspr_symbols)

# Normalize and save as a WAV file
audio_signal = np.int16(audio_signal / np.max(np.abs(audio_signal)) * 32767)  # Normalize to 16-bit PCM
write("wspr_signal.wav", 12000, audio_signal)
