import json

with open("sample_data.json", 'r') as file:
    sample_data = json.load(file)
print("================================================================================")
print("DN                                                 Description           Speed    MTU  ")
print("-------------------------------------------------- --------------------  ------  ------")
for i in range(len(sample_data["imdata"])):
    attributes = sample_data["imdata"][i]["l1PhysIf"]["attributes"]
    print(f"{attributes["dn"]}                              {attributes["descr"]}{attributes["speed"]}   {attributes["mtu"]}")