from pathlib import Path
import os
from dotenv import load_dotenv
from flask.helpers import flash, send_file
import pyunsplash
import requests
import multiprocessing
from PIL import Image
from app.image_utils import ImageText
import csv
from app.messenger import *
import itertools
from app import bot
import pprint

load_dotenv()

size = int(os.getenv('IMAGE_SIZE'))


description = True  # make a file with hashtags and descriptio
logo_draw = False  # draw a logo on i
tag = 'holidays'  # search for this ta
user = 'sgriffle_1'  # folder name where to put i
# how many pics to search fo  # size of the iamges after edit (square
count = 100
logo_size = 64  # size of the log
logo_dis = 96  # distance of the logog to the edge in p
logo = '/Volumes/SHARED/Python/content-generator/pics/00_default/logo.JPG'
font = str(Path.cwd() / 'fonts' / 'Ubuntu-Medium.ttf')
font_author = str(Path.cwd() / 'fonts' / 'Ubuntu-RegularItalic.ttf')
font_size = 48
font_color = (200, 200, 200)
text_place = 'center'


pu = pyunsplash.PyUnsplash(
    api_key=os.getenv('UNSPLASH_API_KEY'))


def sg_get_user_path(recipient_id):
    "returns path of user folder as PosixPath"
    return Path.cwd() / 'pics' / str(recipient_id)


def sg_mkdir(recipient_id):
    "make dir for user"
    path = sg_get_user_path(recipient_id)
    if path.is_dir():
        print(path.glob('**/*'))
        [Path.unlink(file) for file in path.glob('**/*')]
    else:
        os.mkdir(path)


def sg_get_images(topic):
    "get downloadlinks for 3 img for a specific topic"

    images = pu.search(
        type_='photos', query=topic, per_page=os.getenv('NUMBER_IMAGES_GENERATED'))

    return list(images.entries)


def sg_download_imgage(recipient_id, image):
    "save img in user folder"

    image_data = requests.get(image.link_download)
    image_path = sg_get_user_path(recipient_id) / f'{image.id}.png'

    open(image_path, 'wb').write(image_data.content)

    return image_path


def sg_image_proportion(value, input, size):
    "get width and height proportions"

    scale = size/input
    return value * scale


def sg_image_resize(image_path, size):
    "resize image"

    image = Image.open(image_path)
    if image.size[0] < image.size[1]:
        width = size
        height = sg_image_proportion(image.size[1], image.size[0], size)
        h1 = (height - size)/2
        h2 = height - h1
        box = (0, h1, size, h2)
    else:
        height = size
        width = sg_image_proportion(image.size[0], image.size[1], size)
        w1 = (width - size)/2
        w2 = width - w1
        box = (w1, 0, w2, size)
    width = int(width)
    height = int(height)
    image = image.resize((width, height))
    image = image.crop(box)
    #image.save(f'{image_path}.edited.png', 'PNG')
    return image


def sg_get_quotes(topic):
    quotes = []
    with open(Path.cwd() / 'assets' / 'quotes.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for line in csv_reader:
            if len(quotes) == os.getenv('NUMBER_IMAGES_GENERATED'):
                break
            if line[2] == topic or topic in line[0]:
                if len(line[0]) < 200:
                    quotes.append({
                        'quote': line[0],
                        'author': line[1]
                    })
    return quotes


def sg_paste_gradient(image,):
    "paste gradient into a image"
    gradient = Image.open(Path.cwd() / 'assets' / 'gradient.png')
    image.paste(gradient, (0, 0), gradient)

    return image


def sg_place_quote(quot, text_place, image_path):
    quote = quot['quote']
    author = quot['author']

    text_width = size/3 * 2
    text_img_size = ImageText(
        (size, size), background=(255, 255, 255, 0))
    text_size = text_img_size.write_text_box(((size - text_width)/2, 50), quote, box_width=text_width, font_filename=font,
                                             font_size=font_size, color=font_color, place='center')
    # name size
    name_size = text_img_size.write_text_box((0, 0), author, box_width=text_width, font_filename=font_author,
                                             font_size=font_size, color=font_color, place='center')
    # make text
    text_img = ImageText((size, size), background=(255, 255, 255, 0))
    text_y = size - size/8 - text_size[1]

    # make name
    name_y = size - (size/24)*2

    if text_place == 'center':

        # make text
        text_x = (size-text_width)/2
        text_img.write_text_box((text_x, text_y), quote, box_width=text_width, font_filename=font,
                                font_size=font_size, color=font_color, place='center')
        # make name
        name_x = (size-text_width)/2
        text_img.write_text_box((name_x, name_y), author, box_width=text_width, font_filename=font_author,
                                font_size=int(font_size/2), color=font_color, place='center')
    elif text_place == 'left':
        # make text
        text_x = size/12
        text_img.write_text_box((text_x, text_y), quote, box_width=text_width, font_filename=font,
                                font_size=font_size, color=font_color, place='left')
        # make name
        text_img.write_text_box((text_x, name_y), author, box_width=text_width, font_filename=font_author,
                                font_size=int(font_size/2), color=font_color, place='left')
    elif text_place == 'right':
        # make text
        text_x = ((size/12)*11)-text_width
        text_img.write_text_box((text_x, text_y), quote, box_width=text_width, font_filename=font,
                                font_size=font_size, color=font_color, place='right')
        # make name
        name_x = ((size/12)*11)-name_size[0]
        text_img.write_text_box((name_x, name_y), author, box_width=text_width, font_filename=font_author,
                                font_size=int(font_size/2), color=font_color, place='right')

    text_img_path = f'{image_path}.text.png'
    text_img.save(text_img_path)
    text_img = Image.open(text_img_path)
    os.remove(text_img_path)

    return text_img


def sg_edit_image(recipient_id, image, quote):
    "Edits image in a row"
    image_path = sg_download_imgage(recipient_id, image)
    image = sg_image_resize(image_path, int(os.getenv('IMAGE_SIZE')))
    image = sg_paste_gradient(image)
    text_img = sg_place_quote(quote, text_place, image_path)
    image.paste(text_img, (0, 0), text_img)
    edited_image_path = f'{image_path}.edited.png'
    image.save(edited_image_path, 'PNG')
    print('edited image respones')
    pprint.pprint(bot.send_image(
        recipient_id, str(edited_image_path)))


def sg_edit_images(recipient_id, topic):
    images = sg_get_images(topic)
    quotes = sg_get_quotes(topic)

    if not images:
        bot.send_text_message(
            recipient_id, """Sorry, I didn't found enough images :( Try another more general topic!""")
        return "Not enough images"

    sg_mkdir(recipient_id)

    processes = []
    for image, quote in itertools.zip_longest(images, quotes):
        if not image:
            return "edited all images"
        process = multiprocessing.Process(
            target=sg_edit_image, args=[recipient_id, image, quote])
        process.start()
        # process.join()
        processes.append(process)

    [process.join() for process in processes]

    return "Edited Images "
