import smbus
from time import sleep, strftime
import RPi.GPIO as GPIO
from random import randint, seed
from json import loads, load

class LCD1602:
  def __init__(self, address, backlight):
    self.BUS = smbus.SMBus(1)
    self.address = address
    self.backlight = backlight
    
    self.send_cmd(0x33)
    sleep(0.005)
    self.send_cmd(0x32)
    sleep(0.005)
    self.send_cmd(0x28)
    sleep(0.005)
    self.send_cmd(0x0C)
    sleep(0.005)
    self.send_cmd(0x01)
    self.BUS.write_byte(self.address, 0x08)
    
  def write_word(self, data):
    if self.backlight:
      data |= 0x08
    else:
      data &= 0xF7
    self.BUS.write_byte(self.addresss, data)
    
  def send_cmd(self, cmd):
    buf = cmd & 0xF0
    buf |= 0x04
    self.write_word(buf)
    sleep(0.002)
    buf &= 0xFB
    self.write_word(buf)
    
    buf = (cmd & 0x0F) << 4
    buf |= 0x04
    self.write_word(buf)
    sleep(0.002)
    buf &= 0xFB
    self.write_word(buf)
    
  def send_data(self, cmd):
    buf = cmd & 0xF0
    buf |= 0x05
    self.write_word(buf)
    sleep(0.002)
    buf &= 0xFB
    self.write_word(buf)
    
    buf = (cmd & 0x0F) << 4
    buf |= 0x05
    self.write_word(buf)
    sleep(0.002)
    buf &= 0xFB
    self.write_word(buf)
    
  def clear(self):
    self.send_cmd(0x01)
    
  def openlight(self):
    self.BUS.write_byte(self.address, 0x08)
    self.BUS.close()
    
  def write(self, x, y, s):
    if x < 0:
      x = 0
    if x > 15:
      x = 15
    if y < 0:
      y = 0
    if y > 1:
      y = 1
    addr = 0x80 + 0x40 * y + x
    self.send_cmd(addr)
    for c in s:
      self.send_data(ord(c))
      
lcd = LCD1602(0x27, True)
BUTTON_GPIO = 16
seed(114514)

try:
  lcd.clear()
  
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down = GPIO.PUD_UP)
  
  lcd.write(0, 0, "Hello there")
  lcd.write(0, 1, "LCD Dice")
  sleep(3)
  lcd.clear()
  
  while True:
    if not GPIO.input(BUTTON_GPIO):
      with open("../configuration.json", 'r') as f:
        minmax = load(f)
      dice = randint(minmax["min"], minmax["max"])
      
      with open("../dice_history.txt", 'a') as f:
        f.write(f"{strftime('%Y/%m/%d')} {strftime('%H:%M:%S')} {dice}\n")
        
      with open("display_text.txt", 'r') as f:
        text = f.readline().strip()
        
      lcd.write(0, 0, text)
      lcd.write(0, 1, f"[{minmax['min']}, {minmax['max']}]: {dice}")
      sleep(1)
except KeyboardInterrupt:
  print("Keyboard stop")
except Exception as e:
  print(f"Exception: {e}")
finally:
  lcd.clear()
