import pandas as pd

#Data format: 
data = pd.DataFrame(data={"Time":[], "raw-sEMG_L":[],   "raw-sEMG_R":[], 
                                     "raw-EDA_L":[],    "raw-EDA_R":[],
                                     "raw-ACC_L":[],    "raw-ACC_R":[], #raw signals
                                     "nrm-sEMG_L":[],   "nrm-sEMG_R":[], 
                                     "nrm-EDA_L":[],    "nrm-EDA_R":[],
                                     "nrm-ACC_L":[],    "nrm-ACC_R":[], #normalized signals, TBD
                                     "Amplitude-sEMG_L":[], "Amplitude-sEMG_R":[], #start of metrics based on data
                                     "RMS-sEMG_L":[],"RMS-sEMG_R":[],
                                     "NSSCR-EDA_L":[],"NSSCR-EDA_R":[],
                                     "SCRA-EDA_L":[],"SCRA-EDA_R":[]
                                     }) 

#used in frontend for selection in graphs
list_signals = ["raw-sEMG", "raw-EDA", "raw-ACC", 
                "nrm-sEMG", "nrm-EDA", "nrm-ACC",
                "Amplitude-sEMG", "RMS-sEMG", "NSSCR-EDA", "SCRA-EDA"]

#used to map data select in GUI to which columns to plot
dataselectmapping = {"raw-sEMG":["raw-sEMG_L", "raw-sEMG_R"], 
                     "raw-EDA":["raw-EDA_L","raw-EDA_R"], 
                     "raw-ACC":["raw-ACC_L","raw-ACC_R"],  
                     "nrm-sEMG":["nrm-sEMG_L","nrm-sEMG_R"], 
                     "nrm-EDA":["nrm-EDA_L","nrm-EDA_R"], 
                     "nrm-ACC":["nrm-ACC_L","nrm-ACC_R"], 
                     "Amplitude-sEMG":["Amplitude-sEMG_L","Amplitude-sEMG_R"], 
                     "RMS-sEMG":["RMS-sEMG_L","RMS-sEMG_R"], 
                     "NSSCR-EDA":["NSSCR-EDA_L","NSSCR-EDA_R"], 
                     "SCRA-EDA":["SCRA-EDA_L","SCRA-EDA_R"]}

num_dataPointsInPlot = 1000