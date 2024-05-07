import json
import os
import sys
import traceback
import uuid
from functools import wraps
from pathlib import Path
from typing import Callable, Union, List, Dict, Literal, Optional, Tuple, Any

import android

from ru.travelfood.simple_ui import SimpleUtilites as suClass


class HashMap:
    """
        Класс-декоратор для удобной работы с hashMap. Также можно добавить дополнительную логику.
    """

    def __init__(self, hash_map=None, debug: bool = False):
        self.listener = None
        self.hash_map = hash_map
        self.debug_mode = debug

    def __call__(self, func: Callable[..., None]):
        @wraps(func)
        @error_handler_decorator()
        def wrapper(hashMap, *args, **kwargs):
            self.init(hashMap)
            func(self)
            return hashMap

        return wrapper

    def init(self, hashMap):
        self.hash_map = hashMap

    def finish_process(self):
        self.hash_map.put('FinishProcess', '')

    def finish_process_result(self):
        self.hash_map.put('FinishProcessResult', '')

    @property
    def listener(self):
        return self['listener']

    @listener.setter
    def listener(self, v):
        pass

    def set_result_listener(self, listener):
        if listener and isinstance(listener, str):
            self.hash_map.put('SetResultListener', listener)

    def toast(self, text: str):
        android.toast(str(text))

    def basic_notification(self, text, title=None):
        self.hash_map.put(
            "basic_notification",
            json.dumps([{'number': 999, 'title': str(title), 'message': text}])
        )

    def refresh_screen(self):
        """Обновляет экран, не вызывает onStart"""
        self.hash_map.put('RefreshScreen', '')

    def run_event(self, method_name):
        self['RunEvent'] = json.dumps(self._get_event(method_name))

    def run_event_async(self, method_name, post_execute_method=None,
                        do_not_format_post_ex: bool = None,
                        return_event: bool = None):
        run_event = self._get_event(method_name, 'runasync')
        if isinstance(post_execute_method, str):
            if do_not_format_post_ex:
                run_event[0]['postExecute'] = post_execute_method
            else:
                run_event[0]['postExecute'] = json.dumps(self._get_event(post_execute_method))
        elif isinstance(post_execute_method, list):
            overall_post_execute = self.pack_post_execute_handlers(post_execute_method)
            run_event[0]['postExecute'] = overall_post_execute
        if return_event:
            return run_event
        else:
            self['RunEvent'] = json.dumps(run_event)

    def run_event_progress(self, method_name, post_execute_method=None,
                           do_not_format_post_ex: bool = None,
                           return_event: bool = None):
        run_event = self._get_event(method_name, 'runprogress')
        if isinstance(post_execute_method, str):
            if do_not_format_post_ex:
                run_event[0]['postExecute'] = post_execute_method
            else:
                run_event[0]['postExecute'] = json.dumps(self._get_event(post_execute_method))
        elif isinstance(post_execute_method, list):
            overall_post_execute = self.pack_post_execute_handlers(post_execute_method)
            run_event[0]['postExecute'] = overall_post_execute
        if return_event:
            return run_event
        else:
            self['RunEvent'] = json.dumps(run_event)

    def pack_post_execute_handlers(self, post_execute_list):
        post_handlers = []
        for handler in post_execute_list:
            event = self._get_event(handler, action='run')
            post_handlers += event
        return json.dumps(post_handlers)

    def beep(self, tone=''):
        self.hash_map.put('beep', str(tone))

    def _get_event(self, method_name, action=None) -> List[dict]:
        """
        :param method_name: handlers name
        :param action: run|runasync|runprogress

        :return: event dict
        """

        evt = [{
            'action': action if action else 'run',
            'type': 'python',
            'method': method_name,
        }]

        return evt

    def __getitem__(self, item):
        return self.get(item, False)

    def __setitem__(self, key, value):
        self.put(key, value, False)

    def get(self, item, from_json=False):
        if from_json:
            return json.loads(self.hash_map.get(item)) if self.hash_map.get(item) else None
        else:
            return self.hash_map.get(item)

    def get_json(self, item):
        return json.loads(self.hash_map.get(item)) if self.hash_map.get(item) else None

    def get_bool(self, item) -> bool:
        value = str(self.hash_map.get(item)).lower() not in ('0', 'false', 'none')
        return value

    def put(self, key, value: Union[str, List, Dict, bool] = '', to_json=False):
        if to_json:
            self.hash_map.put(key, json.dumps(value))
        else:
            if isinstance(value, bool):
                value = str(value).lower()
            self.hash_map.put(key, str(value))

    def put_bool(self, key, value: Any):
        value = False if str(value).lower() in ('false', 'none', '0') else bool(value)
        self.put(key, value)

    def put_data(self, data: dict, fill_none=False, default=''):
        if data:
            for key, value in data.items():
                if value is None and fill_none:
                    value = default

                self[key] = value

    def containsKey(self, key):
        return self.hash_map.containsKey(key)

    def key_set(self) -> str:
        return self.hash_map.keySet()

    def keys(self) -> List[str]:
        keys = str(self.key_set())
        return keys[1:len(keys) - 1].split(', ')

    def items(self) -> List[Tuple[str, Optional[str]]]:
        return [(key, self[key]) for key in self.keys()]

    def items_size(self, size_filter: int = 1) -> Dict[str, float]:
        items_size = [(item[0], sys.getsizeof(item[1]) / 1024) for item in self.items()]
        if size_filter:
            items_size = filter(lambda x: x[1] > size_filter, items_size)
        return dict(items_size)

    def check_hash_map_size(self, logger, max_size: int = 300):
        """Функция для дебага размера HashMap"""
        items_size = self.items_size()
        overall_size = sum(items_size.values())
        if overall_size > max_size:
            logger.error(f'Размер HashMap превышает {max_size} \n'
                         f'{items_size}')

    def remove(self, key):
        self.hash_map.remove(key)

    def delete(self, key):
        self.hash_map.remove(key)

    def add_to_cv_list(
            self,
            element: Union[str, dict],
            cv_list: Literal['green_list', 'yellow_list', 'red_list', 'gray_list',
                             'blue_list', 'hidden_list', 'object_info_list',
                             'stop_listener_list', 'object_caption_list',
                             'object_detector_mode'],
            _dict: bool = False
    ) -> None:
        """ Добавляет в cv-список элемент, или создает новый список с этим элементом.
            object_info_list - Информация об объекте (снизу). [{'object': object_id: str, 'info': value}]
            object_detector_mode - Режим детектора. [{'object_id': object_id: int, 'mode': barcode|ocr|stop}]
            object_caption_list - Информация об объекте (сверху). [{'object': object_id: str, 'caption': value}]
            stop_listener_list - Блокирует выполние обработчиков для объектов в списке
        """

        if _dict:
            lst = self.get(cv_list, from_json=True) or []
            if element not in lst:
                lst.append(element)
                self.put(cv_list, json.dumps(lst, ensure_ascii=False))

        else:
            lst = self.get(cv_list)
            lst = lst.split(';') if lst else []
            if element not in lst:
                lst.append(element)
                self.put(cv_list, ';'.join(lst))

    def remove_from_cv_list(
        self,
        element: Union[str, dict],
        cv_list: Literal['green_list', 'yellow_list', 'red_list', 'gray_list',
                         'blue_list', 'hidden_list', 'object_info_list',
                         'stop_listener_list', 'object_caption_list',
                         'object_detector_mode'],
        _dict: bool = False
    ):
        """Удаляет из cv-списка"""
        if _dict:
            lst = self.get(cv_list, from_json=True) or []
            try:
                lst.remove(element)
                self.put(cv_list, json.dumps(lst, ensure_ascii=False))
            except ValueError:
                pass
        else:
            lst = self.get(cv_list)
            lst = lst.split(';') if lst else []
            if element in lst:
                lst.remove(element)
                self.put(cv_list, ';'.join(lst))

    def set_vision_settings(
            self,
            values_list: str,
            type_rec: str = 'Text',
            NumberRecognition: bool = False,
            DateRecognition: bool = False,
            PlateNumberRecognition: bool = False,
            min_length: int = 1,
            max_length: int = 20,
            result_var: str = 'ocr_result',
            mesure_qty: int = 1,
            min_freq: int = 1,
            query: str = '',
            control_field: str = '',
            cursor: Optional[list] = None,
            count_objects: int = 0,
            ReplaceO: bool = False,
            ToUpcase: bool = False,
    ):
        """query - SQL запрос для варианта поиска по SQL-таблице с одинм параметром(в который передается распознанный текст )
                Например: select * from SW_Goods where product_number like  ?
           control_field - поле таблицы по которому проверяется OCR , условно Артикул (несмотря на то, что в query оно скорее всего также участвует)
           cursor - Массив  с объектами {"field":<поле таблицы>,"var":<переменная результат>}
           values_list - Режим поиска по списку, либо обработчиком ("~")
           mesure_qty - Количество измерений плотности вероятности (норм. распределение)
           min_freq - Вероятность (в процентах от 0 до 100 для удобства ввода)
           min_length - Минимальная длина текста
           max_length - Максимальная длина текста
           count_objects - Для NumberRecognition количество циклов измерений для решения комбинаторной задачи. Чем больше циклов тем больше точность
           ReplaceO - Заменить буквы О на 0 (нули)
           ToUpcase - Преобразование в верхний регистр
           PlateNumberRecognition - Российские номера (только для ActiveCV)
           NumberRecognition - Распознавание чисел
           DateRecognition - Распознавние дат
           result_field  для распознвания дат и номеров, туда помещается результаты особым образом (смотря что ищем)"""
        if cursor is None:
            cursor = []
        settings = {
            "TypeRecognition": type_rec,
            "NumberRecognition": NumberRecognition,
            "DateRecognition": DateRecognition,
            "PlateNumberRecognition": PlateNumberRecognition,
            "min_length": min_length,
            "max_length": max_length,
            "values_list": values_list,
            "result_var": result_var,
            "mesure_qty": mesure_qty,
            "min_freq": min_freq,
            "query": query,
            "control_field": control_field,
            "cursor": cursor,
            "count_objects": count_objects,
            "ReplaceO": ReplaceO,
            "ToUpcase": ToUpcase
        }
        self.hash_map.put("SetVisionSettings", json.dumps(settings))

    def show_screen(self, screen_name, process_name: Optional[str] = None, data=None):
        name = screen_name if not process_name else f'{process_name}|{screen_name}'
        self.put('ShowScreen', name)
        if data:
            self.put_data(data)

    def show_process_result(self, process, screen, data: dict = None):
        if process and screen:
            self.hash_map.put('ShowProcessResult', f'{process}|{screen}')

            if data:
                self.put_data(data)

    def show_process_screen(self, process: str, screen: Optional[str] = None):
        process_screen = {'process': process, 'screen': screen}
        self.hash_map.put('ShowProcessScreen', json.dumps(process_screen, ensure_ascii=False))

    def switch_process_screen(self, process: str, screen: Optional[str] = None):
        process_screen = f'{process}|{screen}' if screen else process
        self.hash_map.put('SwitchProcessScreen', process_screen)

    def html2png(
            self,
            html: str,
            action: Literal['runasync', 'runprogress'],
            post_exec_handlers: Optional[List] = None,
            width: Optional[str] = None,
            height: Optional[str] = None,
            file_path: Optional[str] = None
    ):
        event = {
            "action": action,
            "type": "html2image",
            "method": html,
            "postExecute": json.dumps(post_exec_handlers) if post_exec_handlers else '[]'
        }

        self.put("RunEvent", json.dumps([event]))
        if width:
            self.put("html2image_width", width)
        if height:
            self.put("html2image_height", height)
        if file_path:
            self.put('html2image_ToFile', file_path)

    def save_external_file(self, path_to_file: str, default_name: str):
        """
        Команда запуска диалога выбора локации сохранения файла и
        имени файла (можно выбрать имя по умолчанию).
        При успешном сохранении генерируется событие FileSave
        """
        file_settings = {
            'path': path_to_file,
            'default': default_name
        }
        self.put('SaveExternalFile', json.dumps(file_settings))

    def open_external_file(self):
        """
        Команда запуска диалога, при открытии файла генерируется событие FileOpen,
        которое можно перехватить в обработчике типа pythonbytes,
        в который попадает байт-массив открытого файла
        """
        self.put('OpenExternalFile')

    def show_dialog(self, listener, title='', buttons=None, dialog_layout=None):
        self.delete('ShowDialogLayout')
        self.put("ShowDialog", listener)

        if dialog_layout:
            self.put('ShowDialogLayout', dialog_layout)

        if title or buttons:
            dialog_style = {
                'title': title or listener,
                'yes': 'Ок',
                'no': 'Отмена'
            }
            if buttons and len(buttons) > 1:
                dialog_style['yes'] = buttons[0]
                dialog_style['no'] = buttons[1]

            self.put('ShowDialogStyle', dialog_style)

    def set_json_screen(self, screen: dict):
        self.put('setJSONScreen', screen, to_json=True)

    def get_json_screen(self):
        self.put('getJSONScreen')

    def json_screen(self):
        return self.get('JSONScreen', from_json=True)
    
    def set_root_layout(self, layout: dict):
        '''
        Установка корневого контейнера экрана
        '''
        self.put("SetRootLayout", layout)

    def get_current_screen(self):
        return self['current_screen_name'] if self.containsKey('current_screen_name') else ''

    def get_parent_screen(self):
        return self['parent_screen'] if self.containsKey('parent_screen') else ''

    def get_current_process(self):
        return self['current_process_name']

    def set_title(self, title):
        self['SetTitle'] = title

    def run_py_thread_progress(self, handlers_name: str):
        """
        Запускает асинхронное фоновое выполнение скрипта c блокирующим прогресс-баром, который блокирует UI-поток.
        В качестве аргумента - имя функции-хендлера.
        """

        self['RunPyThreadProgressDef'] = handlers_name

    def sql_exec(self, query, params=''):
        self._put_sql('SQLExec', query, params)

    def sql_exec_many(self, query, params=None):
        params = params or []
        self._put_sql('SQLExecMany', query, params)

    def sql_query(self, query, params=''):
        self._put_sql('SQLQuery', query, params)

    def _put_sql(self, sql_type, query, params):
        self.put(
            sql_type,
            {"query": query, 'params': params},
            to_json=True
        )

    def back_screen(self):
        self['BackScreen'] = ''

    def no_refresh(self):
        """Блокирует вызов onStart после текущего обработчика"""
        self['noRefresh'] = ''


