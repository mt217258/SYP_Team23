#### LIBRARIES ####
from PyQt5 import QtWidgets, uic
from pyqtgraph import PlotWidget

from widget_datastream import WIDGET_datastream 

from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QWidget

import pandas as pd
import math
import time
import sys

class Worker_DAQ(QObject): 
    sendData = pyqtSignal(list, list, list)
    
    data = pd.DataFrame(data={"Time":[], "sEMG_L":[], "sEMG_R":[]})
    num_samples_window = 50
    
    '''
    def __init__(self, parent):
        #super().__init__(parent)
        self.data = pd.DataFrame(data={"Time":[], "sEMG_L":[], "sEMG_R":[]})
        self.num_samples_window = 50
        self.rcv_data()    
    '''
        
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
    
class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.graph = WIDGET_datastream(self)
        self.setCentralWidget(self.graph)
        self.__linkThreads()
        
    def __linkThreads(self):
        self.thread_DAQ = QThread()
        self.worker_DAQ = Worker_DAQ()
        self.worker_DAQ.moveToThread(self.thread_DAQ)
        
        self.thread_DAQ.started.connect(self.worker_DAQ.run)
        #self.worker.finished.connect(self.thread.quit)
        #self.worker.finished.connect(self.worker.deleteLater)
        #self.thread.finished.connect(self.thread.deleteLater)
        self.worker_DAQ.sendData.connect(self.get_data)
        
        self.thread_DAQ.start()
   
    def get_data(self, sig_time, sig_l, sig_r): #https://github.com/iskandarputra/Real-Time-Py-Serial-Plotter/blob/main/README.md
        print("Data rcvd")
        self.graph.updateGraph(sig_time, sig_l, sig_r)
 
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = Window() # Create an instance of our class
    window.show()
    sys.exit(app.exec()) #program loops forever
    
if __name__ == '__main__':
    main()
