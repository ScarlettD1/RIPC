from pdf2image import convert_from_path
import cv2
import numpy as np
from PIL import Image

from tensorflow import keras

emnist_labels = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122]
model = keras.models.load_model('emnist_model3.h5')


def pruning_blank(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    min_x = image.shape[1]
    min_y = image.shape[0]
    max_x = max_y = 0

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        min_x = min(min_x, x)
        min_y = min(min_y, y)
        max_x = max(max_x, x + w)
        max_y = max(max_y, y + h)

    cropped_image = image[min_y:max_y, min_x:max_x]

    return cropped_image


def find_contours(img):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray, (1, 1), 0)

    thresh_inv = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    contours = cv2.findContours(thresh_inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

    array_task_numbers = np.empty((0, 4), dtype=np.uint32)

    mask = np.ones(img.shape[:2], dtype="uint8") * 255

    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if 900 < w * h < 1300:
            cv2.rectangle(mask, (x, y), (x + w, y + h), (0, 0, 255), -1)
            array_task_numbers = np.append(array_task_numbers, np.array([[y, x, h, w]], dtype=np.uint32), axis=0)
    dict_y = {}
    for i, array in enumerate(array_task_numbers):
        dict_y[i] = array[0]
    sorted_keys = list(sorted(dict_y.items(), key=lambda x: x[1]))
    return array_task_numbers, sorted_keys


def detect_rectangle(img):
    result = []
    array_task_numbers, sorted_keys = find_contours(img)
    cropped_image = img[sorted_keys[0][1]:img.shape[0]]
    img = pruning_blank(cropped_image)
    array_task_numbers, sorted_keys = find_contours(img)
    for i, array in enumerate(sorted_keys):
        coords_number = array_task_numbers[array[0]]
        x1 = coords_number[0] + coords_number[3]
        y1 = coords_number[1] + coords_number[3] + 10
        x2 = coords_number[2]
        y2 = coords_number[3] + (img.shape[1] - coords_number[3])
        result.append({'answer': [x1, y1, x2, y2], 'task_num': {i + 1}})
    return result


def emnist_predict_img(model, img):
    img_arr = np.expand_dims(img, axis=0)
    img_arr = 1 - img_arr/255.0
    img_arr[0] = np.rot90(img_arr[0], 3)
    img_arr[0] = np.fliplr(img_arr[0])
    img_arr = img_arr.reshape((1, 28, 28, 1))

    predict = model.predict([img_arr])
    result = np.argmax(predict, axis=1)
    return chr(emnist_labels[result[0]])


def letters_extract(image, out_size=28):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)[1]
    img_erode = cv2.erode(thresh, np.ones((3, 3), np.uint8), iterations=1)

    # Get contours
    contours, hierarchy = cv2.findContours(img_erode, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    output = image.copy()

    letters = []
    for idx, contour in enumerate(contours):
        (x, y, w, h) = cv2.boundingRect(contour)
        if hierarchy[0][idx][3] == 0:
            cv2.rectangle(output, (x, y), (x + w, y + h), (70, 0, 0), 1)
            letter_crop = gray[y:y + h, x:x + w]

            size_max = max(w, h)
            letter_square = 255 * np.ones(shape=[size_max, size_max], dtype=np.uint8)
            if w > h:
                y_pos = size_max//2 - h//2
                letter_square[y_pos:y_pos + h, 0:w] = letter_crop
            elif w < h:
                x_pos = size_max//2 - w//2
                letter_square[0:h, x_pos:x_pos + w] = letter_crop
            else:
                letter_square = letter_crop

            letters.append((x, w, cv2.resize(letter_square, (out_size, out_size), interpolation=cv2.INTER_AREA)))

    letters.sort(key=lambda x: x[0], reverse=False)

    return letters


def img_to_str(model, image):
    letters = letters_extract(image)
    s_out = ""
    for i in range(len(letters)):
        dn = letters[i+1][0] - letters[i][0] - letters[i][1] if i < len(letters) - 1 else 0
        s_out += emnist_predict_img(model, letters[i][2])
        if (dn > letters[i][1]/4):
            s_out += ' '
    return s_out


def concatenate_images(images):
    total_width = max(image.width for image in images)
    total_height = sum(image.height for image in images)

    new_image = Image.new('RGB', (total_width, total_height))

    y_offset = 0
    for image in images:
        new_image.paste(image, (0, y_offset))
        y_offset += image.height

    return new_image


def start_cropping(file_path):
    images = convert_from_path(file_path, poppler_path=r"../../../soft_with_blanks/poppler-0.68.0/bin")[1:]
    new_images = []
    for i in range(len(images)):
        new_height = 1000
        new_width = new_height * images[i].size[0] // images[i].size[1]
        new_image = images[i].resize((new_width, new_height), Image.ANTIALIAS)
        new_images.append(new_image)
    long_image = concatenate_images(new_images)
    return detect_rectangle(np.array(long_image))
