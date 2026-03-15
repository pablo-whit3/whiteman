import os

os.makedirs("test_dir/sub_dir", exist_ok=True)

print("Directories created")

print("Files in current folder:")
for item in os.listdir("."):
    print(item)

print("Python files:")

for file in os.listdir("."):
    if file.endswith(".py"):
        print(file)