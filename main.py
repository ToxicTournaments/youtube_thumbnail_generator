from ctypes import alignment
import os
from tokenize import String
import pytesseract
import cv2
from PIL import Image
import imagehash
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.fftpack import diff
import time

# your path may be different
pytesseract.pytesseract.tesseract_cmd = '/usr/local/Cellar/tesseract/5.2.0/bin/tesseract'

# file path of videos
video_path = '/Volumes/DiskHFS/'

cutoff = 5  # maximum bits that could be different between the hashes.
osb = ImageFont.truetype('./font/Oswald-Heavy-Italic.ttf', 108)
overlay = Image.open('./templates/overlay.png')
overlay_width, overlay_height = overlay.size
overlay = overlay.resize((1920, 1080))
background = Image.open('./templates/background.png')
background_width, background_height = background.size
versus = Image.open('./templates/versus.png')
versus_width, versus_height = versus.size
versus = versus.resize((1920, 1080))
previous_difference = 100
# Read source image file to compare with image from videos
img = cv2.imread('./source.jpg')
# hgt, wid, channels = img.shape
# cimg = img[0:int(2*hgt/3), 0:wid]  # this line crops
src_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
src_im_pil = Image.fromarray(src_img)
hash0 = imagehash.average_hash(src_im_pil)

titles = ['Pools', 'Prelims', 'Quarter-Finals',
          'Semi-Finals', 'Finals', 'Grand Finals']


# def get_names_from_fight_screen(image):
white_pixel = np.asarray([255, 255, 255])
black_pixel = np.asarray([0, 0, 0])

# def get_character_from_fight_screen(image):

# player One : image[930:987, 494:850] = (0, 255, 0)
# player Two : image[930:987, 1411:1767] = (0, 255, 0)
# Character One : image[930:987, 494:850] = (0, 255, 0)
# Character Two : image[930:987, 494:850] = (0, 255, 0)


def gen_yt_tags(p1, p2, char1, char2, set):
    tags = [p1, p2, p1 + ' vs ' + p2, p2 + ' vs ' + p1, p1 + ' ' + char1, p2 + ' ' + char2,
            'ssbu ' + char1, 'ssbu ' + char2,  char2 +
            ' ssbu', char1 + ' ssbu', char2 + ' ssbu',
            char1 + ' ultimate', char2 + ' ultimate', 'ultimate ' + char1, 'ultimate ' + char2,
            'smash ' + char1, 'smash ' + char2, char1 + ' smash', char2 + ' smash',
            set + ' ' + char1, set + ' ' + char2, char1 + ' ' + set, char2 + ' ' + set,
            'midwest ' + char1, 'midwest ' + char2, char1 + ' midwest', char2 + ' midwest', ]
    # print(tags)
    return tags


def draw_text_psd_style(draw, xy, text, font, tracking=-32, leading=None, **kwargs):
    """
    usage: draw_text_psd_style(draw, (0, 0), "Test",
                tracking=-0.1, leading=32, fill="Blue")

    Leading is measured from the baseline of one line of text to the
    baseline of the line above it. Baseline is the invisible line on which most
    letters—that is, those without descenders—sit. The default auto-leading
    option sets the leading at 120% of the type size (for example, 12‑point
    leading for 10‑point type).

    Tracking is measured in 1/1000 em, a unit of measure that is relative to
    the current type size. In a 6 point font, 1 em equals 6 points;
    in a 10 point font, 1 em equals 10 points. Tracking
    is strictly proportional to the current type size.
    """
    def stutter_chunk(lst, size, overlap=0, default=None):
        for i in range(0, len(lst), size - overlap):
            r = list(lst[i:i + size])
            while len(r) < size:
                r.append(default)
            yield r
    x, y = xy
    font_size = font.size
    lines = text.splitlines()
    if leading is None:
        leading = font.size * 1.2
    for line in lines:
        for a, b in stutter_chunk(line, 2, 1, ' '):
            w = font.getlength(a + b) - font.getlength(b)
            # dprint("[debug] kwargs")
            # print("[debug] kwargs:{}".format(kwargs))

            draw.text((x, y), a, font=font, **kwargs)
            x += w + (tracking / 1000) * font_size
        y += leading
        x = xy[0]


