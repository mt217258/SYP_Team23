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
from frontdisplay import frontend_display

def run_frontend(q_settings, q_commands, q_data, config):
    front = FrontEnd(q_settings, q_commands, q_data, config)
    front.start()
 

#### MAIN ####
def main():
    # Load configuration
    config = configparser.ConfigParser()
    config.read("config.ini")

    # Create queues for communication
    q_settings = multiprocessing.Queue()  # Frontend -> Backend (settings)
    q_commands = multiprocessing.Queue()  # Frontend -> Backend (commands)
    q_data = multiprocessing.Queue()      # Backend -> Frontend (raw data)

    # Initialize backend
    backend = BackEnd(q_settings, q_commands, q_data, config)
    
    # Start backend
    backend.start()
    
    # Start frontend display process (not daemon)
    frontend_process = multiprocessing.Process(
        target=run_frontend, 
        args=(q_settings, q_commands, q_data, config)
    )
    frontend_process.start()

    try:
        while True:
            time.sleep(1)
            if keyboard.is_pressed('ctrl+q'):
                print("Stopping....")
                break
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        # Cleanup
        backend.stop()
        #frontend_process.terminate()  # Properly terminate the process
        #frontend_process.join()
        print("All processes stopped. Exiting program.")

if __name__ == '__main__':
    main()