# -*- coding: utf-8 -*-

import requests
import json
import os
import datetime
import csv
import gzip
ip_sannav = "XXXXX"
username = "XXXXX"
password = "XXXXX"

def sannav_login(ip_sannav, username, password):
    # Imposta l'URL dell'API di login
    login_url = f"https://{ip_sannav}/external-api/v1/login/"

    # Imposta gli header della richiesta
    headers = {
        "username": username,
        "password": password,
        "Content-Type": "application/json"
    }

    # Effettua la richiesta POST per ottenere il session ID
    response = requests.post(login_url, headers=headers, verify=False)

    # Leggi il contenuto della risposta e estrai il session ID
    data = response.json()
    sannav_key = data["sessionId"]
    return sannav_key

def sannav_logout(sannav_key, ip_sannav):
    url = f"https://{ip_sannav}/external-api/v1/logout/"
    headers = {
        "Authorization": sannav_key,
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, verify=False)
    return response.json()

def get_device_ports(ip_sannav, sannav_key, startIndex):
    url = f"https://{ip_sannav}/external-api/v1/inventory/deviceports/"
    params = {
        "startIndex": startIndex,
        "numOfRecords": 5000
    }
    headers = {
        "Authorization": sannav_key
    }

    response = requests.get(url, params=params, headers=headers, verify=False)
    return response.json()

def get_switch_ports(ip_sannav, sannav_key, startIndex):
    url = f"https://{ip_sannav}/external-api/v1/inventory/switchports/"
    params = {
        "startIndex": startIndex,
        "numOfRecords": 5000
    }
    headers = {
        "Authorization": sannav_key
    }

    response = requests.get(url, params=params, headers=headers, verify=False)
    return response.json()

def get_all_device_ports(ip_sannav, sannav_key):
    result = []
    start_index = 0
    while True:
        response = get_device_ports(ip_sannav, sannav_key, start_index)
        result.extend(response['DevicePorts'])
        start_index = response['startIndexToUse']
        if response['numOfEntitiesNotReturned'] == 0:
            break
    return result

def get_all_switch_ports(ip_sannav, sannav_key):
    result = []
    start_index = 0
    while True:
        response = get_switch_ports(ip_sannav, sannav_key, start_index)
        result.extend(response['switchPorts'])
        start_index = response['startIndexToUse']
        if response['numOfEntitiesNotReturned'] == 0:
            break
    return result

def get_switch_details(ip_sannav, sannav_key):
    url = f"https://{ip_sannav}/external-api/v1/inventory/switches/"
    headers = {
        "Authorization": sannav_key
    }
    response = requests.get(url, headers=headers, verify=False)
    data = response.json()
    filtered_data = []
    for switch in data["switches"]:
        filtered_data.append({
            "name": switch["name"],
            "physicalSwitchName": switch["physicalSwitchName"]
        })
    return filtered_data

def save_device_ports_report(ip_sannav, sannav_key):
    """
    Questa funzione unisce due JSON, uno contenente i dettagli degli switch e l'altro contenente tutte le porte dei dispositivi.
    Il risultato viene salvato in un file JSON nella cartella 'result_json'.
    """

    # Ottieni i dettagli degli switch e tutte le porte dei dispositivi
    json1 = get_switch_details(ip_sannav, sannav_key)
    json2 = get_all_device_ports(ip_sannav, sannav_key)

    # Crea una mappa per associare gli switch virtuali a quelli fisici
    map = {}
    for switch in json1:
        vSwitch = switch["name"]
        if vSwitch not in map.keys():
            map[vSwitch] = switch["physicalSwitchName"]

    # Unisci i due JSON
    join_json1_2 = []
    for i in range(len(json2)):
        if "switchName" in json2[i]:
            chiave = json2[i]["switchName"]
            json2[i]["pSwitch"] = None
            if chiave in map.keys():
                json2[i]["pSwitch"] = map[chiave]
        join_json1_2.append(json2[i])

    # Ordina il JSON unito
    join_json1_2 = sorted(join_json1_2, key=lambda x: (x.get("pSwitch", "") or "", x.get("switchName", "") or "", str(x.get("number", 0))))

    # Salva il JSON unito in un file
    if not os.path.exists('result_json'):
        os.makedirs('result_json')

    now = datetime.datetime.now()
    filename = '/var/www/localhost/htdocs/result_json/device_port.json'
    with open(os.path.join('result_json', filename), 'w') as f:
        import json
        json.dump(join_json1_2, f, indent=4)

    print(f"File salvato con successo: {filename}")

