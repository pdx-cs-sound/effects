import numpy as np
from scipy.io import wavfile

SAMPLE_RATE = 48000

def read_wave(filename):
    rate, data = wavfile.read(filename)
    if rate != SAMPLE_RATE:
        raise ValueError(
            f"{filename}: sample rate {rate} != {SAMPLE_RATE}"
        )
    if data.dtype == np.int16:
        signal = data.astype(np.float32) / 32768.0
    elif data.dtype == np.int32:
        signal = data.astype(np.float32) / 2147483648.0
    elif data.dtype == np.uint8:
        signal = (data.astype(np.float32) - 128.0) / 128.0
    elif data.dtype in (np.float32, np.float64):
        signal = data.astype(np.float32)
    else:
        raise ValueError(f"unsupported dtype {data.dtype}")
    if signal.ndim == 2:
        signal = signal.mean(axis=1, dtype=np.float32)
    return rate, signal

def write_wave(filename, signal, rate=SAMPLE_RATE):
    clipped = np.clip(signal, -1.0, 1.0)
    pcm = (clipped * 32767.0).astype(np.int16)
    wavfile.write(filename, rate, pcm)
