#### LIBRARIES ####
# OFF THE SHELF #
import queue


# CUSTOM #
from backend import BackEnd
from frontend import FrontEnd


#### CLASSES ####
    #### MAGIC METHODS ####
    #### MANGELED METHODS #### 
    #### MUGGLE METHODS #### 
    
    
#### MAIN #### (just for testing independently of everything else)
def main():
    #TODO - Start OpenSignals with lsl turned on, if possible
    
    #TODO - verify if correct way to impliment queues
    #see: https://docs.python.org/3/library/queue.html
    q_settings = queue.Queue()
    q_commands = queue.Queue()
    q_data = queue.Queue()
    
    back = BackEnd(q_settings, q_commands, q_data)
    front = FrontEnd(q_settings, q_commands, q_data)
    
    back.start()
    front.start()
    
    #TODO - add code to end back & front when GUI is closed

if __name__ == '__main__':
    main()