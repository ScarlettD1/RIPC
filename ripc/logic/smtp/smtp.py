import smtplib


class Smtp:
    def __init__(self):
        self.__user = 'email@yandex.ru'
        self.__password = 'odbvmasshnioxfdj'
        self.is_initialized = False

        self.smtpObj = smtplib.SMTP(host='smtp.yandex.ru', port=587)
        self.smtpObj.starttls()
        self.smtpObj.ehlo()
        self.__login()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.smtpObj.close()

    def __login(self):
        try:
            self.smtpObj.login(self.__user, self.__password)
        except smtplib.SMTPException as err:
            print("Ошибка при авторизации SMTP", err)
            return
        self.is_initialized = True

    def send_mail(self, subject: str, to_addr: list, text: str):
        if not self.is_initialized:
            print("Ошибка при создании SMTP объекта")
            return False

        # кодировка письма
        charset = 'Content-Type: text/plain; charset=utf-8'
        mime = 'MIME-Version: 1.0'

        # формируем тело письма
        body = "\r\n".join((f"From: {self.__user}", f"To: {', '.join(to_addr)}",
                            f"Subject: {subject}", mime, charset, "", text))
        try:
            self.smtpObj.sendmail(self.__user, to_addr, body.encode('utf-8'))
        except smtplib.SMTPException as err:
            print("Ошибка при отправке сообщения", err)
            return False
        return True
