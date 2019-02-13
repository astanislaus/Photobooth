import pygame
import time
import os
import PIL.Image
import cups
import pifaceio

from threading import Thread
from pygame.locals import *
from time import sleep
from PIL import Image, ImageDraw

import RPi.GPIO as GPIO, time, os, subprocess,shlex

 
# initialise global variables
Numeral = ""  # Numeral is the number display
Message = ""  # Message is a fullscreen message
BackgroundColor = ""
CountDownPhoto = ""
CountPhotoOnCart = "" 
SmallMessage = ""  # SmallMessage is a lower banner message
TotalImageCount = 0  # Counter for Display and to monitor paper usage
PhotosPerCart = 30  # Selphy takes 16 sheets per tray
imagecounter = 0
imagefolder = 'Photos'
templatePath = os.path.join('Photos', 'Template', "template.png") #Path of template image
ImageShowed = False
Printing = False
BUTTON_PIN = 25
#IMAGE_WIDTH = 558
#IMAGE_HEIGHT = 374
IMAGE_WIDTH = 550
IMAGE_HEIGHT = 360 


# Load the background template
bgimage = PIL.Image.open(templatePath)

# initialise pygame
pygame.init()  # Initialise pygame
print("# Initialise pygame -- OK")
pygame.mouse.set_visible(False) #hide the mouse cursor
print("#hide the mouse cursor -- OK")
infoObject = pygame.display.Info()
print("pygame.display.Info() -- OK")
screen = pygame.display.set_mode((infoObject.current_w,infoObject.current_h), pygame.FULLSCREEN)  # Full screen 
print("# Full screen -- OK")
background = pygame.Surface(screen.get_size())  # Create the background object
print("# Create the background object -- OK")
background = background.convert()  # Convert it to a background
print("# Convert it to a background -- OK")

screenPicture = pygame.display.set_mode((infoObject.current_w,infoObject.current_h), pygame.FULLSCREEN)  # Full screen
backgroundPicture = pygame.Surface(screenPicture.get_size())  # Create the background object
backgroundPicture = background.convert()  # Convert it to a background

transform_x = infoObject.current_w # how wide to scale the jpg when replaying
transfrom_y = infoObject.current_h # how high to scale the jpg when replaying


# A function to handle keyboard/mouse/device input events
print("# A function to handle keyboard/mouse/device input events -- commented out OK")
def input(events):
    for event in events:  # Hit the ESC key to quit the slideshow.
        if (event.type == QUIT or
                (event.type == KEYDOWN and event.key == K_ESCAPE)):
            pygame.quit()


# set variables to properly display the image on screen at right ratio
def set_demensions(img_w, img_h):
	# Note this only works when in booting in desktop mode. 
	# When running in terminal, the size is not correct (it displays small). Why?

    # connect to global vars
    global transform_y, transform_x, offset_y, offset_x

    # based on output screen resolution, calculate how to display
    ratio_h = (infoObject.current_w * img_h) / img_w 

    if (ratio_h < infoObject.current_h):
        #Use horizontal black bars
        #print "horizontal black bars"
        transform_y = ratio_h
        transform_x = infoObject.current_w
        offset_y = (infoObject.current_h - ratio_h) / 2
        offset_x = 0
    elif (ratio_h > infoObject.current_h):
        #Use vertical black bars
        #print "vertical black bars"
        transform_x = (infoObject.current_h * img_w) / img_h
        transform_y = infoObject.current_h
        offset_x = (infoObject.current_w - transform_x) / 2
        offset_y = 0
    else:
        #No need for black bars as photo ratio equals screen ratio
        #print "no black bars"
        transform_x = infoObject.current_w
        transform_y = infoObject.current_h
        offset_y = offset_x = 0

def InitFolder():
    global imagefolder
    global Message
 
    Message = 'Folder Check...'
    UpdateDisplay()
    Message = ''
    print(Message)
    #check image folder existing, create if not exists
    if not os.path.isdir(imagefolder):	
        os.makedirs(imagefolder)	
            
    imagefolder2 = os.path.join(imagefolder, 'images')
    if not os.path.isdir(imagefolder2):
        os.makedirs(imagefolder2)

