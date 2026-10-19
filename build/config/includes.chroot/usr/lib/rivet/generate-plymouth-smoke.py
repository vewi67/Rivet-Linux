#!/usr/bin/env python3
"""Generate transparent, subtly animated smoke textures for the Rivet Plymouth theme.

This helper runs only during ISO image configuration. Plymouth consumes the PNG
frames from its initramfs, so no resident animation process is installed.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

WIDTH = 720
HEIGHT = 300
FRAME_COUNT = 8


def resized_noise(seed: int, grid_size: tuple[int, int], output_size: tuple[int, int]) -> Image.Image:
    rng = random.Random(seed)
    source = Image.new("L", grid_size)
    source.putdata([rng.randint(35, 255) for _ in range(grid_size[0] * grid_size[1])])
    return source.resize(output_size, Image.Resampling.BICUBIC)


def build_frame(frame: int, coarse: Image.Image, fine: Image.Image, color: Image.Image) -> Image.Image:
    mask = Image.new("L", (WIDTH, HEIGHT), 0)
    draw = ImageDraw.Draw(mask)
    cycle = (math.pi * 2 * frame) / FRAME_COUNT

    # Overlapping drifting wisps create an irregular smoke silhouette, not a ring.
    for index in range(13):
        center_x = -42 + index * 66
        center_x += math.sin(cycle * 0.8 + index * 0.57) * 17 + frame * 2.0
        center_y = HEIGHT * 0.53 + math.sin(cycle + index * 0.84) * 27
        radius_x = 42 + (index % 3) * 17
        radius_y = 24 + (index % 4) * 9
        opacity = 105 + (index * 17) % 100
        draw.ellipse(
            (
                int(center_x - radius_x),
                int(center_y - radius_y),
                int(center_x + radius_x),
                int(center_y + radius_y),
            ),
            fill=opacity,
        )

    # Thin, longer trails soften the cloud silhouette and suggest upward motion.
    for index in range(5):
        center_x = 50 + index * 145 + math.sin(cycle + index) * 22
        center_y = HEIGHT * 0.48 + math.cos(cycle * 0.75 + index) * 26
        draw.ellipse(
            (int(center_x - 66), int(center_y - 20), int(center_x + 66), int(center_y + 20)),
            fill=95 + (index * 13),
        )

    mask = mask.filter(ImageFilter.GaussianBlur(22))
    # Move the same noise field a little each frame so the haze drifts smoothly.
    left = frame * 8
    top = frame * 3
    crop = (left, top, left + WIDTH, top + HEIGHT)
    noise = Image.blend(coarse.crop(crop), fine.crop(crop), 0.34)
    noise = noise.filter(ImageFilter.GaussianBlur(1.4))
    alpha = ImageChops.multiply(mask, noise).point(lambda value: min(104, int(value * 0.62)))

    frame_image = color.copy().convert("RGBA")
    frame_image.putalpha(alpha)
    return frame_image


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {Path(sys.argv[0]).name} OUTPUT_DIRECTORY", file=sys.stderr)
        return 2

    output_dir = Path(sys.argv[1])
    output_dir.mkdir(parents=True, exist_ok=True)
    noise_size = (WIDTH + 96, HEIGHT + 48)
    coarse = resized_noise(9123, (52, 22), noise_size)
    fine = resized_noise(4817, (160, 68), noise_size)

    pixels = []
    for y in range(HEIGHT):
        for x in range(WIDTH):
            center_glow = 1.0 - min(1.0, abs(x - WIDTH * 0.5) / (WIDTH * 0.65))
            vertical_glow = 1.0 - min(1.0, abs(y - HEIGHT * 0.52) / (HEIGHT * 0.65))
            red = int(12 + 17 * center_glow)
            green = int(53 + 105 * center_glow * vertical_glow)
            blue = int(142 + 88 * center_glow)
            pixels.append((red, green, blue, 0))
    color = Image.new("RGBA", (WIDTH, HEIGHT))
    color.putdata(pixels)

    for frame in range(FRAME_COUNT):
        image = build_frame(frame, coarse, fine, color)
        image.save(output_dir / f"smoke-{frame}.png", format="PNG", optimize=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
