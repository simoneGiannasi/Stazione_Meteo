import serial
import time
from .decode_LOOP import decode_loop_packet
from .conversione import convert_data
serialPort='COM7' #porta seriale per la comunicazione con la console davis vantage pro2

def configure_serial_port(port, baudrate=19200, timeout=2):
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=timeout
        )
        return ser
    except serial.SerialException as e:
        print(f"Errore durante la configurazione della porta seriale: {e}")
        return None

def send_request(ser, command):
    if ser is not None:
        try:
            ser.write(f"{command}\n".encode('ascii'))
            time.sleep(0.5) #attendo mezzo secondo per far si che si instauri la connessione
            response = ser.read(ser.in_waiting or 1)
            return response
        except serial.SerialException as e:
            print(f"Errore durante l'invio del comando: {e}")
            return None
    else:
        print("Porta seriale non configurata correttamente.")
        return None

def dati():
    ser = configure_serial_port(serialPort)
    if ser:
        response = send_request(ser, 'LOOP')
        if response:
            try:
                res = decode_loop_packet(response)
                risposta=convert_data(res)
                #print(risposta)
                print("Dati convertiti con successo")
                return risposta
            except ValueError as e:
                print(e)
                return 0
        else:
            print("Nessuna risposta ricevuta dal dispositivo.")
    else:
        print("Dispositivo non collegato o errore nella configurazione della porta seriale.")


# dati()
#print('fine del programma')