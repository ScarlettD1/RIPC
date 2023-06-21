import numpy as np
import cv2

import pytesseract
from pyzbar.pyzbar import decode
from pdf2image import convert_from_path

pytesseract.pytesseract.tesseract_cmd = r'../soft_with_blanks/tesseract/tesseract.exe'


def decode_codes(image):
    decoded_objects = decode(image)
    for obj in decoded_objects:
        if obj.type == "QRCODE":
            return str(obj.data)
        else:
            return str(obj.data)


def rotate_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Пороговая бинаризация
    _, binary = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY_INV)

    # Нахождение контуров
    contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # Поиск контуров, соответствующих черным квадратам
    squares = []
    for contour in contours:
        # Аппроксимация контура
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Проверка на квадратность контура (4 вершины и выпуклость)
        if len(approx) == 4 and cv2.isContourConvex(approx):
            squares.append(contour)

    # Сортировка квадратов в порядке по часовой стрелке от верхнего левого угла
    squares.sort(key=lambda cnt: tuple(cnt[cnt[:, :, 0].argmin()][0]))

    # Вычисление угла между двумя черными квадратами
    x1, y1, _, _ = cv2.boundingRect(squares[0])
    x2, y2, _, _ = cv2.boundingRect(squares[1])

    angle = np.arctan2(y2 - y1, x2 - x1) * 180. / np.pi

    # Корректировка угла, чтобы он всегда оставался в диапазоне [-45, 45] градусов
    if angle > 45:
        angle -= 90
    elif angle < -45:
        angle += 90

    # Поворот изображения на вычисленный угол
    (h, w) = image.shape[:2]
    center = (w / 2, h / 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_image = cv2.warpAffine(image, M, (w, h))

    return rotated_image


def decode_numbers(image):
    string = pytesseract.image_to_string(image)
    return string


def start_detect(file_path):
    images = convert_from_path(file_path, poppler_path=r"../../../soft_with_blanks/poppler-0.68.0\bin")
    for i in range(len(images)):
        rotated_image = rotate_image(np.array(images[i]))
        decode_result = decode_codes(np.array(rotated_image))
        crop_img = rotated_image[20:80, rotated_image.shape[1] - 360:rotated_image.shape[1] - 50]
        decode_number = decode_numbers(crop_img)
        if decode_number is not None:
            return decode_result
        else:
            if decode_number is None:
                return decode_number
        return ''
