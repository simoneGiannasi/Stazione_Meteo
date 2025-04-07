from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify
import threading
import signal
import sys
from collections import deque
from comunicazione.richiesta_dati import dati
import datetime
from db.gestioneDB import *
import math
import time
from datetime import datetime
from machine_learning.gestione_ml_v1 import *


app = Flask(__name__)
data_deque = deque(maxlen=10)
data_prev_dom = deque(maxlen=1)
data_prev_dDom = deque(maxlen=1)
data_prev_ddDom = deque(maxlen=1)

lock = threading.Lock()
lock_prev_dom = threading.Lock()
lock_prev_dDom = threading.Lock()
lock_prev_ddDom = threading.Lock()

# Evento globale per segnalare la terminazione
shutdown_event = threading.Event()
nomeDB = 'meteoDB'


def signal_handler(sig, frame):
    print("Chiusura in corso...")
    shutdown_event.set()  # Imposta l'evento di shutdown
    # Attendi un po' per dare tempo ai thread di completare
    time.sleep(2)
    sys.exit(0)

def raccogli_dati():
    try:
        while not shutdown_event.is_set():
            print("Raccogliendo dati...")
            informazioni = dati()
            
            ora_corrente = datetime.now()

            if not informazioni or informazioni['wind_direction']=='0':
                totale = (ora_corrente, 0)
                print('Errore nella raccolta dati o stazione non connessa')
            else:
                #print(f"Dati ricevuti prima di salvarli in deque: {informazioni}")  # Debug
               
                totale = (ora_corrente, informazioni)

            with lock:  # Protezione della sezione critica
                data_deque.append(totale)

            #print(f"Dati salvati nel deque: {data_deque[-1]}")  # Debug
            
            # Usa wait con timeout invece di sleep per reagire all'evento di shutdown
            shutdown_event.wait(timeout=60)
    except Exception as e:
        print(f"Errore nel thread raccogli_dati: {e}")

def salva_dati():
    
    minuti = 60   # Da modificare a 5 per riempire il db in 30 secondi
    db = None
    try:        
        while not shutdown_event.is_set():
            now = datetime.now()  # correggi qui
            if now.minute < 30:
                minutes_to_wait = 30 - now.minute
            else:
                minutes_to_wait = minuti - now.minute
            seconds_to_wait = minutes_to_wait * minuti - now.second

            if shutdown_event.wait(timeout=seconds_to_wait):
                break

            with lock:
                if len(data_deque) > 0:
                    dati_lista = list(data_deque)
                else:
                    print("Nessun dato disponibile per il salvataggio")
                    continue
            
            if dati_lista and dati_lista[-1][1] != 0:
                try:
                    db, client = connessione_db(nomeDB)
                    try:
                        crea_collezione(db, 'dati_meteo')
                        dati_meteo_convertiti = converti_struttura_dati(dati_lista[-1][:2])
                        inserisci_dati(db, dati_meteo_convertiti)
                        print(f"Dati salvati alle {datetime.now().strftime('%H:%M:%S')}")
                        #print(ottieni_ultimi_dati(db, 'dati_meteo'))
                    finally:
                        client.close()
                except Exception as e:
                    print(f"Errore durante il salvataggio dei dati: {e}")
    except Exception as e:
        print(f"Errore nel thread salva_dati: {e}")
    finally:
        if db:
            client.close()
            print("Connessione al database chiusa")

