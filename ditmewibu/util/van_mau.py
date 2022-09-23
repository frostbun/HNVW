from random import choice

from requests import get

response = get("https://ditmewibu.com/").text.split("\n")
parsing = False
curr = ""
van_mau = []
for line in response:
    line = line.strip()
    if line.startswith("<") and parsing:
        parsing = False
        van_mau.append(curr)
        curr = ""
    if parsing:
        curr += line.strip("<br>") + "\n"
    if line.startswith("<p"):
        parsing = True
van_mau = van_mau[3:]

def get_van_mau():
    return choice(van_mau)

if __name__ == "__main__":
    print(len(van_mau))
    print(van_mau[0])
    print(van_mau[-1])
