import pickle
import pandas as pd

def prevDomani(umMax, umMed, umMin, prec, tempMed, tempMax, tempMin, velMed, velRaff, press, stag):
    with open("./machine_learning/Modelli/PrecDom.pkl", "rb") as file:
        precDom = pickle.load(file) 
    with open("./machine_learning/Modelli/PressDom.pkl", "rb") as file:
        pressDom = pickle.load(file) 
    with open("./machine_learning/Modelli/TempDom.pkl", "rb") as file:
        tempDom = pickle.load(file) 
    with open("./machine_learning/Modelli/UmidDom.pkl", "rb") as file:
        umidDom = pickle.load(file) 
    with open("./machine_learning/Modelli/VentoMedDom.pkl", "rb") as file:
        ventoMedDom = pickle.load(file) 
    with open("./machine_learning/Modelli/VentoRaffDom.pkl", "rb") as file:
        ventoRaffDom = pickle.load(file)

    feature_names = ['Umidità massima (%)', 'Umidità media (%)', 'Umidità minima (%)', 
                      'Precipitazione (mm)', 'Temperatura media (°C)', 'Temperatura massima (°C)', 
                     'Temperatura minima (°C)', 'Velocità media (m/s)', 
                     'Velocità raffica (m/s)', 'Valore pressione', 'Stagione']

    X_input = pd.DataFrame([[umMax, umMed, umMin, prec, tempMed, tempMax, tempMin, velMed, velRaff, press, stag]], 
                           columns=feature_names)
    #xinput.drop(columns=[...])
    pressionePredetta = pressDom.predict(X_input) 
    #print(pressionePredetta)
    temperaturaPredetta = tempDom.predict(X_input) 
    #print(temperaturaPredetta)
    umiditaPredetta = umidDom.predict(X_input.drop(columns=['Stagione'])) 
    #print(umiditaPredetta)
    #prec, manca tempMed, stag e press
    precipitazionePredetta = precDom.predict(X_input.drop(columns=['Temperatura media (°C)', 'Valore pressione', 'Stagione']))  
    #print(precipitazionePredetta)
    #velocità media, manca stagione e tempMed
    velocitaMediaPredetta = ventoMedDom.predict(X_input.drop(columns=['Temperatura media (°C)', 'Stagione'])) 
    #print(velocitaMediaPredetta)
    #velocità raffica, manca stagione e tempMed
    velocitaRafficaPredetta = ventoRaffDom.predict(X_input.drop(columns=['Temperatura media (°C)', 'Stagione'])) 
    #print(velocitaRafficaPredetta)
    return {'pressione' : pressionePredetta, "temperatura":temperaturaPredetta, "umidità":umiditaPredetta, "precipitazione":precipitazionePredetta, "velocità media":velocitaMediaPredetta, "velocità raffica":velocitaRafficaPredetta}  

def prevDopoDomani(umMax, umMed, umMin, prec, tempMed, tempMax, tempMin, velMed, velRaff, press, stag):
    with open("./machine_learning/Modelli/PrecDopDom.pkl", "rb") as file:
        precDopDom = pickle.load(file)
    with open("./machine_learning/Modelli/PressDopDom.pkl", "rb") as file:
        pressDopDom = pickle.load(file) 
    with open("./machine_learning/Modelli/TempDopDom.pkl", "rb") as file:
        tempDopDom = pickle.load(file) 
    with open("./machine_learning/Modelli/UmidDopDom.pkl", "rb") as file:
        umidDopDom = pickle.load(file) 
    with open("./machine_learning/Modelli/VentoMedDopDom.pkl", "rb") as file:
        ventoMedDopDom = pickle.load(file)
    with open("./machine_learning/Modelli/VentoRaffDopDom.pkl", "rb") as file:
        ventoRaffDopDom = pickle.load(file)  

    feature_names = ['Umidità massima (%)', 'Umidità media (%)', 'Umidità minima (%)', 
                      'Precipitazione (mm)', 'Temperatura media (°C)', 'Temperatura massima (°C)', 
                     'Temperatura minima (°C)', 'Velocità media (m/s)', 
                     'Velocità raffica (m/s)', 'Valore pressione', 'Stagione']

    X_input = pd.DataFrame([[umMax, umMed, umMin, prec, tempMed, tempMax, tempMin, velMed, velRaff, press, stag]], 
                           columns=feature_names)
    #xinput.drop(columns=[...])
    pressionePredetta = pressDopDom.predict(X_input) 
    #print(pressionePredetta)
    temperaturaPredetta = tempDopDom.predict(X_input) 
    #print(temperaturaPredetta)
    umiditaPredetta = umidDopDom.predict(X_input.drop(columns=['Stagione'])) 
    #print(umiditaPredetta)
    #prec, manca tempMed, stag e press
    precipitazionePredetta = precDopDom.predict(X_input.drop(columns=['Temperatura media (°C)', 'Valore pressione', 'Stagione']))  
    #print(precipitazionePredetta)
    #velocità media, manca stagione e tempMed
    velocitaMediaPredetta = ventoMedDopDom.predict(X_input.drop(columns=['Temperatura media (°C)', 'Stagione'])) 
    #print(velocitaMediaPredetta)
    #velocità raffica, manca stagione e tempMed
    velocitaRafficaPredetta = ventoRaffDopDom.predict(X_input.drop(columns=['Temperatura media (°C)', 'Stagione'])) 
    #print(velocitaRafficaPredetta)
    return {'pressione' : pressionePredetta, "temperatura":temperaturaPredetta, "umidità":umiditaPredetta, "precipitazione":precipitazionePredetta, "velocità media":velocitaMediaPredetta, "velocità raffica":velocitaRafficaPredetta}  
 
