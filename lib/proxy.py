import requests
import random
import json

def random_proxy(config_file: dict = {}):
    """
    Récupérer l'adresse http d'un proxy aléatoire, en utilisant les paramètres fournis dans le fichier de configuration.
    """
    with requests.get(f"https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout={config_file['proxy_max_timeout']}&country={config_file['proxy_country_code']}&ssl=all&anonymity=all") as r:
        proxies = r.text.split("\n")
        r.close()


    return str(random.choice(proxies))

def fetch_data(url: str = "", config_file: dict = {}):
    proxies = {"http": random_proxy(config_file)}
    
    if config_file["use_proxies"]:
        with requests.get(url, proxies=proxies) as r:
            data = json.loads(r.text)
            r.close()
    else:
        with requests.get(url) as r:
            data = json.loads(r.text)
            r.close()

    return data