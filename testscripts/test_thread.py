import logging
import threading
import time
import multiprocessing

def make_thread_sensor( side:str, sensorType:str, MAC:str, 
                        q_commandIn:multiprocessing.Queue, 
                        q_dataOut:multiprocessing.Queue):
    print("Inputs are: ", side, sensorType, MAC, q_commandIn, q_dataOut)
    
if __name__ == "__main__":
    side = "L"
    sensorType = "sEMG"
    MAC = "58:8E:81:A2:48:D3"
    q_commandIn = multiprocessing.Queue()
    q_dataOut = multiprocessing.Queue()
    
    print("Inputs are: ", side, sensorType, MAC, q_commandIn, q_dataOut)
    
    thread_sensor_test = threading.Thread(
        target=make_thread_sensor, 
        #kwargs={'side':side}, 
        args=(side, sensorType, MAC, q_commandIn, q_dataOut),
        daemon=True)
    
    
    thread_sensor_test.start()
    
    time.sleep(5)
    