def prevDopoDopoDomani(umMax, umMed, umMin, prec, tempMed, tempMax, tempMin, velMed, velRaff, press, stag):
    with open("./machine_learning/Modelli/PrecDopDopDom.pkl", "rb") as file:
        precDopDopDom = pickle.load(file) 
    with open("./machine_learning/Modelli/PressDopDopDom.pkl", "rb") as file:
        pressDopDopDom = pickle.load(file) 
    with open("./machine_learning/Modelli/TempDopDopDom.pkl", "rb") as file:
        tempDopDopDom = pickle.load(file) 
    with open("./machine_learning/Modelli/UmidDopDopDom.pkl", "rb") as file:
        umidDopDopDom = pickle.load(file) 
    with open("./machine_learning/Modelli/VentoMedDopDopDom.pkl", "rb") as file:
        ventoMedDopDopDom = pickle.load(file)
    with open("./machine_learning/Modelli/VentoRaffDopDopDom.pkl", "rb") as file:
        ventoRaffDopDopDom = pickle.load(file) 

    feature_names = ['Umidità massima (%)', 'Umidità media (%)', 'Umidità minima (%)', 
                      'Precipitazione (mm)', 'Temperatura media (°C)', 'Temperatura massima (°C)', 
                     'Temperatura minima (°C)', 'Velocità media (m/s)', 
                     'Velocità raffica (m/s)', 'Valore pressione', 'Stagione']

    X_input = pd.DataFrame([[umMax, umMed, umMin, prec, tempMed, tempMax, tempMin, velMed, velRaff, press, stag]], 
                           columns=feature_names)
    #xinput.drop(columns=[...])
    pressionePredetta = pressDopDopDom.predict(X_input) 
    #print(pressionePredetta)
    temperaturaPredetta = tempDopDopDom.predict(X_input) 
    #print(temperaturaPredetta)
    umiditaPredetta = umidDopDopDom.predict(X_input.drop(columns=['Stagione'])) 
    #print(umiditaPredetta)
    #prec, manca tempMed, stag e press
    precipitazionePredetta = precDopDopDom.predict(X_input.drop(columns=['Temperatura media (°C)', 'Valore pressione', 'Stagione']))  
    #print(precipitazionePredetta)
    #velocità media, manca stagione e tempMed
    velocitaMediaPredetta = ventoMedDopDopDom.predict(X_input.drop(columns=['Temperatura media (°C)', 'Stagione'])) 
    #print(velocitaMediaPredetta)
    #velocità raffica, manca stagione e tempMed
    velocitaRafficaPredetta = ventoRaffDopDopDom.predict(X_input.drop(columns=['Temperatura media (°C)', 'Stagione'])) 
    #print(velocitaRafficaPredetta)
    return {'pressione' : pressionePredetta, "temperatura":temperaturaPredetta, "umidità":umiditaPredetta, "precipitazione":precipitazionePredetta, "velocità media":velocitaMediaPredetta, "velocità raffica":velocitaRafficaPredetta}  


# with open("./Modelli/PressDom.pkl", "rb") as file:
#         pressDom = pickle.load(file)

# print(prevDomani(100, 92, 68, 2.4, 0.1, 2.3, -1.3, 0.9, 5.9, 942.6, 0))
# print(prevDopoDomani(100, 92, 68, 2.4, 0.1, 2.3, -1.3, 0.9, 5.9, 942.6, 0))
# print(prevDopoDopoDomani(100, 92, 68, 2.4, 0.1, 2.3, -1.3, 0.9, 5.9, 942.6, 0))