def get_text_of_area(x1, x2, y1, y2, image, blackOutBackground):
    # Crop image
    text = ''
    crop_img = image[x1:x2:, y1:y2]

    if blackOutBackground:
        height, width, _ = crop_img.shape

        for i in range(height):
            for j in range(width):
                # img[i, j] is the RGB pixel at position (i, j)
                # check if it's [0, 0, 0] and replace with [255, 255, 255] if so
                if not all(crop_img[i, j] >= [230, 230, 230]):
                    crop_img[i, j] = [0, 0, 0]

    # img = cv2.imread('./source.jpg')

    # img = cv2.resize(img, (600, 360))
    # print(pytesseract.image_to_string(crop_img))
    # cv2.imshow('Result', crop_img)
    # cv2.waitKey(0)

    text = pytesseract.image_to_string(crop_img, lang='eng')
    # print(text)
    return text


def generate_thumbnail(game_title, p1, p2, char1, char2, game_number):
    p1 = p1.replace('\n', '')
    p2 = p2.replace('\n', '')
    char1 = char1.replace(' \n', '')
    char2 = char2.replace(' \n', '')
    char1 = char1.replace('\n', '')
    char2 = char2.replace('\n', '')

    if char1 == 'Roy :-':
        char1 = 'Roy'
    if char2 == 'Roy :-':
        char2 = 'Roy'
    game_type = 'Ultimate Singles'
    print('Generating thumbnail for ' + game_title + ' ' + p1.replace('\n', '') + ' (' +
          char1.replace('\n', '') + ') vs ' + p2.replace('\n', '') + ' (' + char2.replace('\n', '') + ')')
    # Create a new image
    try:
        charOne = Image.open(
            './characters/' + char1.replace(' ', '_').replace('\n', '').replace(':', '').replace('-', '') + '.png')
        charOne = charOne.resize(
            (int(charOne.width / 3), int(charOne.height / 3)))
        charTwo = Image.open(
            './characters/' + char2.replace(' ', '_').replace('\n', '').replace(':', '').replace('-', '') + '.png')
        charTwo = charTwo.resize(
            (int(charTwo.width / 3), int(charTwo.height / 3)))
    except:
        print("Error: Character not found skipping")
        return

    if (p1 == " " or p1 == ""):
        p1 = 'Orb of Light'
    if (p2 == " " or p2 == ""):

        p2 = 'Orb of Light'
    # print('p1: ' + p1)
    # print('p2: ' + p2)
    img = Image.new('RGB', (1920, 1080), 'white')
    img.paste(background, (0, 0), background)

    img.paste(charOne, (int(480 - (charOne.width/2)),
              100), charOne)
    # print('width: ' + str(charOne.width))
    # print('width: ' + str(charTwo.width))
    img.paste(charTwo, (int(1440 - (charTwo.width/2)),
              100), charTwo)
    img.paste(overlay, (0, 0), overlay)
    img.paste(versus, (0, 0), versus)

    # Draw Text Image One
    drawingOne = Image.new('RGBA', (1920, 1080), (255, 255, 255, 0))
    d1 = ImageDraw.Draw(drawingOne)
    # bboxx Returns a tuple x0, y0, x1, y1
    x1, y1, x2, y2 = d1.textbbox(text=p1.upper(), font=osb,
                                 xy=(0, 0))
    # Calculate the width and height of the text
    w = x2 - x1
    h = y2 - y1
    draw_text_psd_style(font=osb, draw=d1, text=p1.upper(), xy=(
        480 - (w/2) + 6, (h/2) + 6), fill=(0, 0, 0), alignment='center')
    draw_text_psd_style(font=osb, draw=d1, text=p1.upper(), xy=(
        480 - w/2, (h/2)), fill=(255, 255, 255), alignment='center')
    drawingOne = drawingOne.rotate(
        2.452, expand=1, fillcolor=(255, 255, 255, 0), resample=Image.Resampling.BICUBIC)
    img.paste(drawingOne, (0, -146+int(h/2)), drawingOne)

    # Draw text Two
    drawingTwo = Image.new('RGBA', (1920, 1080), (255, 255, 255, 0))
    d2 = ImageDraw.Draw(drawingTwo)
    x1, y1, x2, y2 = d2.textbbox(text=p2.upper(), font=osb, xy=(0, 0))
    w = x2 - x1
    h = y2 - y1
    # d2.text((6, 6), p2.upper(),
    #         font=osb, fill=(0, 0, 0), alignment='center')
    # d2.text((0, 0), p2.upper(),
    #         font=osb, fill=(255, 255, 255), alignment='center')
    draw_text_psd_style(font=osb, draw=d2, text=p2.upper(), xy=(
        6, 6), fill=(0, 0, 0), alignment='center')
    draw_text_psd_style(font=osb, draw=d2, text=p2.upper(), xy=(
        0, 0), fill=(255, 255, 255), alignment='center')
    drawingTwo = drawingTwo.rotate(
        2.452, expand=1, fillcolor=(255, 255, 255, 0), resample=Image.Resampling.BICUBIC)
    img.paste(drawingTwo, (1440-int(w/2), -112+int(h/2)), drawingTwo)

    # Draw text Three
    drawingThree = Image.new('RGBA', (1920, 1080), (255, 255, 255, 0))
    d3 = ImageDraw.Draw(drawingThree)
    x1, y1, x2, y2 = d3.textbbox(
        text=game_title.upper(), font=osb, xy=(0, 0))
    w = x2 - x1
    h = y2 - y1
    # d3.text((6, 6), game_title.upper(),
    #         font=osb, fill=(0, 0, 0), alignment='center')
    # d3.text((0, 0), game_title.upper(),
    #         font=osb, fill=(255, 255, 255), alignment='center')
    draw_text_psd_style(font=osb, draw=d3, text=game_title.upper(), xy=(
        6, 6), fill=(0, 0, 0), alignment='center')
    draw_text_psd_style(font=osb, draw=d3, text=game_title.upper(), xy=(
        0, 0), fill=(255, 255, 255), alignment='center')
    drawingThree = drawingThree.rotate(
        2.452, expand=1, fillcolor=(255, 255, 255, 0), resample=Image.Resampling.BICUBIC)
    img.paste(drawingThree, ((480-int(w/2)),
              796+int(h/2) + int((w/300) * 2.452)), drawingThree)
    # print(w)

    # Draw text Four
    drawingFour = Image.new('RGBA', (1920, 1080), (255, 255, 255, 0))
    d4 = ImageDraw.Draw(drawingFour)
    x1, y1, x2, y2 = d4.textbbox(
        text=game_type.upper(), font=osb, xy=(0, 0))
    w = x2 - x1
    h = y2 - y1
    # w, h = d4.textsize(game_type.upper(), font=osb)
    # 810
    # d4.text((, ), game_type.upper(),
    #         font=osb, fill=(0, 0, 0), alignment='center')
    # w, h = d4.textsize(game_type.upper(), font=osb)
    # d4.text((1040, 896), game_type.upper(),
    #         font=osb, fill=(255, 255, 255), alignment='center')
    draw_text_psd_style(font=osb, draw=d4, text=game_type.upper(), xy=(
        6, 6), fill=(0, 0, 0), alignment='center')
    draw_text_psd_style(font=osb, draw=d4, text=game_type.upper(), xy=(
        0, 0), fill=(255, 255, 255), alignment='center')
    drawingFour = drawingFour.rotate(
        2.452, expand=1, fillcolor=(255, 255, 255, 0), resample=Image.Resampling.BICUBIC)
    img.paste(drawingFour, (1440 + 74 - int(w/2), 896 - int(h/2)), drawingFour)

    # img.addp1text
    # img.addp2text
    # img.addtitle
    # img.
    # img.addgamemode
    # img.show()
