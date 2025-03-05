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
from PyQt5.QtWidgets import QMainWindow, QApplication, QTabWidget, QWidget, QVBoxLayout, QAction
import configparser

# CUSTOM #
#from SYP_Widgets import WIDGET_datastream
from widget_datastream import WIDGET_datastream
from widget_controls import WIDGET_controls 
from window_settings import WINDOW_settings
from PyQt5.Qt5.qml.Qt.labs import settings

#### CLASSES ####
class WINDOW_main(QMainWindow):
    #### MAGIC METHODS ####
    def __init__(self, settings, parent=None):
        super(WINDOW_main, self).__init__()
        uic.loadUi('ui_files/mainwindow.ui', self)
        
        self.__initVars()
        
        self.__linkActions()
        self.__linkWidgets()
        self.__linkWindows()  
      
        self.__creatView()
      
    #### MANGELED METHODS ####  
    def __openSettings(self):
        self.window_settings.open()
        
    def __initVars(self):
        #TODO - load settings
        #TODO - if fail, message, offer option for default values
        self.numTabs = 4
        self.settings = settings #configParser object
        
    def __linkActions(self):
        ### SETTINGS ###
        self.ActionSettings = self.findChild(QAction, 'actionSettings')
        self.ActionSettings.triggered.connect(self.__openSettings)
    
    def __linkWidgets(self):
        pass
      
    def __linkWindows(self):
        self.window_settings = WINDOW_settings(self.settings)
        #self.window_settings.open() 
        
    def __creatView(self):
        self.widgetMain = QWidget()
        
        self.widget_tabs = Tabs(self.numTabs)
        self.widget_controls = WIDGET_controls()
        #TODO self.widget_controls = Controls()
    
        self.widgetMain.layout = QVBoxLayout(self) #set layout of view, verticle
        self.widgetMain.layout.addWidget(self.widget_tabs) #add widgets to layout
        self.widgetMain.layout.addWidget(self.widget_controls)
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
    
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    mainwindow = WINDOW_main(settings=config)
    mainwindow.show()
    sys.exit(app.exec()) #program loops forever

if __name__ == '__main__':
    main()