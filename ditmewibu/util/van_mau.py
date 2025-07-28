import random

import requests

van_mau = [line.strip() for line in requests.get("https://raw.githubusercontent.com/comgachienmam147/comgachienmam147.github.io/refs/heads/master/copypasta.txt").text.split("********************")]

for i in range(len(van_mau)):
    van_mau[i] = "\n".join(van_mau[i].split("\n")[4:])

van_mau = van_mau[:-1]

def get_van_mau():
    return random.choice(van_mau)

if __name__ == "__main__":
    print(len(van_mau))
    print("********************")
    print(van_mau[0])
    print("********************")
    print(van_mau[-1])
    print("********************")
    print(get_van_mau())
