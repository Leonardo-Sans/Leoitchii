#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Cria um ICO original do Leoitchii, sem copiar assets de jogos.
Coracao de fantasia em vermelho/rubi com borda dourada e fundo transparente.
Somente biblioteca padrao; tamanhos 16, 24, 32, 48, 64, 128, 256 px.
"""
import math
import struct
import sys
from pathlib import Path

SIZES = (16, 24, 32, 48, 64, 128, 256)


def heart(x, y, scale):
    # Curva implicita original usada para desenhar um coracao estilizado.
    xx, yy = x / scale, y / scale
    return (xx * xx + yy * yy - 1.0) ** 3 - xx * xx * yy ** 3 <= 0


def pixel(x, y, size):
    # Supersampling 2x: reduz serrilhado do icone no Windows.
    red = green = blue = alpha = 0.0
    for iy in range(2):
        for ix in range(2):
            px = (x + (ix + .5) / 2 - size / 2) / (size / 2) * 1.22
            py = (size / 2 - y - (iy + .5) / 2) / (size / 2) * 1.32 + 0.10
            color = None
            if heart(px - .026, py + .04, 1.05):
                color = (38, 17, 12, 255)  # contorno quase preto
            if heart(px, py, 1.01):
                color = (231, 178, 62, 255)  # dourado
            if heart(px, py + .012, .895):
                glow = max(0.0, min(1.0, (py + .5) / 1.5))
                color = (int(150 + 90 * glow), int(20 + 28 * glow),
                         int(28 + 13 * glow), 255)
                if px < -.22 and py > .25 and (px + .45) ** 2 + (py - .55) ** 2 < .06:
                    color = (255, 220, 166, 255)  # pequeno reflexo
            if color:
                red += color[0] / 4
                green += color[1] / 4
                blue += color[2] / 4
                alpha += color[3] / 4
    return (int(blue), int(green), int(red), int(alpha))


def dib(size):
    rgba_rows = []
    mask_rows = []
    mask_stride = ((size + 31) // 32) * 4
    for y in reversed(range(size)):
        rgba = bytearray()
        mask = bytearray(mask_stride)
        for x in range(size):
            b, g, r, a = pixel(x, y, size)
            rgba.extend((b, g, r, a))
            if a == 0:
                mask[x // 8] |= 1 << (7 - x % 8)
        rgba_rows.append(bytes(rgba))
        mask_rows.append(bytes(mask))
    data = b"".join(rgba_rows) + b"".join(mask_rows)
    header = struct.pack("<IiiHHIIiiII", 40, size, 2 * size, 1, 32, 0,
                         len(data), 0, 0, 0, 0)
    return header + data


def build():
    frames = [(size, dib(size)) for size in SIZES]
    offset = 6 + 16 * len(frames)
    entries = []
    for size, data in frames:
        entries.append(struct.pack("<BBBBHHII", size if size < 256 else 0,
                                   size if size < 256 else 0, 0, 0, 1, 32,
                                   len(data), offset))
        offset += len(data)
    return struct.pack("<HHH", 0, 1, len(frames)) + b"".join(entries) + b"".join(
        data for _, data in frames)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python scripts/gerar-icone-leoitchii-v07.py saida.ico")
    target = Path(sys.argv[1])
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(build())
    print(f"Icone original Leoitchii: {target} ({target.stat().st_size} bytes)")
