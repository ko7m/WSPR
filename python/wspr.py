# WSPR protocol encoding

import numpy as np
from scipy.io.wavfile import write

ALPHABET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ '
ALPHABET_IDX = {c:i for i,c in enumerate(ALPHABET)}

LOC_ALPHABET = 'ABCDEFGHIJKLMNOPQR'
LOC_ALPHABET_IDX = {c:i for i,c in enumerate(LOC_ALPHABET)}

SYNC = [1,1,0,0,0,0,0,0,1,0,0,0,1,1,1,0,0,0,1,0,0,1,0,1,1,1,
        1,0,0,0,0,0,0,0,1,0,0,1,0,1,0,0,
        0,0,0,0,1,0,1,1,0,0,1,1,0,1,0,0,0,1,1,0,1,0,0,0,0,1,
        1,0,1,0,1,0,1,0,1,0,0,1,0,0,1,0,
        1,1,0,0,0,1,1,0,1,0,1,0,0,0,1,0,0,0,0,0,1,0,0,1,0,0,
        1,1,1,0,1,1,0,0,1,1,0,1,0,0,0,1,
        1,1,0,0,0,0,0,1,0,1,0,0,1,1,0,0,0,0,0,0,0,1,1,0,1,0,
        1,1,0,0,0,1,1,0,0,0]

def encode_word(callsign, locator, dbm):
    if not callsign[2].isnumeric():
        assert callsign[1].isnumeric()
        callsign = ' ' + callsign
    if len(callsign) < 6:
        callsign = callsign + (' ' * (6-len(callsign)))
    assert len(callsign) == 6

    callsign = [ALPHABET_IDX[c] for c in callsign]
    assert callsign[1] < 36
    assert callsign[2] < 10
    assert callsign[3] >= 10
    assert callsign[4] >= 10
    assert callsign[5] >= 10

    n_callsign = callsign[0]
    n_callsign = 36*n_callsign + callsign[1]
    n_callsign = 10*n_callsign + callsign[2]
    n_callsign = 27*n_callsign + (callsign[3]-10)
    n_callsign = 27*n_callsign + (callsign[4]-10)
    n_callsign = 27*n_callsign + (callsign[5]-10)
    assert n_callsign < 37*36*10*27*27*27

    assert len(locator) == 4
    assert locator[2:].isnumeric()

    locator = [LOC_ALPHABET_IDX[c] for c in locator[:2]] + \
              [ALPHABET_IDX[c] for c in locator[2:]]

    n_locator = (179 - 10*locator[0] - locator[2])*180 + \
                10*locator[1] + locator[3]
    assert n_locator >= 179
    assert n_locator <= 32220

    assert 0 <= dbm <= 60
    corr = [0, -1, 1, 0, -1, 2, 1, 0, -1, 1]
    n_dbm = dbm + corr[dbm % 10] + 64
    
    n = (n_callsign << (15+7)) | (n_locator << 7) | n_dbm

    # MSB -> LSB order
    return n


def convolute(n):
    def parity(x):
        assert x >= 0
        p = 0
        while x:
            p ^= (x & 1)
            x = x >> 1
        return p

    # Add zero bits at the end for padding
    # Total number of bits at this stage: 81
    n = n << 31

    r0 = 0
    r1 = 0
    for i in range(81):
        b = (n >> 80) & 1
        n = n << 1
        r0 = (r0 << 1) | b
        r1 = (r1 << 1) | b
        b0 = parity(r0 & 0xF2D05351)
        b1 = parity(r1 & 0xE4613C47)
        yield b0
        yield b1


def interleave(s):
    def byte_bit_reverse(x):
        assert x >= 0 and x <= 255
        return int("{0:08b}".format(x)[::-1], 2)

    d = [None]*162
    s_i = 0
    for i in range(256):
        d_i = byte_bit_reverse(i)
        if d_i < 162:
            d[d_i] = s[s_i]
            s_i += 1
    assert s_i == 162, s_i
    assert not (None in d), d
    return d


def wspr_encode(callsign, locator, dbm):
    n = encode_word(callsign.upper(), locator.upper(), dbm)
    #print("0x{:X}".format(n))
    convoluted = list(convolute(n))
    interleaved = interleave(convoluted)
    assert len(SYNC) == len(interleaved), (len(SYNC), len(interleaved))
    symbols = [s + 2*x for s, x in zip(SYNC, interleaved)]
    return symbols

def generate_ws_signal(ws_symbols, base_freq=1500.0, spacing=1.46, sample_rate=12000, symbol_duration=8192):
    """
    Generate the WSPR audio signal based on the given symbols.
    """
    signal = []
    t = np.arange(symbol_duration) / sample_rate  # Time array for one symbol
    for symbol in ws_symbols:
        freq = base_freq + symbol * spacing
        waveform = np.sin(2 * np.pi * freq * t)
        signal.extend(waveform)
    return np.array(signal)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 4:
        print('Usage: %s callsign locator dbm' % sys.argv[0])
        sys.exit(1)
    callsign = sys.argv[1]
    locator = sys.argv[2]
    dbm = int(sys.argv[3])
    symbols = wspr_encode(callsign, locator, dbm)

    # Generate the audio
    audio_signal = generate_ws_signal(symbols)

    # Normalize and save as a 16 bit PCM WAV file
    audio_signal = np.int16(audio_signal / np.max(np.abs(audio_signal)) * 32767)
    write("wspr_signal.wav", 12000, audio_signal)
