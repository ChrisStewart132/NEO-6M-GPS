import time
from machine import Pin, SPI

from nokia5110 import Nokia5110
from neo6m import NEO6M

# initial lat long position for relative positioning
xi,yi,ti = None, None, None

def display_nmea_data(nmea_data, lcd):
    global xi,yi,ti
    
    lcd.clear()
    
    if nmea_data["GGA"] and nmea_data["GGA"]["fix"] != "0":
        x,y,ti = nmea_data["GGA"]["lat"], nmea_data["GGA"]["long"], None
        if xi == None:
            xi,yi = x,y
        x,y  = float(xi) - float(x), float(yi) - float(y)
        lcd.write_text_at_position("alt sl:" + nmea_data["GGA"]["alt sl"], 0, 1)
        lcd.write_text_at_position("alt sl:" + nmea_data["GGA"]["alt sl"], 0, 1)
        lcd.write_text_at_position("h:" + nmea_data["GGA"]["hd"], 0, 2)
        #if nmea_data["GGA"]["lat_direction"] in ["s","S"]:        
            #lcd.write_text_at_position("x:-" + str(x), 0, 3)
        #else:
        lcd.write_text_at_position("x:" + str(x), 0, 3)
        lcd.write_text_at_position("y:" + str(y), 0, 4)
    else:
        lcd.write_text_at_position("loading...", 1, 0)
        if nmea_data["GGA"]:
            t = nmea_data["GGA"]["time"]
            if ti == None:
                ti = t
            delta_t = str(float(t)-float(ti))
            lcd.write_text_at_position("t:" + delta_t, 0, 1)
    

def main():
    spi = SPI(0, baudrate=1000000, polarity=0, phase=0, sck=Pin(2), mosi=Pin(3))  
    dc = 19  # Data/Command pin
    rst = 18  # Reset pin
    cs = 20  # Chip Select pin
    lcd = Nokia5110(spi, dc, rst, cs)
    lcd.clear()

    gps = NEO6M()
    
    tick = 0
    while True:
        try:
            gps.read_data()
        except Exception as e:
            print(e)
        time.sleep(0.2)
        
        tick += 1
        if tick % 5 == 0:
            try:
                display_nmea_data(gps.nmea_data, lcd)
            except Exception as e:
                print(e) 
        

# If the module is run directly, execute the main function.
if __name__ == "__main__":
    main()
