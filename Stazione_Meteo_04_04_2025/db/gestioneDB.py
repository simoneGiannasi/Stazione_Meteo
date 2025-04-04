from pymongo import MongoClient
from datetime import datetime, time

COLLEZIONE_DATI_GIORNALIERI = "dati_giornalieri"

def converti_struttura_dati(dati_originali):
    """
    Converte la struttura dati originale in un dizionario formattato.
    
    Args:
        dati_originali: Lista contenente datetime e dizionario con dati meteo
        
    Returns:
        dizionario strutturato nel formato richiesto
    """
    # Estrai timestamp e dizionario dalla lista originale
    timestamp = dati_originali[0]
    dati_meteo_originali = dati_originali[1]
    
    # Crea un nuovo dizionario con la struttura desiderata
    dati_meteo = {
        "date_hour": timestamp,  # Nome coerente con il campo timeField
        **dati_meteo_originali
    }
    
    # Converti i campi specifici che richiedono una formattazione diversa
    dati_meteo["extra_temp_hum_alarms"] = bytes([0]*8)
    dati_meteo["soil_leaf_alarms"] = bytes([0]*4)
    
    return dati_meteo

def connessione_db(nomeDB):
    # Connessione al database
    client = MongoClient("mongodb://localhost:27017")
    db = client[nomeDB]
    return db, client

def crea_collezione(db,nomeCollezione):
    # Verifica se la collezione esiste prima di crearla
    if nomeCollezione not in db.list_collection_names():
        db.create_collection(nomeCollezione, timeseries={"timeField": 'date_hour'}) #sono collezioni ottimizzate, caso particolare con mongo db

def ottieni_ultimi_dati(db, nomeCollezione):
    # Esegue una query per ottenere l'ultimo documento inserito
    ultimo_dato = db[nomeCollezione].find().sort("date_hour", -1).limit(1)
    return list(ultimo_dato)

def inserisci_dati(db, dati):
    db.dati_meteo.insert_one(dati)

def min_max_temp(db, collection):
    oggi = datetime.now().date()
    inizio_giorno = datetime.combine(oggi, time.min)  # Inizio della giornata (00:00:00)
    fine_giorno = datetime.combine(oggi, time.max)    # Fine della giornata (23:59:59)

    # Query per filtrare i dati di temperatura esterna per oggi
    query = {
        'date_hour': {
            '$gte': inizio_giorno,
            '$lte': fine_giorno
        }
    }

    # Esegui la query e ottieni i risultati
    risultati = list(db[collection].find(query, {'outside_temp': 1, 'date_hour': 1, '_id': 0}))

    # Verifica se ci sono risultati
    if risultati:
        # Estrai tutte le temperature
        temperature = [doc['outside_temp'] for doc in risultati]
        
        # Calcola il minimo e il massimo
        temp_minima = min(temperature)
        temp_massima = max(temperature)
        # Calcola la media
        temp_media = sum(temperature) / len(temperature)
    else:
        temp_minima = 0
        temp_massima = 0
        temp_media = 0

    return temp_minima, temp_massima, temp_media

def calcola_raffica_vento(db, collezione):
    # Ottieni la data di oggi
    oggi = datetime.now().date()
    inizio_giorno = datetime.combine(oggi, time.min)  # Inizio della giornata (00:00:00)
    fine_giorno = datetime.combine(oggi, time.max)    # Fine della giornata (23:59:59)

    # Query per filtrare i dati meteo per oggi
    query = {
        'date_hour': {
            '$gte': inizio_giorno,
            '$lte': fine_giorno
        }
    }

    # Recupera solo i dati del vento
    collection = db[collezione]
    risultati = list(collection.find(query, {
        'wind_speed': 1, 
        'date_hour': 1, 
        '_id': 0
    }))

    # Inizializza le variabili
    raffica = None
    orario_raffica = None
    
    if risultati:
        # Trova il documento con la velocità massima del vento
        doc_raffica = max(
            [doc for doc in risultati if 'wind_speed' in doc], 
            key=lambda x: x['wind_speed']
        )
        
        # Estrai raffica e orario
        raffica = doc_raffica['wind_speed']
        orario_raffica = str(doc_raffica['date_hour'])
        orario_raffica = orario_raffica[10:16]

    
    return raffica, orario_raffica


def temperature_giornaliere(db, collection_name):
    # Fetch last 24 records sorted by timestamp
    records = list(db[collection_name].find().sort('date_hour', -1).limit(24))
    
    # Return a list of dictionaries with multiple metrics
    return [
        {
            'temperature': float(record['outside_temp']), 
            'barometer': float(record['barometer']),
            'outside_humidity': float(record['outside_humidity']),
            'timestamp': record['date_hour'].isoformat()
        } 
        for record in records
    ]


