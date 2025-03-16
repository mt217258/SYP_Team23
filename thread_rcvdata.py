'''
Author:             Matthew McLaughlin
Contact:            mt217258@dal.ca
Description:        PyQT widget for displaying streamed data 
TODO List:          
'''

#### LIBRARIES ####
from PyQt5.QtCore import QObject, pyqtSignal
import pandas as pd

#### CLASSES ####
class Worker_DAQ(QObject): 
    sendData = pyqtSignal(list, list, list)
    
    data = pd.DataFrame(data={"Time":[], "sEMG_L":[], "sEMG_R":[]})
    num_samples_window = 50
            
    def run(self):
        count = 1
        while(True):
            print("Sampled: ", count)
            sample = pd.DataFrame(data={"Time":[count], "sEMG_L":[math.sin(2*math.pi*count/50)], "sEMG_R":[math.sin(2*math.pi*count/50+3)]})
            self.data = pd.concat([self.data, sample], ignore_index=True)
            count += 1
            self.windowData()
            self.sendData.emit(list(self.data["Time"]), list(self.data["sEMG_L"]), list(self.data["sEMG_R"]))
            #self.sendData.emit()
            print(self.data)
            time.sleep(0.5)
        
    def windowData(self):
        if len(self.data > self.num_samples_window):
            self.data = self.data[len(self.data)-self.num_samples_window:]

#### MAIN #### (just for testing independently of everything else)
def main():
    pass

if __name__ == '__main__':
    main()