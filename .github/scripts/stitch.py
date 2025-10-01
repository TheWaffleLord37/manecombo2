from PIL import Image
import os
from datetime import datetime
import string
import re
import sys

# ----------------------------
# Use folder passed in from GitHub Action, or default
# ----------------------------
chunk_dir = sys.argv[1] if len(sys.argv) > 1 else "chunks"
output_dir = "combo"
os.makedirs(output_dir, exist_ok=True)

# ----------------------------
# Define reverse prefixes (zzzzz -> aaaaa)
# ----------------------------
prefixes = []
letters = string.ascii_lowercase
for c1 in reversed(letters):
    for c2 in reversed(letters):
        for c3 in reversed(letters):
            for c4 in reversed(letters):
                for c5 in reversed(letters):
                    prefixes.append(c1 + c2 + c3 + c4 + c5)

# Determine next available prefix
existing_files = [f for f in os.listdir(output_dir) if f.endswith(".png")]
used_prefixes = [f.split("_")[0].replace("combo-", "") for f in existing_files]
next_prefix = next((p for p in prefixes if p not in used_prefixes), "zzzzz")

# ----------------------------
# Configuration: explicit chunk layout
# ----------------------------
chunk_cols = 4  # number of chunk columns in original split
chunk_rows = 3  # number of chunk rows in original split

# ----------------------------
# Gather and sort chunks numerically
# ----------------------------
chunks = [f for f in os.listdir(chunk_dir) if re.match(r"chunk_\d+\.png", f)]
if not chunks:
    raise SystemExit("❌ No chunks found")

chunks.sort(key=lambda x: int(re.findall(r'\d+', x)[0]))

# Validate total chunks
num_chunks = len(chunks)
if num_chunks != chunk_cols * chunk_rows:
    raise ValueError(f"Expected {chunk_cols * chunk_rows} chunks, but found {num_chunks}")

# ----------------------------
# Load chunk images and record sizes
# ----------------------------
chunk_images = []
chunk_sizes = []
for filename in chunks:
    path = os.path.join(chunk_dir, filename)
    img = Image.open(path)
    chunk_images.append(img)
    chunk_sizes.append(img.size)  # (width, height)

# ----------------------------
# Compute column widths and row heights
# ----------------------------
col_widths = []
for c in range(chunk_cols):
    max_w = max(chunk_sizes[r*chunk_cols + c][0] for r in range(chunk_rows))
    col_widths.append(max_w)

row_heights = []
for r in range(chunk_rows):
    max_h = max(chunk_sizes[r*chunk_cols + c][1] for c in range(chunk_cols))
    row_heights.append(max_h)

total_width = sum(col_widths)
total_height = sum(row_heights)

# ----------------------------
# Create final canvas and paste chunks
# ----------------------------
final = Image.new("RGBA", (total_width, total_height), (0,0,0,0))

y_offset = 0
for r in range(chunk_rows):
    x_offset = 0
    for c in range(chunk_cols):
        idx = r * chunk_cols + c
        img = chunk_images[idx]
        final.paste(img, (x_offset, y_offset))
        x_offset += col_widths[c]
    y_offset += row_heights[r]

# ----------------------------
# Save stitched combo
# ----------------------------
timestamp = datetime.utcnow().strftime("%Y-%m-%d__%Hh%MmUTC")
outfile = os.path.join(output_dir, f"combo-{next_prefix}_{timestamp}.png")
final.save(outfile, "PNG")
print(f"✅ Saved stitched combo as {outfile}")
