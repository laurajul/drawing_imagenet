import kagglehub
import shutil
from pathlib import Path

current_dir = Path.cwd()

# Download latest version
path = kagglehub.dataset_download("ifigotin/imagenetmini-1000")

print("Path to dataset files:", path)

# Move contents to data/
dest = Path("data")
dest.mkdir(parents=True, exist_ok=True)
for item in Path(path).iterdir():
    shutil.move(str(item), dest)
print("Moved to:", dest)