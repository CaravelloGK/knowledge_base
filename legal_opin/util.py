import os, requests, time, urllib3, re, pdfplumber, json, datetime
from datetime import datetime
from bs4 import BeautifulSoup
from pathlib import Path
from lxml.html import fromstring
import warnings
from typing import Dict, List, Optional, Union
from django.conf import settings
from openpyxl.styles.builtins import warning

from .models import Unfriendly_countries


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class EgrulDownloader:
    """
    Класс по скачиванию выписки из ЕГРЮЛ с сайта egrul.nalog
    На входе получает ИНН
    возвращает путь к файл выписки в формате PDF
    """

    def __init__(self, inn: str):
        self.inn = inn
        self.url = "https://egrul.nalog.ru"
        self.egrul_dir = os.path.join(settings.BASE_DIR, 'EGRUL')
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/137.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
        })

    def _now_ms(self):
        return str(int(time.time() * 1000))

    def _step1_get_search_token(self) -> str:
        url = f"{self.url}/"
        data = {"query": self.inn}
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": self.url,
            "Referer": f"{self.url}/index.html"
        }
        r = self.session.post(url, data=data, headers=headers, timeout=10)
        r.raise_for_status()
        js = r.json()
        token = js.get("t")
        if not token:
            raise RuntimeError("Не пришёл search-token")
        return token

    def _step2_search(self, search_token: str) -> dict:
        url = f"{self.url}/search-result/{search_token}"
        ts = self._now_ms()
        params = {"r": ts, "_": ts}
        headers = {
            "Referer": f"{self.url}/index.html",
            "Accept": "*/*",
        }
        r = self.session.get(url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        js = r.json()
        rows = js.get("rows") or []
        if not rows:
            raise RuntimeError("По ИНН ничего не найдено")
        return rows[0]

    def _step3_request_vypiska(self, row_token: str) -> str:
        url = f"{self.url}/vyp-request/{row_token}"
        ts = self._now_ms()
        params = {"r": ts, "_": ts}
        headers = {
            "Referer": f"{self.url}/index.html",
            "Accept": "*/*",
        }
        r = self.session.get(url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        js = r.json()

        if js.get("captchaRequired"):
            raise RuntimeError("На сайте требуется капча")
        request_token = js.get("t")
        if not request_token:
            raise RuntimeError("Не пришёл request-token для выписки")
        return request_token

    def _step4_poll_status(self, request_token: str, timeout=60, interval=1.0):
        url = f"{self.url}/vyp-status/{request_token}"
        start = time.time()
        headers = {
            "Referer": f"{self.url}/index.html",
            "Accept": "*/*",
        }

        final_statuses = {"SUCCESS", "READY", "COMPLETED"}  # подставьте то, что реально приходит

        while True:
            ts = str(int(time.time() * 1000))
            params = {"r": ts, "_": ts}
            resp = self.session.get(url, params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            js = resp.json()
            if js.get("result") is True:
                return
            status = js.get("status", "").upper()
            if status in final_statuses:
                return
            if time.time() - start > timeout:
                raise TimeoutError(f"Выписка не сформировалась за {timeout} сек. Последний js: {js}")
            time.sleep(interval)

    def _step5_download_pdf(self, request_token: str, out_filename: str) -> str:
        url = f"{self.url}/vyp-download/{request_token}"
        resp = self.session.get(url, timeout=15)
        resp.raise_for_status()

        content = resp.content
        # Полный путь до файла
        full_path = os.path.join(self.egrul_dir, out_filename)
        # Сохраняем файл
        with open(full_path, "wb") as f:
            f.write(content)

        return full_path

    def download(self) -> str:
        now = datetime.now()
        date_now = now.strftime("%Y-%m-%d %H:%M")
        out_filename = f'egrul_{self.inn}_{date_now}.pdf'
        search_token = self._step1_get_search_token()
        rec = self._step2_search(search_token)
        row_token = rec.get("t")  # это был прежний file-token
        if not row_token:
            raise RuntimeError("В записи нет поля 't'")
        request_token = self._step3_request_vypiska(row_token)
        if request_token != "На сайте требуется капча" and request_token != "Не пришёл request-token для выписки":
            self._step4_poll_status(request_token)
            pdf_full_path = self._step5_download_pdf(request_token, out_filename)
            return pdf_full_path
        else:
            pdf_full_path = 'Ошибка'
            return pdf_full_path


class EgripParser:
    """
        Класс по парсингу выписки
        На вход принимает путь к файлу выписки (pdf)
        возвращает массив данных
    """
    SECTION_ALIASES = {
        'general_info': [
            'наименование', 'место нахождения', 'сведения о регистрации', 'сведения о состоянии юридического лица',
            'сведения о регистрирующем органе',
            'cведения о прекращении юридического лица', 'сведения о наличии корпоративного договора',
            'сведения об учете в налоговом органе'
        ],
        'registrar': [
            'о держателе реестра акционеров акционерного общества'
        ],
        'directors': [
            'сведения о лице, имеющем право без доверенности'
        ],
        'capital': [
            'уставном капитале', 'складочном капитале', 'уставном фонде', 'паевом фонде', 'принадлежащей обществу'
        ],
        'participants': [
            'участниках / учредителях юридического лица', 'акционерах общества', 'сведения о единственном акционере'
        ],
        'registry_records': [
            'сведения о записях, внесенных в единый государственный'
        ]
    }

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.all_sections = {key: [] for key in self.SECTION_ALIASES}
        self.registry_rows = []
        self.participants_header = ""

    @staticmethod
    def detect_section(header: str) -> Optional[str]:
        header = header.strip().lower()
        for k, aliases in EgripParser.SECTION_ALIASES.items():
            for alias in aliases:
                if alias in header:
                    return k
        return None

    @staticmethod
    def should_parse_full_info(general_info: Dict[str, str]) -> bool:
        """Возвращает True для ООО или акционерных обществ по наименованию"""
        val = general_info.get('Полное наименование', '') + ' ' + general_info.get('Сокр. наименование', '')
        val = val.lower()
        return any(
            term in val for term in [
                'акционерн', 'общество с ограниченной ответственностью',
                'ооо ', 'пао ', 'зао ', 'оао ', 'ао '
            ]
        )

    @staticmethod
    def parse_general_info_section(rows):
        result = {}
        found_main = False
        for i, row in enumerate(rows):
            # --- Новый блок! Корпоративный договор ---
            for cell in (row[1], row[2]):
                if cell and "корп" in cell.lower() and "договор" in cell.lower():
                    result["Корпоративный договор"] = cell.replace('\n', ' ').strip()
                    # После этого — постараемся найти ГРН и дату в ближайших строках
                    for j in range(i + 1, min(i + 6, len(rows))):
                        next_row = rows[j]
                        for subcell in (next_row[1], next_row[2]):
                            if subcell:
                                m_grn = re.search(r'\b\d{10,}\b', subcell)
                                m_date = re.search(r'\d{2}\.\d{2}\.\d{4}', subcell)
                                if m_grn:
                                    result['Корпоративный договор ГРН'] = m_grn.group(0)
                                if m_date:
                                    result['Корпоративный договор Дата'] = m_date.group(0)
                    break  # нашли, идём дальше по строкам

            # --- Ваш проверенный код ---
            k = (row[1] or '').replace('\n', ' ').strip().lower()
            v = (row[2] or '').replace('\n', ' ').strip()
            if 'полное наименование на русском языке' in k and not found_main:
                result['Полное наименование'] = v
                found_main = True
            elif 'сокращенное наименование на русском языке' in k:
                result['Сокр. наименование'] = v
            elif 'огрн' in k and 'ОГРН' not in result:
                result['ОГРН'] = v
            elif 'адрес юридического лица' in k:
                result['Адрес'] = v
            elif 'дата регистрации' in k:
                result['Дата регистрации'] = v
            elif 'инн юридического лица' in k and 'ИНН' not in result:
                result['ИНН'] = v
            elif 'кпп юридического лица' in k and 'КПП' not in result:
                result['КПП'] = v
            elif 'дата прекращения' in k:
                result['Дата прекращения'] = v
            elif 'способ прекращения' in k:
                result['Способ прекращения'] = v
            elif k.strip() == 'состояние':
                result['Состояние ЮЛ'] = v
        return result

    @staticmethod
    def parse_registrar_info_section(rows: List[List[str]]) -> Dict[str, str]:
        result = {}
        field_mapping = {
            'полное наименование': 'Наименование реестродержателя',
            'инн': 'ИНН',
            'огрн': 'ОГРН'
        }

        for row in rows:
            k = (row[1] or '').replace('\n', ' ').strip().lower()
            v = (row[2] or '').replace('\n', ' ').strip()

            for field_key, field_name in field_mapping.items():
                if field_key in k and field_name not in result:
                    result[field_name] = v
                    break
        return result

    @staticmethod
    def parse_directors_section(rows):
        directors = []
        person = None
        pre_person_date = None
        temp_person_attrs = {}  # Буфер для ИНН и ОГРН до появления person

        for row in rows:
            k = (row[1] or '').replace('\n', ' ').strip()
            v = (row[2] or '').replace('\n', ' ').strip()
            if "ГРН и дата" in k and "о данном лице" in k:
                m = re.search(r'(\d{2}\.\d{2}\.\d{4})', v)
                if m:
                    pre_person_date = m.group(1)

            # Случай с УК --- КОПИМ в буфер, если person ещё не завелся: только для ИНН/ОГРН!
            if k == "ИНН" and person is None:
                temp_person_attrs['ИНН'] = v
                continue
            if k == "ОГРН" and person is None:
                temp_person_attrs['ОГРН'] = v
                continue

            # --- Новый человек: ФЛ ---
            if ('Фамилия' in k and 'Имя' in k) or ('Фамилия' in k and 'Имя' in k and 'Отчество' in k):
                if person: directors.append(person.copy())
                fio = v.replace('\n', ' ').split()
                person = {'Тип': 'ФЛ', 'ФИО': ' '.join(fio)}
                # Буфер сливаем!
                if temp_person_attrs:
                    person.update(temp_person_attrs)
                    temp_person_attrs = {}
                if pre_person_date:
                    person['Дата избрания'] = pre_person_date
                    pre_person_date = None
                continue

            # --- Новый человек: ЮЛ (УК) ---
            if k in ("Полное наименование", "Наименование") or 'наименование' in k.lower():
                if person: directors.append(person.copy())
                person = {'Тип': 'ЮЛ', 'Наименование УК': v}
                # Буфер сливаем!
                if temp_person_attrs:
                    person.update(temp_person_attrs)
                    temp_person_attrs = {}
                if pre_person_date:
                    person['Дата избрания'] = pre_person_date
                    pre_person_date = None
                continue

            # --- Остальные поля для уже заведенного person ---
            if person is not None:
                if k == "ИНН":
                    person['ИНН'] = v
                elif k == "ОГРН":
                    person['ОГРН'] = v
                elif k == "Должность":
                    person['Должность'] = v
                elif k == "Дополнительные сведения":
                    person['Дополнительные сведения'] = v

        if person: directors.append(person.copy())
        return directors

    @staticmethod
    def parse_capital_section(rows: List[List[str]]) -> Dict[str, str]:
        cap = {}
        field_mapping = {
            'Вид': 'Вид',
            'Размер.*?руб': 'Размер УК (руб)',
            'Размер доли.*?процент': 'Размер доли, принадлежащей обществу (%)',
            'Номинальная стоимость доли': 'Номинал доли, принадлежащей обществу (руб)'
        }

        for row in rows:
            k = (row[1] or '').replace('\n', ' ').strip()
            v = (row[2] or '').replace('\n', ' ').strip()

            for pattern, field_name in field_mapping.items():
                if re.search(pattern, k, re.IGNORECASE) and field_name not in cap:
                    cap[field_name] = v
                    break
        return cap

    @staticmethod
    def parse_participants_section(rows):
        import re

        participants = []
        person = None
        current_enc = None
        in_encumbrance = False
        in_mo_mode = False
        pending_du = None
        pif_name = None
        in_pif_uk_mode = False  # флаг: идёт сбор управляющей компании для ПИФ

        encumbrance_keywords = [
            'сведения о договоре залога',
            'сведения о наложении ареста',
            'сведения об ограничении распоряжения долей',
            'отметка о снятии обременения'
        ]

        last_trustee_idx = -1

        for idx, row in enumerate(rows):
            # -- Пропускаем строки, относящиеся к уже разобранному блоку доверительного управляющего
            if idx <= last_trustee_idx:
                continue

            k = (row[1] or '').replace('\n', ' ').strip().lower()
            v = (row[2] or '').replace('\n', ' ').strip()
            # print(f"IDX={idx}, k={k!r}, v={v!r}, pending_du={pending_du}, person={person}")

            # ---- КЛЮЧ: Начался блок нового участника — добавь предыдущего ----
            if k == "грн и дата внесения в егрюл сведений о данном лице":
                # Не добавлять пустые person (например, если person только что инициализирован/является пустым словарём)
                if person and ('ФИО' in person or 'наименование' in person):
                    if pending_du:
                        if 'обременения' not in person:
                            person['обременения'] = []
                        person['обременения'].append(pending_du)
                        pending_du = None
                    participants.append(person.copy())
                person = {}
                continue

            # --- Случай с ПИФ. Собрать имя ПИФ
            if 'полное название паевого инвестиционного фонда' in k:
                pif_name = v
                continue
            # Обнаружение блока управляющей компании для ПИФ
            if row[1] and isinstance(row[1], str) and 'управляющей компании' in row[1].lower():
                in_pif_uk_mode = True
                continue
            # -----------

            # --- Блок: доверительное управление, надёжный сбор и пропуск всех строк блока
            if (
                    row[1]
                    and isinstance(row[1], str)
                    and "доверительн" in row[1].lower()
                    and "управляющ" in row[1].lower()
            ):
                if person:
                    participants.append(person.copy())
                    person = None
                du_data = {'тип обременения': 'доверительное управление'}
                du_fio_buf = []
                j = idx + 1
                while j < len(rows):
                    k2 = (rows[j][1] or '').replace('\n', ' ').strip().lower()
                    v2 = (rows[j][2] or '').replace('\n', ' ').strip()
                    if not k2 and not v2:
                        j += 1
                        continue
                    if 'огрн' in k2:
                        du_data['ОГРН доверительного управляющего'] = v2
                    elif 'инн' in k2:
                        du_data['ИНН доверительного управляющего'] = v2
                    elif 'полное наименование' in k2 or 'наименование' in k2:
                        du_data['наименование доверительного управляющего'] = v2
                    elif 'фамилия имя отчество' in k2 and v2:
                        du_data['наименование доверительного управляющего'] = v2
                    elif 'фамилия' == k2 and v2:
                        du_fio_buf.append(v2)
                    elif 'имя' == k2 and v2:
                        du_fio_buf.append(v2)
                    elif 'отчество' == k2 and v2:
                        du_fio_buf.append(v2)
                    elif 'грн и дата' in k2 and v2:
                        m = re.search(r'(\d{2}\.\d{2}\.\d{4})', v2)
                        if m:
                            du_data['Дата записи'] = m.group(1)
                        m_grn = re.search(r'\d{9,}', v2)
                        if m_grn:
                            du_data['ГРН'] = m_grn.group(0)
                    elif 'гражданство' in k2:
                        du_data['гражданство'] = v2

                    # Конец блока ДУ — встретили нового участника или др. явный признак
                    if ((k2 and ('фамилия' in k2 and 'имя' in k2)) or (k2 and 'участник' in k2)):
                        break
                    j += 1
                if du_fio_buf and 'наименование доверительного управляющего' not in du_data:
                    du_data['наименование доверительного управляющего'] = " ".join(du_fio_buf)

                # --- ИСПРАВЛЕНИЕ: к последнему участнику
                if participants:
                    if 'обременения' not in participants[-1]:
                        participants[-1]['обременения'] = []
                    participants[-1]['обременения'].append(du_data)
                # ---
                pending_du = None  # больше не нужен (очно привязали)
                last_trustee_idx = j - 1
                continue
            # --- Конец блока с ДУ

            # --- Классические обработчики участника
            if not in_encumbrance and 'участник / учредитель' in k:
                if person:
                    if pending_du:
                        if 'обременения' not in person:
                            person['обременения'] = []
                        person['обременения'].append(pending_du)
                        pending_du = None
                    # print(f"ADD PARTICIPANT! idx={idx} person={person}")
                    participants.append(person.copy())
                person = {}
                in_mo_mode = True
                continue

            if not in_encumbrance and not in_mo_mode and 'грн и дата внесения в егрюл сведений о данном лице' in k:
                if current_enc and in_encumbrance and person:
                    if 'обременения' not in person:
                        person['обременения'] = []
                    person['обременения'].append(current_enc.copy())
                if person and 'наименование' in person:
                    if pending_du:
                        if 'обременения' not in person:
                            person['обременения'] = []
                        person['обременения'].append(pending_du)
                        pending_du = None
                    participants.append(person.copy())
                person = {}
                current_enc = None
                in_encumbrance = False
                continue

            if any(kw in k for kw in encumbrance_keywords):
                if current_enc and in_encumbrance and person:
                    if 'обременения' not in person:
                        person['обременения'] = []
                    person['обременения'].append(current_enc.copy())
                current_enc = {}
                in_encumbrance = True
                enc_type = next((kw for kw in encumbrance_keywords if kw in k), 'иное обременение')
                current_enc['тип обременения'] = enc_type
                if v:
                    current_enc['описание'] = v
                continue

            if in_encumbrance and current_enc is not None:
                m_num = re.search(r'номер договора залога:\s*([^\s]+)', v, re.I)
                if 'номер договора залога' in k or m_num:
                    current_enc['номер договора'] = m_num.group(1) if m_num else v
                m_data = re.search(r'дата договора залога:\s*([^\s]+)', v, re.I)
                if 'дата договора залога' in k or m_data:
                    current_enc['дата договора'] = m_data.group(1) if m_data else v
                if ('нотариус' in k and 'фамилия' in k and 'имя' in k) or 'сведения о нотариусе' in k:
                    current_enc['нотариус'] = v
                if (('грн и дата внесения в егрюл записи' in k and 'содержащей указанные сведения' in k) or
                        ('грн и дата внесения в егрюл сведений о данном лице' in k)):
                    m = re.search(r'(\d{2}\.\d{2}\.\d{4})', v)
                    if m:
                        current_enc['дата записи обременения'] = m.group(1)
                if k == 'огрн' and not ('участник' in k or 'данном лице' in k):
                    current_enc['ОГРН залогодержателя'] = v
                    current_enc['залогодержатель: тип'] = 'ЮЛ'
                elif k == 'инн' and not ('участник' in k or 'данном лице' in k):
                    current_enc['ИНН залогодержателя'] = v
                    current_enc['залогодержатель: тип'] = 'ЮЛ'
                elif k == 'полное наименование' and not ('участник' in k or 'данном лице' in k):
                    current_enc['наименование залогодержателя'] = v
                    current_enc['залогодержатель: тип'] = 'ЮЛ'
                    if person is not None:
                        if 'обременения' not in person:
                            person['обременения'] = []
                        person['обременения'].append(current_enc.copy())
                    current_enc = None
                    in_encumbrance = False
            elif not in_encumbrance and person is not None:
                if 'фамилия' in k and 'имя' in k and 'отчество' in k:
                    person['Тип'] = 'ФЛ'
                    person['ФИО'] = v.replace('\n', ' ').strip()
                elif (k in (
                "полное наименование", "наименование")):  # Ищем полное наименование + проверка на ПИФ и УК к нему
                    if in_pif_uk_mode:
                        person['Тип'] = 'ПИФ(в лице УК)'
                        # person['наименование_управляющей_компании'] = v   # Если нужно наименование УК ПИФа
                        if pif_name:
                            person['наименование'] = f"{pif_name} в лице {v}"
                        else:
                            person['наименование'] = v
                        in_pif_uk_mode = False
                        pif_name = None  # сбросить после формирования пары
                    else:
                        person['Тип'] = 'ЮЛ'
                        person['наименование'] = v
                elif "латинице" in k:
                    person['наименование латиницей'] = v
                elif "страна происхождения" in k:
                    person['страна происхождения'] = v
                elif k == "регистрационный номер":
                    person['Регистрационный номер'] = v
                    person['Тип'] = 'ЮЛ'
                elif k == "огрн":
                    person['ОГРН'] = v
                    person['Тип'] = 'ЮЛ'
                elif k == "инн":
                    person['ИНН'] = v
                elif 'номинальная стоимость' in k:
                    person['Номинал доли (руб)'] = v
                elif 'размер доли' in k and ('процент' in k or '%' in k):
                    person['Размер доли (%)'] = v + "%"
                elif 'размер доли' in k and 'дробях' in k:
                    person['Размер доли (в дробях)'] = v
                elif "грн и дата" in k and "содержащей указанные" in k:
                    m = re.search(r'(\d{2}\.\d{2}\.\d{4})', v)
                    if m and 'Дата записи' not in person:
                        person['Дата записи'] = m.group(1)
                elif "дополнительные сведения" in k:
                    person['Дополнительные сведения'] = v
                elif "гражданство" in k:
                    person['гражданство'] = v

        if person:
            if pending_du:
                if 'обременения' not in person:
                    person['обременения'] = []
                person['обременения'].append(pending_du)
                pending_du = None
            # print(f"ADD PARTICIPANT! idx={idx} person={person}")
            participants.append(person.copy())
        return participants

    @staticmethod
    # Информация об Уставе и последних изменениях в него
    def parse_docs_section(rows):
        from datetime import datetime
        import re
        def _parse_date(dt):
            if not dt: return None
            try:
                return datetime.strptime(dt, "%d.%m.%Y")
            except Exception:
                return None

        block_idxs = []
        for i, row in enumerate(rows):
            k = (row[1] or '').strip().lower()
            if k.startswith('причина внесения записи в егрюл'):
                block_idxs.append(i)
        block_idxs.append(len(rows))
        blocks = []
        for i in range(len(block_idxs) - 1):
            start = block_idxs[i]
            end = block_idxs[i + 1]
            reason_row = rows[start]
            reason = (reason_row[2] or '').strip().lower()
            if ('государственная регистрация' in reason) or ('создание юридического лица' in reason):
                block = {
                    'start': start,
                    'end': end,
                    'reason': reason,
                    'rows': rows[start:end],
                }
                blocks.append(block)

        charters = []
        izm_list = []

        # Новое! Анализ каждого документа внутри блока, собираем что есть
        for bidx, block in enumerate(blocks):
            best_charter = None
            best_izm = None
            charter_priority = 0  # 2=идеальный устав, 1=похожее, 0=нет
            for i in range(block['start'], block['end']):
                row = rows[i]
                k = (row[1] or '').strip().lower()
                v = (row[2] or '').strip()
                if 'наименование документа' not in k:
                    continue
                v_lc = v.lower()

                # плохо: "капитал" (отсекаем), "решение" без "устав"/"учр" (отсекаем), "иной" и т.п.
                if 'капитал' in v_lc or 'иной докум' in v_lc:
                    continue

                # Если это именно устав — строго
                if (('устав' in v_lc or 'учр' in v_lc) and
                        'изм' not in v_lc and 'заявлен' not in v_lc and 'решен' not in v_lc and 'проток' not in v_lc):
                    docinfo = {
                        'Тип': 'Устав', 'Наименование': v,
                        # 'Дата': None, 'Номер': None,
                        'ГРН': None, 'ДатаГРН': None, 'Причина': block['reason'],
                        # 'block_idx': bidx
                    }
                    for k_rel in range(block['start'], block['end']):
                        krow = (rows[k_rel][1] or '').strip().lower()
                        vrow = (rows[k_rel][2] or '').strip()
                        if 'грн и дата внесения записи' in krow or krow == 'грн':
                            m1 = re.search(r'\d{9,}', vrow)
                            m2 = re.search(r'(\d{2}\.\d{2}\.\d{4})', vrow)
                            if m1: docinfo['ГРН'] = m1.group(0)
                            if m2: docinfo['ДатаГРН'] = m2.group(1)
                    best_charter = docinfo
                    charter_priority = 2
                    break  # внутри блока приоритет устава! дальше не ищем

                # Если это изменения в устав
                elif ('изм' in v_lc and 'заявлен' not in v_lc and
                      ('учр' in v_lc or 'устав' in v_lc)):
                    docinfo = {
                        'Тип': 'Изменение устава', 'Наименование': v,
                        # 'Дата': None, 'Номер': None,
                        'ГРН': None, 'ДатаГРН': None, 'Причина': block['reason'],
                        # 'block_idx': bidx
                    }
                    for k_rel in range(block['start'], block['end']):
                        krow = (rows[k_rel][1] or '').strip().lower()
                        vrow = (rows[k_rel][2] or '').strip()
                        if 'грн и дата внесения записи' in krow or krow == 'грн':
                            m1 = re.search(r'\d{9,}', vrow)
                            m2 = re.search(r'(\d{2}\.\d{2}\.\d{4})', vrow)
                            if m1: docinfo['ГРН'] = m1.group(0)
                            if m2: docinfo['ДатаГРН'] = m2.group(1)
                    best_izm = docinfo
                    charter_priority = max(charter_priority, 1)
                    # не break — вдруг есть устав ниже по строкам?

            if charter_priority == 2 and best_charter:  # нашли идеальный устав
                charters.append(best_charter)
            elif charter_priority == 1 and best_izm:
                izm_list.append(best_izm)
            # всё прочее игнорируем

        # Теперь находим самый свежий устав и ВСЕ последующие изменения
        if not charters:
            return {}
        charters_sorted = sorted(
            [c for c in charters if c['ДатаГРН']],
            key=lambda x: _parse_date(x['ДатаГРН']),
            reverse=True  # Порядок отображения изменений к уставу: от старого к новому. Если нужно наоборот - false
        )
        fresh_charter = charters_sorted[0]
        charter_date = _parse_date(fresh_charter['ДатаГРН'])
        izm_candidates = []
        for izm in izm_list:
            izm_date = _parse_date(izm['ДатаГРН'])
            if izm_date and charter_date and izm_date > charter_date:
                izm_candidates.append(izm)
        izm_candidates_sorted = sorted(
            izm_candidates,
            key=lambda x: _parse_date(x['ДатаГРН']),
            reverse=True
        )

        def clean_dict(d):
            return {k: (v.replace('\n', ' ').strip() if isinstance(v, str) else v)
                    for k, v in d.items() if v not in (None, "", [], {})}

        fresh_izm_list = [clean_dict(izm) for izm in izm_candidates_sorted]
        result = {}
        if fresh_charter: result['Устав'] = clean_dict(fresh_charter)
        if fresh_izm_list:
            result['Изменения'] = fresh_izm_list  # теперь это список всех изменений
        return result

    def eiopr_access_restricted(self) -> bool:
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                txt = page.extract_text() or ""
                if re.search(
                        r'Сведения о лице, имеющем право без доверенности.*?Доступ к сведениям ограничен',
                        txt,
                        re.IGNORECASE | re.DOTALL
                ):
                    return True
        return False

    def participants_access_restricted(self) -> bool:
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                txt = page.extract_text() or ""
                if (
                        re.search(r'Сведения об участниках.*?Доступ к сведениям ограничен', txt,
                                  re.IGNORECASE | re.DOTALL)
                        or re.search(r'Сведения о единственном акционере.*?Доступ к сведениям ограничен', txt,
                                     re.IGNORECASE | re.DOTALL)
                ):
                    return True
        return False

    def extract_tables(self) -> None:
        registry_mode = False
        current_section = None

        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                for table in page.extract_tables():
                    for row in table:
                        if row.count(None) == 2 and row[0]:
                            sec = self.detect_section(row[0])
                            if sec == "participants":
                                self.participants_header = row[0].lower()
                            if sec:
                                current_section = sec
                            if sec == 'registry_records':
                                registry_mode = True
                                continue
                            if ("выписка сформирована" in row[0].lower() or (sec and sec != 'registry_records')):
                                registry_mode = False
                                continue
                            continue
                        if registry_mode and len(row) >= 3 and row[1] and row[2]:
                            self.registry_rows.append(row)
                        elif current_section and len(row) >= 3 and row[1] and row[2]:
                            self.all_sections[current_section].append(row)

    def parse(self) -> Dict:
        self.extract_tables()

        directors_restricted = self.eiopr_access_restricted()
        participants_restricted = self.participants_access_restricted()

        participants = self.parse_participants_section(self.all_sections['participants'])
        if "единственном акционере" in self.participants_header:
            for pers in participants:
                pers['Размер доли (%)'] = "100"

        data = {
            'general_info': self.parse_general_info_section(self.all_sections['general_info']),
            'registrar': self.parse_registrar_info_section(self.all_sections['registrar']),
            'capital': self.parse_capital_section(self.all_sections['capital']),
            'directors': ([{
                "restricted": True,
                "msg": "Доступ к сведениям о лице, имеющем право без доверенности вести дела, ограничен (merged cell, не таблица)"
            }] if directors_restricted else self.parse_directors_section(self.all_sections['directors'])),
            'participants': ([{
                "restricted": True,
                "msg": "Доступ к сведениям об участниках ограничен (merged cell, не таблица)"
            }] if participants_restricted else participants),
            'charter_doc': self.parse_docs_section(self.registry_rows),
        }

        if not self.should_parse_full_info(data['general_info']):
            return {
                'org_type': data['general_info'].get('Полное наименование', 'Нет данных'),
                'msg': 'Не ООО / АО'
            }
        print('ДАННЫЕ ПАРСЕРА ЧИТЫЕ', data, sep='\n')
        return data


class Parsers_sites:
    """
        Класс для парсига сайтов и получения информации
        На вход принимает ИНН
        Возвращает массив
    """
    def __init__(self, INN):
        self.inn = str(INN)
        # Один Session для всех запросов
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/137.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
        })

    def Reestr_bankrupt_parser2(self):
        # Метод для парсига сайта ЕФРСБ (банкротство)
        search_page = (
            "https://bankrot.fedresurs.ru/bankrupts?"
            f"searchString={self.inn}"
            "&regionId=all"
            "&isActiveLegalCase=null"
            "&offset=0"
            "&limit=15"
        )
        try:
            self.session.get(search_page, verify=False, timeout=5)
        except requests.RequestException:
            return "Не удалось открыть страницу поиска"

        api_url = "https://bankrot.fedresurs.ru/backend/cmpbankrupts"
        params = {
            "searchString": self.inn,
            "regionId": "all",
            "isActiveLegalCase": "null",
            "limit": "15",
            "offset": "0",
        }
        headers = {
            "Referer": search_page,
            "Origin": "https://bankrot.fedresurs.ru",
        }

        try:
            resp = self.session.get(api_url,
                                    params=params,
                                    headers=headers,
                                    verify=False,
                                    timeout=5)
            resp.raise_for_status()
        except requests.RequestException:
            return "Ответ от ресурса не получен"

        data = resp.json()
        total = data.get("total", 0)

        if total == 1:
            rec = data["pageData"][0]
            info_1 = "Клиент включен в реестр"

            last = rec.get("lastLegalCase") or {}
            num = last.get("number", "")
            stage = last.get("status", {}).get("description", "")
            status = rec.get("status", "")

            if num:
                info_2 = f"Судебное дело №{num}, стадия — {stage}. Текущий статус — {status}"
            else:
                info_2 = f"Текущий статус — {status}"
            return [info_1, info_2]

        elif total == 0:
            return "Клиент отсутствует в реестре"
        return f"Найдено {total} записей, ожидали 0 или 1"


    def REESTR_EST_MONOPOL_parser(self):
        # Реестр естественных монополий.
        url = "http://apps.eias.fas.gov.ru/FindCem/"
        url_1 = 'http://apps.eias.fas.gov.ru/FindCEM/Search/Report'
        requests.packages.urllib3.disable_warnings()
        s = requests.Session()
        try:
            response_main_page = s.get(url, verify=False, timeout=(2, 2))
            cookies_from_headers = response_main_page.cookies.get_dict()
            soup_main_page = BeautifulSoup(response_main_page.content, 'html.parser')
            request_verification_token = soup_main_page.find('input', {'name': '__RequestVerificationToken'})['value']
            data = {
                '__RequestVerificationToken': request_verification_token,
                'INN': self.inn,
            }
            cookies = {
                '__RequestVerificationToken_L0ZpbmRDRU01': cookies_from_headers.get(
                    '__RequestVerificationToken_L0ZpbmRDRU01'),
                'ASP.NET_SessionId': cookies_from_headers.get('ASP.NET_SessionId'),
            }
            headers = {
                'Accept': '/',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest',
            }
            response = requests.post(
                url_1,
                cookies=cookies,
                headers=headers,
                data=data,
                verify=False,
            )
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                td_tags = soup.find_all('td')
                if td_tags:
                    element1 = "Клиент включен в реестр"
                else:
                    element1 = "Клиент отсутствует в реестре"
                return element1
        except requests.Timeout:
            element1 = "Ответ от ресурса не получен"
            return element1


    def DeveloperReestr_parser(self):
        # РЕЕСТР ЗАСТРОЙЩИКОВ
        inn = str(self.inn)
        URL = "https://xn--80az8a.xn--d1aqf.xn--p1ai/%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D1%8B/%D0%B5%D0%B4%D0%B8%D0%BD%D1%8B%D0%B9-%D1%80%D0%B5%D0%B5%D1%81%D1%82%D1%80-%D0%B7%D0%B0%D1%81%D1%82%D1%80%D0%BE%D0%B9%D1%89%D0%B8%D0%BA%D0%BE%D0%B2?search=" + inn
        requests.packages.urllib3.disable_warnings()
        payload = {}
        files = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                          "AppleWebKit/537.36 (KHTML, like Gecko)"
                          "Chrome/107.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = requests.request("POST", URL, headers=headers, data=payload, files=files, verify=False)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            itog = [i.text for i in soup.find_all('p')]
            Zastroi = 'Клиент включен в реестр' if inn in itog else 'Клиент отсутствует в реестре'
            return Zastroi
        else:
            Zastroi = 'Ответ от ресурса не был получен'
            return Zastroi

    def ZakupkiReestr_parser(self):
        # Реестр закупок
        INN = str(self.inn)
        URL = "https://zakupki.gov.ru/epz/organization/search/results.html?searchString=" + str(
            INN) + "&morphology=on&search-filter=%D0%94%D0%B0%D1%82%D0%B5+%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%89%D0%B5%D0%BD%D0%B8%D1%8F&fz94=on&fz223=on&F=on&S=on&M=on&NOT_FSM=on&registered94=on&notRegistered=on&sortBy=NAME&pageNumber=1&sortDirection=false&recordsPerPage=_10&showLotsInfoHidden=false"
        requests.packages.urllib3.disable_warnings()
        payload = {}
        files = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                          "AppleWebKit/537.36 (KHTML, like Gecko)"
                          "Chrome/107.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        try:
            response = requests.request("POST", URL, headers=headers, data=payload, files=files, verify=False)
            resp = response.text
            resp_tree = fromstring(resp)
            if response.status_code == 200:
                if resp.find('row no-gutters registry-entry__form mr-0') > 0:
                    path = resp_tree.xpath("//div[@class='registry-entry__header-top__title']")
                    if len(path) > 1:
                        Mess_2 = "Клиент включен, требуется ручная проверка"
                    else:
                        law = str(path[0].text_content())
                        if '44-ФЗ' in law:
                            Mess_2 = "Клиент включен в реестр 44-ФЗ"
                            return Mess_2
                        elif '223-ФЗ' in law:
                            Mess_2 = "Клиент включен в реестр 223-ФЗ"
                            return Mess_2
                        elif resp_tree.xpath(
                                "//div[@class='registry-entry__header-top__title']/*[text()='223-ФЗ']") and resp_tree.xpath(
                                "//div[@class='registry-entry__header-top__title']/*[text()='44-ФЗ']"):
                            Mess_2 = "Клиент включен в реестр 44-ФЗ/223-ФЗ"
                elif resp.find('noRecords') > 0:
                    Mess_2 = "Клиент отсутствует в реестре"
                    return Mess_2
                else:
                    Mess_2 = "Ответ от ресурса не был получен"
                    return Mess_2
            else:
                Mess_2 = "Ответ от ресурса не был получен"
                return Mess_2
        except:
            Mess_2 = "Ответ от ресурса не был получен"
            return Mess_2


    def Reestr_nedobrosov_parser(self):
        # Реестр недобросовестных поставщиков. Запрос по API. Без GUI
        INN = str(self.inn)
        URL = "https://zakupki.gov.ru/epz/dishonestsupplier/search/results.html?searchString=" + str(
            INN) + "&morphology=on&search-filter=%D0%94%D0%B0%D1%82%D0%B5+%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%89%D0%B5%D0%BD%D0%B8%D1%8F&sortBy=UPDATE_DATE&pageNumber=1&sortDirection=false&recordsPerPage=_10&showLotsInfoHidden=false&fz94=on&fz223=on&ppRf615=on"

        requests.packages.urllib3.disable_warnings()
        payload = {}
        files = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                          "AppleWebKit/537.36 (KHTML, like Gecko)"
                          "Chrome/107.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        try:
            response = requests.request("POST", URL, headers=headers, data=payload, files=files, verify=False)
            resp = response.text
            if response.status_code == 200:
                if resp.find(
                        'row no-gutters registry-entry__form mr-0') > 0:
                    Mess_3 = "Клиент включен в реестр"
                elif resp.find(
                        'noRecords') > 0:
                    Mess_3 = "Клиент отсутствует в реестре"
                else:
                    Mess_3 = "Ответ от ресурса не был получен"
            else:
                Mess_3 = "Ответ от ресурса не был получен"
            return Mess_3
        except:
            Mess_3 = "Ответ от ресурса не был получен"
            return Mess_3


class Converter:
    """
    класс отвечающий за конвертацию массива из ЕГРЮ в массив для форм
    также дополнительно получает данные с сайтов и подтягивает в словарь для форм
    """
    def __init__(self, mass):
        self.mass_info = mass


    def general_info(self):
        # получаем данные по ЮЛ
        base_info = self.mass_info['general_info']
        reg = self.mass_info['registrar']

        # получаем инфо по реестродержателю
        if 'Наименование реестродержателя' in reg:
            reg_info = reg['Наименование реестродержателя']
            if 'ИНН' in reg:
                reg_inn = reg['ИНН']
            else:
                reg_inn = ''
        else:
            reg_info = ''
            reg_inn = ''

        # поллучаем информацию по ОПФ
        opf = ''
        if "ООО" in base_info['Сокр. наименование']:
            opf = 'ООО'
        elif "АО" in base_info['Сокр. наименование']:
            opf = "АО"
        elif "ЗАО" in base_info['Сокр. наименование']:
            opf = "ЗАО"
        elif "ПАО" in base_info['Сокр. наименование']:
            opf = "ПАО"
        elif "ОАО" in base_info['Сокр. наименование']:
            opf = "ОАО"

        uk = self.mass_info['capital']  # уставной капитал
        if len(uk) == 0:
            uk_inf = ''
        else:
            uk_inf = uk['Размер УК (руб)']

        # проверяем статус
        if 'Состояние ЮЛ' in base_info:
            stat = base_info['Состояние ЮЛ']
        elif 'Способ прекращения' in base_info:
            inf_1 = base_info['Способ прекращения']
            inf_2 = base_info['Дата прекращения']
            stat = f'{inf_1}, дата прекращения {inf_2}'
        else:
            stat = 'ЮЛ действующие'

        if 'Корпоративный договор' in base_info:
            korp_dog = True
        else:
            korp_dog = False

        # проверяем есть ли доли, принадлежащие обществу
        if 'Размер доли, принадлежащей обществу (%)' in uk:
            first_block = uk['Размер доли, принадлежащей обществу (%)']
            second_block = uk['Номинал доли, принадлежащей обществу (руб)']
            dolya = f'Размер доли, принадлежащей обществу (%) - {first_block}; Номинал доли, принадлежащей обществу (руб) - {second_block}'
        else:
            dolya = ''

        # проверяем изменения в устав
        ustav = self.mass_info['charter_doc']
        if 'Устав' in ustav:
            ustav_base = ustav['Устав']
            ustav_base_1 = ustav_base.get('Наименование', '')
            ustav_base_2 = ustav_base.get('ГРН', '')
            ustav_base_3 = ustav_base.get('ДатаГРН', '')
            ustav_base_4 = ustav_base.get('Причина', '')
            ustav_info = f'{ustav_base_1}\nГРН: {ustav_base_2}\nДатаГРН: {ustav_base_3}\nПричина: {ustav_base_4}'
        else:
            ustav_info = ''
        if 'Изменения' in ustav:
            ustav_change = ustav['Изменения']
            # Может быть либо словарь, либо список словарей
            if isinstance(ustav_change, dict):
                changes = [ustav_change]
            elif isinstance(ustav_change, list):
                changes = ustav_change
            else:
                changes = []

            parts = []
            for ch in changes:
                name = ch.get('Наименование', '') if isinstance(ch, dict) else ''
                grn = ch.get('ГРН', '') if isinstance(ch, dict) else ''
                date_grn = ch.get('ДатаГРН', '') if isinstance(ch, dict) else ''
                reason = ch.get('Причина', '') if isinstance(ch, dict) else ''
                piece = f'{name}\nГРН: {grn}\nДата ГРН: {date_grn}\nПричина: {reason}'
                if piece.strip():
                    parts.append(piece)
            ustav_change_info = '\n\n'.join(parts)
        else:
            ustav_change_info = ''

        # подключаем парсеры сайтов
        get_reestr = Parsers_sites(base_info['ИНН'])

        # банкротство
        bankrot = get_reestr.Reestr_bankrupt_parser2()
        if bankrot != "Клиент отсутствует в реестре":
            bankrot_info = True
            bankrot_dop_info = bankrot[1]
        else:
            bankrot_info = False
            bankrot_dop_info = ''

        # закупки
        zakup = get_reestr.ZakupkiReestr_parser()
        if zakup != "Клиент отсутствует в реестре":
            zakup_info = True
            if zakup == 'Клиент включен в реестр 223-ФЗ':
                laws_zakup = '223-ФЗ'
            elif zakup == 'Клиент включен в реестр 44-ФЗ':
                laws_zakup = '44-ФЗ'
            else:
                laws_zakup = '44-ФЗ и 223-ФЗ'
        else:
            zakup_info = False
            laws_zakup = ''

        monopol = get_reestr.REESTR_EST_MONOPOL_parser()
        monopol_inf = True if monopol != 'Клиент отсутствует в реестре' else False

        zastroy = get_reestr.DeveloperReestr_parser()
        zastroy_inf = True if zastroy != 'Клиент отсутствует в реестре' else False

        # проверяем статус
        if stat == 'Юридическое лицо находится в процессе реорганизации в форме присоединения к нему других юридических лиц' or stat == 'Находится в стадии ликвидации':
            stat_fisk = True
            inf_stat_risk = stat
        else:
            stat_fisk = False
            inf_stat_risk = ''

        # формируем итоговый массив
        legal_entity_data = {
            'name': base_info['Полное наименование'],  # Название
            'inn': base_info['ИНН'],  # ИНН из запроса
            'ogrn': base_info['ОГРН'],  # ОГРН
            'legal_form': opf,  # Организационно-правовая форма
            'status': stat,  # Статус
            'authorized_capital': uk_inf,  # Уставной капитал
            'registrar': reg_info,
            'registrar_inn': reg_inn,
            'address': base_info['Адрес'],
            'capital_org': dolya,
            'info_ustav': ustav_info,
            'info_ustav_doc': ustav_change_info,
            'bankrot': bankrot_info,
            'bankrot_dop_info': bankrot_dop_info,
            'zakup': zakup_info,
            'laws_zakup': laws_zakup,
            'reorganization': stat_fisk,
            'reorganization_dop_info': inf_stat_risk,
            'monopol': monopol_inf,
            'zastroy': zastroy_inf,
            'corp_dogovor': korp_dog
        }
        print('Итоговые данные, сконвертированные для форсы', legal_entity_data, sep='\n')
        return legal_entity_data

    def check_enemy(self, value):
        # проверяем на недружественное лицо участника
        countries_list = Unfriendly_countries.objects.all()
        warning = True if countries_list.filter(name=value).exists() else False
        return warning


    def check_eio_part(self, mass_1, mass_2):
        # проверяем на ЕИО == единственный участник
        if len(mass_1) == 1 and len(mass_2) == 1:
            exec = mass_1[0]
            part = mass_2[0]
            exec_inn = exec['inn'] if 'inn' in exec else ''
            part_inn = part['inn'] if 'inn' in part else ''
            if exec_inn == part_inn:
                return True
            else:
                return False

    def eio_info(self):
        # формируем массив по ЕИО
        eio = self.mass_info['directors']
        executive_body_data = []
        if eio:  # Если есть данные о руководителе
            num_executives = len(eio)  # Количество руководителей
            executives = eio[:num_executives]  # Берем только нужное количество записей
            for executive in executives:

                # проверяем ФЛ или УК
                if 'Наименование УК' in executive:
                    name = executive['Наименование УК']
                else:
                    name = executive['ФИО']

                # если ФЛ, получаем должность, в ином случае - ""
                if 'Должность' in executive:
                    info = executive['Должность']
                else:
                    info = ''

                if 'ИНН' in executive:
                    inn = executive['ИНН']
                else:
                    inn = ''

                date_new = datetime.strptime(executive['Дата избрания'], "%d.%m.%Y").date()
                executive_body_data.append({
                    'name': name,  # Должность + ФИО
                    'inn': inn,  # ИНН
                    'job_title': info,
                    'date_of_authority': date_new.strftime("%Y-%m-%d")
                })
        return executive_body_data

    def participants(self):
        # формируем массив по участнику
        participants = self.mass_info['participants']
        war = ''

        participant_data = []
        if participants:  # Если есть данные об участниках
            num_participants = len(participants)  # Количество участников

            participants = participants[:num_participants]  # Берем только нужное количество записей
            for participant in participants:
                # собираем информацию по участникам

                # Если информация скрыта
                if 'Тип' in participant:
                    name, inn, adress = '', '', ''
                    # Общаяя информация
                    type_p = participant['Тип']
                    if type_p == 'ЮЛ':
                        name = participant['наименование']
                        if 'ИНН' in participant:
                            inn = participant['ИНН']
                        else:
                            inn = ''
                        if 'страна происхождения' in participant:
                            adress = participant['страна происхождения']
                            war = self.check_enemy(adress)
                        else:
                            adress = ''
                    elif type_p == 'ФЛ':
                        name = participant['ФИО']
                        if 'ИНН' in participant:
                            inn = participant['ИНН']
                        else:
                            inn = ''
                        if 'гражданство' in participant:
                            adress = participant['гражданство']
                            war = self.check_enemy(adress)
                        else:
                            adress = ''

                    # Информация о доле
                    value = (participant.get('Размер доли (%)') or participant.get('Размер доли (в дробях)'))
                    if value is not None:
                        share = value
                    else:
                        share = ''

                    dop_info = ''
                else:
                    name = ''
                    inn = ''
                    share = ''
                    adress = ''
                    dop_info = 'Доступ к сведениям об участниках ограничен'

                # информация об обременении долей
                if 'обременения' in participant:
                    # pass
                    inf_obr = participant['обременения']
                    print('Обременения долей', type(inf_obr), len(inf_obr), inf_obr, sep='\n')
                    lst = list(inf_obr[0].values())
                    string = '\n'
                    for el in lst:
                        string += str(el)
                        string += ' '
                    share_info = string
                else:
                    share_info = ''
                participant_data.append({
                    'name': name,
                    'inn': inn,
                    'share': share,
                    'share_info': share_info,
                    'address': adress,
                    'dop_info': dop_info
                })
        if war == True:
            SEM = True
            SEM_dop_info = f'Выявленны признаки недружественной юрисдикции'
        else:
            SEM = False
            SEM_dop_info = ''
        # print(participant_data)
        return participant_data, SEM, SEM_dop_info

    def itog(self):
        # формируем итоговый массив
        legal_entity_data = self.general_info()
        executive_body_data = self.eio_info()
        participant_data, SEM, SEM_dop_info = self.participants()
        if SEM:
            legal_entity_data['SEM'] = True
            legal_entity_data['SEM_dop_info'] = SEM_dop_info
        else:
            legal_entity_data['SEM'] = False
            legal_entity_data['SEM_dop_info'] = ''
        get_info_check_eio_part = self.check_eio_part(executive_body_data, participant_data)
        legal_entity_data['eio_uchast'] = get_info_check_eio_part

        info = [legal_entity_data, executive_body_data, participant_data]
        return info


class Date_Converter():
    def __init__(self, date):
        self.value = date

    def converter_date(self):
        date_str = self.value.isoformat()
        print(date_str, type(date_str))
        return date_str


def compare_formset_data(db_objects, session_data_list, fields_to_compare):
    """
    Сравнивает список объектов из БД со списком словарей из сессии.
    Возвращает словарь с добавленными, удаленными и измененными элементами.
    """
    db_map = {obj.pk: obj for obj in db_objects}
    session_map = {item.get('id'): item for item in session_data_list if item.get('id')}

    changed_items = {}
    new_items = []

    # Находим измененные и новые
    for item_data in session_data_list:
        item_id = item_data.get('id')
        if item_id and item_id in db_map:
            db_obj = db_map[item_id]
            changes = {}
            for field in fields_to_compare:
                # Приводим к строке, чтобы избежать проблем сравнения None и ''
                old_value = str(getattr(db_obj, field, ''))
                new_value = str(item_data.get(field, ''))
                if old_value != new_value:
                    changes[field] = {'old': old_value, 'new': new_value}
            if changes:
                changed_items[item_id] = changes
        elif not item_id:
            new_items.append(item_data)

    # Находим удаленные
    deleted_items = []
    db_ids = set(db_map.keys())
    session_ids = set(session_map.keys())
    deleted_ids = db_ids - session_ids
    for item_id in deleted_ids:
        deleted_items.append(db_map[item_id])

    return {'changed': changed_items, 'new': new_items, 'deleted': deleted_items}