# dati_originali = [datetime(2025, 2, 28, 22, 51, 26, 838436), 
# {
#     'bar_trend': 'In rapida diminuzione', 
#     'packet_type': 0,
#     'next_record': 272,
#     'barometer': 995.4,
#     'inside_temp': 20.3,
#     'inside_humidity': 43,
#     'wind_speed': 255,
#     'wind_direction': 32767,
#     'rain_rate': 65535,
#     'storm_rain': 0.0,
#     'storm_start_date': '2127-15-31',
#     'day_rain': 0.0,
#     'month_rain': 0.0,
#     'year_rain': 0.0,
#     'day_et': 0.0,
#     'month_et': 0.0,
#     'year_et': 0.0,
#     'leaf_wetness_4': 0,
#     'inside_alarms': 0,
#     'rain_alarms': 0,
#     'outside_alarms': 0,
#     'extra_temp_hum_alarms': b'\x00\x00\x00\x00\x00\x00\x00\x00',
#     'soil_leaf_alarms': b'\x00\x00\x00\x00',
#     'transmitter_battery': 0,
#     'console_battery': 1.330078125, 
#     'forecast_icons': 7, 
#     'forecast_rule': 172, 
#     'sunrise': '07:37', 
#     'sunset': '18:59'
# }]

# nomeDB='meteoDB'
# db=connessione_db(nomeDB)
# crea_collezione(db,'dati_meteo')
# dati_meteo_convertiti = converti_struttura_dati(dati_originali)
# inserisci_dati(db, dati_meteo_convertiti)
# print(ottieni_ultimi_dati(db,'dati_meteo'))

def prendi_precipitazioni_giornaliere(db, collezione):
    # Ottieni la data di oggi
    oggi = datetime.now().date()
    inizio_giorno = datetime.combine(oggi, time.min)  # Inizio della giornata (00:00:00)
    fine_giorno = datetime.combine(oggi, time.max)    # Fine della giornata (23:59:59)

    # Query per filtrare i dati meteo per oggi
    query = {
        'date_hour': {
            '$gte': inizio_giorno,
            '$lte': fine_giorno
        }
    }

    # Recupera il dato più recente per oggi
    collection = db[collezione]
    ultimo_dato = collection.find_one(query, sort=[('date_hour', -1)])
    
    # Estrai il valore day_rain se disponibile
    if ultimo_dato and 'day_rain' in ultimo_dato:
        return ultimo_dato['day_rain']
    else:
        return 0.0
    

def calcoli_giornalieri_meteo(db, collezione):
    dati = {}
    # Calcola le temperature minime e massime e medie
    temp_minima, temp_massima, temp_media = min_max_temp(db, collezione)
    raffica, orario_raffica = calcola_raffica_vento(db, collezione)
    precipitazioni = prendi_precipitazioni_giornaliere(db, collezione)
    
    # Inserisci i valori nel dizionario dati
    dati["temp_minima"] = temp_minima
    dati["temp_massima"] = temp_massima
    dati["temp_media"] = temp_media
    dati["raffica"] = raffica
    dati["orario_raffica"] = orario_raffica
    dati["precipitazioni"] = precipitazioni
    
    # Aggiungi la data corrente al dizionario
    dati["data"] = datetime.now().date()
    
    # Inserisci i dati calcolati nella collezione "dati_giornalieri"
    db[COLLEZIONE_DATI_GIORNALIERI].insert_one(dati) 
    return dati

def get_tabelladati(db):
    
    # Recupera gli ultimi 5 giorni di dati dalla collezione dati_giornalieri
    # Ordina per data in ordine decrescente e limita a 5 risultati
    tabella_dati = list(db[COLLEZIONE_DATI_GIORNALIERI].find({}, {
        '_id': 0,
        'data': 1,
        'temp_media': 1,
        'temp_minima': 1,
        'temp_massima': 1,
        'raffica': 1,
        'precipitazioni': 1
    }).sort('data', -1).limit(5))
    
    # Formatta i dati per la visualizzazione
    for dato in tabella_dati:
        # Converti la data in formato italiano (DD/MM/YYYY)
        if 'data' in dato and dato['data']:
            dato['data_formattata'] = dato['data'].strftime('%d/%m/%Y')
        else:
            dato['data_formattata'] = 'N/D'
        
        # Formatta le temperature con un decimale e aggiungi il simbolo °C
        if 'temp_media' in dato:
            dato['temp_media_formattata'] = f"{dato['temp_media']:.1f}°C"
        if 'temp_minima' in dato:
            dato['temp_minima_formattata'] = f"{dato['temp_minima']:.1f}°C"
        if 'temp_massima' in dato:
            dato['temp_massima_formattata'] = f"{dato['temp_massima']:.1f}°C"
        
        # Formatta la velocità del vento
        if 'raffica' in dato and dato['raffica'] is not None:
            dato['raffica_formattata'] = f"{dato['raffica']:.1f} km/h"
        else:
            dato['raffica_formattata'] = 'N/D'
        
        # Formatta le precipitazioni
        if 'precipitazioni' in dato:
            dato['precipitazioni_formattate'] = f"{dato['precipitazioni']:.1f} mm"

    return tabella_dati