@app.route('/')
def index():
    dati = {}
    with lock:
        if len(data_deque) > 0:
            dati = list(data_deque)
        

    if dati[-1][1] != 0:  # Se legge i dati: stazione online
        # La lettura è OK
        db, client= connessione_db(nomeDB)        # Errore nella lettura, la stazione è offline
        dati_mongo_db = ottieni_ultimi_dati(db, "dati_meteo",1)
        #print(f"Dati salvati sul mongodb= {dati_mongo_db}")
        data_ora = str(dati_mongo_db[0]["date_hour"])
        giorno = data_ora[:10]
        ora = data_ora[11:16]
        giorno = datetime.strptime(giorno, "%Y-%m-%d")
        mesi_italiani = {
            1: "gennaio", 2: "febbraio", 3: "marzo", 4: "aprile",
            5: "maggio", 6: "giugno", 7: "luglio", 8: "agosto",
            9: "settembre", 10: "ottobre", 11: "novembre", 12: "dicembre"
        }
        data_formattata = f"{giorno.day} {mesi_italiani[giorno.month]} {giorno.year}"
        data = [(data_formattata,ora),dati_mongo_db[0]]
        data.append(('success', 'attiva'))
        data[1]["min_temp"], data[1]["max_temp"],_ = min_max_temp(db, "dati_meteo")
        data[1]["raffica"], data[1]["orario_raffica"] = calcola_raffica_vento(db, "dati_meteo")
        client.close()

        
    
    else:                # Errore nella lettura, la stazione è offline
        db, client= connessione_db(nomeDB)        
        dati_mongo_db = ottieni_ultimi_dati(db, "dati_meteo",1)
        #print(f"Dati salvati sul mongodb= {dati_mongo_db}")
        data_ora = str(dati_mongo_db[0]["date_hour"])
        giorno = data_ora[:10]
        ora = data_ora[11:16]
        giorno = datetime.strptime(giorno, "%Y-%m-%d")
        mesi_italiani = {
            1: "gennaio", 2: "febbraio", 3: "marzo", 4: "aprile",
            5: "maggio", 6: "giugno", 7: "luglio", 8: "agosto",
            9: "settembre", 10: "ottobre", 11: "novembre", 12: "dicembre"
        }
        data_formattata = f"{giorno.day} {mesi_italiani[giorno.month]} {giorno.year}"
        data = [(data_formattata,ora),dati_mongo_db[0],('danger', 'non disponibile')]
        data[1]["min_temp"], data[1]["max_temp"], _ = min_max_temp(db, "dati_meteo")
        data[1]["raffica"], data[1]["orario_raffica"] = calcola_raffica_vento(db, "dati_meteo")
        client.close()
        
    # Calcola la temperatura percepita usando la formula del Wind Chill
    outside_temp = data[1]["outside_temp"]
    wind_speed = data[1]["wind_speed"]
    umidita = data[1]["outside_humidity"]
    temp_perc = (
        13.12 +
        0.6215 * outside_temp -
        11.37 * wind_speed ** 0.16 +
        0.3965 * outside_temp * wind_speed ** 0.16
    )
    data[1]["temp_perc"] = round(temp_perc, 2)

    #Calcola il punto di rugiada dato la temperatura (°C) e l'umidità relativa (%)
    #usando la formula di Magnus-Tetens.
    
    a = 17.27
    b = 237.7  # °C
    
    alpha = ((a * outside_temp) / (b + outside_temp)) + math.log(umidita / 100.0)
    punto_di_rugiada = (b * alpha) / (a - alpha)
    data[1]["punto_di_rugiada"] = round(punto_di_rugiada,1)

    with lock_prev_dom:
        if len(data_prev_dom) > 0:
            dom = data_prev_dom[0]
            #print(f"Domani: {dom}")
            for i in dom.keys():
                try:
                    dom[i] = round(dom[i][0], 2)
                except:
                    dom[i] = round(dom[i], 2)
        else:
            dom = {"standard"}
    
    with lock_prev_ddDom:
        if len(data_prev_ddDom) > 0:
            dopodomani = data_prev_ddDom[0]
            print(f"Dopodomani: {dopodomani}")
            for i in dopodomani.keys():
                try:
                    dopodomani[i] = round(dopodomani[i][0], 2)
                except:
                    dopodomani[i] = round(dopodomani[i], 2)
        else:
            dopodomani = {"standard"}
    with lock_prev_dDom:
        if len(data_prev_dDom) > 0:
            tregiorni = data_prev_dDom[0]
            for i in tregiorni.keys():
                try:
                    tregiorni[i] = round(tregiorni[i][0], 2)
                except:
                    tregiorni[i] = round(tregiorni[i], 2)
        else:
            tregiorni = {"standard"}
    #print(f"Domani: {dom}, Dopodomani: {dopodomani}, Tra tre giorni: {tregiorni}")

# Da fare gestione giorni (data) e emojy da implementare
    return render_template('index.html', data=data, domani = dom, dopodomani = dopodomani, tregiorni = tregiorni)

@app.route('/archivio-dati')
def archivio_dati():
    try:
        db, client = connessione_db(nomeDB)
        tabella_dati = get_tabelladati(db)
        #print(tabella_dati)
        client.close()
    except Exception as e:
        print(f"Errore nella lettura dei dati: {e}")
        tabella_dati = []  # Inizializza la tabella_dati come vuota in caso di errore
    return render_template('archivio-dati.html', tabella_dati=tabella_dati)
    
