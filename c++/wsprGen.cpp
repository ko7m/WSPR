#include <iostream>
#include <fstream>
#include <vector>
#include <cmath>
#include <cstdint>
#include <algorithm>

const double BASE_FREQ = 1500.0;       // Base frequency in Hz
const double SPACING = 1.46;           // Frequency spacing in Hz
const int SAMPLE_RATE = 12000;         // Sample rate in Hz
const int SYMBOL_DURATION = 8192;      // Symbol duration in samples

std::vector<double> generateWSPRSignal(const std::vector<int>& ws_symbols) {
    std::vector<double> signal;
    signal.reserve(ws_symbols.size() * SYMBOL_DURATION);

    for (int symbol : ws_symbols) {
        double freq = BASE_FREQ + symbol * SPACING;
        for (int n = 0; n < SYMBOL_DURATION; ++n) {
            double t = static_cast<double>(n) / SAMPLE_RATE;
            double sample = std::sin(2.0 * M_PI * freq * t);
            signal.push_back(sample);
        }
    }
    return signal;
}

std::vector<int16_t> normalizeSignal(const std::vector<double>& signal) {
    std::vector<int16_t> normalized_signal;
    normalized_signal.reserve(signal.size());

    double max_amplitude = *std::max_element(signal.begin(), signal.end(),
                                             [](double a, double b) { return std::abs(a) < std::abs(b); });

    for (double sample : signal) {
        int16_t normalized_sample = static_cast<int16_t>((sample / max_amplitude) * 32767);
        normalized_signal.push_back(normalized_sample);
    }
    return normalized_signal;
}

void writeWAVFile(const std::string& filename, const std::vector<int16_t>& signal) {
    std::ofstream file(filename, std::ios::binary);

    // WAV file header parameters
    int32_t file_size = 36 + signal.size() * sizeof(int16_t);
    int16_t audio_format = 1; // PCM
    int16_t num_channels = 1; // Mono
    int32_t byte_rate = SAMPLE_RATE * num_channels * sizeof(int16_t);
    int16_t block_align = num_channels * sizeof(int16_t);
    int16_t bits_per_sample = 16;
    int32_t data_chunk_size = signal.size() * sizeof(int16_t);

    // Write WAV header
    file.write("RIFF", 4);
    file.write(reinterpret_cast<const char*>(&file_size), 4);
    file.write("WAVE", 4);
    file.write("fmt ", 4);
    int32_t subchunk1_size = 16;
    file.write(reinterpret_cast<const char*>(&subchunk1_size), 4);
    file.write(reinterpret_cast<const char*>(&audio_format), 2);
    file.write(reinterpret_cast<const char*>(&num_channels), 2);
    file.write(reinterpret_cast<const char*>(&SAMPLE_RATE), 4);
    file.write(reinterpret_cast<const char*>(&byte_rate), 4);
    file.write(reinterpret_cast<const char*>(&block_align), 2);
    file.write(reinterpret_cast<const char*>(&bits_per_sample), 2);
    file.write("data", 4);
    file.write(reinterpret_cast<const char*>(&data_chunk_size), 4);

    // Write audio data
    for (int16_t sample : signal) {
        file.write(reinterpret_cast<const char*>(&sample), sizeof(int16_t));
    }
}

int main() {
    std::vector<int> wspr_symbols = {4,3,0,2,0,0,0,2,3,0,2,2,3,1,3,0,0,2,3,2,0,1,0,1,3,3,1,0,0,2,2,2,2,0,1,0,2,1,0,3,2,0,2,2,0,2,3,0,3,3,2,2,1,1,2,3,2,2,0,3,1,0,1,0,0,0,0,1,1,0,3,0,3,0,1,2,3,2,0,1,0,0,3,0,3,3,0,0,0,3,1,0,1,0,3,2,2,0,1,2,2,2,0,2,1,2,0,1,0,2,3,3,1,2,1,1,2,2,1,3,0,1,0,0,0,1,1,1,2,0,0,0,2,1,0,1,0,0,3,3,0,2,0,2,0,2,0,3,1,2,3,0,3,1,2,2,2,1,1,2,0,2
    };

    auto wspr_signal = generateWSPRSignal(wspr_symbols);
    auto normalized_signal = normalizeSignal(wspr_signal);
    writeWAVFile("wspr_signal.wav", normalized_signal);

    std::cout << "WAV file generated successfully." << std::endl;
    return 0;
}