# game_title, p1, p2, char1, char2, game_number
    thumbnail_path = './thumbnails/' + str(game_number) + '_' + p1.replace(
        '\n', '') + '_vs_' + p2.replace('\n', '') + '/' + game_title
    if not os.path.exists('./thumbnails/' + str(game_number) + '_' + p1.replace('\n', '') +
                          '_vs_' + p2.replace('\n', '')):
        os.mkdir('./thumbnails/' + str(game_number) + '_' + p1.replace('\n', '') +
                 '_vs_' + p2.replace('\n', ''))
    img.save(thumbnail_path + '.png', 'PNG')
    img.close()
    yt_tags = gen_yt_tags(p1, p2, char1, char2, game_title)
    for tag in yt_tags:
        with open(thumbnail_path + '.txt', 'a') as f:
            f.write(tag + ', ')

    return

# def test_color_of_fight_screen(image):
#     # color a section of image green
#     image[840:937, 1320:1830] = (0, 255, 0)
#     cv2.imwrite('testgreen.jpg', image)


game_number = 0
# Read video files
for i, file in enumerate(os.listdir(video_path)):
    # ToDo: if file starts with a period skip
    if (file == '0 Full Livestream.mp4'):
        print('skipping 0 Full Livestream.mp4')
        continue
    if os.path.isfile(os.path.join(video_path, file)):
        print('Processing file: ' + file)
        # print(file)
        vidcap = cv2.VideoCapture(video_path + file)
        success, image = vidcap.read()
        count = 0
        while success:
            # save frame as JPEG file
            success, image = vidcap.read()
            if (count % 120 == 0):
                # cv2.imwrite("frame%d.jpg" % count, image)

                if (img is not None):
                    # Compare source image with frame from video
                    # If similarity is higher than 0.7, then print the video name
                    # convert image to histogram equalized image

                    height, width, channels = image.shape
                    # if image[0, 0][2] != 169:
                    #     continue
                    cimage = image[0:int(2*height/3), 0:width]
                    conimage = cv2.cvtColor(cimage, cv2.COLOR_BGR2RGB)
                    # # print(conimage[0, 0][2])
                    # if conimage[0, 0][2] != 12:
                    #     # print('skipping')
                    #     continue
                    # else:
                    #     print('Red value before: ' + str(cimage[0, 0][2]))
                    image_pil = Image.fromarray(conimage)
                    hash1 = imagehash.average_hash(image_pil)
                    difference = hash0 - hash1
                    if (difference < 20):
                        print('Difference: ' + str(difference))

                    if (previous_difference < 7 and difference >= 7):
                        print('Generating thumbnail for game: ' + str(game_number))
                        for title in titles:
                            generate_thumbnail(title,
                                               get_text_of_area(
                                                   930, 987, 494, 850, previous_image, blackOutBackground=False),
                                               get_text_of_area(
                                                   930, 987, 1411, 1767, previous_image, blackOutBackground=False),
                                               get_text_of_area(
                                                   845, 920, 440, 915, previous_image, blackOutBackground=True),
                                               get_text_of_area(
                                                   845, 920, 1355, 1830, previous_image, blackOutBackground=True),
                                               game_number
                                               )

                        game_number += 1
                        # rating = cv2.compareHist(
                        #     hist_img, hist_img2, cv2.HISTCMP_CORREL)
                        # if (cv2.compareHist(hist_img, hist_img2, cv2.HISTCMP_CORREL)):

                        # speed up the process by skipping writing frames
                        if not os.path.exists("frame_data/" + "frame" + str(count) + 'rating' + ' ' + str(abs(difference)).replace('.', '') + ".jpg"):
                            cv2.imwrite("frame_data/" + "frame" + str(count) + 'rating' +
                                        ' ' + str(abs(difference)).replace('.', '') + ".jpg", cimage)
                        else:
                            print("File 1 already exists")

                        # speed up the process by skipping writing frames
                        if not os.path.exists("frame_data/" + "frame" + str(count) + 'rating' + ' ' + str(abs(difference)).replace('.', '') + "og.jpg"):
                            cv2.imwrite("frame_data/" + "frame" + str(count) + 'rating'
                                        ' ' + str(abs(difference)).replace('.', '') + "og.jpg", img)
                        else:
                            print("File 2 already exists")
                    # print(rating)
                    # # print(file)
                    # if (difference < 20):
                    #     print('Previous difference: ' +
                    #           str(previous_difference) + '\n')
                    previous_difference = difference
                    previous_image = image

                # print('Read a new frame: ', success)
            count += 1


# Reads all text on the image and returns as a string
# Update: Read just the coordinates for the text
# custom_config = r'--oem 3 --psm 6'
# pytesseract.image_to_string(img, config=custom_config)


# for title in titles:
#     generate_thumbnail(title)