@app.route('/progetto')
def progetto():
    return render_template('progetto.html')

@app.route('/api/grafici')
def grafici_api():
    try:
        db, client = connessione_db(nomeDB)
        temperature_day = temperature_giornaliere(db, "dati_meteo")
        client.close() 
        return jsonify(temperature_day)
    except Exception as e:
        print(f"Error accessing database: {e}")
        return jsonify([])  # Return empty list if error occurs
                    
@app.route('/dati_live')
def dati_live():
    return render_template('dati_live.html')

@app.route('/api/live-data')
def live_data_api():
    with lock:
        if len(data_deque) > 0:
            latest_data = list(data_deque)[-1]
            
            # Check if we have valid data
            if latest_data[1] != 0:  # Station online
                # Valid data from the station
                result = latest_data[1].copy()  # Make a copy to avoid modifying the cached data
                result['timestamp'] = latest_data[0].strftime('%Y-%m-%d %H:%M:%S')
                print(type(result))
                # Calculate additional metrics
                outside_temp = result["outside_temp"]
                wind_speed = result["wind_speed"]
                umidita = result["outside_humidity"]
                
                # Perceived temperature
                temp_perc = (
                    13.12 +
                    0.6215 * outside_temp -
                    11.37 * wind_speed ** 0.16 +
                    0.3965 * outside_temp * wind_speed ** 0.16
                )
                result["temp_perc"] = round(temp_perc, 2)
                
                # Dew point
                a = 17.27
                b = 237.7  # °C
                alpha = ((a * outside_temp) / (b + outside_temp)) + math.log(umidita / 100.0)
                punto_di_rugiada = (b * alpha) / (a - alpha)
                result["punto_di_rugiada"] = round(punto_di_rugiada, 1)
                
                # Get data from database
                try:
                    db, client = connessione_db(nomeDB)
                    result["min_temp"], result["max_temp"], _ = min_max_temp(db, "dati_meteo")
                    result["raffica"], result["orario_raffica"] = calcola_raffica_vento(db, "dati_meteo")
                    client.close()
                except Exception as e:
                    print(f"Error accessing database: {e}")
                    result["min_temp"], result["max_temp"] = (0, 0)
                    result["raffica"], result["orario_raffica"] = (0, "00:00")
                
                return jsonify({"status": "online", "data": result})
            else:
                # Station offline, use database data
                try:
                    db, client = connessione_db(nomeDB)
                    dati_mongo_db = ottieni_ultimi_dati(db, "dati_meteo",1)[0]
                    dati_mongo_db["min_temp"], dati_mongo_db["max_temp"], _ = min_max_temp(db, "dati_meteo")
                    dati_mongo_db["raffica"], dati_mongo_db["orario_raffica"] = calcola_raffica_vento(db, "dati_meteo")
                    client.close()
                    
                    return jsonify({"status": "offline", "data": dati_mongo_db})
                except Exception as e:
                    print(f"Error accessing database: {e}")
                    return jsonify({"status": "error", "message": "Cannot retrieve data"})
        else:
            return jsonify({"status": "error", "message": "No data available"})

def calcolaStagione():
    oggi = datetime.now()
    giorno = oggi.day
    mese = oggi.month

    if (mese == 12 and giorno >= 1) or mese in [1, 2] or (mese == 3 and giorno < 21):
        #inverno
        return 0
    elif (mese == 3 and giorno >= 21) or mese in [4, 5] or (mese == 6 and giorno < 21):
        #primavera
        return 1
    elif (mese == 6 and giorno >= 21) or mese in [7, 8] or (mese == 9 and giorno < 23):
        #estate
        return 2
    elif (mese == 9 and giorno >= 23) or mese in [10, 11] or (mese == 12 and giorno < 1):
        #autunno
        return 3

