#!/usr/bin/env python
# -*- coding: utf-8 -*-

import string
import sys
import select
from time import sleep
import termios
import tty

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

import Image
import ImageDraw
import ImageFont
import random

import RPi.GPIO as GPIO

__snakeDir__ = random.randint(1,4)*3
__snakeHeadX__ = 62
__snakeHeadY__ = 30

'''
def dirTurnTo3(channel):
	global __snakeDir__
	if __snakeDir__ != 3 and __snakeDir__ != 9:
		__snakeDir__ = 3
def dirTurnTo6(channel):
	global __snakeDir__
	if __snakeDir__ != 6 and __snakeDir__ != 12:
		__snakeDir__ = 6
def dirTurnTo9(channel):
	global __snakeDir__
	if __snakeDir__ != 9 and __snakeDir__ != 3:
		__snakeDir__ = 9
def dirTurnTo12(channel):
	global __snakeDir__
	if __snakeDir__ != 12 and __snakeDir__ != 6:
		__snakeDir__ = 12
'''
def dirTurnLeft(channel):
	global __snakeDir__
	if __snakeDir__ == 3:
		__snakeDir__ = 12
	else:
		__snakeDir__ = __snakeDir__ - 3

def dirTurnRight(channel):
	global __snakeDir__
	if __snakeDir__ == 12:
		__snakeDir__ = 3
	else:
		__snakeDir__ = __snakeDir__ + 3

if __name__ == "__main__":
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(23,GPIO.IN,pull_up_down=GPIO.PUD_UP)
	GPIO.setup(24,GPIO.IN,pull_up_down=GPIO.PUD_UP)
	try:
		GPIO.add_event_detect(23,GPIO.RISING,callback=dirTurnLeft,bouncetime=200)
		GPIO.add_event_detect(24,GPIO.RISING,callback=dirTurnRight,bouncetime=200)
		# Raspberry Pi pin configuration 
		RST = 17
		# Note the following are only used with SPI: 
		DC = 27
		SPI_PORT = 0
		SPI_DEVICE = 0

		# 128x64 display with hardware SPI
		disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))
		 
		# Initialize library
		disp.begin()
		 
		# Clear display
		disp.clear()
		disp.display()
		
		# Create blank image for drawing.
		# Make sure to create image with mode '1' for 1-bit color.
		width = disp.width
		height = disp.height
	except KeyboardInterrupt:
		print "*** GPIO clean up ***"
		GPIO.cleanup()
		print "*** disp clear ***"
		disp.clear()
		disp.display()
	in_speed = raw_input("请选择难度等级 慢[1-10]快 :")
	real_speed = 1.0/(string.atof(in_speed)*10.0)
	# 非阻塞输入用于退出
	old_settings = termios.tcgetattr(sys.stdin)
	tty.setcbreak(sys.stdin.fileno())
	while True:
		sleep(real_speed)
		# 绘图 BEGIN
		image = Image.new('1', (width, height))
		draw = ImageDraw.Draw(image)
 		font_zh = ImageFont.truetype('simsun.ttf',14)
 		output_text = '当前方向:%i'%__snakeDir__
 		draw.text((0,0),unicode(output_text ,'utf-8'),font=font_zh, fill=255)
		draw.rectangle((__snakeHeadX__,__snakeHeadY__,__snakeHeadX__+4,__snakeHeadY__+4),outline=255,fill=0)
		if __snakeDir__ == 3:
			__snakeHeadX__ += 4
			if __snakeHeadX__ >= 124:
				__snakeHeadX__ -= 4
		if __snakeDir__ == 9:
			__snakeHeadX__ -= 4
			if __snakeHeadX__ <= 0:
				__snakeHeadX__ += 4
		if __snakeDir__ == 6:
			__snakeHeadY__ += 4
			if __snakeHeadY__ >= 60:
				__snakeHeadY__ -= 4
		if __snakeDir__ == 12:
			__snakeHeadY__ -= 4
			if __snakeHeadY__ <= 0:
				__snakeHeadY__ += 4
		disp.image(image)
		disp.display()
		# 绘图 END
		if select.select([sys.stdin],[],[],0) == ([sys.stdin],[],[]):
			c = sys.stdin.read(1)
			if c == '\x1b': break
			sys.stdout.write(c)
			sys.stdout.flush()
	termios.tcsetattr(sys.stdin,termios.TCSADRAIN,old_settings)
	print "*** As always,have a nice day ***"
	print "*** clean up ***"
	GPIO.cleanup()
