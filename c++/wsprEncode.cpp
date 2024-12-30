#include <iostream>
#include <vector>
#include <cmath>
#include <fstream>
#include <bitset>
#include <stdexcept>

std::vector<int> sync_vector = {
    1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0,
    0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0,
    0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0,
    0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1,
    0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0,
    0, 0
};

int normalize_char(char ch) {
    if ('0' <= ch && ch <= '9') {
        return ch - '0';
    } else if ('A' <= ch && ch <= 'Z') {
        return ch - 'A' + 10;
    } else if (ch == ' ') {
        return 36;
    } else {
        throw std::invalid_argument("Invalid character in input");
    }
}

int encode_callsign(const std::string& callsign) {
    int encoded_call = normalize_char(callsign[0]);
    encoded_call = encoded_call * 36 + normalize_char(callsign[1]);
    encoded_call = encoded_call * 10 + normalize_char(callsign[2]);
    encoded_call = encoded_call * 27 + normalize_char(callsign[3]) - 10;
    encoded_call = encoded_call * 27 + normalize_char(callsign[4]) - 10;
    encoded_call = encoded_call * 27 + normalize_char(callsign[5]) - 10;
    return encoded_call;
}

int encode_locator_power(const std::string& locator, int power) {
    int encoded_loc = (179 - 10 * (normalize_char(locator[0]) - 10) - normalize_char(locator[2])) * 180;
    encoded_loc += 10 * (normalize_char(locator[1]) - 10) + normalize_char(locator[3]);
    encoded_loc = encoded_loc * 128 + power + 64;
    return encoded_loc;
}

int parity(int x) {
    return std::bitset<32>(x).count() % 2;
}

std::vector<int> convolutional_encode(const std::vector<int>& message) {
    int shiftreg = 0;
    std::vector<int> symbols;
    for (int byte : message) {
        for (int i = 0; i < 8; ++i) {
            shiftreg = (shiftreg << 1) | ((byte >> (7 - i)) & 1);
            symbols.push_back(parity(shiftreg & 0xF2D05351));
            symbols.push_back(parity(shiftreg & 0xE4613C47));
        }
    }
    return symbols;
}

#if 0
std::vector<int> interleave_sync(const std::vector<int>& symbols) {
    std::vector<int> reordered_symbols(symbols.size());
    for (size_t i = 0; i < symbols.size(); ++i) {
        std::bitset<8> i_rev(i);
        int i_rev_int = static_cast<int>(i_rev.to_ulong());
        if (i_rev_int < symbols.size()) {
            reordered_symbols[i_rev_int] = sync_vector[i_rev_int] + 2 * symbols[i];
        }
    }
    return reordered_symbols;
}
#endif

std::vector<int> interleave_sync(const std::vector<int>& symbols) {
    std::vector<int> reordered_symbols(symbols.size());
    for (size_t i = 0; i < symbols.size(); ++i) {
        int i_rev_int = 0;
        for (int j = 0; j < 8; ++j) {
            i_rev_int |= ((i >> j) & 1) << (7 - j);
        }
        if (i_rev_int < symbols.size()) {
            reordered_symbols[i_rev_int] = sync_vector[i_rev_int] + 2 * symbols[i];
        }
    }
    return reordered_symbols;
}

std::vector<int> encode_wspr(const std::string& callsign, const std::string& locator, int power) {
    int encoded_call = encode_callsign(callsign);
    int encoded_loc_power = encode_locator_power(locator, power);
    std::vector<int> message = {
        encoded_call >> 20,
        (encoded_call >> 12) & 0xFF,
        (encoded_call >> 4) & 0xFF,
        (encoded_call << 4) & 0xF0
    };
    message.push_back((encoded_loc_power >> 18) & 0xFF);
    message.push_back((encoded_loc_power >> 10) & 0xFF);
    message.push_back((encoded_loc_power >> 2) & 0xFF);
    std::vector<int> symbols = convolutional_encode(message);
    return interleave_sync(symbols);
}

int main() {
    std::string callsign = "KO7M  ";
    std::string locator = "CN87";
    int power = 10;
    std::vector<int> wspr_symbols = encode_wspr(callsign, locator, power);

    // Output the symbols
    for (int symbol : wspr_symbols) {
        std::cout << symbol << " ";
    }
    std::cout << std::endl;

    return 0;
}
