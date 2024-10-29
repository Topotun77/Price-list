import os
from pprint import pprint
import pandas as pd

WORD_DICT = {
    'name': ['товар', 'название', 'наименование', 'продукт'],
    'price': ['розница', 'цена'],
    'weight': ['вес', 'масса', 'фасовка'],
}


class PriceMachine:

    def __init__(self):
        self.data: pd.DataFrame | list = []
        self.result: pd.DataFrame | list = []

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
                    data_ = pd.read_csv(filepath, encoding='utf-8')
                    field_list = data_.columns.values
                    print(f'Список полей: {field_list}')
                    for field in field_list:
                        # Здесь можно организовать цикл по WORD_DICT, это сократит код, и добавит
                        # универсальности в случае, если у нас добавятся еще поля, но будет менее
                        # читаемо, поэтому оставила простой перебор
                        if field in WORD_DICT['name']:
                            data_ = data_.rename(columns={field: 'name'})
                        elif field in WORD_DICT['price']:
                            data_ = data_.rename(columns={field: 'price'})
                        elif field in WORD_DICT['weight']:
                            data_ = data_.rename(columns={field: 'weight'})
                        else:
                            data_ = data_.drop(field, axis=1)
                    data_['price_kg'] = round(data_['price'] / data_['weight'], 2)
                    data_['file_name'] = str(fl_)
                    if len(self.data) == 0:
                        self.data = data_
                    else:
                        self.data = pd.concat([self.data, data_], axis=0)
                    # print(data_)
        print('--- Обработка закончена ---\n')
        return self.data

    def export_to_html(self, fname='output_pd.html'):
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
            i = 1
            for ind, row in self.result.iterrows():
                result += (f'<tr><td>{i}</td><td>{row["name"]}</td><td>{row["price"]:.2f}</td>'
                           f'<td>{row["weight"]}</td><td>{row["file_name"]}</td>'
                           f'<td>{row["price_kg"]:.2f}</td></tr>\n')
                i += 1
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
        dt: pd.DataFrame = self.data
        self.result = dt[dt['name'].str.contains(text, case=False)]
        self.result = self.result.sort_values(by='price_kg')
        return self.result

    def print_result(self):
        """
        Печать в виде таблицы красиво
        """
        print('-' * 103)
        print(f'| {"№":^4} | {"Название":^40} | {"Цена":^10} | {"Вес":^5} | {"Файл":^15} | {"Цена за кг.":^10}|\n',
              '-'*103, sep='')
        i = 1
        for ind, row in self.result.iterrows():
            print(f'| {(i):>4} | {row["name"]:<40} | {row["price"]:>10.2f} | '
                  f'{str(row["weight"]):>5} | {row["file_name"]:<15} | {row["price_kg"]:10.2f} |')
            i += 1
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
        print(pm.result)                # Печать в формате pandos
        pm.print_result()               # Печать в красивом формате

    html_flag = input('Вывести данные последнего запроса в HTML-файл (Y/N)? ')
    if html_flag.lower() != 'n':
        pm.export_to_html()
    print('the end')
    print('Результат выгрузки HTML-файла: ', pm.export_to_html())
