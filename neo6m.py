from machine import UART, Pin
import time

class NEO6M:
    # NMEA sentence fields
    GGA_FIELDS = ["time", "lat", "lat_direction", "long", "lon_direction", "fix", "nSat", "hd", "alt sl", "alt WGS84"]
    GSA_FIELDS = ["time", "fix_status", "mode", "satellites_used", "hdop", "vdop", "pdop", "gps_age", "diff_age", "checksum"]
    GSV_FIELDS = ["time", "total_messages", "message_number", "satellites_in_view", "sat_id", "elevation", "azimuth", "snr", "checksum"]
    GLL_FIELDS = ["lat", "lat_direction", "long", "lon_direction", "time", "status", "checksum"]
    RMC_FIELDS = ["time", "status", "lat", "lat_direction", "long", "lon_direction", "speed", "course", "date", "magnetic_variation", "checksum"]
    VTG_FIELDS = ["track", "track_magnetic", "speed_knots", "speed_kmh", "status"]

    def __init__(self, uart_num=1, baudrate=9600, tx_pin=8, rx_pin=9):
        self.uart = UART(uart_num, baudrate=baudrate, tx=Pin(tx_pin), rx=Pin(rx_pin))
        self.nmea_data = {
            "GGA": None,
            "GSA": None,
            "GSV": None,
            "GLL": None,
            "RMC": None,
            "VTG": None
        }

    def process_line(self, line):
        """
        Process a line of NMEA data and store the result in nmea_data.
        """
        values = line.decode('utf-8').strip().split(",")
        key = values[0][3:]

        if key == "GGA":
            processed_line = {self.GGA_FIELDS[i]: values[i + 1] for i in range(min(len(self.GGA_FIELDS), len(values) - 1))}
            self.nmea_data["GGA"] = processed_line

        elif key == "GSA":
            processed_line = {self.GSA_FIELDS[i]: values[i + 1] for i in range(min(len(self.GSA_FIELDS), len(values) - 1))}
            self.nmea_data["GSA"] = processed_line

        elif key == "GSV":
            if len(values) < 4:
                return
            processed_line = {
                "time": values[1],
                "total_messages": values[2],
                "message_number": values[3],
                "satellites": []
            }
            for i in range(4, len(values) - 4, 4):
                satellite_info = {
                    "sat_id": values[i],
                    "elevation": values[i + 1],
                    "azimuth": values[i + 2],
                    "snr": values[i + 3]
                }
                processed_line["satellites"].append(satellite_info)
            self.nmea_data["GSV"] = processed_line

        elif key == "GLL":
            processed_line = {self.GLL_FIELDS[i]: values[i + 1] for i in range(min(len(self.GLL_FIELDS), len(values) - 1))}
            self.nmea_data["GLL"] = processed_line

        elif key == "RMC":
            processed_line = {self.RMC_FIELDS[i]: values[i + 1] for i in range(min(len(self.RMC_FIELDS), len(values) - 1))}
            self.nmea_data["RMC"] = processed_line

        elif key == "VTG":
            processed_line = {self.VTG_FIELDS[i]: values[i + 1] for i in range(min(len(self.VTG_FIELDS), len(values) - 1))}
            self.nmea_data["VTG"] = processed_line
            self.print_data()

    def read_data(self):
        """
        Continuously reads data from the GPS module via UART.
        """
        if self.uart.any():
            line = self.uart.readline()
            if line:
                try:
                    self.process_line(line)
                except Exception as e:
                    print(e)
        
    def print_data(self):
        """
        Prints the current parsed NMEA data.
        """
        for key in self.nmea_data.keys():
            print(key, self.nmea_data[key])
        print("\n\n")

    def get_latest_data(self, sentence_type):
        """
        Returns the latest NMEA data for the given sentence type (e.g., 'GGA', 'RMC').
        """
        return self.nmea_data.get(sentence_type, None)


# Example usage (when running the script directly)
def main():
    gps = NEO6M()
    while True:
        gps.read_data()
        time.sleep(0.2)

# If the module is run directly, execute the main function.
if __name__ == "__main__":
    main()