def DisplayText(fontSize, textToDisplay):
    global Numeral
    global Message
    global screen
    global background
    global pygame
    global ImageShowed
    global screenPicture
    global backgroundPicture
    global CountDownPhoto

    if (BackgroundColor != ""):
            #print(BackgroundColor)
            background.fill(pygame.Color("black"))
    if (textToDisplay != ""):
            #print(displaytext)
            font = pygame.font.Font(None, fontSize)
            text = font.render(textToDisplay, 1, (227, 157, 200))
            textpos = text.get_rect()
            textpos.centerx = background.get_rect().centerx
            textpos.centery = background.get_rect().centery
            if(ImageShowed):
                    backgroundPicture.blit(text, textpos)
            else:
                    background.blit(text, textpos)

def UpdateDisplay():
    # init global variables from main thread
    global Numeral
    global Message
    global screen
    global background
    global pygame
    global ImageShowed
    global screenPicture
    global backgroundPicture
    global CountDownPhoto
   
    background.fill(pygame.Color("white"))  # White background
    DisplayText(100, Message)
    DisplayText(800, Numeral)
    DisplayText(500, CountDownPhoto)

    if (BackgroundColor != ""):
            print(BackgroundColor)
            background.fill(pygame.Color("black"))
    if (Message != ""):
            #print(Displaytext)
            font = pygame.font.Font(None, 100)
            text = font.render(Message, 1, (227, 157, 200))
            textpos = text.get_rect()
            textpos.centerx = background.get_rect().centerx
            textpos.centery = background.get_rect().centery
            if(ImageShowed):
                    backgroundPicture.blit(text, textpos)
            else:
                    background.blit(text, textpos)

    if (Numeral != ""):
            #print(displaytext)
            font = pygame.font.Font(None, 800)
            text = font.render(Numeral, 1, (227, 157, 200))
            textpos = text.get_rect()
            textpos.centerx = background.get_rect().centerx
            textpos.centery = background.get_rect().centery
            if(ImageShowed):
                    backgroundPicture.blit(text, textpos)
            else:
                    background.blit(text, textpos)

    if (CountDownPhoto != ""):
            #print(displaytext)
            font = pygame.font.Font(None, 500)
            text = font.render(CountDownPhoto, 1, (227, 157, 200))
            textpos = text.get_rect()
            textpos.centerx = background.get_rect().centerx
            textpos.centery = background.get_rect().centery
            if(ImageShowed):
                    backgroundPicture.blit(text, textpos)
            else:
                    background.blit(text, textpos)
    
    if(ImageShowed == True):
    	screenPicture.blit(backgroundPicture, (0, 0))   	
    else:
    	screen.blit(background, (0, 0))
   
    pygame.display.flip()
    return


def ShowPicture(file, delay):
    global pygame
    global screenPicture
    global backgroundPicture
    global ImageShowed
    backgroundPicture.fill((0, 0, 0))
    img = pygame.image.load(file)
    img = pygame.transform.scale(img, screenPicture.get_size())  # Make the image full screen
    #backgroundPicture.set_alpha(200)
    backgroundPicture.blit(img, (0,0))
    screen.blit(backgroundPicture, (0, 0))
    pygame.display.flip()  # update the display
    ImageShowed = True
    time.sleep(delay)

# display one image on screen
def show_image(image_path):	
	screen.fill(pygame.Color("white")) # clear the screen	
	img = pygame.image.load(image_path) # load the image
	img = img.convert()	
	set_demensions(img.get_width(), img.get_height()) # set pixel dimensions based on image	
	x = (infoObject.current_w / 2) - (img.get_width() / 2)
	y = (infoObject.current_h / 2) - (img.get_height() / 2)
	screen.blit(img,(x,y))
	pygame.display.flip()

def CapturePicture():
    global imagecounter
    global imagefolder
    global Numeral
    global Message
    global screen
    global background
    global screenPicture
    global backgroundPicture
    global pygame
    global ImageShowed
    global CountDownPhoto
    global BackgroundColor

    BackgroundColor = ""
    Numeral = ""
    Message = ""
    UpdateDisplay()
