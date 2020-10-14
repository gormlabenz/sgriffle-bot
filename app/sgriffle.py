import logging
from pathlib import Path
import os
from dotenv import load_dotenv
import pyunsplash
import requests
import multiprocessing
from PIL import Image, ImageFont, ImageDraw
from app.image_utils import ImageText
import csv
import glob

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

size = 1080


description = True  # make a file with hashtags and descriptio
logo_draw = False  # draw a logo on i
tag = 'holidays'  # search for this ta
user = 'sgriffle_1'  # folder name where to put i
# how many pics to search fo  # size of the iamges after edit (square
count = 100
logo_size = 64  # size of the log
logo_dis = 96  # distance of the logog to the edge in p
logo = '/Volumes/SHARED/Python/content-generator/pics/00_default/logo.JPG'
font = 'Ubuntu-Medium.ttf'
font_author = 'Ubuntu-RegularItalic.ttf'
font_size = 48
font_color = (200, 200, 200)
text_place = 'center'


pu = pyunsplash.PyUnsplash(
    api_key=os.getenv('UNSPLASH_API_KEY'))


def sg_mkdir(user_id):
    "make dir for user"
    path = Path.cwd() / 'pics' / str(user_id)
    if path.is_dir():
        print(path.glob('**/*'))
        [Path.unlink(file) for file in path.glob('**/*')]
    else:
        os.mkdir(path)


def sg_get_images(topic):
    "get downloadlinks for 3 img for a specific topic"

    images = pu.search(
        type_='photos', query=topic, per_page=3)

    return images.entries


def sg_download_imgage(downloadlink, image_path):
    "save img in user folder"

    image = requests.get(downloadlink)
    open(image_path, 'wb').write(image.content)


def sg_download_imgages(topic, user_id):
    "Bulk download images via multiprocessing"

    processes = []
    image_paths = []
    images = sg_get_images(topic)

    sg_mkdir(user_id)

    for image in images:
        image_path = Path.cwd() / 'pics' / user_id / f'{image.id}.png'
        process = multiprocessing.Process(target=sg_download_imgage, args=[
                                          image.link_download, image_path])
        process.start()
        processes.append(process)
        image_paths.append(image_path)

    [process.join() for process in processes]

    if image_paths:
        return image_paths
    else:
        return logging.warning('Not enough images')


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
    image.save(image_path, 'JPEG')


def sg_images_resize(image_paths, size):
    "Buld resizing of images"

    processes = []

    for image_path in image_paths:
        process = multiprocessing.Process(
            target=sg_image_resize, args=[image_path, size])
        process.start()
        processes.append(process)

    [process.join() for process in processes]


def sg_get_quotes(topic):
    quotes = []
    with open(Path.cwd() / 'quotes_en.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for line in csv_reader:
            if len(quotes) == 3:
                break
            if line[2] == topic or topic in line[0]:
                if len(line[0]) < 200:
                    quotes.append({
                        'quote': line[0],
                        'author': line[1]
                    })
    return quotes


def sg_paste_gradient(image_path):
    "paste gradient into a image"
    gradient = Image.open(Path.cwd() / 'templates' / 'gradient.png')
    image = Image.open(image_path)

    gradient = gradient.resize((image.size))
    image.paste(gradient, (0, 0), gradient)

    return image


def sg_place_quote(quot, text_place):
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

    return text_img


def sg_quote_image(image_path, text_place, quot, font_size, font, font_author, font_color):
    # place text
    text_img = sg_place_quote(quot, text_place)

    text_path = image_path + '.text.png'
    text_img.save(text_path)

    return text_path


def sg_paste_quote(image_path, text_place, quot, font_size, font, font_author, font_color):
    # define variables

    text_img = sg_quote_image(image_path, text_place,
                              quot, font_size, font, font_author, font_color)

    # text_img.save(image_path)
    # gradient
    image = Image.open(image_path)
    image = sg_paste_gradient(image_path)
    # paste text
    text_img = Image.open(text_img)
    image.paste(text_img, (0, 0, size, size), text_img)
    image.save(image_path)

    """ # paste logo
    if self.get('logo_draw'):
        image.paste(Image.open(self.logo), (0,0,100,100), self.get('logo'))
    # save image
    image.save(os.path.join(self.pics, f'{index}.jpg'))
    # make description file
    if self.get('description'):
        self.save_description(index)
    else:
        self.description_print = '' """
    print(f'Saved photo')


if __name__ == "__main__":
    sg_mkdir('1')
    image_paths = sg_download_imgages('hate', '1')
    print(image_paths)
    sg_images_resize(image_paths, size)
    quote = {'quote': 'Hurray, finaaly we did it!', 'author': 'Gorm Labenz'}
    [sg_paste_quote(str(image_path), 'left', quote, font_size,
                    font, font_author, font_color) for image_path in image_paths]
