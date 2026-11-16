import hashlib
import pandas as pd
from pathlib import Path

raw_folder = Path("data/raw")
out_folder = Path("outputs/provenance")
out_folder.mkdir(parents=True, exist_ok=True)

files = ["co-est2024-alldata.csv", "food_environment_atlas_2025.zip", "places_county_2024.csv"]

def get_sha256(file_path):
    f = open(file_path, "rb")
    data = f.read()
    f.close()
    return hashlib.sha256(data).hexdigest()

rows = []
for name in files:
    path = raw_folder / name
    checksum = get_sha256(path)
    size = path.stat().st_size
    print(name, size, checksum)
    rows.append({"file": name, "size_bytes": size, "sha256": checksum})

df = pd.DataFrame(rows)
df.to_csv(out_folder / "checksums.csv", index=False)
print("saved to", out_folder / "checksums.csv")
