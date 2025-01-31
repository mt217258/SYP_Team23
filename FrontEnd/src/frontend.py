'''
Author:             Matthew McLaughlin
Contact:            mt217258@dal.ca
Description:        PyQT widget for displaying streamed data 
TODO List:          
'''

#### LIBRARIES ####
# OFF THE SHELF #

# CUSTOM #
from thread_rcvdata import Worker_DAQ
from widget_datastream import WIDGET_datastream
from mainwindow import MainWindow

#### CLASSES ####
class FrontEnd():
    #### MAGIC METHODS ####
    def __init__(self):
        self.mainwindow = MainWindow()
    
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