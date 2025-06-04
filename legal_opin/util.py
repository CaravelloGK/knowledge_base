"""
Класс для запросов выписки
"""
import urllib3
import xml.etree.ElementTree as ET
import requests
import time
from datetime import datetime
import os
import base64
from EDO_Project import settings


class EGRUL_Find:
    def __init__(self, INN):
        self.INN = str(INN)
        base_dir = settings.MEDIA_ROOT
        self.folder = f'{base_dir}/egrul'
        self.current_datetime = datetime.now().date()

    def search_dir(self):
        file_name = f'egrul_inn_{self.INN}_date_{self.current_datetime}.xml'
        files = os.listdir(self.folder)
        return file_name if file_name in files else 0

    def get_egrul_single(self, id_task):
        """Отдельный метод для опроса одного ИНН с индивидуальным таймаутом"""
        start_time = time.time()
        time_duration = 20 * 60  # 20 минут в секундах

        while time.time() - start_time < time_duration:
            try:
                url = f'http://localhost:8080/egr?taskID={id_task}'
                response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    print('Успешный ответ')
                    content = response.content.decode('utf-8')
                    if content:  # Проверяем, что ответ не пустой
                        tree = ET.ElementTree(ET.fromstring(content))
                        file_name = f'egrul_inn_{self.INN}_date_{self.current_datetime}.xml'
                        os.makedirs(self.folder, exist_ok=True)
                        tree.write(os.path.join(self.folder, file_name), encoding="utf-8")
                        print(f'Файл {file_name} сохранен!')
                        return file_name
                else:
                    print("Retry request")
                # Если ответ не готов, ждем перед повторным запросом
                time.sleep(10)  # Увеличиваем интервал между запросами

            except (requests.exceptions.RequestException, ET.ParseError) as e:
                print(f'Ошибка для ИНН {self.INN}: {e}. Повторяем запрос...')
                time.sleep(10)
                continue

        print(f'Достигнут таймаут 20 минут для ИНН {self.INN}')
        return None

    def get_egrul(self):
        """Основной метод для инициализации запроса"""
        url = f'http://localhost:8080/task-id?inn={self.INN}&typeMode=XML'
        try:
            response = requests.get(url, timeout=10)
            id_task = str(response.text)
            print(f'Получен ID задачи для ИНН {self.INN}: {id_task}')
            return self.get_egrul_single(id_task)
        except requests.exceptions.RequestException as e:
            print(f'Ошибка при получении ID задачи для ИНН {self.INN}: {e}')
            return None

    def itog(self):
        try_find = self.search_dir()
        if try_find != 0:
            print(f'Нашли существующую выписку для ИНН {self.INN}: {try_find}')
            return try_find
        else:
            print(f'Запрашиваем новую выписку для ИНН {self.INN}')
            return self.get_egrul()