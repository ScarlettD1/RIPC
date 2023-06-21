from datetime import datetime
import numpy as np

import cv2
from PIL import ImageDraw, Image, ImageFont

import qrcode
import barcode
from barcode.writer import ImageWriter
from pdf2image import convert_from_path

barcode.base.Barcode.default_writer_options['write_text'] = False


def create_qrcode(image, number_blank):
    data = number_blank
    code = qrcode.make(data)
    code_img = np.asarray(code, dtype='uint8') * 255
    code_img = cv2.resize(code_img, (140, 140))
    k = 0
    for i in range(40, code_img.shape[0] + 40):
        l = 0
        for j in range(70, code_img.shape[1] + 70):
            image[i, j] = code_img[k, l]
            l += 1
        k += 1
    return image


def create_barcode(image, number_blank):
    barcode_class = barcode.get_barcode_class('code128')
    barcode_image = barcode_class(number_blank, writer=ImageWriter()).render()
    barcode_img = np.asarray(barcode_image, dtype='uint8')
    barcode_img = cv2.rotate(barcode_img, cv2.ROTATE_90_CLOCKWISE)
    k = 0
    for i in range((int(image.shape[0] / 2)) - (int(barcode_img.shape[0] / 2)),
                   barcode_img.shape[0] + (int(image.shape[0] / 2)) - (int(barcode_img.shape[0] / 2))):
        l = 0
        for j in range(int(image.shape[1] - barcode_img.shape[1] / 2), image.shape[1] - 15):
            image[i, j] = barcode_img[k, l]
            l += 1
        k += 1
    return image


def create_form_number(image, number_blank):
    img = Image.new('RGB', (300, 80), color=(255, 255, 255))
    fnt = ImageFont.truetype("arial.ttf", 40)
    ImageDraw.Draw(img).text((0, 0), number_blank, font=fnt, fill=(0, 0, 0))
    text_img = np.asarray(img, dtype='uint8')
    k = 0
    for i in range(30, text_img.shape[0]):
        l = 0
        for j in range(image.shape[1] - text_img.shape[1] - 75, image.shape[1] - 75):
            image[i, j] = text_img[k, l]
            l += 1
        k += 1
    return image


def create_black_rectangle(image):
    draw = ImageDraw.Draw(image)

    sizes = [70, 70, 90, 90]

    draw.rectangle([0, 0, sizes[0], sizes[0]], fill='black')
    draw.rectangle([image.width - sizes[1], 0, image.width, sizes[1]], fill='black')
    draw.rectangle([0, image.height - sizes[2], sizes[2], image.height], fill='black')
    draw.rectangle([image.width - sizes[3], image.height - sizes[3], image.width, image.height], fill='black')

    return image


def start_generate(count_main):
    edit_blanks = []
    number_blank = str(datetime.now().time()).replace(":", "").replace(".", "")[:-2]
    for i in range(len(count_main)):
        if i + 1 < 10:
            modified_number_blank = f"{number_blank}0{i + 1}"
        else:
            modified_number_blank = f"{number_blank}{i + 1}"
        images = convert_from_path(f"File_Storage\complect\\{i + 1}.pdf", poppler_path=r"../../../soft_with_blanks/poppler-0.68.0\bin")
        image = create_qrcode(np.array(images[i]), modified_number_blank)
        image = create_barcode(image, modified_number_blank)
        image = create_form_number(image, modified_number_blank)
        pil_img = Image.fromarray(image)
        pil_img = create_black_rectangle(pil_img)
        edit_blanks.append(pil_img)

    return edit_blanks
