#### LIBRARIES ####
# OFF THE SHELF #
import queue
import threading
import sys
import configparser

# CUSTOM #
from Backend.BackEnd import BackEnd
from FrontEnd.frontend import FrontEnd

#### CLASSES ####
    #### MAGIC METHODS ####
    #### MANGELED METHODS #### 
    #### MUGGLE METHODS #### 
    
    
#### MAIN #### (just for testing independently of everything else)
def main():
    #TODO - Start OpenSignals with lsl turned on, if possible
    #TODO - front and back end on different threads
    
    #TODO - verify if correct way to impliment queues
    #see: https://docs.python.org/3/library/queue.html
    q_settings = queue.Queue()
    q_commands = queue.Queue()
    q_data = queue.Queue()
    
    back = BackEnd(q_settings, q_commands, q_data)
    front = FrontEnd(q_settings, q_commands, q_data)
    
    back.start()
    front.start()
    
    #TODO - add code to close back & front when GUI is closed
    #back.stop()
    #front.stop()

if __name__ == '__main__':
    main()