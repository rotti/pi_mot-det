#!/usr/bin/python
import StringIO
import subprocess
import os
import time
#import datetime
from datetime import datetime
from PIL import Image

# Original code written by brainflakes and modified to exit
# image scanning for loop as soon as the sensitivity value is exceeded.
# this can speed taking of larger photo if motion detected early in scan
 
# Motion detection settings:
# need future changes to read values dynamically via command line parameter or xml file
# --------------------------
# Threshold      - (how much a pixel has to change by to be marked as "changed")
# Sensitivity    - (how many changed pixels before capturing an image) needs to be higher if noisy view
# ForceCapture   - (whether to force an image to be captured every forceCaptureTime seconds)
# filepath       - location of folder to save photos
# filenamePrefix - string that prefixes the file name for easier identification of files.
# captureDelay   - delay timer in seconds to slow down capturing. default 1 capture per second
threshold = 20
sensitivity = 140
forceCapture = True
forceCaptureTime = 60 * 60 # Once an hour
filepath = "/home/pi/mot_det/mot-pics"
filenamePrefix = "capture"
#captureDelay = 10
# File photo size settings
saveWidth = 1280
saveHeight = 960
diskSpaceToReserve = 40 * 1024 * 1024 # Keep 40 mb free on disk


# Capture a small test image (for motion detection)
def captureTestImage():
    #command = "raspistill -v -w %s -h %s -t 0 -e bmp -o -" % (100, 75)
    command = "raspistill -t 1 -w 100 -h 75 -e bmp -n -o base.bmp"
    imageData = StringIO.StringIO()
    imageData.write(subprocess.check_output(command, shell=True))
    imageData.seek(0)
    im = Image.open("base.bmp")
    buffer = im.load()
    imageData.close()
    return im, buffer


# Save a full size image to disk
def saveImage(width, height, diskSpaceToReserve):
    keepDiskSpaceFree(diskSpaceToReserve)
    time = datetime.now()
    filename = filepath + "/" + filenamePrefix + "-%04d%02d%02d%02d%02d%02d.jpg" % ( time.year, time.month, time.day, time.hour, time.minute, time.second)
    command = "raspistill --nopreview -hf -w 1296 -h 972 -t 10 -e jpg -q 15 -o " + filename
    subprocess.call(command, shell=True)
    print "Captured ", filename


# Keep free space above given level
def keepDiskSpaceFree(bytesToReserve):
    if (getFreeSpace() < bytesToReserve):
        for filename in sorted(os.listdir(".")):
            if filename.startswith(fileNamePrefix) and filename.endswith(".jpg"):
                os.remove(filename)
                print "Deleted %s to avoid filling disk" % filename
                if (getFreeSpace() > bytesToReserve):
                    return


# Get available disk space
def getFreeSpace():
    st = os.statvfs(".")
    du = st.f_bavail * st.f_frsize
    return du


# Get first image
image1, buffer1 = captureTestImage()


# Reset last capture time
lastCapture = time.time()


# added this to give visual feedback of camera motion capture activity.  Can be removed as required
os.system('clear')
print "            Motion Detection Started"
print "            ------------------------"
print "Pixel Threshold (How much)   = " + str(threshold)
print "Sensitivity (changed Pixels) = " + str(sensitivity)
print "File Path for Image Save     = " + filepath
print "---------- Motion Capture File Activity --------------"


while (True):

    # Get comparison image
    image2, buffer2 = captureTestImage()

    # Count changed pixels
    changedPixels = 0
    for x in xrange(0, 100):
        # Scan one line of image then check sensitivity for movement
        for y in xrange(0, 75):
            # Just check green channel as it's the highest quality channel
            pixdiff = abs(buffer1[x,y][1] - buffer2[x,y][1])
            if pixdiff > threshold:
                changedPixels += 1

        # Changed logic - If movement sensitivity exceeded then
        # Save image and Exit before full image scan complete
        if changedPixels > sensitivity:   
            lastCapture = time.time()

            #skip capturing at night
            t = datetime.now()
            if t.hour > 6 or t.hour < 19:
                #time.sleep(captureDelay)
                saveImage(saveWidth, saveHeight, diskSpaceToReserve)
                break
        continue

    # Check force capture
    if forceCapture:
        if time.time() - lastCapture > forceCaptureTime:
            changedPixels = sensitivity + 1
  
    # Swap comparison buffers
    image1  = image2
    buffer1 = buffer2

