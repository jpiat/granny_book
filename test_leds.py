import serial
import time


color_table = {'black' : 0x00, 'white' : 0x07, 
		'red' : 0x01, 'lime' : 0x04, 
		'blue' : 0x02, 'yellow' : 0x03, 'cyan' : 0x06, 
		'magenta' : 0x05}


ser = serial.Serial('/dev/ttyAMA0', 9600)
buffer = [0x00]*14
i = 0
for j in range(0, 14):
	buffer[j] =color_table[color_table.keys()[i]]
	i = i + 1
	if i >= len(color_table):
		i = 0
ser.write(buffer)
time.sleep(5)
while True:
	for i in range(0, 14):
		buffer = [0x00]*14
		buffer[i] = 0x07
		ser.write(buffer)
		time.sleep(0.05)
