import sys
from tabulate import tabulate # pip install tabulate

if __name__ == "__main__":
    sys.exit("Please fun CFM_Bot.py instead of make_pages.py")


def make_pages(result, headers):
    length = len(result)
    num = length//15
    sendList = []
    counter = 0

    if(length % 15 != 0):
        num += 1

    for x in range(num):
        counter += 1

        if length <= 15:
            group = result[0:length]
        else:
            group = result[0:15]
            result = result[15::]

        sendList.append(f"```\n{tabulate(group, headers = headers)}\n\n[Page {counter}/{num}]```")

    return sendList