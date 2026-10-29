# import package pygame
from cgi import test
from functools import total_ordering
from platform import node
from tkinter.messagebox import NO
import pygame
import os
import enum
import types
from HonorsRules import GenerateModeList
from MachineClasses import Machine
from HonorsRules import Keyboard_Mapping_Dict
from pyftdi.ftdi import Ftdi
from pyftdi.spi import SpiController
from HonorsIndicator import Indicator
#import spidev





# Enable SPI using ftdi chip
Ftdi.show_devices()
devices = Ftdi.list_devices()
if len(devices)>0:
	print('FTDI Detected')
	spi_present = True
	spi = SpiController()
	spi.configure('ftdi://ftdi:232h:/1')
	spi_port = spi.get_port(cs=0, freq=250E3, mode=0)# Assuming D3 is used for chip select.
else:
	spi_present = False
	print('FTDI Not Detected. Running in Debug Mode')

msg = [0x76]

#Initialize Pygame
pygame.init()
pygame.font.init()
pygame.mixer.pre_init(44100,-16,1,1024)
pygame.mixer.init();
#Create game clock
clock = pygame.time.Clock()

# Form screen with 1280x720 size
# and with resizable
screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))  

# set title
pygame.display.set_caption('Honors Pinball Engine')

#Define starting background image
background_name = "Background_Images/Monogram.png" 

test_machine = Machine()




# run window
running = True

old_value = 0

while running:

	#Draw blank screen
	screen.fill((0, 0, 0))
	
	#Create event list and preload with time tick event
	test_event_list = [GameEvents.TIME_TICK]
	

	#This is were we would get node board info via spi and check for machine events
	#test_machine.led_states[3] = 0x01;
	#test_machine.led_states[3] = 0x01;
	write_buf = bytearray([
		test_machine.led_states[0],		#I/O Board: LED Bank 0
		test_machine.led_states[1],		#I/O Board: LED Bank 1
		test_machine.led_states[2],		#I/O Board: LED Bank 2
		0x44,							#I/0 Board: Mode 0
		test_machine.led_states[3],							#Driver Board: Driver 0
		0x66,							#Driver Board: Mode 0
		0x77,0x88,0x99,0xAA,0xBB])		#Filler to read remaining data from bridge board.

	if(test_machine.led_states[3] != 0):
		print(f'Driver States: {test_machine.led_states[3]:x}')
	####################################################
	#Parse node board data
	####################################################
	if spi_present:
		#Read data from bridge board
		node_board_events = spi_port.exchange(out=write_buf,readlen=0,start=True,stop=True,duplex=True)
		#print(node_board_events.hex())
		#test_index= 0
		#for byte in node_board_events:
		#	print(f"Byte {test_index}: {byte:x}")
		#print(hex(node_board_events[8]))
		#Loop through each possible event
		#new_value = node_board_events[7]
		#print(f'Flipper States: {node_board_events[7]:x}')
		#if old_value != new_value:
		#	print(f'Flipper States: {node_board_events[7]:x}')
		#	print(f'Falling Edges: {node_board_events[8]:x}')
		#	print(f'Rising Edges: {node_board_events[9]:x}')
		#old_value = new_value

		for event in GameEvents:
			if event.event_mask is not None:
				if event.event_mask[0]>1:
					if node_board_events[event.event_mask[0]] & event.event_mask[1]:
						print(event)
						test_event_list.append(event)
						pass

	
	#Loop through pygames events and check for key presses
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		if event.type == pygame.KEYDOWN:
			#Detect keyboard emulated events
			if event.key in Keyboard_Mapping_Dict:
				#print(event.unicode)
				print(Keyboard_Mapping_Dict[event.key])
				test_event_list.append(Keyboard_Mapping_Dict[event.key])


	#Update high level game states	
	test_machine.update(test_event_list,screen)

	# Update the display
	pygame.display.flip()
	#print(clock.get_fps())

	# Limit the frame rate
	clock.tick(30)
	
  
# quit pygame after closing window
pygame.quit()
