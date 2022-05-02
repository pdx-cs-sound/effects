import sys, wave
import numpy as np

# Read a tone from a wave file.
def read_wave(filename):
    w = wave.open(filename, "rb")
    info = w.getparams()
    fbytes = w.readframes(info.nframes)
    w.close()
    sampletypes = {
        1: (np.uint8, -(1 << 7), 1 << 8),
        2: (np.int16, 0.5, 1 << 16),
        4: (np.int32, 0.5, 1 << 32),
    }
    if info.sampwidth not in sampletypes:
        raise IOException()
    sampletype, sampleoff, samplewidth = sampletypes[info.sampwidth]
    samples = np.frombuffer(fbytes, dtype=sampletype)
    scale = 2.0 / samplewidth
    fsamples = scale * (samples + sampleoff)
    if info.nchannels == 1:
        channels = np.array(fsamples)
    else:
        channels = np.reshape(fsamples, (-1, info.nchannels))
        channels = np.transpose(channels)
    return (info, channels)

# Write a tone to a wave file.
def write_wave(filename, info, channels):
    samples = np.reshape(np.transpose(channels), (-1,))
    sampletypes = {
        1: ('u1', (1 << 7), 1 << 8),
        2: ('<i2', 0.5, 1 << 16),
        4: ('<i4', 0.5, 1 << 32),
    }
    if info.sampwidth not in sampletypes:
        raise IOException()
    sampletype, sampleoff, samplewidth = sampletypes[info.sampwidth]
    scale = samplewidth / 2.0
    fsamples = scale * samples + sampleoff
    hsamples = np.array(fsamples, dtype=sampletype)
    w = wave.open(filename, "wb")
    w.setparams(info)
    w.writeframes(hsamples)
    w.close()
