from colorama import init, Fore, Back
import requests
import json
from main import version
import time

init(autoreset=True)


latest = float(json.loads(requests.get("https://api.github.com/repos/Luckyluka17/Wezzer/releases").text)[0]["name"])
actual = float(version)

if actual < latest:
    print(Fore.RED + Back.YELLOW + "/!\\" + Back.RESET + Fore.RED + " Une mise à jour est disponible. Il est recommandé de mettre à jour votre image Docker et de recréer votre conteneur pour bénéficier des dernières fonctionnalités et correctifs.")
    for i in range(0, 6):
        print(f"\rCe message sera ignoré dans {6-i} secondes", end="\r")
        time.sleep(1)
