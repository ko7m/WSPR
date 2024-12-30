import numpy as np

# Synchronization vector (162 bits)
sync_vector = [
    1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0,
    0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0,
    0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0,
    0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1,
    0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0,
    0, 0
]

def normalize_char(ch):
    """Normalize characters 0..9 A..Z <space> to 0..36"""
    if '0' <= ch <= '9':
        return ord(ch) - ord('0')
    elif 'A' <= ch <= 'Z':
        return ord(ch) - ord('A') + 10
    elif 'a' <= ch <= 'z':
        return ord(ch) - ord('a') + 10
    elif ch == ' ':
        return 36
    else:
        raise ValueError("Invalid character in input")

def encode_callsign(callsign):
    """Encode a callsign"""
    encoded_call = normalize_char(callsign[0])
    encoded_call = encoded_call * 36 + normalize_char(callsign[1])
    encoded_call = encoded_call * 10 + normalize_char(callsign[2])
    encoded_call = encoded_call * 27 + normalize_char(callsign[3]) - 10
    encoded_call = encoded_call * 27 + normalize_char(callsign[4]) - 10
    encoded_call = encoded_call * 27 + normalize_char(callsign[5]) - 10
    return encoded_call

def encode_locator_power(locator, power):
    """Encode locator and power"""
    encoded_loc = (179 - 10 * (normalize_char(locator[0]) - 10) - normalize_char(locator[2])) * 180
    encoded_loc += 10 * (normalize_char(locator[1]) - 10) + normalize_char(locator[3])
    encoded_loc = encoded_loc * 128 + power + 64
    return encoded_loc

def parity(x):
    """Compute parity of x"""
    return x.bit_count() % 2

def convolutional_encode(message):
    """Convolutionally encode a message"""
    i = 0
    ich = 0
    isym = 0
    shiftreg = 0
    symbols = [0] * 162  # Assuming symt needs to store 162 symbols

    while i <= 80:
        if i % 8 == 0:
            ch = message[ich]  # Get next byte of encoded message
            ich += 1
        if ch & 0x80:  # Check if the MSB is set
            shiftreg |= 1
        symbols[isym] = parity(shiftreg & 0xF2D05351)
        isym += 1
        symbols[isym] = parity(shiftreg & 0xE4613C47)
        isym += 1
        ch <<= 1  # Left shift ch by 1 bit
        shiftreg <<= 1  # Left shift shiftreg by 1 bit
        i += 1

    return symbols

def interleave_sync(symbols):
    """Interleave and synchronize symbols"""
    reordered_symbols = [0] * len(symbols)
    for i in range(len(symbols)):
        i_rev = int('{:08b}'.format(i)[::-1], 2)
        if i_rev < len(symbols):
            reordered_symbols[i_rev] = sync_vector[i_rev] + 2 * symbols[i]
    return reordered_symbols

def encode_wspr(callsign, locator, power):
    """Main WSPR encoding function"""
    encoded_call = encode_callsign(callsign)
    encoded_loc_power = encode_locator_power(locator, power)
    message = [(encoded_call >> i) & 0xFF for i in (20, 12, 4)]
    message += [(encoded_call << 4) & 0x0FF]
    message[3] = message[3] + (0x0f & encoded_loc_power >> 18)

    message += [(encoded_loc_power >> i) & 0xFF for i in (10, 2)]
    message += [(encoded_loc_power << 6) & 0xFF]
    message += [0 for i in range(4)]
    for byte in message:
        print("0x{:X}".format(byte))
    symbols = convolutional_encode(message)
    return interleave_sync(symbols)

# Test encoding
callsign = "KO7M  "
locator = "CN87"
power = 10
wspr_symbols = encode_wspr(callsign, locator, power)
print(wspr_symbols)