def save_switch_ports_report(ip_sannav, sannav_key):
    """
    Questa funzione unisce due JSON, uno contenente i dettagli degli switch e l'altro contenente tutte le porte dei dispositivi.
    Il risultato viene salvato in un file JSON nella cartella 'result_json'.
    """

    # Ottieni i dettagli degli switch e tutte le porte dei dispositivi
    json1 = get_switch_details(ip_sannav, sannav_key)
    json2 = get_all_switch_ports(ip_sannav, sannav_key)

    # Crea una mappa per associare gli switch virtuali a quelli fisici
    map = {}
    for switch in json1:
        vSwitch = switch["name"]
        if vSwitch not in map.keys():
            map[vSwitch] = switch["physicalSwitchName"]

    # Unisci i due JSON
    join_json1_2 = []
    for i in range(len(json2)):
        if "switchName" in json2[i]:
            chiave = json2[i]["switchName"]
            json2[i]["pSwitch"] = None
            if chiave in map.keys():
                json2[i]["pSwitch"] = map[chiave]
        join_json1_2.append(json2[i])

    # Ordina il JSON unito
    join_json1_2 = sorted(join_json1_2, key=lambda x: (x.get("pSwitch", "") or "", x.get("switchName", "") or "", str(x.get("portIndex", 0))))

    # Salva il JSON unito in un file
    if not os.path.exists('result_json'):
        os.makedirs('result_json')

    now = datetime.datetime.now()
    filename = '/var/www/localhost/htdocs/result_json/switch_port.json'
    with open(os.path.join('result_json', filename), 'w') as f:
        import json
        json.dump(join_json1_2, f, indent=4)

    print(f"File salvato con successo: {filename}")


### ---
sannav_key = sannav_login(ip_sannav, username, password)

save_device_ports_report(ip_sannav, sannav_key)
save_switch_ports_report(ip_sannav, sannav_key)
sannav_logout(sannav_key,ip_sannav)

def load_json(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_csv():
    base_dir = "/var/www/localhost/htdocs/result_json/"
    device_file = os.path.join(base_dir, "device_port.json")
    switch_file = os.path.join(base_dir, "switch_port.json")
    output_file = os.path.join(base_dir, "output.csv")

    device_data = load_json(device_file)
    switch_data = load_json(switch_file)

    # Creiamo un dizionario per accesso rapido ai dati dello switch
    switch_dict = {switch["wwn"]: switch for switch in switch_data if "wwn" in switch}

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "SWITCH", "P.IDX", "S/P", "SPEED", "SPEED_SUP",
            "CTX", "CTX_NAME", "PHY/NPIV", "WWPN", "ALIAS",
            "ROLE", "ZONE", "RESULT_JSON"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for device in device_data:
            switch_info = switch_dict.get(device.get("switchPortWwn"), {})  # Recupero info switch

            speed = switch_info.get("speed", "Unknown")
            if switch_info.get("speedNegotiated") == 1:
               speed = "N" + str(speed)
            else:
               speed = str(speed) + "G"

            speed_sup = switch_info.get("maxPortSpeed", "")
            if speed_sup == 32:
                speed_sup = "8,16,32_Gbps"
            elif speed_sup == 16:
                speed_sup = "4,8,16_Gbps"
            elif speed_sup == 8:
                speed_sup = "2,4,8_Gbps"

            alias = device.get("zoneAlias", "")
            actzonec = device.get("activeZoneCount")
            zone = "None"

            # Se l'alias non esiste, usa remoteDevice
            if not alias:
               alias = device.get('deviceSymbolicName',switch_info.get("remoteDevice", "No_Alias-cazzometto?"))
               zone = "None"
            else:
               # Se zoneAlias è valorizzato e activeZoneCount è assente o 0, aggiungi (UnZ)
               if actzonec is None or actzonec == 0:
                  alias += " (UnZ)"
                  zone = "None"
               else:
                  zone = device.get("activeZones", "")

            merged_entry = {
                "SWITCH": switch_info.get("pSwitch", "Unknown"),
                "P.IDX": switch_info.get("portIndex", "Unknown"),
                "S/P": f"{switch_info.get('slotNumber', 'Unknown')}/{switch_info.get('portNumber', 'Unknown')}",
                "SPEED": speed,
                "SPEED_SUP": speed_sup,
                "CTX": switch_info.get("virtualFabricId", ""),
                "CTX_NAME": device.get("fabricName", "Unknown"),
                "PHY/NPIV": "NPIV" if switch_info.get("npiv", 0) == 1 else "Physical",
                "WWPN": device.get("wwn", "Unknown"),
                "ALIAS": alias,
                "ROLE": device.get("portRole", ""),
                "ZONE": zone,
                "RESULT_JSON": json.dumps({**device, **switch_info})
            }

            # Se alias è mancante, usiamo remoteDevice dello switch
            if not merged_entry["ALIAS"] or merged_entry["ALIAS"] == "No_Alias":
                merged_entry["ALIAS"] = switch_info.get("remoteDevice", "No_Alias - definirecampo?")

            # DEBUG: Stampa un'anteprima della riga prima di scriverla
            #print("Writing entry:", merged_entry)

            writer.writerow(merged_entry)

# Esegui la generazione del CSV
generate_csv()
with open("/var/www/localhost/htdocs/result_json/output.csv", 'rb') as orig_file:
    with gzip.open("/var/www/localhost/htdocs/result_json/output.csv.gz", 'wb') as zipped_file:
        zipped_file.writelines(orig_file)

