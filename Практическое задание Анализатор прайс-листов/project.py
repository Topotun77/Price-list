import os
from pprint import pprint
import csv

WORD_DICT = {
    'name': ['товар', 'название', 'наименование', 'продукт'],
    'price': ['розница', 'цена'],
    'weight': ['вес', 'масса', 'фасовка'],
}


class PriceMachine:

    def __init__(self):
        self.data = []
        self.result = []

    def load_prices(self, file_path=''):
        """
            Сканирует указанный каталог. Ищет файлы со словом price в названии.
            В файле ищет столбцы с названием товара, ценой и весом.
            Допустимые названия для столбца с товаром:
                товар
                название
                наименование
                продукт
                
            Допустимые названия для столбца с ценой:
                розница
                цена
                
            Допустимые названия для столбца с весом (в кг.)
                вес
                масса
                фасовка
        """
        file_path = os.path.abspath(file_path)
        for dir_, _, files in os.walk(file_path):
            print('\nСписок файлов для обработки:', files)
            for fl_ in files:
                filepath = os.path.join(dir_, fl_)
                if 'price' in str(fl_):
                    print(f'Обнаружен файл: {fl_}, обрабатываем...')
                    with open(filepath, newline='', encoding='utf-8') as cf:
                        data_ = csv.DictReader(cf)
                        print(f'Список полей: {data_.fieldnames}')
                        if data_:
                            for dt in data_:
                                product_line: dict = {}
                                for i in data_.fieldnames:
                                    # Здесь можно организовать цикл по WORD_DICT, это сократит код, и добавит
                                    # универсальности в случае, если у нас добавятся еще поля, но будет менее
                                    # читаемо, поэтому оставила простой перебор
                                    if i in WORD_DICT['name']:
                                        product_line['name'] = dt[i]
                                    elif i in WORD_DICT['price']:
                                        product_line['price'] = float(dt[i])
                                    elif i in WORD_DICT['weight']:
                                        product_line['weight'] = int(dt[i])
                                if product_line:
                                    product_line['file_name'] = str(fl_)
                                    self.data += [product_line]
                            # self.data += data_
        print('--- Обработка закончена ---\n')
        return self.data

    def export_to_html(self, fname='output.html'):
        """
        Вывод результатов в HTML-файл
        """
        result = '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Позиции продуктов</title>
        </head>
        <body>
            <table border="1">
                <thead>
                <tr>
                    <th>Номер</th>
                    <th>Название</th>
                    <th>Цена</th>
                    <th>Фасовка</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>
                </thead>
                <tbody>
        '''
        try:
            for i in range(len(self.result)):
                data = self.result[i]
                result += (f'<tr><td>{i+1}</td><td>{data["name"]}</td><td>{data["price"]:.2f}</td>'
                           f'<td>{data["weight"]}</td><td>{data["file_name"]}</td>'
                           f'<td>{data["price_kg"]:.2f}</td></tr>\n')
            result += '</tbody></table></body></html>'
            with open(fname, mode='w', encoding='utf-8') as fn:
                fn.write(result)
            return True
        except Exception as er:
            print(er.args)
            return False

    def find_text(self, text: str) -> list:
        """
        Возвращает список позиций, содержащий текст text в названии продукта
        :param text: текст для поиска
        :return: список найденных строк
        """
        self.result = []
        for dt in self.data:
            if text.lower() in dt['name'].lower():
                data = {**dt, 'price_kg': round(dt["price"] / dt["weight"], 2)}
                self.result += [data]
        if self.result:
            self.result.sort(key=lambda x: x['price_kg'])
        return self.result

    def print_result(self):
        """
        Печать в виде таблицы
        """
        print('-' * 103)
        print(f'| {"№":^4} | {"Название":^40} | {"Цена":^10} | {"Вес":^5} | {"Файл":^15} | {"Цена за кг.":^10}|\n',
              '-'*103, sep='')
        for i in range(len(self.result)):
            data = self.result[i]
            print(f'| {(i + 1):>4} | {data["name"]:<40} | {data["price"]:>10.2f} | '
                  f'{str(data["weight"]):>5} | {data["file_name"]:<15} | {data["price_kg"]:10.2f} |')
        print('-'*103)


if __name__ == '__main__':
    file_path = input('Введите путь к файлам с данными (пустой ввод - текущий каталог):')
    pm = PriceMachine()
    pprint(pm.load_prices(file_path))
    while True:
        search_str = input('\nВведите строку для поиска (Для выхода наберите "exit"): ')
        if search_str.lower() == 'exit':
            break
        pm.find_text(search_str)
        pm.print_result()

    html_flag = input('Вывести данные последнего запроса в HTML-файл (Y/N)? ')
    if html_flag.lower() != 'n':
        print('Результат выгрузки HTML-файла: ', pm.export_to_html())
    print('the end')
