"""HEIC/HEIF -> PNG via pillow-heif.

Sandbox-safe: reads the source and writes the PNG to the two explicit paths given on argv,
with no reliance on the Darwin per-user temp dir (which `sips` needs and the sandbox blocks).
Usage: python3 heic-to-png.py <src.heic> <dst.png>
"""
import sys

from PIL import Image
import pillow_heif

pillow_heif.register_heif_opener()
Image.open(sys.argv[1]).convert("RGB").save(sys.argv[2], format="PNG")
