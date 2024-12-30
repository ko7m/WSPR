import numpy as np
import wave

# Constants
FS = 48000                  # Sample rate (48 kHz)
BAUD_RATE = 1.4648          # Symbol rate
SYMBOL_DURATION = 1 / BAUD_RATE
TONE_SPACING = BAUD_RATE    # Tone spacing (1.4648 Hz)
BASE_FREQUENCY = 1500       # Base frequency in Hz (adjust as needed)
AMPLITUDE = 0.5             # Signal amplitude

# Generate WSPR symbols (example: 162 random symbols for demonstration)
np.random.seed(0)
symbols = np.random.randint(0, 4, size=162)
print("Random WSPR symbols:")
print(symbols)

# Generate the signal
def generate_ws_signal(symbols, fs, base_freq, tone_spacing, amplitude):
    samples_per_symbol = int(fs * SYMBOL_DURATION)
    signal = []

    print("Tones:")
    for symbol in symbols:
        # Compute tone frequency for the current symbol
        tone_freq = base_freq + symbol * tone_spacing
        print(tone_freq)

        # Generate sine wave for the symbol's tone
        t = np.arange(samples_per_symbol) / fs
        tone = amplitude * np.sin(2 * np.pi * tone_freq * t)

        # Append the tone to the signal
        signal.extend(tone)

    return np.array(signal)

# Create WSPR signal
wspr_signal = generate_ws_signal(symbols, FS, BASE_FREQUENCY, TONE_SPACING, AMPLITUDE)

# Save to WAV file
def save_to_wav(signal, fs, filename):
    # Scale signal to 16-bit range
    scaled_signal = np.int16(signal / np.max(np.abs(signal)) * 32767)

    # Write to WAV file
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)            # Mono
        wf.setsampwidth(2)            # 16-bit samples
        wf.setframerate(fs)           # Sampling rate
        wf.writeframes(scaled_signal.tobytes())

save_to_wav(wspr_signal, FS, 'wspr_signal.wav')
print("WSPR signal saved as 'wspr_signal.wav'")