def create_file(
        ext: str,
        folder: Optional[str] = None,
        file_name: Optional[str] = None,
):
    """Создание файла с необходимым расширением."""
    path = Path(suClass.get_temp_dir())
    if folder:
        path /= folder
        path.mkdir(parents=True, exist_ok=True)

    file_path = f'{path}/{file_name}.{ext}' if file_name else f'{path}/{str(uuid.uuid4())}.{ext}'
    open(file_path, 'w').close()
    return file_path


def error_handler_decorator(logger=None):
    """Полный traceback ошибки в удобном виде"""
    def inner_decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_info = str(e) + '\n'
                for tb in traceback.extract_tb(e.__traceback__):
                    file_name = os.path.basename(tb.filename)
                    line_number = tb.lineno
                    error_info += f"File: {file_name} Line: {line_number - 3}\n"
                if logger:
                    logger.error(error_info)
                print(error_info)
                raise e
        return wrapper
    return inner_decorator


class ButtonRedrawClass:
    """
    Класс для изменения внешнего вида кнопок.
    Перерисовка кнопок должна происходить в on_post_start обработчиках
    """
    _buttons_to_redraw = []

    @classmethod
    def set_buttons_to_redraw(cls, buttons_to_redraw: List[str]):
        """Устанавливает список переменых кнопок для перерисовки. Обновлять этот список лучше всего в on_start"""
        cls._buttons_to_redraw = buttons_to_redraw

    @classmethod
    def redraw_buttons(cls):
        """Перерсовывает все кнопки, переменные которых находятся в переменной класса _buttons_to_redraw"""
        for button in cls._buttons_to_redraw:
            ButtonRedrawClass.redraw_button(button)

    @staticmethod
    def redraw_button(
            button_name: str,
            first_color: str = '#FFFFFF',
            second_color: str = '#FFFFFF',
            corner_radius: int = 0,
            stroke_color: Optional[str] = '#000000',
            stroke_width: int = 1,
            margin_left: int = 10,
            margin_top: int = 5,
            margin_right: int = 10,
            margin_bottom: int = 5,
            padding_left: int = 3,
            padding_top: int = 3,
            padding_right: int = 3,
            padding_bottom: int = 3,
            button_height: int = 37
    ):
        """Перерисовывет кнопку если она есть на экране
        button_name - переменная кнопки
        density - коэффициент для сохранения пропорций элемента на разных экранах
        """
        from android.widget import Switch, TextView, LinearLayout
        from android.graphics.drawable import GradientDrawable
        from android.graphics import Color
        from ru.travelfood.simple_ui import ImportUtils as iuClass
        btn = iuClass.getView(button_name)
        if not btn:
            return
        context = iuClass.getContext()
        density = context.getResources().getDisplayMetrics().density
        gradient_drawable = GradientDrawable()
        gradient_drawable.setColors([Color.parseColor(first_color), Color.parseColor(second_color)])
        if corner_radius:
            gradient_drawable.setCornerRadius(corner_radius * density)
        if stroke_color:
            gradient_drawable.setStroke(int(stroke_width * density), Color.parseColor(stroke_color))
        button_layout_params = LinearLayout.LayoutParams(btn.getLayoutParams())
        margin_bottom = int(margin_bottom * density)
        margin_top = int(margin_top * density)
        margin_left = int(margin_left * density)
        margin_right = int(margin_right * density)
        button_layout_params.setMargins(margin_left, margin_top, margin_right, margin_bottom)
        height = int(button_height * density)
        btn.setMinimumHeight(height)
        btn.setHeight(height)
        btn.setPadding(int(padding_left * density), padding_top, int(padding_right * density), padding_bottom)
        btn.setLayoutParams(button_layout_params)
        btn.setBackground(gradient_drawable)


def import_library_whl(name_of_file: str) -> None:
    """Подключение любой библиотеки Python к конфигурации"""
    import zipfile
    import sys
    import os

    whl_path = suClass.get_stored_file(name_of_file)
    target_dir = suClass.get_temp_dir()
    sys.path.append(target_dir)
    with zipfile.ZipFile(whl_path, "r") as whl:
        whl.extractall(target_dir)
    sys.path.append(os.path.join(target_dir, name_of_file))

