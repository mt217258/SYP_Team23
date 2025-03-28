#### LIBRARIES ####
# OFF THE SHELF #
import multiprocessing
import threading
import configparser
import time
import keyboard

# CUSTOM #
from backend import BackEnd
from frontend import FrontEnd


#### MAIN ####
def main():
    # Load configuration
    config = configparser.ConfigParser()
    config.read("config.ini")

    # Create queues for communication
    q_settings = multiprocessing.Queue()  # Frontend -> Backend (settings)
    q_commands = multiprocessing.Queue()  # Frontend -> Backend (commands)
    q_data = multiprocessing.Queue()      # Backend -> Frontend (raw data)

    # Initialize backend and frontend
    frontend = FrontEnd(q_settings, q_commands, q_data, config)
    backend = BackEnd(q_settings, q_commands, q_data, config)

    # Start processes
    
    backend.start()
    frontend.start()
    
    try:
        while True:
            time.sleep(1)
            if keyboard.is_pressed('ctrl+q'):
                print("Stopping....")
                break
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        backend.stop()
        frontend_thread.join()
        print("All threads stopped. Exiting program.")

if __name__ == '__main__':
    main()