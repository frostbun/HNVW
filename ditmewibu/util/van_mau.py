import random

import requests

van_mau_list = [
    line.strip()
    for line in requests.get(
        "https://raw.githubusercontent.com/comgachienmam147/comgachienmam147.github.io/refs/heads/master/copypasta.txt"
    ).text.split("********************")
]

van_mau_list = [
    " ".join(line.strip() for line in van_mau.split("\r\n")[4:])
    for van_mau in van_mau_list
]

van_mau_list = [van_mau for van_mau in van_mau_list if van_mau != ""]


def get_van_mau():
    return random.choice(van_mau_list)


if __name__ == "__main__":
    print(len(van_mau_list))
    print("********************")
    print(van_mau_list[0])
    print("********************")
    print(van_mau_list[-1])
    print("********************")
    print(get_van_mau())
