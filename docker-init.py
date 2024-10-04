import os
import yaml
from colorama import init, Fore

init(autoreset=True)

workdir = "/data"
default_settings = {
    "api": "api.open-meteo.com",
    # Proxy (https://docs.proxyscrape.com/)
    "use_proxies": True,
    "proxy_country_code": "all",
    "proxy_max_timeout": 50,
    # Personnalisation
    "footer": ""
}

if not os.path.exists(f"{workdir}/config.yml"):

    print(Fore.YELLOW + "Création du fichier de paramètres...")

    with open(f"{workdir}/config.yml", "w", encoding="utf-8") as f:
        yaml.safe_dump(default_settings, f, default_flow_style=False)
        f.close()