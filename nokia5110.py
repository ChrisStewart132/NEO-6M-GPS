import time
from machine import Pin, SPI

# Constants for the display
LCD_WIDTH = 84
LCD_HEIGHT = 48

CMD_MODE = 0
DATA_MODE = 1

# Commands for PCD8544
LCD_CMD_FUNCTIONSET = 0x20
LCD_CMD_DISPLAYCONTROL = 0x08
LCD_CMD_SETYADDR = 0x40
LCD_CMD_SETXADDR = 0x80
LCD_CMD_SETTEMP = 0x04
LCD_CMD_BIAS = 0x10
LCD_CMD_VOP = 0x80

# 5x8 pixel font for numbers, lowercase letters, and some punctuation
font = {
    '0': [0x3E, 0x51, 0x49, 0x45, 0x3E],  # '0'
    '1': [0x00, 0x42, 0x7F, 0x40, 0x00],  # '1'
    '2': [0x42, 0x61, 0x51, 0x49, 0x46],  # '2'
    '3': [0x21, 0x41, 0x45, 0x4B, 0x31],  # '3'
    '4': [0x18, 0x14, 0x12, 0x7F, 0x10],  # '4'
    '5': [0x27, 0x45, 0x45, 0x45, 0x39],  # '5'
    '6': [0x3C, 0x4A, 0x49, 0x49, 0x30],  # '6'
    '7': [0x01, 0x71, 0x09, 0x05, 0x03],  # '7'
    '8': [0x36, 0x49, 0x49, 0x49, 0x36],  # '8'
    '9': [0x06, 0x49, 0x49, 0x29, 0x1E],  # '9'
    'a': [0x20, 0x54, 0x54, 0x54, 0x78],  # 'a'
    'b': [0x7F, 0x48, 0x48, 0x48, 0x30],  # 'b'
    'c': [0x38, 0x44, 0x44, 0x44, 0x20],  # 'c'
    'd': [0x38, 0x44, 0x44, 0x44, 0x7F],  # 'd'
    'e': [0x38, 0x54, 0x54, 0x54, 0x18],  # 'e'
    'f': [0x08, 0x7E, 0x09, 0x01, 0x02],  # 'f'
    'g': [0x18, 0xA4, 0xA4, 0xA4, 0x7C],  # 'g'
    'h': [0x7F, 0x08, 0x08, 0x08, 0x70],  # 'h'
    'i': [0x00, 0x44, 0x7D, 0x40, 0x00],  # 'i'
    'j': [0x40, 0x80, 0x80, 0x80, 0x7D],  # 'j'
    'k': [0x7F, 0x10, 0x28, 0x44, 0x00],  # 'k'
    'l': [0x00, 0x41, 0x7F, 0x40, 0x00],  # 'l'
    'm': [0x7C, 0x04, 0x18, 0x04, 0x78],  # 'm'
    'n': [0x7C, 0x08, 0x04, 0x04, 0x78],  # 'n'
    'o': [0x38, 0x44, 0x44, 0x44, 0x38],  # 'o'
    'p': [0xFC, 0x24, 0x24, 0x24, 0x18],  # 'p'
    'q': [0x18, 0x24, 0x24, 0xFC, 0x80],  # 'q'
    'r': [0x7C, 0x08, 0x04, 0x04, 0x08],  # 'r'
    's': [0x48, 0x54, 0x54, 0x54, 0x20],  # 's'
    't': [0x04, 0x3F, 0x44, 0x40, 0x20],  # 't'
    'u': [0x3C, 0x40, 0x40, 0x20, 0x7C],  # 'u'
    'v': [0x1C, 0x20, 0x40, 0x20, 0x1C],  # 'v'
    'w': [0x3C, 0x40, 0x30, 0x40, 0x3C],  # 'w'
    'x': [0x44, 0x28, 0x10, 0x28, 0x44],  # 'x'
    'y': [0x1C, 0xA0, 0xA0, 0xA0, 0x7C],  # 'y'
    'z': [0x44, 0x64, 0x54, 0x4C, 0x44],  # 'z'
    ' ': [0x00, 0x00, 0x00, 0x00, 0x00],  # ' '
    '.': [0x00, 0x60, 0x60, 0x00, 0x00],  # '.'
    ',': [0x00, 0x80, 0x60, 0x00, 0x00],  # ','
    '!': [0x00, 0xBF, 0x00, 0x00, 0x00],  # '!'
    '?': [0x02, 0x01, 0x51, 0x09, 0x06],  # '?'
    '-': [0x08, 0x08, 0x08, 0x08, 0x08],  # '-'
    '_': [0x80, 0x80, 0x80, 0x80, 0x80],  # '_'
    ':': [0x00, 0x36, 0x36, 0x00, 0x00],  # ':'
    ';': [0x00, 0x56, 0x36, 0x00, 0x00],  # ';'
}

