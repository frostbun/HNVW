import random

import requests

lines = [line.strip() for line in requests.get("https://ditmewibu.com/").text.split("\n")]
parsing = False
curr = ""
van_mau = []

for line in lines:
    if line.startswith("<") and "<br>" not in line and parsing:
        parsing = False
        van_mau.append(curr.strip())
        curr = ""
    if parsing:
        sep = "\n" if "<br>" in line else " "
        curr += line.strip("<br>") + sep
    if line.startswith("<p"):
        parsing = True

van_mau = van_mau[1:-3]

def get_van_mau():
    return random.choice(van_mau)

if __name__ == "__main__":
    print(len(van_mau))
    print(van_mau[0])
    print(van_mau[-1])
    print(get_van_mau())