#    time.sleep(1)
    CountDownPhoto = ""
    UpdateDisplay()
    background.fill(pygame.Color("black"))
    screen.blit(background, (0, 0))
    pygame.display.flip()
#    camera.start_preview()
    BackgroundColor = "black"


    # Construct Unique Filename using time and image number
    imagecounter = imagecounter + 1
    ts = time.time()
    filename = os.path.join(imagefolder, 'images', str(imagecounter)+"_"+str(ts) + '.jpg')
    print(filename)
    gphoto2CmdLine = "gphoto2 --capture-image-and-download --filename " + filename
    print(gphoto2CmdLine)
    args = shlex.split(gphoto2CmdLine)
    print(args)

    #these links are helpful for understanding the details of Popen (process open)
    #https://docs.python.org/2/library/subprocess.html#subprocess.Popen
    #https://www.programcreek.com/python/example/50/subprocess.Popen

    gpout = subprocess.Popen(args)
    print(gpout)
    print("Starting Camera Capture...")

    # Count down from 3 to 1 before  picture is actually taken
    # 3s is OK for Nikon Coolpix but will be different for other cameras
    for x in range(3, -1, -1):
        if x == 0:                        
                Numeral = ""
                Message = "Strike Your Pose !!"
        else:                        
                Numeral = str(x)
                Message = ""                
        UpdateDisplay()
        time.sleep(1)

   # time.sleep(3)
    Message = "Great Shot !"
    print(Message)
    UpdateDisplay()
    time.sleep(1)
    Message = "Now relax While I fetch the photo"
    print(Message)
    UpdateDisplay()
    time.sleep(5)
    Message = "Nearly there..."
    print(Message)
    UpdateDisplay()

    gpout1=gpout.wait()
    print(gpout1)
    print("GPHOTO2 is done")

#    if "ERROR" not in gpout1: 
#                 snap += 1
#                 GPIO.output(POSE_LED, False)
#                 time.sleep(0.5)
#                 print("please wait while your photos print...")
    ShowPicture(filename, 2)
    ImageShowed = False
    return filename

def TakePictures():
    global imagecounter
    global imagefolder
    global Numeral
    global Message
    global screen
    global background
    global pygame
    global ImageShowed
    global CountDownPhoto
    global BackgroundColor
    global Printing
    global PhotosPerCart
    global TotalImageCount

    input(pygame.event.get())
    CountDownPhoto = "1/3"        
    filename1 = CapturePicture()

    CountDownPhoto = "2/3"
    filename2 = CapturePicture()

    CountDownPhoto = "3/3"
    filename3 = CapturePicture()

    CountDownPhoto = ""
    Message = "Wait Please..."
    UpdateDisplay()


    basewidth = 570 #575

    #image1 = PIL.Image.open(filename1)
    image1 = Image.open(filename1)
    wpercent = (basewidth / float(image1.size[0]))
    hsize = int((float(image1.size[1]) * float(wpercent)))
    image1 = image1.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
    #img.save(filename)

    #image2 = PIL.Image.open(filename2)
    image2 = Image.open(filename2)
    wpercent = (basewidth / float(image2.size[0]))
    hsize = int((float(image2.size[1]) * float(wpercent)))
    image2 = image2.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
    #img.save(filename)

    #image3 = PIL.Image.open(filename3)   
    image3 = Image.open(filename3)
    wpercent = (basewidth / float(image3.size[0]))
    hsize = int((float(image3.size[1]) * float(wpercent)))
    image3 = image3.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
    #img.save(filename)    
    
    
    
    TotalImageCount = TotalImageCount + 1

    bgimage.paste(image1, (600, 0))     #bgimage.paste(image1, (625, 30))
    bgimage.paste(image2, (600, 400))   #bgimage.paste(image2, (625, 405))
    bgimage.paste(image3, (30, 400))     #bgimage.paste(image3, (55, 405))
    # Create the final filename
    ts = time.time()
    Final_Image_Name = os.path.join(imagefolder, "Final_" + str(TotalImageCount)+"_"+str(ts) + ".jpg")
    print(Final_Image_Name)
    # Save it to the usb drive
    bgimage.save(Final_Image_Name)
    # Save a temp file, its faster to print from the pi than usb
    bgimage.save('/home/pi/Desktop/tempprint.jpg')
    ShowPicture('/home/pi/Desktop/tempprint.jpg',3)
    #bgimage2 = bgimage.rotate(90)
    #bgimage2.save('/home/pi/Desktop/tempprint.jpg')
    ImageShowed = False
    Message = "Press and hold Button to Print"
    UpdateDisplay()
