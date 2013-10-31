import os
os.environ['http_proxy']=''
import pygame
import time
import random
from facebook_client import facebook_client
from facebook_client import FaceBookException
from subprocess import call
import fbk_friend  
import serial
import binascii

SPACER_OFFSET = 5
NAME_SIZE = 48
TEXT_SIZE = 40

def splitText(txt, n):
	split_text = txt.split(' ')
	text_list = []
	cur_txt = ''
	i = 0
	while i < len(split_text):
		if len(split_text[i]) >= n: # long words makes my life difficult
			text_list.append(split_text[i])
			i = i + 1
			continue 
		while i < len(split_text) and len(cur_txt)+len(split_text[i]) < n:
			cur_txt = cur_txt+' '+split_text[i]
			i = i + 1
		text_list.append(cur_txt)
		cur_txt = ''	
	
	return text_list
 
class pyscope :
    screen = None;
    
    def __init__(self):
        "Ininitializes a new pygame screen using the framebuffer"
        # Based on "Python GUI in Linux frame buffer"
        # http://www.karoltomala.com/blog/?p=679
        disp_no = os.getenv("DISPLAY")
        if disp_no:
            print "I'm running under X display = {0}".format(disp_no)
        
        # Check which frame buffer drivers are available
        # Start with fbcon since directfb hangs with composite output
        drivers = ['fbcon', 'directfb', 'svgalib']
        found = False
        for driver in drivers:
            # Make sure that SDL_VIDEODRIVER is set
            if not os.getenv('SDL_VIDEODRIVER'):
                os.putenv('SDL_VIDEODRIVER', driver)
            try:
                pygame.display.init()
            except pygame.error:
                print 'Driver: {0} failed.'.format(driver)
                continue
            found = True
            break
    
        if not found:
            raise Exception('No suitable video driver found!')
        
        self.size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        print "Framebuffer size: %d x %d" % (self.size[0], self.size[1])
        self.screen = pygame.display.set_mode(self.size, pygame.FULLSCREEN)
        # Clear the screen to start
        self.screen.fill((0, 0, 0))
	self.bls = None        
        # Initialise font support
        pygame.font.init()
	#disable mouse cursor display
	pygame.mouse.set_visible(False)
        # Render the screen
        pygame.display.update()
	self.ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=0.1) 

    def __del__(self):
        "Destructor to make sure pygame shuts down, etc."

    def clearLedBuffer(self):
	 self.buffer = [0x00]*14
		
    def setLed(self, index, color): 
	self.buffer[index] = color	

    def writeLeds(self):
	self.ser.write(self.buffer)

    def getKey(self):
	key = 0
	while True:
		line = self.ser.readline()
		#print str(line)
		if not line : break
		for c in line:
			if c != 'O' and c != 'K' and c != '\n' and c != '\r':
				key = c
	try:
		return ord(key)
	except TypeError:
		return key

    def showBlason(self):
	if self.bls == None:
		self.bls = pygame.image.load("/root/blason.jpg")
	title_font = pygame.font.SysFont("monospace", 72, True)
	background = (255, 255, 255)
	title_background = (164, 164, 164)
	for i in range(-160, 0, 2):
        	self.screen.fill(background)
		self.screen.blit(self.bls, self.bls.get_rect().move((self.size[0]/2)-(self.bls.get_rect().width/2)+i, 0))
		pygame.display.update()
	title = title_font.render('Mamie Book', 1, (0,0,0))
	self.screen.fill(title_background, title.get_rect().move(((self.size[0]/2)-(title.get_rect().width/2) , 70)).inflate(20, 10))
        self.screen.blit(title, ((self.size[0]/2)-(title.get_rect().width/2), 70) )
	pygame.display.update()
	
    def displayPhoto(self, status):
	if status == None:
                return
        background = (255, 255, 255)
        name_background = (164, 164, 164)
        self.screen.fill(background)
        offset = 10
        #img = pygame.image.load("test.jpg")
        name_font = pygame.font.SysFont("monospace", NAME_SIZE, True)
        msg_font = pygame.font.SysFont("monospace", TEXT_SIZE, True)
        split_msg = splitText(status[0], 2.5*(self.size[0]/NAME_SIZE))
	self.screen.fill(name_background, pygame.Rect(0, 0, self.size[0], (NAME_SIZE*len(split_msg))+5))
        for t in range(0, len(split_msg)):
                label_name = name_font.render(split_msg[t].decode('utf-8'), 1, (0,0,0))
                self.screen.blit(label_name, (2, offset))
                offset = offset + NAME_SIZE
        #offset = offset + SPACER_OFFSET
	call(['wget', '-O', '/tmp/fbk_img.jpg', status[3].replace('https://', 'http://')])
        call(['convert', '/tmp/fbk_img.jpg', '-resize', '340x340', '/tmp/fbk_img_resize.jpg'])
        img = pygame.image.load("/tmp/fbk_img_resize.jpg")
        self.screen.blit(img, img.get_rect().move((self.size[0]/2)-(img.get_rect().width/2) , offset))
	offset = offset + img.get_rect().height
	split_msg = splitText(status[1], 3*(self.size[0]/TEXT_SIZE))
        for t in range(0, len(split_msg)):
                label_msg = msg_font.render(split_msg[t].decode('utf-8'), 1, (0,0,0))
                self.screen.blit(label_msg, (2,offset))
                offset = offset + TEXT_SIZE	
	pygame.display.update()
	

    def displayStatus(self, status):
	if status == None:
		return 
        background = (255, 255, 255)
        name_background = (164, 164, 164)
	self.screen.fill(background)
	offset = 10
	#img = pygame.image.load("test.jpg")
	name_font = pygame.font.SysFont("monospace", NAME_SIZE, True)
	msg_font = pygame.font.SysFont("monospace", TEXT_SIZE, True)
	split_msg = splitText(status[0], 2.5*(self.size[0]/NAME_SIZE))
	self.screen.fill(name_background, pygame.Rect(0, 0, self.size[0], (NAME_SIZE*len(split_msg))+5))
	for t in range(0, len(split_msg)):
                label_name = name_font.render(split_msg[t].decode('utf-8'), 1, (0,0,0))
                self.screen.blit(label_name, (2, offset))
		offset = offset + NAME_SIZE
	offset = offset + SPACER_OFFSET
	split_msg = splitText(status[1], 3*(self.size[0]/TEXT_SIZE))
	for t in range(0, len(split_msg)):
		label_msg = msg_font.render(split_msg[t].decode('utf-8'), 1, (0,0,0))
		self.screen.blit(label_msg, (2,offset))
		offset = offset + TEXT_SIZE
	offset = offset + SPACER_OFFSET
	if len(status) > 2:
		label_media = msg_font.render(status[2], 1, (0,0,128))
		self.screen.blit(label_media, (10, offset))
		offset = offset + TEXT_SIZE
        #self.screen.blit(img, img.get_rect())
	# Update the display
        pygame.display.update()
 
# Create an instance of the PyScope class
scope = pyscope()
fbk = facebook_client()
scope.showBlason()	
time.sleep(5)
#print fbk.friendlist
while True:
	scope.clearLedBuffer()
	key = scope.getKey()
	line = key >> 4
	col = key & 0x0F
	print "col: "+str(col)+" line: "+str(line)
	for k  in fbk_friend.flist_id.keys():
		try:
			stream = fbk.getLatestStream(k)
		except FaceBookException as e:
			print str(e)+" :  Auth error !"
			continue
		if len(stream) > 0:
			scope.setLed(fbk_friend.flist_id[k]['index'] ,fbk_friend.flist_id[k]['color'])
			#print "stream received "
			if fbk_friend.flist_id[k]['key'] == key:
				if len(stream[0]) < 4:
                                        scope.displayStatus(stream[0])
                                else:
                                        scope.displayPhoto(stream[0])
	scope.writeLeds()
scope.showBlason()
time.sleep(5)
