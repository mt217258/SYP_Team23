import pandas as pd

#Data format: 
data = pd.DataFrame(data={"Time":[], "raw-sEMG_L":[],   "raw-sEMG_R":[], 
                                     "raw-EDA_L":[],    "raw-EDA_R":[],
                                     "raw-ACC_L":[],    "raw-ACC_R":[], #raw signals
                                     "nrm-sEMG_L":[],   "nrm-sEMG_R":[], 
                                     "nrm-EDA_L":[],    "nrm-EDA_R":[],
                                     "nrm-ACC_L":[],    "nrm-ACC_R":[]}) #normalized signals, TBD

#used in frontend for selection in graphs
list_signals = ["raw-sEMG", "raw-EDA", "raw-ACC", "raw-ACC", "nrm-sEMG", "nrm-EDA", "nrm-ACC", "nrm-ACC"]