class Nokia5110:
    def __init__(self, spi, dc, rst, cs):
        self.spi = spi
        self.dc = Pin(dc, Pin.OUT)  # Data/Command pin
        self.rst = Pin(rst, Pin.OUT)  # Reset pin
        self.cs = Pin(cs, Pin.OUT)  # Chip Select pin

        self._reset()
        self._init_lcd()

    def _reset(self):
        self.rst.value(0)
        time.sleep_ms(100)
        self.rst.value(1)

    def _write_byte(self, value, mode):
        # Set data/command mode
        self.dc.value(mode)
        # Select the display (CS low)
        self.cs.value(0)
        # Send the byte over SPI
        self.spi.write(bytearray([value]))
        # Deselect the display (CS high)
        self.cs.value(1)

    def _init_lcd(self):
        # Initialize the display with some default commands
        self._write_byte(LCD_CMD_FUNCTIONSET | 0x01, CMD_MODE)  # Set extended instruction set
        self._write_byte(LCD_CMD_VOP | 0x40, CMD_MODE)  # Set contrast (Vop)
        self._write_byte(LCD_CMD_BIAS | 0x04, CMD_MODE)  # Set Bias system
        self._write_byte(LCD_CMD_FUNCTIONSET, CMD_MODE)  # Set basic instruction set
        self._write_byte(LCD_CMD_DISPLAYCONTROL | 0x04, CMD_MODE)  # Normal display mode

    def clear(self):
        # Clear the display (write zeros to all pixels)
        for i in range(LCD_WIDTH * LCD_HEIGHT // 8):
            self._write_byte(0x00, DATA_MODE)

    def set_cursor(self, x, y):
        # Set the cursor position
        self._write_byte(LCD_CMD_SETXADDR | x, CMD_MODE)
        self._write_byte(LCD_CMD_SETYADDR | y, CMD_MODE)

    def write_data(self, data):
        # Write data to the display (for example, to display pixels)
        for byte in data:
            self._write_byte(byte, DATA_MODE)

    def write_text_at_position(self, text, x, y):
        """
        Writes a string of characters to the Nokia 5110 display at the given position.
        
        :param text: String containing characters to write (e.g., 'hello123!')
        :param x: X position (column, 0 to 83)
        :param y: Y position (row, 0 to 5 as there are 6 banks of 8 pixels)
        """
        self.set_cursor(x, y)
        text = text.lower()
        for char in text:
            if char in font:
                # Write each byte of the character's font pattern
                self.write_data(font[char])
                # Add one column of padding (optional, for spacing between characters)
                self.write_data([0x00])
            else:
                # Handle invalid characters (e.g., unsupported symbols) by adding blank spaces
                self.write_data([0x00] * 6)


def main():
    # Example usage:
    # Define SPI0 with the appropriate pins for CLK and TX
    spi = SPI(0, baudrate=1000000, polarity=0, phase=0, sck=Pin(2), mosi=Pin(3))  # Adjust pins to your board

    # Define GPIOs for control pins
    dc = 19  # Data/Command pin
    rst = 18  # Reset pin
    cs = 20  # Chip Select pin

    lcd = Nokia5100(spi, dc, rst, cs)
    lcd.clear()

    # Example: Write text "hello123!" at position (x=0, y=0)
    lcd.write_text_at_position("hello123!", 0, 0)

    # Example: Write text "world." at position (x=30, y=1)
    lcd.write_text_at_position("world.", 30, 1)


# If the module is run directly, call main().
if __name__ == "__main__":
    main()




