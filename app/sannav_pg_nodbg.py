# -*- coding: utf-8 -*-

import requests, json, os, datetime, csv, gzip, subprocess
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()  # Carica le variabili dal file .env
ip_sannav = os.getenv("IP_SANNAV")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

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
    if not os.path.exists('/app/result_json'):
        os.makedirs('/app/result_json')

    now = datetime.datetime.now()
    filename = '/app/result_json/device_port.json'
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
    if not os.path.exists('/app/result_json'):
        os.makedirs('/app/result_json')

    now = datetime.datetime.now()
    filename = '/app/result_json/switch_port.json'
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
    base_dir = "/app/result_json/"
    device_file = os.path.join(base_dir, "device_port.json")
    switch_file = os.path.join(base_dir, "switch_port.json")
    output_file = os.path.join(base_dir, "output.csv")

    device_data = load_json(device_file)
    switch_data = load_json(switch_file)

    # Scrivo riga intestazione su output_file
    with open(output_file, mode='w', newline='') as csvfile:
        fieldnames = [
            "SWITCH", "VSWITCH", "P.IDX", "S/P", "SPEED", "SFP SUPP", "CTX", "CTX NAME",
            "PHY/NPIV", "STATE", "STATUS", "WWPN", "ALIAS", "ROLE", "ZONE", "NOTE"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # --------------------------
        # Prima passo sulle OFFLINE
        # --------------------------
        for port in switch_data:
            if port.get("state") != "Offline":
                continue
            speed = port.get("speed", "Unknown")
            stat = port.get("status")

            if port.get("speedNegotiated") == 1:
               speed = "N" + str(speed)
            else:
               speed = str(speed) + "G"

            speed_sup_map = {32: "8,16,32_Gbps", 16: "4,8,16_Gbps", 8: "2,4,8_Gbps"}
            speed_sup = speed_sup_map.get(port.get("maxPortSpeed"), "")

            if port.get("status") == "Disabled (Persistent)":
                stat = f"{port.get('status')} - {port.get('statusMessage')}"

            row = {
              "SWITCH": port.get("pSwitch"),
              "VSWITCH": port.get("switchName"),
              "P.IDX": port.get("portIndex"),
              "S/P": f"{port.get('slotNumber')}/{port.get('portNumber')}",
              "SPEED": speed,
              "SFP SUPP": speed_sup,
              "CTX": port.get("virtualFabricId"),
              "CTX NAME": port.get("fabricName"),
              "PHY/NPIV": "Physical",
              "STATE": port.get("state"),
              "STATUS": stat,
              "WWPN": "None",
              "ALIAS": "No_device_connected",
              "ROLE": "None",
              "ZONE": "None",
              "NOTE": f"PortID: {port.get('portId')}"
            }
            writer.writerow(row)

        # ---------------------------------------
        # Ora passo sulle ONLINE - solo Physical
        # ---------------------------------------
        for port in switch_data:
            if port.get("state") != "Online":
                continue

            switch_port_wwn = port.get("wwn")
            switch_port_id = port.get("portId")

            matching_device = None
            for device in device_data:
                if (device.get("portId") == switch_port_id and
                    device.get("switchPortWwn") == switch_port_wwn):
                    matching_device = device
                    break

            alias = "None"
            zone = "None"
            role = "None"
            wwpn = port.get("remotePortWwn")

            if matching_device:
                #wwpn = matching_device.get("wwn", switch_port_wwn)
                actzonec = matching_device.get("activeZoneCount")
                alias = matching_device.get("zoneAlias", "")
                zone = "None"

                speed = port.get("speed", "Unknown")
                if port.get("speedNegotiated") == 1:
                   speed = "N" + str(speed)
                else:
                   speed = str(speed) + "G"

                speed_sup_map = {32: "8,16,32_Gbps", 16: "4,8,16_Gbps", 8: "2,4,8_Gbps"}
                speed_sup = speed_sup_map.get(port.get("maxPortSpeed"), "")

                if not alias:
                    alias_f = matching_device.get("symbolicName") or matching_device.get("deviceSymbolicName") or port.get("remoteDevice") or matching_device.get("vendor")
                    alias = f"No_Alias - {alias_f}"
                else:
                    if actzonec is None or actzonec == 0:
                        alias += " (UnZ)"
                        zone = "None"
                    else:
                        zone = matching_device.get("activeZones", "")

                role = matching_device.get("portRole") or port.get("connectedDeviceType")
                note = f"PortID: {port.get('portId')} matched in device file"
            else:
                alias = f"No_Alias - {port.get('remoteDevice') }"
                zone = "None"
                role = port.get("connectedDeviceType")
                note = f"PortID: {port.get('portId')} no match in device file"

            if port.get("state") == "Online" and not switch_port_wwn:
                note += " | WARNING: Porta online senza device"

            # Scrivo la riga della PHYSICAL
            row = {
              "SWITCH": port.get("pSwitch"),
              "VSWITCH": port.get("switchName"),
              "P.IDX": port.get("portIndex"),
              "S/P": f"{port.get('slotNumber')}/{port.get('portNumber')}",
              "SPEED": speed,
              "SFP SUPP": speed_sup,
              "CTX": port.get("virtualFabricId"),
              "CTX NAME": port.get("fabricName"),
              "PHY/NPIV": "Physical",
              "STATE": port.get("state"),
              "STATUS": port.get("status"),
              "WWPN": wwpn,
              "ALIAS": alias,
              "ROLE": role,
              "ZONE": zone,
              "NOTE": note
            }
            writer.writerow(row)

            # --------------------------
            # CERCO eventuali NPIV legati alla Physical
            # --------------------------
            port_id_prefix = str(switch_port_id)[:4]
            for device in device_data:
                dev_port_id = str(device.get("portId"))

                # Escludo la porta fisica gia' scritta
                if dev_port_id == str(switch_port_id):
                   continue

                # Cerco solo NPIV con stesso prefisso port_id_prefix (prime 4 cifre) e stesso switchPortWwn
                if dev_port_id.startswith(port_id_prefix) and device.get("switchPortWwn") == switch_port_wwn:
                   alias = device.get("zoneAlias", "")
                   zone = "None"
                   role = device.get("portRole", "None")

                   speed = port.get("speed", "Unknown")
                   if port.get("speedNegotiated") == 1:
                      speed = "N" + str(speed)
                   else:
                      speed = str(speed) + "G"

                   speed_sup_map = {32: "8,16,32_Gbps", 16: "4,8,16_Gbps", 8: "2,4,8_Gbps"}
                   speed_sup = speed_sup_map.get(port.get("maxPortSpeed"), "")

                   actzonec = device.get("activeZoneCount")
                   if not alias:
                       alias_f = device.get("deviceSymbolicName") or device.get("vendor")
                       alias = f"No_Alias - {alias_f}"
                   else:
                       if not actzonec:
                           alias += " (UnZ)"
                       else:
                           zone = device.get("activeZones", "")

                   # Scrivo la riga NPIV trovata
                   npiv_row = {
                     "SWITCH": port.get("pSwitch"),
                     "VSWITCH": port.get("switchName"),
                     "P.IDX": port.get("portIndex"),
                     "S/P": f"{port.get('slotNumber')}/{port.get('portNumber')}",
                     "SPEED": speed,
                     "SFP SUPP": speed_sup,
                     "CTX": port.get("virtualFabricId"),
                     "CTX NAME": port.get("fabricName"),
                     "PHY/NPIV": "NPIV",
                     "STATE": port.get("state"),
                     "STATUS": port.get("status"),
                     "WWPN": device.get("wwn", "None"),
                     "ALIAS": alias,
                     "ROLE": device.get("portRole", "None"),
                     "ZONE": zone,
                     "NOTE": f"NPIV matched by prefix on PortID {port.get('portId')}"
                   }
                   writer.writerow(npiv_row)

    print("CSV generato con successo!")

# Esegui la generazione del CSV
generate_csv()

# Gzippo file per download più rapidio
with open ("/app/result_json/output.csv", 'rb') as orig_file:
    with gzip.open("/app/result_json/output.csv.gz", 'wb') as zipped_file:
        zipped_file.writelines(orig_file)

print(f"File compresso: {zipped_file}")

# Update DB
result = subprocess.run(["python", "/app/update_db.py"], capture_output=True, text=True)
print(result.stdout)  # Stampa l'output dello script eseguito
