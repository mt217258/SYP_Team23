import pandas as pd

data1 = pd.DataFrame(data={"Time":[], "raw-sEMG_L":[],   "raw-sEMG_R":[], 
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

print("Data1: ",data1)

data2 =  pd.DataFrame(data={"Time":[1], "raw-sEMG_L":[2], 
                                        "raw-EDA_L":[3],
                                        "raw-ACC_L":[4]})
print("Data2: ",data2)

data3 = pd.concat([data1, data2], ignore_index=True) 
print("Data3: ",data3)

data4 =  pd.DataFrame(data={"Time":[1], "raw-sEMG_R":[5], 
                                        "raw-EDA_R":[6],
                                        "raw-ACC_R":[6]})
print("Data4: ",data4)

data5 = pd.concat([data3, data4], ignore_index=True)
print("Data5: ",data5)

data6 = data2.merge(data4, how='outer', on='Time')
print("Data6: ", data6)
print("Data2: ",data2)

rawData = [[2,3,4],1]

blankDict = {}
        
sample = rawData[0]
blankDict['Time'] = [rawData[1]]

print(blankDict)