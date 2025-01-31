'''
Author:             Matthew McLaughlin
Contact:            mt217258@dal.ca
Description:        Simple backend to read in data using pluxBioSignals
                    library. 
TODO List:          Stream muscleBan data
'''

#### LIBRARIES ####
from pylsl import StreamInlet, resolve_streams
#### GLOBAL VARIABLES ####
#### CLASSES ####

#class <>
    #### MAGIC METHODS ####
    #### MANGELED METHODS ####
    #### MUGGLE METHODS ####  
    
#### VULGAR METHODS #### (they have no class) 

#### MAIN ####
def main():
    # Resolve an available OpenSignals stream 
    print("# Looking for an available OpenSignals stream...") 
    #os_stream = resolve_stream("name", "OpenSignals")
    os_stream = resolve_streams()  #use resolve_streams
    
    # Create an inlet to receive signal samples from the stream 
    inlet = StreamInlet(os_stream[0]) 
    
    while True: 
        # Receive samples 
        sample, timestamp = inlet.pull_sample() 
        print(timestamp, sample) 

if __name__ == '__main__':
    main()
