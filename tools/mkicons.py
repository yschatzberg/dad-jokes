"""Generate the dadjokes.wtf app icons: WTF marker-written on a sticky note.

Pure stdlib - no PIL on this machine - so it rasterises a scene function and
writes the PNG chunks by hand. Letters are stroke paths measured by distance
to a line segment, which gives round marker-pen caps for free.

Renders once at high resolution and downsamples, so the antialiasing comes
from area-averaging rather than per-pixel supersampling.
"""
import math
import os
import struct
import zlib

DESK = (0x17, 0x14, 0x0F)
PAPER = (0xFB, 0xE9, 0x4F)
INK = (0x2B, 0x27, 0x24)

TILT = math.radians(-8.0)
COS, SIN = math.cos(-TILT), math.sin(-TILT)

NOTE_HALF = 0.32      # note half-width as a fraction of the canvas

# Two pen strokes on the note. The top one is heavy enough to read WTF out of
# its middle - the letters are knocked back to paper rather than drawn in ink.
# Coords are note-local, u and v run -1..1 with v downward; entries are
# (start, end, half-width), which gives round marker caps from the distance
# test for free.
_LINE = -0.16                 # vertical centre of the top stroke
BARS = [
    ((-0.40, _LINE), (0.40, _LINE), 0.215),     # the heavy top stroke
    ((-0.56, 0.44), (0.18, 0.44), 0.038),       # a second, lighter stroke
]

_LT, _LB = -0.325, 0.01       # letter extents, centred in the heavy stroke
_NIB = 0.035                  # letter stroke half-width
KNOCKOUT = [
    # W - one continuous zig-zag, the way you'd actually write it
    ((-0.42, _LT), (-0.365, _LB), _NIB),
    ((-0.365, _LB), (-0.31, -0.21), _NIB),
    ((-0.31, -0.21), (-0.255, _LB), _NIB),
    ((-0.255, _LB), (-0.20, _LT), _NIB),
    # T
    ((-0.15, _LT), (0.03, _LT), _NIB),
    ((-0.06, _LT), (-0.06, _LB), _NIB),
    # F
    ((0.11, _LT), (0.11, _LB), _NIB),
    ((0.11, _LT), (0.29, _LT), _NIB),
    ((0.11, -0.16), (0.23, -0.16), _NIB),
]

# Sits high on its own; nudge it to read as centred on the tilted note.
_OFF_U, _OFF_V = 0.02, 0.03
BARS = [((ax + _OFF_U, ay + _OFF_V), (bx + _OFF_U, by + _OFF_V), w)
        for (ax, ay), (bx, by), w in BARS]
# the word needs a touch more than the bar to sit centred inside it, because
# the bar's round caps add width the endpoints don't account for
_WORD_U = 0.07
KNOCKOUT = [((ax + _OFF_U + _WORD_U, ay + _OFF_V), (bx + _OFF_U + _WORD_U, by + _OFF_V), w)
            for (ax, ay), (bx, by), w in KNOCKOUT]


def _hits(strokes, u, v):
    for (ax, ay), (bx, by), w in strokes:
        vx, vy = bx - ax, by - ay
        wx, wy = u - ax, v - ay
        L2 = vx * vx + vy * vy
        t = 0.0 if L2 == 0 else max(0.0, min(1.0, (wx * vx + wy * vy) / L2))
        dx, dy = wx - t * vx, wy - t * vy
        if dx * dx + dy * dy <= w * w:
            return True
    return False


def on_stroke(u, v):
    """True where ink should land: inside a bar, but not inside a letter."""
    if not _hits(BARS, u, v):
        return False
    return not _hits(KNOCKOUT, u, v)


def scene(x, y, n):
    """Colour at pixel centre (x, y) on an n x n canvas."""
    c = n / 2.0
    half = NOTE_HALF * n

    dx, dy = x - c, y - c
    lx = dx * COS - dy * SIN
    ly = dx * SIN + dy * COS

    if abs(lx) > half or abs(ly) > half:
        return DESK

    u, v = lx / half, ly / half
    if on_stroke(u, v):
        return INK

    r, g, b = PAPER
    # the adhesive strip reads a touch darker through the paper
    if v < -1.0 + 0.26 * 2:
        r, g, b = int(r * 0.955), int(g * 0.955), int(b * 0.955)
    return (r, g, b)


def render(n):
    buf = bytearray(n * n * 3)
    i = 0
    for py in range(n):
        yc = py + 0.5
        for px in range(n):
            cr, cg, cb = scene(px + 0.5, yc, n)
            buf[i] = cr
            buf[i + 1] = cg
            buf[i + 2] = cb
            i += 3
    return buf


def downsample(src, sn, dn):
    """Area-average sn x sn down to dn x dn."""
    out = bytearray(dn * dn * 3)
    scale = sn / dn
    for dy in range(dn):
        y0, y1 = int(dy * scale), max(int(dy * scale) + 1, int((dy + 1) * scale))
        for dx in range(dn):
            x0, x1 = int(dx * scale), max(int(dx * scale) + 1, int((dx + 1) * scale))
            tr = tg = tb = cnt = 0
            for sy in range(y0, min(y1, sn)):
                row = sy * sn * 3
                for sx in range(x0, min(x1, sn)):
                    j = row + sx * 3
                    tr += src[j]
                    tg += src[j + 1]
                    tb += src[j + 2]
                    cnt += 1
            k = (dy * dn + dx) * 3
            out[k] = tr // cnt
            out[k + 1] = tg // cnt
            out[k + 2] = tb // cnt
    return out


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
    out = os.environ.get(
        'ICON_OUT',
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out_icons'))
    os.makedirs(out, exist_ok=True)

    MASTER = 1536
    print('rendering master', MASTER)
    master = render(MASTER)

    for name, size in [('icon-512.png', 512), ('icon-192.png', 192),
                       ('apple-touch-icon.png', 180)]:
        write_png(os.path.join(out, name), size, downsample(master, MASTER, size))
        print('wrote', name, size)
