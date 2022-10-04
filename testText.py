import os
import pytesseract
import cv2
from PIL import Image
import imagehash
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


osb = ImageFont.truetype('./font/Oswald-Heavy-Italic.ttf', 400)
overlay = Image.open('./templates/overlay.png')
overlay_width, overlay_height = overlay.size
overlay = overlay.resize((1920, 1080))
background = Image.open('./templates/background.png')
background_width, background_height = background.size
versus = Image.open('./templates/versus.png')
versus_width, versus_height = versus.size
versus = versus.resize((1920, 1080))
# Read source image file to compare with image from videos
img = Image.open('./source.jpg')
# hgt, wid, channels = img.shape
# cimg = img[0:int(2*hgt/3), 0:wid]  # this line crops


# Draw text One
d1 = ImageDraw.Draw(img)
w, h = d1.textsize('DRAGONBYTE', font=osb)
d1.text(((0) + 10, 110), 'DRAGONBYTE',
        font=osb, fill=(0, 0, 0), spacing=-32)
w, h = d1.textsize('DRAGONBYTE', font=osb)
d1.text((0, 100), 'DRAGONBYTE',
        font=osb, fill=(255, 255, 255), spacing=-32)
img = img.rotate(2.452, expand=True)
img.show()


text = "Sample Text"
total_text_width, total_text_height = draw.textsize(text, font=font)
width_difference = desired_width_of_text - total_text_width
gap_width = int(width_difference / (len(text) - 1))
xpos = left_side_padding
for letter in text:
    draw.text((xpos, 0), letter, (0, 0, 0), font=font)
    letter_width, letter_height = draw.textsize(letter, font=font)
    xpos += letter_width + gap_width
