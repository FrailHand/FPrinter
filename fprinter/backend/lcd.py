import i2c_lcd


class LCD():
    ERASE = "               "
    ADDRESS = 0x39

    def __init__(self, i2c_addr=LCD.ADDRESS):

        self.mylcd = i2c_lcd.lcd(addr=i2c_addr)

    def write(self, l1=None, l2=None):

        if l1 is not None:
            self.clear(1)
            self.mylcd.lcd_display_string(l1, 1)

        if l2 is not None:
            self.clear(2)
            self.mylcd.lcd_display_string(l2, 2)

    def clear(self, line=None):
        if line is None:
            self.mylcd.lcd_display_string(LCD.ERASE, 1)
            self.mylcd.lcd_display_string(LCD.ERASE, 2)
        else:
            self.mylcd.lcd_display_string(LCD.ERASE, line)
