#!/usr/bin/env python3
"""Generate original Battlefield 6 Guide brand PNG/ICO assets."""

from __future__ import annotations

import math
import os
import struct
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "brand"

CHARCOAL = (17, 17, 15, 255)
BLACK = (8, 8, 6, 255)
PAPER = (235, 226, 209, 255)
MUTED = (184, 177, 167, 255)
RED = (237, 47, 40, 255)
AMBER = (240, 174, 55, 255)
OLIVE = (125, 138, 79, 255)
CYAN = (141, 215, 203, 255)
TRANSPARENT = (0, 0, 0, 0)


def blend(dst: tuple[int, int, int, int], src: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    sr, sg, sb, sa = src
    if sa == 255:
        return src
    if sa == 0:
        return dst
    dr, dg, db, da = dst
    alpha = sa / 255
    out_a = alpha + da / 255 * (1 - alpha)
    if out_a == 0:
        return TRANSPARENT
    r = int((sr * alpha + dr * (da / 255) * (1 - alpha)) / out_a)
    g = int((sg * alpha + dg * (da / 255) * (1 - alpha)) / out_a)
    b = int((sb * alpha + db * (da / 255) * (1 - alpha)) / out_a)
    return (r, g, b, int(out_a * 255))


class Canvas:
    def __init__(self, width: int, height: int, bg: tuple[int, int, int, int] = TRANSPARENT) -> None:
        self.width = width
        self.height = height
        self.pixels = [bg] * (width * height)

    def set(self, x: int, y: int, color: tuple[int, int, int, int]) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            idx = y * self.width + x
            self.pixels[idx] = blend(self.pixels[idx], color)

    def fill_rect(self, x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int, int]) -> None:
        x0, x1 = max(0, min(x0, x1)), min(self.width, max(x0, x1))
        y0, y1 = max(0, min(y0, y1)), min(self.height, max(y0, y1))
        for y in range(y0, y1):
            row = y * self.width
            for x in range(x0, x1):
                self.pixels[row + x] = blend(self.pixels[row + x], color)

    def line(self, x0: float, y0: float, x1: float, y1: float, color: tuple[int, int, int, int], width: int = 1) -> None:
        dx = x1 - x0
        dy = y1 - y0
        steps = max(1, int(max(abs(dx), abs(dy))))
        radius = max(0, width // 2)
        for i in range(steps + 1):
            t = i / steps
            x = int(round(x0 + dx * t))
            y = int(round(y0 + dy * t))
            for yy in range(y - radius, y + radius + 1):
                for xx in range(x - radius, x + radius + 1):
                    if (xx - x) ** 2 + (yy - y) ** 2 <= radius * radius + 1:
                        self.set(xx, yy, color)

    def circle(self, cx: float, cy: float, radius: float, color: tuple[int, int, int, int], width: int = 1) -> None:
        r2 = radius * radius
        inner = max(0, radius - width)
        inner2 = inner * inner
        x0 = int(max(0, cx - radius - 2))
        x1 = int(min(self.width, cx + radius + 2))
        y0 = int(max(0, cy - radius - 2))
        y1 = int(min(self.height, cy + radius + 2))
        for y in range(y0, y1):
            for x in range(x0, x1):
                d2 = (x - cx) ** 2 + (y - cy) ** 2
                if inner2 <= d2 <= r2:
                    self.set(x, y, color)

    def fill_circle(self, cx: float, cy: float, radius: float, color: tuple[int, int, int, int]) -> None:
        r2 = radius * radius
        x0 = int(max(0, cx - radius))
        x1 = int(min(self.width, cx + radius + 1))
        y0 = int(max(0, cy - radius))
        y1 = int(min(self.height, cy + radius + 1))
        for y in range(y0, y1):
            for x in range(x0, x1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r2:
                    self.set(x, y, color)

    def polygon(self, points: list[tuple[float, float]], color: tuple[int, int, int, int]) -> None:
        min_x = max(0, int(min(x for x, _ in points)))
        max_x = min(self.width - 1, int(max(x for x, _ in points)) + 1)
        min_y = max(0, int(min(y for _, y in points)))
        max_y = min(self.height - 1, int(max(y for _, y in points)) + 1)
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                inside = False
                j = len(points) - 1
                for i, point in enumerate(points):
                    xi, yi = point
                    xj, yj = points[j]
                    if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1) + xi:
                        inside = not inside
                    j = i
                if inside:
                    self.set(x, y, color)

    def save_png(self, path: Path) -> bytes:
        raw = bytearray()
        for y in range(self.height):
            raw.append(0)
            for x in range(self.width):
                raw.extend(self.pixels[y * self.width + x])
        png = b"\x89PNG\r\n\x1a\n"
        png += chunk(b"IHDR", struct.pack(">IIBBBBB", self.width, self.height, 8, 6, 0, 0, 0))
        png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        png += chunk(b"IEND", b"")
        path.write_bytes(png)
        return png


def chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def scaled(color: tuple[int, int, int, int], alpha: int) -> tuple[int, int, int, int]:
    return color[0], color[1], color[2], alpha


def draw_mark(size: int, bg: tuple[int, int, int, int] = TRANSPARENT) -> Canvas:
    c = Canvas(size, size, bg)
    s = size
    if bg[3]:
        for y in range(s):
            shade = int(10 + 12 * (y / max(1, s - 1)))
            c.line(0, y, s, y, (shade, shade, max(6, shade - 3), 255))
    else:
        c.fill_circle(s * 0.5, s * 0.5, s * 0.47, scaled(CHARCOAL, 245))

    margin = s * 0.16
    c.line(margin, margin, s - margin, margin, scaled(PAPER, 142), max(2, s // 95))
    c.line(s - margin, margin, s - margin, s - margin, scaled(PAPER, 142), max(2, s // 95))
    c.line(s - margin, s - margin, margin, s - margin, scaled(PAPER, 142), max(2, s // 95))
    c.line(margin, s - margin, margin, margin, scaled(PAPER, 142), max(2, s // 95))

    for i in range(1, 4):
        p = margin + (s - margin * 2) * i / 4
        c.line(p, margin, p, s - margin, scaled(PAPER, 28), max(1, s // 180))
        c.line(margin, p, s - margin, p, scaled(PAPER, 28), max(1, s // 180))

    cx, cy = s * 0.52, s * 0.52
    c.circle(cx, cy, s * 0.29, scaled(AMBER, 160), max(2, s // 85))
    c.circle(cx, cy, s * 0.17, scaled(CYAN, 92), max(2, s // 115))
    c.line(s * 0.23, s * 0.64, s * 0.79, s * 0.28, scaled(RED, 235), max(7, s // 18))
    c.line(s * 0.29, s * 0.76, s * 0.75, s * 0.76, scaled(RED, 235), max(7, s // 18))
    c.line(s * 0.25, s * 0.36, s * 0.73, s * 0.36, scaled(PAPER, 215), max(5, s // 26))
    c.fill_circle(s * 0.73, s * 0.36, max(5, s // 28), RED)
    c.fill_circle(s * 0.31, s * 0.76, max(4, s // 34), AMBER)
    return c


def draw_social() -> Canvas:
    w, h = 1200, 630
    c = Canvas(w, h, BLACK)
    for y in range(h):
        shade = int(8 + 18 * y / h)
        c.line(0, y, w, y, (shade, shade, max(6, shade - 5), 255))

    for x in range(0, w, 56):
        c.line(x, 0, x, h, scaled(PAPER, 18), 1)
    for y in range(0, h, 56):
        c.line(0, y, w, y, scaled(PAPER, 16), 1)

    for radius in (92, 184, 276, 368):
        c.circle(850, 310, radius, scaled(AMBER, 70), 2)
    c.line(620, 120, 1130, 430, scaled(RED, 210), 8)
    c.line(520, 480, 1040, 180, scaled(CYAN, 95), 4)
    c.line(90, 520, 540, 520, scaled(RED, 220), 10)
    c.line(90, 92, 505, 92, scaled(PAPER, 225), 8)
    c.line(90, 92, 90, 520, scaled(PAPER, 225), 8)

    mark = draw_mark(260, TRANSPARENT)
    paste(c, mark, 90, 160)

    # Abstract title blocks: text-like without using official marks.
    c.fill_rect(390, 190, 940, 245, PAPER)
    c.fill_rect(390, 270, 800, 326, PAPER)
    c.fill_rect(830, 270, 1015, 326, RED)
    c.fill_rect(390, 376, 915, 396, scaled(MUTED, 210))
    c.fill_rect(390, 418, 650, 436, scaled(CYAN, 170))
    c.fill_rect(675, 418, 1040, 436, scaled(AMBER, 175))

    c.fill_rect(90, 560, 285, 574, scaled(OLIVE, 180))
    c.fill_rect(310, 560, 560, 574, scaled(MUTED, 135))
    c.fill_rect(990, 74, 1120, 88, scaled(RED, 210))
    return c


def paste(dst: Canvas, src: Canvas, x0: int, y0: int) -> None:
    for y in range(src.height):
        for x in range(src.width):
            dst.set(x0 + x, y0 + y, src.pixels[y * src.width + x])


def make_ico(path: Path, sizes: tuple[int, ...] = (16, 32, 48, 64)) -> None:
    images = []
    for size in sizes:
        canvas = draw_mark(size, BLACK)
        png = canvas.save_png(OUT / f"favicon-{size}.png")
        images.append((size, png))

    header = struct.pack("<HHH", 0, 1, len(images))
    directory = bytearray()
    data = bytearray()
    offset = 6 + 16 * len(images)
    for size, png in images:
        directory.extend(
            struct.pack(
                "<BBBBHHII",
                size if size < 256 else 0,
                size if size < 256 else 0,
                0,
                0,
                1,
                32,
                len(png),
                offset,
            )
        )
        data.extend(png)
        offset += len(png)
    path.write_bytes(header + bytes(directory) + bytes(data))
    for size, _ in images:
        (OUT / f"favicon-{size}.png").unlink(missing_ok=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    draw_mark(1024, TRANSPARENT).save_png(OUT / "logo-mark.png")
    draw_mark(512, BLACK).save_png(OUT / "favicon.png")
    draw_mark(180, BLACK).save_png(OUT / "apple-touch-icon.png")
    draw_social().save_png(OUT / "social-card.png")
    make_ico(ROOT / "favicon.ico")


if __name__ == "__main__":
    main()
