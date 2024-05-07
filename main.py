import os

import android
from ui_utils import HashMap


class QRPriceChecker:
    current_selected_file_path = None
    current_selected_file_name = None
    current_selected_file_items_count = None
    labels_to_print = None
    count_labels_to_print = None
    labels_to_print_discount = None
    count_labels_to_print_discount = None

    def __init__(self):
        self.listeners = {}
        self._set_listeners()

    def on_start(self, hash_map: HashMap):
        hash_map['selected_file_name'] = self.current_selected_file_name or 'Выберите файл CSV'
        hash_map['selected_file_items_count'] = 'Количество элементов в файле: ' + str(
            self.current_selected_file_items_count or 0)
        hash_map['count_labels_to_print'] = f'К печати: {self.count_labels_to_print or 0}'
        hash_map['count_labels_to_print_discount'] = f'К печати(Скидка): {self.count_labels_to_print_discount or 0}'

    def on_input(self, hash_map: HashMap):
        if hash_map.listener in self.listeners:
            self.listeners[hash_map.listener](hash_map)

    def _set_listeners(self):
        self.listeners['btn_print_labels'] = self._print_labels
        self.listeners['btn_print_labels_discount'] = self._print_labels_discount
        self.listeners['btn_start_active_cv'] = self._start_active_cv
        self.listeners['btn_select_file'] = self._select_file
        self.listeners['ON_BACK_PRESSED'] = self.on_back_pressed

    def _print_labels(self, hash_map: HashMap):
        pass

    def _print_labels_discount(self, hash_map: HashMap):
        pass

    def _start_active_cv(self, hash_map: HashMap):
        pass

    def _select_file(self, hash_map: HashMap):
        import csv
        android.toast('Select file')
        hash_map.put('OpenExternalFile', '')

    def on_back_pressed(self, hash_map: HashMap):
        pass


qr_price_checker = QRPriceChecker()


@HashMap()
def qr_on_start(hash_map: HashMap):
    qr_price_checker.on_start(hash_map)


@HashMap()
def qr_on_input(hash_map: HashMap):
    qr_price_checker.on_input(hash_map)


def read_file(hashMap, imageBytes):
    from ru.travelfood.simple_ui import SimpleUtilites as suClass
    filename = suClass.get_temp_dir() + os.sep + "test_file.FILE"
    hashMap.put("toast", filename)
    hashMap.put("beep", "")
    with open(filename, 'wb') as f:
        f.write(imageBytes)

    return hashMap