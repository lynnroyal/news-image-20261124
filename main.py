#!/usr/bin/env python3
"""Sum up 24 November 2026 world news in one image.
Deterministic, stdlib only, no network, no randomness, no time.
Output: /output/entry.png when /output exists, else entry.png next to this file.
PNG: 1024x1024 RGB, written with zlib (stdlib) and a 5x7 bitmap font.
"""
import os
import struct
import zlib

W = 1024
H = 1024

WHITE = (255, 255, 255)
NAVY = (15, 42, 68)
NAVY2 = (21, 58, 92)
RED = (192, 57, 43)
DARK = (17, 17, 17)
GREY = (85, 85, 85)
LIGHT = (238, 242, 245)
GOLD = (201, 162, 39)

FONT = {
    'A': ["01110","10001","10001","11111","10001","10001","10001"],
    'B': ["11110","10001","10001","11110","10001","10001","11110"],
    'C': ["01110","10001","10000","10000","10000","10001","01110"],
    'D': ["11110","10001","10001","10001","10001","10001","11110"],
    'E': ["11111","10000","10000","11110","10000","10000","11111"],
    'F': ["11111","10000","10000","11110","10000","10000","10000"],
    'G': ["01110","10001","10000","10111","10001","10001","01111"],
    'H': ["10001","10001","10001","11111","10001","10001","10001"],
    'I': ["01110","00100","00100","00100","00100","00100","01110"],
    'J': ["00111","00010","00010","00010","00010","10010","01100"],
    'K': ["10001","10010","10100","11000","10100","10010","10001"],
    'L': ["10000","10000","10000","10000","10000","10000","11111"],
    'M': ["10001","11011","10101","10101","10001","10001","10001"],
    'N': ["10001","11001","10101","10011","10001","10001","10001"],
    'O': ["01110","10001","10001","10001","10001","10001","01110"],
    'P': ["11110","10001","10001","11110","10000","10000","10000"],
    'Q': ["01110","10001","10001","10001","10101","10010","01101"],
    'R': ["11110","10001","10001","11110","10100","10010","10001"],
    'S': ["01111","10000","10000","01110","00001","00001","11110"],
    'T': ["11111","00100","00100","00100","00100","00100","00100"],
    'U': ["10001","10001","10001","10001","10001","10001","01110"],
    'V': ["10001","10001","10001","10001","10001","01010","00100"],
    'W': ["10001","10001","10001","10101","10101","10101","01010"],
    'X': ["10001","10001","01010","00100","01010","10001","10001"],
    'Y': ["10001","10001","01010","00100","00100","00100","00100"],
    'Z': ["11111","00001","00010","00100","01000","10000","11111"],
    '0': ["01110","10001","10011","10101","11001","10001","01110"],
    '1': ["00100","01100","00100","00100","00100","00100","01110"],
    '2': ["01110","10001","00001","00110","01000","10000","11111"],
    '3': ["11111","00010","00100","00010","00001","10001","01110"],
    '4': ["00010","00110","01010","10010","11111","00010","00010"],
    '5': ["11111","10000","11110","00001","00001","10001","01110"],
    '6': ["00110","01000","10000","11110","10001","10001","01110"],
    '7': ["11111","00001","00010","00100","01000","01000","01000"],
    '8': ["01110","10001","10001","01110","10001","10001","01110"],
    '9': ["01110","10001","10001","01111","00001","00010","01100"],
    ' ': ["00000","00000","00000","00000","00000","00000","00000"],
    '.': ["00000","00000","00000","00000","00000","01100","01100"],
    ',': ["00000","00000","00000","00000","01100","00100","01000"],
    ':': ["00000","01100","01100","00000","01100","01100","00000"],
    ';': ["00000","01100","01100","00000","01100","00100","01000"],
    '-': ["00000","00000","00000","01110","00000","00000","00000"],
    "'": ["00100","00100","01000","00000","00000","00000","00000"],
    '/': ["00001","00010","00010","00100","01000","01000","10000"],
    '(': ["00010","00100","01000","01000","01000","00100","00010"],
    ')': ["01000","00100","00010","00010","00010","00100","01000"],
    '%': ["10001","10010","00010","00100","01000","10001","10001"],
    '!': ["00100","00100","00100","00100","00100","00000","00100"],
    '?': ["01110","10001","00001","00110","00100","00000","00100"],
    '+': ["00000","00100","00100","11111","00100","00100","00000"],
    '=': ["00000","00000","11111","00000","11111","00000","00000"],
    '&': ["01100","10010","10100","01000","10101","10010","01101"],
    '$': ["00100","01111","10100","01110","00101","11110","00100"],
}

