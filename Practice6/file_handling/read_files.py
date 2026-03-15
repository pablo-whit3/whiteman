with open("sample_data.txt", "r") as f:
    print(f.read())
with open("sample_data.txt", "a") as f:
    f.write("appending new lines\n")
    f.write("I'm good, thank you\n")
    f.write("Did you watch the game yesterday?\n")
with open("sample_data.txt", "r") as f:
    print(f.read())