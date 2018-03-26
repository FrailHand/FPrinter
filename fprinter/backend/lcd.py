import I2C_LCD_driver
from time import *

class LCD():

	ERASE = "               "

	def __init__(self):
		
		self.mylcd = I2C_LCD_driver.lcd()
		

	def print(self, l1, l2):


		if l1 is not None:
			ecran.clear(1)
			mylcd.lcd_display_string(l1, 1)

		if l2 is not None:
			ecran.clear(2)
			mylcd.lcd_display_string(l2, 2)


	def clear(self,line = None):
		if line is None: 
			mylcd.lcd_display_string(LCD.ERASE, 1)
			mylcd.lcd_display_string(LCD.ERASE, 2)
		else :
			mylcd.lcd_display_string(LCD.ERASE, line)