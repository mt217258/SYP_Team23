import queue
import pandas as pd
import configparser
from PyQt5 import QtWidgets
import sys
import numpy as np
import multiprocessing
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from window_main import WINDOW_main
from thread_rcvdata import Worker_DAQ
import time
from common import dataselectmapping, data

class FrontEnd:
    def __init__(self, q_settings, q_commands, q_data, config):
        self.q_settings = q_settings
        self.q_commands = q_commands
        self.q_data = q_data
        self.settings = config

        self.isStreaming = False
        self.isRecording = False
        self.window_width = 30  # in minutes
        self.window_offset = 0  # percentage (0-100)

        self.app = QtWidgets.QApplication(sys.argv)
        self.data = data

        # Create the main window (loaded via the UI file)
        self.mainwindow = WINDOW_main(settings=config, Q_settings=q_settings, filepath="config.ini")
        self.__linkThreads()
        self.__linkControlSignals()

        self.plot_update_timer = QTimer()
        self.plot_update_timer.timeout.connect(self._throttled_updateGraphs)
        self.plot_update_timer.start(100)
        self.pending_update = False

    def _throttled_updateGraphs(self):
        if self.pending_update and self.isStreaming:
            self.updateGraphs()
            self.pending_update = False

    def __linkControlSignals(self):
        self.mainwindow.widget_controls.signal_streaming.connect(self.__updateStreaming)
        self.mainwindow.widget_controls.signal_recordname.connect(self.__updateFilename)
        self.mainwindow.widget_controls.signal_recording.connect(self.__updateRecording)
        self.mainwindow.widget_controls.signal_width.connect(self.__updateWindowWidth)
        self.mainwindow.widget_controls.signal_offset.connect(self.__updateWindowOffset)

    def __updateStreaming(self, onoff):
        if not self.isStreaming and not onoff:
            self.index_lastSampleBeforePause = len(self.data)
        self.isStreaming = onoff

    def __updateFilename(self, filename):
        self.filename = filename

    def __updateRecording(self, onoff):
        if not self.isRecording:
            self.q_commands.put("Record:")
        else:
            self.q_commands.put("Stop")
        self.isStreaming = onoff

    def __updateWindowWidth(self, width):
        self.window_width = width
        self.updateGraphs()

    def __updateWindowOffset(self, offset):
        self.window_offset = offset
        self.updateGraphs()

    def __linkThreads(self):
        self.thread_DAQ = QThread()
        self.worker_DAQ = Worker_DAQ(self.q_data)
        self.worker_DAQ.moveToThread(self.thread_DAQ)
        self.thread_DAQ.started.connect(self.worker_DAQ.run)
        self.worker_DAQ.sendData.connect(self.__getData)
        self.thread_DAQ.start()

    def __getData(self, batch_df):
        try:
            if batch_df.empty:
                return

            # Safely flatten any multi-row batch down to a single row (first sample only)
            batch_df = batch_df.map(lambda x: x.iloc[0] if hasattr(x, 'iloc') else x, na_action='ignore')

            # Identify columns to convert to numeric
            numeric_cols = [col for col in batch_df.columns if col not in ['Time', 'nSeq']]

            # Convert columns safely, one by one
            for col in numeric_cols:
                try:
                    batch_df[col] = pd.to_numeric(batch_df[col], errors='coerce')
                except Exception as e:
                    print(f"[WARN] Could not convert column: {col} — {e}")

            # Drop rows with all-NaNs in important signal columns (optional)
            if batch_df[numeric_cols].isna().all(axis=1).any():
                print("[__getData] Warning: All signal columns are NaN — skipping this batch")
                return

            # Initialize time if needed
            if self.data.empty:
                self.synthetic_timestamp = time.time()

            if 'Time' not in batch_df.columns or batch_df['Time'].isnull().all():
                start_time = self.synthetic_timestamp
                batch_df['Time'] = [start_time]
                self.synthetic_timestamp += 1 / 400  # simulate 400 Hz
            else:
                self.synthetic_timestamp = batch_df['Time'].iloc[-1] + (1 / 400)

            # Append to main data
            self.data = pd.concat([self.data, batch_df], ignore_index=True)

            # Trim buffer if it grows too large
            if len(self.data) > 10000:
                self.data = self.data.iloc[-5000:]

            # Trigger graph update
            self.pending_update = True
            if hasattr(self, 'mainwindow'):
                self.mainwindow.update()

        except Exception as e:
            import traceback
            print("[ERROR in __getData]")
            traceback.print_exc()

    def updateGraphs(self):
        currentTab = self.mainwindow.widget_tabs.currentWidget()
        for plot in currentTab.listPlots:
            data2plot = plot.combobox.currentText()
            left_key, right_key = dataselectmapping.get(data2plot, (None, None))

            left = self.data.get(left_key)
            right = self.data.get(right_key)

            # Fallback: if 'nrm-*' signal missing or all NaN, try 'raw-*'
            if left_key and (left is None or left.isna().all()) and 'nrm' in left_key:
                fallback_key = left_key.replace('nrm', 'raw')
                left = self.data.get(fallback_key)

            if right_key and (right is None or right.isna().all()) and 'nrm' in right_key:
                fallback_key = right_key.replace('nrm', 'raw')
                right = self.data.get(fallback_key)

            # Check for time axis and valid left/right
            time_data = self.data.get("Time")
            if time_data is not None and left is not None and right is not None:
                plot.updateGraph(time_data, left, right)
            else:
                plot.updateGraph([], [], [])

    def start(self):
        self.mainwindow.show()
        ret = self.app.exec()
        self.__cleanup()
        sys.exit(ret)

    def __cleanup(self):
        self.thread_DAQ.quit()
        self.thread_DAQ.wait()

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
