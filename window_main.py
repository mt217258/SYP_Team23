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
import queue

# CUSTOM #
#from SYP_Widgets import WIDGET_datastream
from widget_datastream import WIDGET_datastream
from widget_controls import WIDGET_controls 
from window_settings import WINDOW_settings
from PyQt5.Qt5.qml.Qt.labs import settings

#### CLASSES ####
class WINDOW_main(QMainWindow):
    #### MAGIC METHODS ####
    def __init__(self, settings:configparser.ConfigParser, Q_settings, filepath, parent=None):
        super(WINDOW_main, self).__init__()
        uic.loadUi('ui_files/mainwindow.ui', self)
        
        self.settings = settings #configParser object
        self.q_settings = Q_settings
        self.filepath = filepath
        #print("Settings type in main is: " , type(self.settings))
        
        self.numTabs = 4
        
        self.__linkActions()
        self.__linkWidgets()
        self.__linkWindows()  
      
        self.__creatView()
        #self.__initViews()
        self.__loadViews()
<<<<<<< Updated upstream
<<<<<<< Updated upstream
        if not self.layout():
            self.setLayout(QVBoxLayout())
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
      
    #### MANGELED METHODS ####  
    def __openSettings(self):
        self.window_settings.open()
        
    def __initViews(self):
        self.__loadViews()
        
    def __loadViews(self):
        setting_name_template = "t{tab_num:d}p{plot_num:d}"
        for tab in self.widget_tabs.list_tabs:
            for plot in tab.listPlots:
                tab_num= tab.tab_number + 1 #index starts at 0, names at 1
                plot_num= plot.plot_num + 1
                
                setting_name = setting_name_template.format(tab_num=tab_num,plot_num=plot_num)
                setting = self.settings['Views'][setting_name]
                cb_index = plot.combobox.findText(setting)
                plot.combobox.setCurrentIndex(cb_index)
        
    def __linkActions(self):
        ### SETTINGS ###
        self.ActionSettings = self.findChild(QAction, 'actionSettings')
        self.ActionSettings.triggered.connect(self.__openSettings)
        
        self.ActionViews = self.findChild(QAction, 'actionSave_View_Settings')
        self.ActionViews.triggered.connect(self.__saveViews)
    
    def __saveViews(self):
        setting_name_template = "t{tab_num:d}p{plot_num:d}"
        for tab in self.widget_tabs.list_tabs:
            for plot in tab.listPlots:
                tab_num= tab.tab_number + 1 #index starts at 0, names at 1
                plot_num= plot.plot_num + 1
                
                setting_name = setting_name_template.format(tab_num=tab_num,plot_num=plot_num)
                print(setting_name)
                self.settings['Views'][setting_name] = plot.combobox.currentText()
        
        with open(self.filepath, 'w') as configfile: #write file
            print("Start: Writing settings to config")
            self.settings.write(configfile)
            print("End: Writing settings to config")
        
    def __linkWidgets(self):
        pass
      
    def __linkWindows(self):
        self.window_settings = WINDOW_settings(self.settings, self.q_settings, 'config.ini')
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
            tab = Tab(i)
            self.list_tabs.append(tab)
            self.addTab(tab, tabname.format(i+1)) 
            
    #### MUGGLE METHODS ####   

class Tab(QWidget):
    #### MAGIC METHODS ####
    def __init__(self, number, parent=None):
        super(QWidget, self).__init__()
        self.tab_number = number
        self.listPlots = []
        
        self.layout = QVBoxLayout(self)
        self.__create_plots()
        self.setLayout(self.layout)
        
    #### MANGELED METHODS #### 
    def __create_plots(self):
        for i in range(0,4):
            self.listPlots.append(WIDGET_datastream(i))
            self.layout.addWidget(self.listPlots[i])
            
    #### MUGGLE METHODS #### 

#### MAIN #### (just for testing independently of everything else)
def main():
    app = QApplication(sys.argv)
    
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    q_settings = queue.Queue()
    
    mainwindow = WINDOW_main(settings=config, Q_settings=q_settings, filepath="config.ini")
    mainwindow.show()
    sys.exit(app.exec()) #program loops forever

if __name__ == '__main__':
    main()