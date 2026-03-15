import shutil
import os
import time

os.makedirs("dest", exist_ok=True)

with open("test.txt", "w") as f:
    f.write("test")

shutil.copy("test.txt", "dest/test_copy.txt")

print("Copy done")

time.sleep(10)

shutil.move("test.txt", "dest/test.txt")

print("Move done")