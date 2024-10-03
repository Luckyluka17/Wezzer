import os
import yaml
from colorama import init, Fore

init(autoreset=True)

workdir = "/data"

if not os.path.exists(f"{workdir}/config.yml"):

    print(Fore.YELLOW + "Création du fichier de paramètres...")

    with open(f"{workdir}/config.yml", "w", encoding="utf-8") as f:
        yaml.safe_dump(
            {
                "api": "api.open-meteo.com",
                "server_description": "",
                # Pour remplir les paramètres ci-dessous, veuillez consulter https://docs.proxyscrape.com/
                "use_proxies": True,
                "proxy_country_code": "all",
                "proxy_max_timeout": 50
            },
            f,
            default_flow_style=False
        )
        f.close()