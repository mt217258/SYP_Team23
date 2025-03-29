'''
Author:             Matthew McLaughlin
Contact:            mt217258@dal.ca
Description:        
TODO List:          
'''

#### LIBRARIES ####
# OFF THE SHELF #
import queue
import pandas as pd
import configparser
from PyQt5 import QtWidgets
import sys
<<<<<<< Updated upstream
import numpy as np
=======

>>>>>>> Stashed changes
import multiprocessing
from PyQt5.QtCore import QObject, QThread, pyqtSignal
#from PyQt5.QtWidgets import QApplication

# CUSTOM #
from window_main import WINDOW_main
from thread_rcvdata import Worker_DAQ
from common import dataselectmapping, data
#from future.backports.test.pystone import FALSE

#### CLASSES ####
class FrontEnd():
    #### MAGIC METHODS ####
    def __init__(self, q_settings, q_commands, q_data, config):
        self.q_settings = q_settings
        self.q_commands = q_commands
        self.q_data = q_data
        self.settings = config
        
        #self.mode = "Pause" #"Stream", "Pause", "Stop"
        self.isStreaming = False
        self.isRecording = False
        
        self.window_width = 30 #in mins
        self.window_offset = 0 #in int from 0 -> 100
        
        self.app = QtWidgets.QApplication(sys.argv)
        self.data = data  
        
        self.mainwindow = WINDOW_main(settings=config, Q_settings=q_settings, filepath="config.ini")
        self.__linkThreads()
        self.__linkControlSignals()
<<<<<<< Updated upstream

        from PyQt5.QtCore import QTimer

        # Timer for throttling plot updates
        self.plot_update_timer = QTimer()
        self.plot_update_timer.timeout.connect(self._throttled_updateGrpahs)
        self.plot_update_timer.start(100)

        # Buffer for accumulated data between timer ticks
        self.pending_update = False
        
    #### MANGELED METHODS ####

    def _throttled_updateGrpahs(self):
        if self.pending_update and self.isStreaming:
            self.updateGraphs()
            self.pending_update = False

=======
        
    #### MANGELED METHODS ####
>>>>>>> Stashed changes
    def __linkControlSignals(self):
        self.mainwindow.widget_controls.signal_streaming.connect(self.__updateStreaming)
        self.mainwindow.widget_controls.signal_recordname.connect(self.__updateFilename)
        self.mainwindow.widget_controls.signal_recording.connect(self.__updateRecording)
        self.mainwindow.widget_controls.signal_width.connect(self.__updateWindowWidth)
        self.mainwindow.widget_controls.signal_offset.connect(self.__updateWindowOffset)
    
    def __updateStreaming(self, onoff):
        print("FE: Streaming update to: ", onoff)
        if not self.isStreaming and onoff: #streaming turned on
            pass
        if not self.isStreaming and not onoff: #streaming paused
            self.index_lastSampleBeforePause = len(self.data)
        self.isStreaming = onoff
    
    def __updateFilename(self, filename):
        self.filename = filename
    
    def __updateRecording(self, onoff):
        if not self.isRecording:
            self.q_commands.put("Record:".format(name=self.filename)) #
        else:
            self.q_commands.put("Stop") #stop recording & streaming
        self.isStreaming = onoff
    
    def __updateWindowWidth(self, width):
        print("FE: Window width updated to: ", width)
        self.window_width = width
        self.updateGraphs()
    
    def __updateWindowOffset(self, offset):
        print("FE: Window offset updated to: ", offset)
        self.window_offset = offset
        self.updateGraphs() 
    
    def __linkThreads(self):
        self.thread_DAQ = QThread() #create thread
        self.worker_DAQ = Worker_DAQ(self.q_data) #create object to run in thread
        self.worker_DAQ.moveToThread(self.thread_DAQ) #move object to thread
        
        self.thread_DAQ.started.connect(self.worker_DAQ.run) #when thread started, run worker's run()
        #self.thread_DAQ.started.connect(self.worker_DAQ.test_run) #used for testing

        self.worker_DAQ.sendData.connect(self.__getData) #link pyqt signals
        
        self.thread_DAQ.start()
        
