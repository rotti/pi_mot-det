(Cat) Motion Detection with Rasperry PI
==================================

The project initialy based on the work of
Brainflakes - https://www.raspberrypi.org/forums/viewtopic.php?t=45235
I added a few more ideas based on https://github.com/pageauc/pi-timolo

I am using the motion detection to watch the cat feeding place. So i
skip taking and processing pictures in the night time. Can't see anything :)
I just keep one picture every 5 minutes. I don't need 30 pictures of a cat
moving around the bowl...

After taking pictures i process them and upload them to google drive. When
the pictures are uploaded the PI sends a message to a Telegram chat group 
(wife and me). 

process.py is used to clean up my picture folder and to watermark/upload/inform


## Features
* process.py
  * just use one picture every x seconds (standard time=300)
  * upload pictures to google drive
  * inform about the upload via Telegram
  * watermark the pictures with timestamp
  * remove every picture taken between 18:00 and 8:00 (can't see cats in the night)
 

##Additional installation and tips
* use cron to execute process.py every n hours (I am using every 2 hours)
* put mot_det.py to your /etc/rc.local to start picture taking after PI start
* name your google drive folder like the folder where the pictures are stored ("mot-pics" in my example)
* use the google drive scripting API to clean up your google drive folder. Can be done like "cron"
* Telegram reads /home/pi/tg/tg-server.pub When executing process.py via "root cron" (sudo crontab -e) you need to copy tg-server.pub to /root
* google drive
  * ARM binary: https://github.com/odeke-em/drive/releases/tag/v0.2.8-arm-binary
  * project: https://github.com/odeke-em/drive
* Telegram for PI 
  * http://www.instructables.com/id/Telegram-on-Raspberry-Pi/
  * https://github.com/vysheng/tg