STORIES = [
    ("1", "HACKED DATA PUTS RUSSIAN DEATH TOLL IN UKRAINE NEAR 500,000", "LEAKED FIGURES POINT TO HEAVY LOSSES SINCE 2022"),
    ("2", "UKRAINE SINKS RUSSIAN WARSHIP OFF LIBYA IN DRONE ATTACK", "SEVEN SEA DRONES HIT BASE IN BENGHAZI"),
    ("3", "NVIDIA REINSTATES JENSEN HUANG AS CEO AFTER TRUMP PUSH", "STUNNING REVERSAL AT THE CHIPMAKER"),
    ("4", "NATO WARNS RUSSIA MAY LAUNCH NUCLEAR SPACE WEAPON NEXT MONTH", "ALLIES VOW SPACE DEFENCE"),
    ("5", "UN: WARS PUT FOOD AID AT RISK FOR 7.3 MILLION MORE PEOPLE", "FOOD AGENCY CHIEF WARNS OF GROWING NEED"),
    ("6", "US NAMED A HOST OF THE 2031 WOMENS WORLD CUP", "FIFA CONFIRMS US AS CO-HOST"),
]

def wrap(text, max_chars):
    words = text.split(" ")
    lines = []
    cur = ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        for i in range(w * h):
            self.px[i*3] = bg[0]
            self.px[i*3+1] = bg[1]
            self.px[i*3+2] = bg[2]

    def rect(self, x, y, rw, rh, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + rw)
        y1 = min(self.h, y + rh)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                o = base + (xx - x0) * 3
                self.px[o] = color[0]
                self.px[o+1] = color[1]
                self.px[o+2] = color[2]

    def text(self, x, y, s, scale, color):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[' '])
            for r in range(7):
                row = glyph[r]
                for c in range(5):
                    if row[c] == '1':
                        self.rect(cx + c*scale, y + r*scale, scale, scale, color)
            cx += 6 * scale
        return cx

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale

def chunk(b, size):
    out = struct.pack(">I", len(b)) + size + b
    out += struct.pack(">I", zlib.crc32(size + b) & 0xFFFFFFFF)
    return out

def write_png(path, canvas):
    raw = bytearray()
    for y in range(canvas.h):
        raw.append(0)
        start = y * canvas.w * 3
        raw.extend(canvas.px[start:start + canvas.w * 3])
    comp = zlib.compress(bytes(raw), 9)
    png = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png += chunk(ihdr, b"IHDR")
    png += chunk(comp, b"IDAT")
    png += chunk(b"", b"IEND")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

def main():
    c = Canvas(W, H, WHITE)
    # Header
    c.rect(0, 0, W, 168, NAVY)
    c.rect(0, 168, W, 6, GOLD)
    c.text(48, 36, "WORLD NEWS", 7, WHITE)
    c.text(48, 108, "TUESDAY  24 NOVEMBER 2026", 3, (200, 220, 235))
    # Red date badge on right
    c.rect(812, 36, 164, 56, RED)
    c.text(836, 52, "24 NOV", 3, WHITE)
    y = 206
    for num, headline, sub in STORIES:
        # number block
        c.rect(48, y, 56, 56, RED)
        c.text(48 + 18, y + 14, num, 4, WHITE)
        # headline, wrapped at 38 chars, scale 3
        lines = wrap(headline, 38)
        ly = y + 2
        for line in lines:
            c.text(128, ly, line, 3, DARK)
            ly += 30
        # subline, scale 2
        c.text(128, ly + 4, sub, 2, GREY)
        # divider
        y = ly + 36
        if num != "6":
            c.rect(48, y - 14, W - 96, 2, LIGHT)
    # Footer
    c.rect(0, 958, W, 66, LIGHT)
    c.text(48, 972, "SOURCES: JAPAN TIMES - SCMP - MANILA TIMES", 2, GREY)
    c.text(48, 996, "24 NOVEMBER 2026 - ALL EVENTS REPORTED ON THIS DATE", 2, GREY)
    out = "/output/entry.png" if os.path.isdir("/output") else "entry.png"
    # When run from the repo root locally, also ensure output/ exists for test
    if out == "entry.png" and os.path.isdir("output"):
        out = "output/entry.png"
    size = write_png(out, c)
    print("wrote %s %d bytes" % (out, size))

if __name__ == "__main__":
    main()
