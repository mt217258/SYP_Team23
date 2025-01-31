'''
Author:             
Contact:            
Description:        
TODO List:   

Data format: data = pd.DataFrame(data={"Time":[], "sEMG_L":[], "sEMG_R":[]})
       
'''

#### LIBRARIES ####
# OFF THE SHELF #
import queue
import pandas as pd
from pylsl import * #TODO: update with just the stuff we need
# CUSTOM #

#### CLASSES ####
class BackEnd():
    #### MAGIC METHODS ####
    def __init__(self, q_settings, q_commands, q_data):
        self.q_settings = q_settings
        self.q_commands = q_commands
        self.q_data = q_data
    
    #### MANGELED METHODS #### 
    #### MUGGLE METHODS #### 
    def start(self):
        pass
    
    def stop(self):
        pass

#### MAIN #### (just for testing independently of everything else)
def main():
    pass

if __name__ == '__main__':
    main()