def mezzanotte():
    while not shutdown_event.is_set():
        try:
            now = datetime.now()
            target_time = now.replace(hour=17, minute=10, second=0, microsecond=0)
            if now > target_time:
                target_time = target_time + timedelta(days=1)
            seconds_to_wait = (target_time - now).total_seconds()
            if shutdown_event.wait(timeout=seconds_to_wait):
                break
                
            
           
            try:
                db, client = connessione_db(nomeDB)
                calcoli_giornalieri = calcoli_giornalieri_meteo(db, "dati_meteo")
                client.close()
                if calcoli_giornalieri['pressione_media']!=0:
                    stagione=calcolaStagione()

                    # { 
                    # "data": data_attuale, # La data corrente
                    # "temp_minima": valore_numerico, # Temperatura minima 
                    # "temp_massima": valore_numerico, # Temperatura massima 
                    # "temp_media": valore_numerico, # Temperatura media 
                    # "umidita_minima": valore_numerico, # Umidità minima 
                    # "umidita_massima": valore_numerico, # Umidità massima 
                    # "umidita_media": valore_numerico, # Umidità media 
                    # "velocita_vento_media": valore_numerico, # Velocità media del vento 
                    # "raffica": valore_numerico, # Velocità massima del vento (raffica) 
                    # "pressione_media": valore_numerico, # Pressione barometrica media 
                    # "precipitazioni": valore_numerico # Quantità totale di precipitazioni 
                    # }

                    try:
                        dom = prevDomani(
                            calcoli_giornalieri['umidita_massima'],
                            calcoli_giornalieri['umidita_media'],
                            calcoli_giornalieri['umidita_minima'],
                            calcoli_giornalieri['precipitazioni'],
                            calcoli_giornalieri['temp_media'],
                            calcoli_giornalieri['temp_massima'],
                            calcoli_giornalieri['temp_minima'],
                            calcoli_giornalieri['velocita_vento_media'],
                            calcoli_giornalieri['raffica'],
                            calcoli_giornalieri['pressione_media'],
                            stagione
                        )
                        dDom = prevDopoDomani(
                            calcoli_giornalieri['umidita_massima'],
                            calcoli_giornalieri['umidita_media'],
                            calcoli_giornalieri['umidita_minima'],
                            calcoli_giornalieri['precipitazioni'],
                            calcoli_giornalieri['temp_media'],
                            calcoli_giornalieri['temp_massima'],
                            calcoli_giornalieri['temp_minima'],
                            calcoli_giornalieri['velocita_vento_media'],
                            calcoli_giornalieri['raffica'],
                            calcoli_giornalieri['pressione_media'],
                            stagione
                        )
                        ddDom = prevDopoDopoDomani(
                            calcoli_giornalieri['umidita_massima'],
                            calcoli_giornalieri['umidita_media'],
                            calcoli_giornalieri['umidita_minima'],
                            calcoli_giornalieri['precipitazioni'],
                            calcoli_giornalieri['temp_media'],
                            calcoli_giornalieri['temp_massima'],
                            calcoli_giornalieri['temp_minima'],
                            calcoli_giornalieri['velocita_vento_media'],
                            calcoli_giornalieri['raffica'],
                            calcoli_giornalieri['pressione_media'],
                            stagione
                        )

                        #dalvataggio su code
                        with lock_prev_dom:
                            data_prev_dom.append(dom)
                        with lock_prev_dDom:
                            data_prev_dDom.append(dDom)
                        with lock_prev_ddDom:
                            data_prev_ddDom.append(ddDom)

                    except Exception as e:
                        print(f"Errore durante machine learning")
                        

                    #a questo punto, i dati sono già stati salvati sul db
                    #adesso machine learning!

                else:
                    print('dati non calcolati')

                
            except Exception as e:
                print(f"Errore nell'accesso al database: {e}")
                
        except Exception as e:
            print(f"Errore nel thread mezzanotte: {e}")
            shutdown_event.wait(timeout=60)

        
if __name__ == "__main__":
    # Registra i gestori di segnali
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Attendi un po' per far si che la seriale si possa attivare
    time.sleep(2)

    # Avvia thread per la raccolta dati
    riperimento_dati = threading.Thread(target=raccogli_dati)
    riperimento_dati.daemon = True
    riperimento_dati.start()

    # Avvia thread per il salvataggio dati
    archiviazione_dati = threading.Thread(target=salva_dati)
    archiviazione_dati.daemon = True
    archiviazione_dati.start()
    

    archiviazione_dati_mn = threading.Thread(target=mezzanotte)
    archiviazione_dati_mn.daemon = True
    archiviazione_dati_mn.start()

    # Avvia l'applicazione Flask
    try:
        app.run(debug=True, host="0.0.0.0", port=4444)  # togliere poi il debug
    except KeyboardInterrupt:
        print("Arresto del server richiesto...")
    finally:
        print("Arresto dell'applicazione...")
        shutdown_event.set()