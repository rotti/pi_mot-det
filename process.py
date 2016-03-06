#!/usr/bin/python

import glob
import os
from datetime import datetime
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


path = "/home/pi/mot_det/mot-pics/" #path where images are stored
wildcard = "*.jpg" # *.filetype
imageWidth = 1280
imageHeight = 960
font_type = '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf'
font = ImageFont.truetype(font_type, 22, encoding='unic')


#extract time_flags from pic-filenames and sort list
def extract_timestamp(files):
    extracted_timestamp = []
    for f in files:
        timestamp = int(filter(str.isdigit, f))
        extracted_timestamp.append(timestamp)
    extracted_timestamp.sort()
    return extracted_timestamp

#replace XXX with telegram channel and your google drive folder
def upload_and_inform(pic_amount):
    up2gdrive = '/home/pi/mot_det/gdrive push -no-prompt -ignore-conflict ' + path + wildcard
    tg_msg = '/home/pi/tg/bin/telegram-cli -k /home/pi/tg/tg-server.pub -W -e "msg XXX ' + str(pic_amount) + ' new pics! look @ XXX"'
    os.system(up2gdrive)
    os.system(tg_msg)


def cleanup_pictures(leftover_pics):
    for f in leftover_pics:
        os.remove(f)


def collect_pictures(files):
    return glob.glob(files)


def watermark_pictures(leftover_pics):
    rawtexts = extract_timestamp(leftover_pics)
    for raws in rawtexts:
        mark_image(restore_filename(raws), image_text(raws))


def mark_image(imagename, text):
    x = (imageWidth/10) - 100
    y = (imageHeight - 20)
    text_color = ( 155, 155, 155 )

    image = Image.open(imagename)
    mark = ImageDraw.Draw(image)
    mark.text(( x, y ), text, text_color, font=font)
    image.save(imagename)


def image_text(text):   
    text = str(text)
    text = text.decode('utf-8')
    text = (text[0:4] + "-" + text[4:6] + "-" + text[6:8] + ", " + 
           text[8:10] + ":" + text[10:12] + ":" + text[12:14])
    return text


def restore_filename(timestamp):
    fullname = path + "capture-" + str(timestamp) + ".jpg"
    return fullname


#store jpgs in list and reverse them
filenames = collect_pictures(path + wildcard)
if len(filenames) > 1:
    filenames.sort()
    filenames = filenames[::-1]

    time_flags = extract_timestamp(filenames)

    #define some lists
    time_flags_orig = time_flags
    pics2keep = []
    pics2delete = []

    #always keep the first pic & delete last pic
    pics2keep.append(time_flags[0])
    pics2delete.append(time_flags[-1])

    #define how many seconds the interval should be
    time = 300

    #go backwards through the pics and invest time interval between them
    #always compare last to second last pic timestamp
    #keep the last one in list if interval is ok and remove it aferwards
    for i in time_flags:
        interval = time_flags[-1] - time_flags[-2]
      
        #keep good pics
        if interval > time:
            pics2keep.append(time_flags[-1])
  
        #remove last element and reverse/sort afterwards
        del time_flags[-1]
        time_flags = time_flags[::-1]
        time_flags.sort()

    pics2keep.sort()
    
    #find out which pics we delete immediately
    pics2delete = list(set(time_flags_orig) - set(pics2keep))

    #also delete pics between 18:00 to 8:00 because the night is dark and full of terrors
    #we know the hour of the picture in the timestamp: YYYYMMDDHHMMSS
    for bad_hours in pics2keep:
        hour = int(repr(bad_hours)[-7:-5])
        if hour <=8 or hour >=18:
            pics2delete.append(bad_hours)

    for f in pics2delete:
        f = restore_filename(f)
        #print "remove" ,f
        os.remove(f)

else:
    print path, " is empty. no pictures found. ", str(datetime.now())


#mark image with date
#upload all pictures to google drive, inform via telegram and delete afterwards
leftover_pics = collect_pictures(path + wildcard)
if leftover_pics:
     print "processing ... ", str(datetime.now())
     watermark_pictures(leftover_pics)  
     upload_and_inform(len(leftover_pics))
     cleanup_pictures(leftover_pics)
else:
     print "nothing to upload and to inform about. ", str(datetime.now())
