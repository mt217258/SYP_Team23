'''
Author:             Matthew McLaughlin
Contact:            mt217258@dal.ca
Description:        
TODO List:          
'''

#### LIBRARIES ####
# OFF THE SHELF #
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QTabWidget, QWidget, QVBoxLayout
# CUSTOM #
from widget_datastream import WIDGET_datastream

#### CLASSES ####
class MainWindow(QMainWindow):
    #### MAGIC METHODS ####
    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        uic.loadUi('../ui_files/mainwindow.ui', self)
        
        self.__initVars()
        
        self.__linkActions()
        self.__linkWidgets()
        self.__linkWindows()  
      
        self.__creatView()
      
    #### MANGELED METHODS ####  
    def __initVars(self):
        self.numTabs = 4
     
    def __linkActions(self):
        pass
    
    def __linkWidgets(self):
        pass
      
    def __linkWindows(self):
        pass 
        
    def __creatView(self):
        self.widgetMain = QWidget()
        
        self.widget_tabs = Tabs(self.numTabs)
        #TODO self.widget_controls = Controls()
    
        self.widgetMain.layout = QVBoxLayout(self) #set layout of view, verticle
        self.widgetMain.layout.addWidget(self.widget_tabs) #add widgets to layout
        #self.widgetMain.layout.addWidget(self.widget_controls)
        self.widgetMain.setLayout(self.widgetMain.layout) #apply layout
        self.setCentralWidget(self.widgetMain) #set main widget as central
        
    #### MUGGLE METHODS #### 
           
class Tabs(QTabWidget):
    #### MAGIC METHODS ####
    def __init__(self, numTabs):
        super(QTabWidget, self).__init__()
        self.numTabs = numTabs
        self.list_tabs = []
        
        self.__createTabs()

    #### MANGELED METHODS #### 
    def __createTabs(self):
        tabname = "View {}"
        for i in range(0, self.numTabs):
            tab = Tab()
            self.list_tabs.append(tab)
            self.addTab(tab, tabname.format(i+1)) 
            
    #### MUGGLE METHODS ####   

class Tab(QWidget):
    #### MAGIC METHODS ####
    def __init__(self, parent=None):
        super(QWidget, self).__init__()
        self.listPlots = []
        
        self.layout = QVBoxLayout(self)
        self.__create_plots()
        self.setLayout(self.layout)
        
    #### MANGELED METHODS #### 
    def __create_plots(self):
        for i in range(0,3):
            self.listPlots.append(WIDGET_datastream())
            self.layout.addWidget(self.listPlots[i])
            
    #### MUGGLE METHODS #### 

#### MAIN #### (just for testing independently of everything else)
def main():
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec()) #program loops forever

if __name__ == '__main__':
    main()