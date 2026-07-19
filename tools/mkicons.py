"""Generate the dadjokes.wtf app icons: a tilted yellow note on the dark desk.

Pure stdlib - no PIL on this machine - so it rasterises by supersampling a
scene function and writes the PNG chunks by hand.
"""
import math
import os
import struct
import zlib

DESK = (0x17, 0x14, 0x0F)
PAPER = (0xFB, 0xE9, 0x4F)
INK = (0x2B, 0x27, 0x24)

ANGLE = math.radians(-8.0)
COS, SIN = math.cos(-ANGLE), math.sin(-ANGLE)

# ink bars in note-local coords, as fractions of the note half-width:
# two thin lines (the setup) and one heavier line (the punchline)
BARS = [
    (-0.62, 0.40, -0.32, -0.22),
    (-0.62, 0.14, -0.16, -0.06),
    (-0.62, 0.52, 0.08, 0.25),
]


def scene(x, y, n):
    """Colour at continuous point (x, y) on an n x n canvas."""
    cx = cy = n / 2.0
    half = 0.32 * n

    dx, dy = x - cx, y - cy
    lx = dx * COS - dy * SIN
    ly = dx * SIN + dy * COS

    if abs(lx) > half or abs(ly) > half:
        return DESK

    r, g, b = PAPER

    # the adhesive strip reads a touch darker through the paper
    if ly < -half + 0.26 * (2 * half):
        r, g, b = int(r * 0.955), int(g * 0.955), int(b * 0.955)

    ux, uy = lx / half, ly / half
    for x0, x1, y0, y1 in BARS:
        if x0 <= ux <= x1 and y0 <= uy <= y1:
            return INK

    return (r, g, b)


def render(n, ss=3):
    """Supersample ss x ss per pixel for antialiased edges."""
    buf = bytearray(n * n * 3)
    inv = 1.0 / (ss * ss)
    offs = [(i + 0.5) / ss for i in range(ss)]
    i = 0
    for py in range(n):
        for px in range(n):
            tr = tg = tb = 0
            for oy in offs:
                for ox in offs:
                    c = scene(px + ox, py + oy, n)
                    tr += c[0]
                    tg += c[1]
                    tb += c[2]
            buf[i] = int(tr * inv)
            buf[i + 1] = int(tg * inv)
            buf[i + 2] = int(tb * inv)
            i += 3
    return buf


def write_png(path, n, buf):
    raw = bytearray()
    stride = n * 3
    for y in range(n):
        raw.append(0)  # filter type 0
        raw += buf[y * stride:(y + 1) * stride]

    def chunk(typ, data):
        return (struct.pack('>I', len(data)) + typ + data
                + struct.pack('>I', zlib.crc32(typ + data) & 0xFFFFFFFF))

    png = (b'\x89PNG\r\n\x1a\n'
           + chunk(b'IHDR', struct.pack('>IIBBBBB', n, n, 8, 2, 0, 0, 0))
           + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
           + chunk(b'IEND', b''))
    with open(path, 'wb') as fh:
        fh.write(png)


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out_icons')
    out = os.environ.get('ICON_OUT', out)
    os.makedirs(out, exist_ok=True)
    for name, size in [('icon-192.png', 192), ('icon-512.png', 512),
                       ('apple-touch-icon.png', 180)]:
        write_png(os.path.join(out, name), size, render(size))
        print('wrote', name, size)
