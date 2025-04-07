from pymongo import MongoClient
from datetime import datetime, time, timedelta


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

def ottieni_ultimi_dati(db, nomeCollezione, num):
    '''ottieni un numero di dati pari al num'''
    ultimo_dato = db[nomeCollezione].find().sort("date_hour", -1).limit(num)
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
    '''
    questa funzione verrà richiamata a mezzanotte, serve per il machine learning e per i dati da archiviare
    come parametri richiede l'oggetto db e il nome della collezione su cui prendere i dati
    salva sul db nella collezione COLLEZIONE_DATI_GIORNALIERI, i dati riguardanti la media delle ultime 24 ore (dinamiche)
    restiuisce inoltre un dizionario:
    {
        "data": data_attuale,                    # La data corrente
        "temp_minima": valore_numerico,          # Temperatura minima
        "temp_massima": valore_numerico,         # Temperatura massima
        "temp_media": valore_numerico,           # Temperatura media
        "umidita_minima": valore_numerico,       # Umidità minima
        "umidita_massima": valore_numerico,      # Umidità massima
        "umidita_media": valore_numerico,        # Umidità media
        "velocita_vento_media": valore_numerico, # Velocità media del vento
        "raffica": valore_numerico,              # Velocità massima del vento (raffica)
        "pressione_media": valore_numerico,      # Pressione barometrica media
        "precipitazioni": valore_numerico        # Quantità totale di precipitazioni
    }
    '''
    ora_attuale = datetime.now()

    risultati = ottieni_ultimi_dati(db, collezione, 47)
    dati = {
        "data": datetime.combine(ora_attuale.date(), datetime.min.time())
    }
    
    print(f"Trovati {len(risultati)} record per le ultime 24 ore")
    
    # Verifica la struttura dei dati
    # if risultati and len(risultati) > 0:
    #     print("Esempio di documento:")
    #     print(risultati[0])
    
    
    # Controlla se ci sono risultati
    if risultati:
        temperature = [doc.get('outside_temp', 0) for doc in risultati if 'outside_temp' in doc and doc['outside_temp'] is not None]
        umidita = [doc.get('outside_humidity', 0) for doc in risultati if 'outside_humidity' in doc and doc['outside_humidity'] is not None]
        velocita_vento = [doc.get('wind_speed', 0) for doc in risultati if 'wind_speed' in doc and doc['wind_speed'] is not None]
        
        # Attenzione particolare al campo barometer
        pressione = []
        for doc in risultati:
            if 'barometer' in doc and doc['barometer'] is not None:
                try:
                    val = float(doc['barometer'])
                    pressione.append(val)
                except (ValueError, TypeError):
                    print(f"Valore barometer non valido: {doc['barometer']}")
        
        
        
        if temperature:
            dati["temp_minima"] = min(temperature)
            dati["temp_massima"] = max(temperature)
            dati["temp_media"] = sum(temperature) / len(temperature)
        else:
            dati["temp_minima"] = dati["temp_massima"] = dati["temp_media"] = 0
            
        if umidita:
            dati["umidita_minima"] = min(umidita)
            dati["umidita_massima"] = max(umidita)
            dati["umidita_media"] = sum(umidita) / len(umidita)
        else:
            dati["umidita_minima"] = dati["umidita_massima"] = dati["umidita_media"] = 0
            
        if velocita_vento:
            dati["velocita_vento_media"] = sum(velocita_vento) / len(velocita_vento)
            dati["raffica"] = max(velocita_vento)
        else:
            dati["velocita_vento_media"] = dati["raffica"] = 0
                            
        if pressione:
            dati["pressione_media"] = sum(pressione) / len(pressione)
        else:
            dati["pressione_media"] = 0
            print("ATTENZIONE: Nessun valore valido di pressione trovato!")
    else:
        # Valori predefiniti se non ci sono dati
        dati["temp_minima"] = dati["temp_massima"] = dati["temp_media"] = 0
        dati["umidita_minima"] = dati["umidita_massima"] = dati["umidita_media"] = 0
        dati["velocita_vento_media"] = dati["raffica"] = 0
        dati["pressione_media"] = 0
        print("ATTENZIONE: Nessun record trovato per le ultime 24 ore!")
    
    # Ottieni il valore delle precipitazioni (resta la funzione esistente)
    dati["precipitazioni"] = prendi_precipitazioni_giornaliere(db, collezione)
    
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
    }).sort('data', 1).limit(5))
    
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
