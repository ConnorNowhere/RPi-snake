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

import linkList

class apple:
	def __init__(self,x,y):
		self.x = x
		self.y = y

__snakeDir__ = random.randint(1,4)*3
__snakeBody__ = linkList.LinkList()
__score__ = 0
__eatFlag__ = 0
__goFlag__ = 0
__apple__ = apple(0,0)

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
def initSnakeBody(initlen):
	global __snakeBody__
	global __snakeDir__
	#head_x = random.randint(1,32)*4
	#head_y = random.randint(1,16)*4
	head_x = 64
	head_y = 40
	for i in range(0,string.atoi(initlen)):
		if __snakeDir__ == 3:
			item = linkList.Node(head_x-4*i,head_y)
		elif __snakeDir__ == 6:
			item = linkList.Node(head_x,head_y-4*i)
		elif __snakeDir__ == 9:
			item = linkList.Node(head_x+4*i,head_y)
		elif __snakeDir__ == 12:
			item = linkList.Node(head_x,head_y+4*i)
		__snakeBody__.append(item)

def setApple(image):
	global __eatFlag__
	global __apple__
	
	if __eatFlag__ == 1:
		__eatFlag__ = 0
		x = random.randint(1,32)*4
		y = random.randint(1,16)*4
		if x >= 124:
			x = 124
		if x <= 0:
			x = 0
		if y >= 60:
			y = 60
		if y <= 20:
			y = 20
		# print "eat apple"
		__apple__.x = x
		__apple__.y = y
	
	#print __apple__.x
	#print __apple__.y
	draw = ImageDraw.Draw(image)
	x = __apple__.x
	y = __apple__.y
	draw.ellipse((x,y,x+4,y+4), outline=255, fill=0)
	return image

def drawSnakeBody(image):
	global __snakeBody__
	draw = ImageDraw.Draw(image)
	length = __snakeBody__.getlength()
	for i in range(0,length):
		t = __snakeBody__.getitem(i)
		if i == 0:
			draw.rectangle((t.cur_x,t.cur_y,t.cur_x+4,t.cur_y+4),outline=255,fill=0)
		else:
			draw.rectangle((t.cur_x,t.cur_y,t.cur_x+4,t.cur_y+4),outline=0,fill=255)
	return image

def snakeMove(curHeadX,curHeadY):
	global __snakeBody__
	length = __snakeBody__.getlength()
	for i in range(1,length):
		__snakeBody__.getitem(length-i).cur_x = __snakeBody__.getitem(length-i-1).cur_x
		__snakeBody__.getitem(length-i).cur_y = __snakeBody__.getitem(length-i-1).cur_y
	__snakeBody__.getitem(0).cur_x = curHeadX
	__snakeBody__.getitem(0).cur_y = curHeadY

def isGameOver():
	global __snakeBody__
	global __goFlag__
	length = __snakeBody__.getlength()
	dict = {}
	for i in range(0,length):
		t = __snakeBody__.getitem(i)
		index = t.cur_x + (t.cur_y - 1)*128
		if index in dict:
			__goFlag__ = 1
			break
		else:
			index = t.cur_x + (t.cur_y - 1)*128
			dict[index] = 1
	head_x = __snakeBody__.getitem(0).cur_x
	head_y = __snakeBody__.getitem(0).cur_y
	if head_x < 0 or head_y < 20 or head_x >= 128 or head_y >=64:
		__goFlag__ = 1

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "Please input command like \"sudo python snake.py 1 4\""
		print "This means that level 1 and initial snake's length = 4"
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
	# init snake body
	initSnakeBody(sys.argv[2])
	#for i in range(0,4):
	#	print "%i - %i"%(__snakeBody__.getitem(i).cur_x,__snakeBody__.getitem(i).cur_y)
	__goFlag__ = 0
	__eatFlag__ = 1 
	in_speed = sys.argv[1]
	real_speed = 1.0/(string.atof(in_speed)*10.0)
	# 非阻塞输入用于退出
	old_settings = termios.tcgetattr(sys.stdin)
	tty.setcbreak(sys.stdin.fileno())
	
	while True:
		if __goFlag__ == 1:
			image = Image.new('1',(width,height))
			draw = ImageDraw.Draw(image)
			#font_zh = ImageFont.truetype('simsun.ttf',11)
			font_zh = ImageFont.load_default()
			font_en = ImageFont.truetype('robotastic.ttf',20)
			draw.text((0,0),'http:ghost.micheal.cn',font=font_zh,fill=255)
			draw.text((25,20),'GAME',font=font_en,fill=255)
			draw.text((25,40),'OVER',font=font_en,fill=255)
			disp.image(image)
			disp.display()
			break			
		sleep(real_speed)
		# 绘图 BEGIN
		image = Image.new('1', (width, height))	
		draw = ImageDraw.Draw(image)
 		# draw screen boder
		draw.rectangle((0,20,127,63),outline=255,fill=0)
		# draw apple
		image = setApple(image)	
		cx = __snakeBody__.getitem(0).cur_x
		cy = __snakeBody__.getitem(0).cur_y
		if cx == __apple__.x and cy == __apple__.y:
			__eatFlag__ = 1
			__score__ += 10
			last = __snakeBody__.getlength()
			newNode = linkList.Node(__snakeBody__.getitem(last-1).cur_x,__snakeBody__.getitem(last-1).cur_y)
			__snakeBody__.append(newNode)
		
		# draw snake body
		image = drawSnakeBody(image)
				
		# info start
		font_zh = ImageFont.truetype('simsun.ttf',14)
		# output_text = 'cd=%i cx=%i cy=%i'%(__snakeDir__,cx,cy)
		output_text = 'Score:%i'%__score__
		draw.text((0,0),unicode(output_text ,'utf-8'),font=font_zh, fill=255)
		# draw.text((0,10),'a.x=%i a.y=%i ef=%i'%(__apple__.x,__apple__.y,__eatFlag__),font=font_zh,fill = 255)
		# info end
		if __snakeDir__ == 3:
			cx += 4
			if cx > 128:
				cx -= 4
		if __snakeDir__ == 9:
			cx -= 4
			if cx < 0:
				cx += 4
		if __snakeDir__ == 6:
			cy += 4
			if cy > 64:
				cy -= 4
		if __snakeDir__ == 12:
			cy -= 4
			if cy < 0:
				cy += 4
		snakeMove(cx,cy)
		#__snakeBody__.getitem(0).cur_x = cx
		#__snakeBody__.getitem(0).cur_y = cy
		# __snakeBody__.getitem(0).cur_dir = __snakeDir__
		disp.image(image)
		disp.display()
		isGameOver()
		# 绘图 END
		if select.select([sys.stdin],[],[],0) == ([sys.stdin],[],[]):
			c = sys.stdin.read(1)
			if c == '\x1b': break
			sys.stdout.write(c)
			sys.stdout.flush()
	termios.tcsetattr(sys.stdin,termios.TCSADRAIN,old_settings)
	
	if __goFlag__ == 1:
		print "*** Game over. Your score: %i ***"%__score__
	print "*** As always,have a nice day ***"
	print "*** clean up ***"
	raw_input("press enter to continue >>>")
	#disp.clear()
	#disp.display()
	GPIO.cleanup()
