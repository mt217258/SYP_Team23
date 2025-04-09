import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QTabWidget, QWidget, QVBoxLayout, QAction
import configparser
import queue
from widget_datastream import WIDGET_datastream
from widget_controls import WIDGET_controls 
from window_settings import WINDOW_settings

class WINDOW_main(QMainWindow):
    def __init__(self, settings:configparser.ConfigParser, Q_settings, filepath, parent=None):
        super(WINDOW_main, self).__init__(parent)
        uic.loadUi('ui_files/mainwindow.ui', self)
        self.settings = settings
        self.q_settings = Q_settings
        self.filepath = filepath
        self.numTabs = 4

        self.__linkActions()
        self.__linkWidgets()
        self.__linkWindows()  
        self.__createView()
        self.__loadViews()

    def __openSettings(self):
        self.window_settings.open()
        
    def __loadViews(self):
        setting_name_template = "t{tab_num:d}p{plot_num:d}"
        for tab in self.widget_tabs.list_tabs:
            for plot in tab.listPlots:
                tab_num = tab.tab_number + 1
                plot_num = plot.plot_num + 1
                setting_name = setting_name_template.format(tab_num=tab_num, plot_num=plot_num)
                setting = self.settings['Views'][setting_name]
                cb_index = plot.combobox.findText(setting)
                plot.combobox.setCurrentIndex(cb_index)
        
    def __linkActions(self):
        self.ActionSettings = self.findChild(QAction, 'actionSettings')
        self.ActionSettings.triggered.connect(self.__openSettings)
        
        self.ActionViews = self.findChild(QAction, 'actionSave_View_Settings')
        self.ActionViews.triggered.connect(self.__saveViews)
    
    def __saveViews(self):
        setting_name_template = "t{tab_num:d}p{plot_num:d}"
        for tab in self.widget_tabs.list_tabs:
            for plot in tab.listPlots:
                tab_num = tab.tab_number + 1
                plot_num = plot.plot_num + 1
                setting_name = setting_name_template.format(tab_num=tab_num, plot_num=plot_num)
                self.settings['Views'][setting_name] = plot.combobox.currentText()
        with open(self.filepath, 'w') as configfile:
            self.settings.write(configfile)
        
    def __linkWidgets(self):
        pass
      
    def __linkWindows(self):
        self.window_settings = WINDOW_settings(self.settings, self.q_settings, self.filepath)
        
    def __createView(self):
        self.widgetMain = QWidget()
        self.widget_tabs = Tabs(self.numTabs)
        self.widget_controls = WIDGET_controls()
        layout = QVBoxLayout()
        layout.addWidget(self.widget_tabs)
        layout.addWidget(self.widget_controls)
        self.widgetMain.setLayout(layout)
        self.setCentralWidget(self.widgetMain)

class Tabs(QTabWidget):
    def __init__(self, numTabs):
        super(Tabs, self).__init__()
        self.numTabs = numTabs
        self.list_tabs = []
        self.__createTabs()

    def __createTabs(self):
        tabname = "View {}"
        for i in range(self.numTabs):
            tab = Tab(i)
            self.list_tabs.append(tab)
            self.addTab(tab, tabname.format(i+1))

class Tab(QWidget):
    def __init__(self, number, parent=None):
        super(Tab, self).__init__(parent)
        self.tab_number = number
        self.listPlots = []
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.__create_plots()

    def __create_plots(self):
        for i in range(4):
            plot_widget = WIDGET_datastream(i)
            self.listPlots.append(plot_widget)
            self.layout().addWidget(plot_widget)

def main():
    app = QApplication(sys.argv)
    config = configparser.ConfigParser()
    config.read("config.ini")
    q_settings = queue.Queue()
    mainwindow = WINDOW_main(settings=config, Q_settings=q_settings, filepath="config.ini")
    mainwindow.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