#    time.sleep(1)
    Message = ""
    UpdateDisplay()
    Printing = False
    WaitForPrintingEvent()
    Numeral = ""
    Message = ""
    print(Printing)
    if Printing:
            if (TotalImageCount <= PhotosPerCart):
                    if os.path.isfile('/home/pi/Desktop/tempprint.jpg'):
                            # Open a connection to cups
                            conn = cups.Connection()
                            # get a list of printers
                            printers = conn.getPrinters()
                            # select printer 0
                            printer_name = printers.keys()[0]
                            print(printer_name)
                            printer_name = printers.keys()[1]
                            print(printer_name)
                            printer_name = printers.keys()[2]
                            print(printer_name)
                            printer_name = "Photos_10cm_x_15cm"
			    Message = "Let's Print That Masterpiece!"  #Using Printer name  : " + printer_name
                            UpdateDisplay()
                            time.sleep(0.1)
                            # print the buffer file
                            printqueuelength = len(conn.getJobs())
                            if printqueuelength > 1:
                                    ShowPicture('/home/pi/Desktop/tempprint.jpg',3)
                                    conn.enablePrinter(printer_name)
                                    Message = "Hmm, I've had a problem"                
                                    UpdateDisplay()
                                    time.sleep(1)
                            else:
                                    conn.printFile(printer_name, '/home/pi/Desktop/tempprint.jpg', "PhotoBooth", {})
                                    time.sleep(40)            
            else:
                    Message = "Nous vous enverrons vos photos"
                    Numeral = ""
                    UpdateDisplay()
                    time.sleep(1)
                
    Message = ""
    Numeral = ""
    ImageShowed = False
    UpdateDisplay()
    time.sleep(1)

def MyCallback(channel):
    global Printing
    GPIO.remove_event_detect(BUTTON_PIN)
    Printing=True

def WaitForPrintingEvent():
    global BackgroundColor
    global Numeral
    global Message
    global Printing
    global pygame
    pf = pifaceio.PiFace()
    countDown = 10
#    GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING)
#    GPIO.add_event_callback(BUTTON_PIN, MyCallback)
    
    while Printing == False and countDown > 0:
        
        pf.read()
        input_state = pf.read_pin(0) 
#        print(input_state) # is True")
        if input_state == True:
 #           print("input_state is True (button has been pressd)")
 #           print(input_state)
            Printing = True
#            pygame.quit()
            return

        if(Printing == True):
            return
        for event in pygame.event.get():			
            if event.type == pygame.KEYDOWN:				
                if event.key == pygame.K_DOWN:
 #                   GPIO.remove_event_detect(BUTTON_PIN)
                    Printing = True
                    return        
        BackgroundColor = ""
        Numeral = str(countDown)
        Message = "Press and hold button to print!"
        UpdateDisplay()        
        countDown = countDown - 1
        time.sleep(0.5)

 #   GPIO.remove_event_detect(BUTTON_PIN)


def WaitForEvent():
    global pygame
    pf = pifaceio.PiFace()
    NotEvent = True
    while NotEvent:
        pf.read()
        input_state = pf.read_pin(0) #False #windows10 GPIO.input(BUTTON_PIN)


        if input_state == True:
 #           print("NoEvent is True")
 #           print(input_state)
            NotEvent = False
            return

        for event in pygame.event.get():   
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                if event.key == pygame.K_DOWN:
                    NotEvent = False
                    return
        time.sleep(0.2)

def main(threadName, *args):
 #   print("main(threadName, *args) --Starting Mainthread ")
    InitFolder()
 #   print("InitFolder() -- OK ")
    while True:
        show_image('images/start_camera.jpg')
        WaitForEvent()
        time.sleep(1)
        TakePictures()


# launch the main thread
Thread(target=main, args=('Main', 1)).start()