<<<<<<< Updated upstream
    def __getData(self, batch_df):
        try:
            print("\n" + "="*50)
            print("📦 ENHANCED BATCH PROCESSING")
            print("="*50)

            # =====================
            # Initial Validation
            # =====================
            if batch_df.empty:
                print("⚠️ Empty batch received")
                return

            print(f"\n📊 Batch Metadata:")
            print(f"- Columns: {list(batch_df.columns)}")
            print(f"- Size: {len(batch_df)} rows")
            print(f"- Pre-concat buffer: {len(self.data) if hasattr(self, 'data') else 0} rows")

            # =====================
            # Data Processing
            # =====================
            # Flatten data if needed (handles both single and multi-row cases)
            batch_df = batch_df.map(lambda x: x.iloc[0] if hasattr(x, 'iloc') else x, na_action='ignore')
        
            # Convert numeric columns
            numeric_cols = [col for col in batch_df.columns if col not in ['Time', 'nSeq']]
            print(f"\n🔢 Converting columns: {numeric_cols}")
            batch_df[numeric_cols] = batch_df[numeric_cols].apply(pd.to_numeric, errors='coerce')

            # Handle missing/invalid data
            nan_report = batch_df.isna().sum()
            if nan_report.any():
                print("\n⚠️ NaN Report:")
                print(nan_report.to_string())
                clean_df = batch_df.dropna()
                dropped = len(batch_df) - len(clean_df)
                if dropped > 0:
                    print(f"\n♻️ Removed {dropped} invalid rows")
            else:
                clean_df = batch_df.copy()
                print("\n✅ No NaN values found")

            # =====================
            # Timestamp Handling
            # =====================
            # Initialize buffer if needed
            if not hasattr(self, 'data'):
                self.data = pd.DataFrame(columns=clean_df.columns)
                self.synthetic_timestamp = time.time()
                print("🆕 Initialized new data buffer")

            # Generate synthetic timestamps if needed
            if len(clean_df) > 0:
                if 'Time' not in clean_df.columns or clean_df['Time'].isnull().all():
                    print("⏱️ Generating synthetic timestamps (400Hz)")
                    start_time = self.synthetic_timestamp
                    clean_df['Time'] = [start_time + i*(1/400) for i in range(len(clean_df))]
                    self.synthetic_timestamp = clean_df['Time'].iloc[-1] + (1/400)
                else:
                    self.synthetic_timestamp = clean_df['Time'].iloc[-1] + (1/400)

            # =====================
            # Buffer Management
            # =====================
            # Add to buffer with progress tracking
            before = len(self.data)
            self.data = pd.concat([self.data, clean_df], ignore_index=True)
            print(f"\n📈 Buffer update: {before} → {len(self.data)} rows")

            # Downsample if buffer too large
            if len(self.data) > 10000:
                self.data = self.data.iloc[-5000:]
                print("📉 Downsampled buffer to 5000 points")

            # =====================
            # Time Analysis
            # =====================
            if len(self.data) > 1 and 'Time' in self.data.columns:
                time_span = self.data['Time'].iloc[-1] - self.data['Time'].iloc[0]
                print(f"\n⏱️ Temporal Analysis:")
                print(f"- Span: {time_span:.3f} seconds")
            
                if time_span > 0:
                    print(f"- Rate: {len(self.data)/time_span:.1f} Hz")
                    time_diffs = np.diff(self.data['Time'])
                    print(f"- Intervals: min={time_diffs.min():.4f}s, max={time_diffs.max():.4f}s, avg={time_diffs.mean():.4f}s")
                else:
                    print("- Rate: ∞ (instantaneous)")

            # =====================
            # Data Preview
            # =====================
            if not self.data.empty:
                print("\n🔍 Latest Samples:")
                # Show available channels (dynamically handles EDA_L/EDA_R)
                preview_cols = ['Time']
                for ch in ['raw-EDA_L', 'raw-EDA_R']:
                    if ch in self.data.columns or ch.split('-')[-1] in self.mac_addresses.values():
                        preview_cols.append(ch)
            
                print(self.data[preview_cols].tail(2).to_string(
                    index=False, 
                    float_format=lambda x: f"{x:.3f}" if not pd.isna(x) else "NaN"
                ))

            # =====================
            # Visualization
            # =====================
            self.pending_update = True
            if hasattr(self, 'mainwindow'):
                self.mainwindow.update()

            print("\n✅ Processing complete\n")

        except Exception as e:
            print(f"\n❌ CRITICAL ERROR in __getData:")
            print(f"Type: {type(e).__name__}")
            print(f"Message: {str(e)}")
            import traceback
            traceback.print_exc()
            # Attempt to preserve remaining functionality
            if hasattr(self, 'data'):
                print(f"⚠️ Current buffer preserved ({len(self.data)} samples)")

=======
    def __getData(self, sample):
        self.data = pd.concat([self.data, sample])
        #TODO - downsample data
        if self.isStreaming:
            self.updateGraphs() 
     
>>>>>>> Stashed changes
    def __linkWindows(self):
        pass    
    
    def __linkActions(self):
        pass
        
    def __windowData(self):
        pass
    
    #### MUGGLE METHODS #### 
    def start(self):
        self.mainwindow.show()
        sys.exit(self.app.exec()) #program loops forever
    
    def stop(self):
        pass
    
    def accumulateData(self, dataSet):
        pass
    
    def updateGraphs(self):
        #TODO - window data
        
        #currentTabview = self.mainwindow.widget_tabs.currentIndex() #grab index of tab in view
        currentTab = self.mainwindow.widget_tabs.currentWidget()  #grab that tab
        for plot in currentTab.listPlots: #for the plots within current tab
            data2plot = plot.combobox.currentText() #what should this graph show
            left_data, right_data = dataselectmapping[data2plot]
            #print(left_data, self.data[left_data])
            plot.updateGraph(self.data["Time"], self.data[left_data], self.data[right_data])
        
    def sendCommand(self, command):
        pass
    
    def sendSettings(self):
        pass

    #def load_settings(self):
    #    pass

#### MAIN #### (just for testing independently of everything else)
def main():
    q_settings = multiprocessing.Queue()
    q_commands = multiprocessing.Queue()
    q_data = multiprocessing.Queue()
    
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    front = FrontEnd(q_settings, q_commands, q_data, config)
    front.start()

if __name__ == '__main__':
    main()