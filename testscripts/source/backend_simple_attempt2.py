# Imports
from pylsl import StreamInlet, resolve_streams

class Lsl():

    def recv_data_unspecified_OS_stream(self):
        # Resolve an available OpenSignals stream
        print("# Looking for an available OpenSignals stream...")
        self.os_stream = resolve_streams("name", "OpenSignals")
        #MTM - want to return stream with name OpenSignals??, resolve_streams returns full list

        # Create an inlet to receive signal samples from the stream
        self.inlet = StreamInlet(self.os_stream[0])

        try:
            while True:
                # Receive samples
                sample, timestamp = self.inlet.pull_sample()
                print(timestamp, sample)
        except KeyboardInterrupt:
            self.inlet.close_stream()


    def recv_data_PLUX_device(self, mac_address):
        # Resolve stream
        print("# Looking for an available OpenSignals stream from the specified device...")
        self.os_stream = resolve_streams("type", mac_address)

        # Create an inlet to receive signal samples from the stream
        self.inlet = StreamInlet(self.os_stream[0])

        try:
            while True:
                # Receive samples
                samples, timestamp = self.inlet.pull_sample()
                print(timestamp, samples)
        except KeyboardInterrupt:
            self.inlet.close_stream()


    def recv_data_host(self, hostname):
        # Resolve stream
        print("# Looking for an available OpenSignals stream from the specified host...")
        self.os_stream = resolve_streams("hostname", hostname)

        # Create an inlet to receive signal samples from the stream
        self.inlet = StreamInlet(self.os_stream[0])

        try:
            while True:
                # Receive samples
                samples, timestamp = self.inlet.pull_sample()
                print(timestamp, samples)
        except KeyboardInterrupt:
            self.inlet.close_stream()


    def recv_stream_metadata(self):
        # Get information about the stream
        self.stream_info = self.inlet.info()

        # Get individual attributes
        stream_name = self.stream_info.name()
        stream_mac = self.stream_info.type()
        stream_host = self.stream_info.hostname()
        stream_n_channels = self.stream_info.channel_count()

        # Store sensor channel info & units in the dictionary
        stream_channels = dict()
        channels = self.stream_info.desc().child("channels").child("channel")
 
        # Loop through all available channels
        for i in range(stream_n_channels):

            # Get the channel number (e.g. 1)
            channel = i + 1

            # Get the channel type (e.g. ECG)
            sensor = channels.child_value("label")

            # Get the channel unit (e.g. mV)
            unit = channels.child_value("unit")

            # Store the information in the stream_channels dictionary
            stream_channels.update({channel: [sensor, unit]})
            channels = channels.next_sibling()
        print(f"======= Stream Metadata =======\nStream Name > {stream_name}\nStream MAC > {stream_mac}\nStream Host > {stream_host}\nStream Number of Channels > {stream_n_channels}\n+++ Channels [sensor, units] > {stream_channels}")



def show_menu():
    print('')
    for temp_id in MENU_IMPUT.keys():
        print(str(temp_id) + ' | ' + MENU_IMPUT[temp_id])

def process_action(user_action):
    if user_action == '0':
        lsl.recv_data_unspecified_OS_stream()
    elif user_action == '1':
        mac_address = str(input('MAC address: '))
        lsl.recv_data_PLUX_device(mac_address)
    elif user_action == '2':
        hostname = str(input('Host name: '))
        lsl.recv_data_host(hostname)
    elif user_action == '3':
        lsl.recv_stream_metadata()


if __name__ == "__main__":
    MENU_IMPUT = {0: 'Receving Data From an Unspecified OpenSignals Stream',
                  1: 'Receving Data From a Specific PLUX Device in an OpenSignals Stream',
                  2: 'Receving Data From a Specific Host Providing the OpenSignals Stream',
                  3: 'Receving Stream Metadata'
                  }

    lsl = Lsl()

    while True:
        show_menu()
        user_action = str(input('New action: '))
        process_action(user_action)