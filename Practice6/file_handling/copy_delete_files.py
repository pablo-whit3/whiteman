import shutil
import os
import time

source = "sample_data.txt"
backup = "sample_backup.txt"

shutil.copy(source, backup)
print("File copied")

time.sleep(10)

if os.path.exists(backup):
    os.remove(backup)
    print("Backup deleted")
else:
    print("File not found")