'''
Author:             Matthew McLaughlin
Contact:            mt217258@dal.ca
Description:        PyQT widget for displaying streamed data 
TODO List:          
'''

#### LIBRARIES ####
from PyQt5.QtCore import QObject, pyqtSignal
import pandas as pd
import math
import time
import multiprocessing
from common import data

#### CLASSES ####
class Worker_DAQ(QObject):
    sendData = pyqtSignal(pd.DataFrame) #must be outside init, don't know why, just leave it there
    
    def __init__(self, q_data):
        super(Worker_DAQ, self).__init__()
        self.data_queue = q_data
        #self.data = data
        
    #    def run(self):
    #        while(True):
    #            pass
     
    #sendData = pyqtSignal(list, list, list)
    
    #data = pd.DataFrame(data={"Time":[], "sEMG_L":[], "sEMG_R":[]})
    num_samples_window = 50
    
    def run(self):
        while(True):
            #waiting until there is seomthing in queue
            while self.data_queue.empty():
                pass 
            
            #pop queue and pass it through signal to front end
            sample = self.data_queue.get()
            self.sendData.emit(sample) 
            
            
    def test_run(self):
        count = 1
        while(True):
            #print("Sampled: ", count)
            sample = pd.DataFrame(data={"Time":[count], "raw-sEMG_L":[math.sin(2*math.pi*count/50)], "raw-sEMG_R":[math.sin(2*math.pi*count/50+3)]})
            #print("Sample: ", sample)
            #self.data = pd.concat([self.data, sample], ignore_index=True)
            #print(self.data)
            count += 1
            #self.windowData()
            #self.sendData.emit(list(self.data["Time"]), list(self.data["sEMG_L"]), list(self.data["sEMG_R"]))
            print("Backend sending: ", sample)
            self.sendData.emit(sample)
            
            #self.sendData.emit()
            #print(self.data)
            time.sleep(2)
        
    def windowData(self):
        if len(self.data > self.num_samples_window):
            self.data = self.data[len(self.data)-self.num_samples_window:]
    

#### MAIN #### (just for testing independently of everything else)
def main():
    pass

if __name__ == '__main__':
    main()