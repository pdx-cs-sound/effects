# Audio Chorus
# Bart Massey

import argparse, audio, math, sounddevice
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument(
    "-d", "--delay",
    help="Base delay in ms.",
    type=float,
    default=1.0,
)
ap.add_argument(
    "-w", "--wet",
    help="Fraction of wet signal.",
    type=float,
    default=0.5,
)
ap.add_argument(
    "-f", "--frequency",
    help="Chorus LFO frequency in Hz.",
    type=float,
    default=0.25,
)
ap.add_argument(
    "-a", "--amplitude",
    help="Chorus LFO amplitude in ms.",
    type=float,
    default=1,
)
ap.add_argument(
    "infile",
    help="Input audio file.",
)
ap.add_argument(
    "outfile",
    nargs="?",
    help="Output audio file.",
)
args = ap.parse_args()

class RingBuffer(object):
    def __init__(self, length):
        self.length = length
        self.buf = [None] * length
        self.head = 0
        self.nbuf = 0

    def enqueue(self, s):
        assert self.nbuf < self.length
        tail = (self.head + self.nbuf) % self.length
        self.nbuf += 1
        self.buf[tail] = s

    def dequeue(self):
        assert self.nbuf > 0
        self.nbuf -= 1
        s = self.buf[self.head]
        self.head = (self.head + 1) % self.length
        return s

    def lookback(self, n):
        assert n <= self.nbuf
        i = (self.head + n) % self.length
        return self.buf[i]

    def is_empty(self):
        return self.nbuf == 0

# Unit tests for buffer
tbuf = RingBuffer(3)
tbuf.enqueue(1)
tbuf.enqueue(2)
tbuf.enqueue(3)
assert tbuf.dequeue() == 1
tbuf.enqueue(4)
assert tbuf.lookback(3) == 2
assert tbuf.dequeue() == 2
assert tbuf.dequeue() == 3
assert tbuf.dequeue() == 4
assert tbuf.is_empty()

info, psignal = audio.read_wave(args.infile)
npsignal = len(psignal)
rate = info.framerate

ampl = args.amplitude * rate / 1000
delay = max(args.delay * rate / 1000, ampl)
freq = 2 * math.pi * args.frequency / rate
wet = args.wet
bufsiz = int(delay + ampl) + 1
buf = RingBuffer(bufsiz)
outsignal = []
for (i, s) in enumerate(psignal):
    buf.enqueue(s)
    if i < bufsiz - 1:
        y = s
    else:
        lb = delay + ampl * math.sin(i * freq)
        #frac, floor = math.modf(lb)
        #y0 = buf.lookback(int(floor))
        #y1 = buf.lookback(int(math.ceil(lb)))
        #y = y0 * frac + y1 * (1 - frac)
        y = buf.lookback(int(lb))
        buf.dequeue()
    outsignal.append((1 - wet) * s + wet * y)
psignal = np.array(outsignal)

if args.outfile is None:
    sounddevice.play(psignal, samplerate=rate, blocking=True)
else:
    audio.write_wave(args.outfile, info, psignal)
