from src.payment_checker import EventParser
from src.excluded_players import EXCLUDED_PLAYERS
import tkinter as tk
from tkinter import filedialog
from collections import defaultdict
from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation
import os
import sys
import re

def create_personal_message(name, dates):
    """Создание персонализированного сообщения"""
    # Словарь для персонализированных обращений
    name_mappings = {
        "Maxim Зinovyev": "Макс",
        "Konstantin Podlesnyi": "Костя", 
        "Anya Vilkova": "Аня",
        "Kirill Kriukov": "Кирилл",
        "Ilya Kolomiytsev": "Илья",
        "Anna Kersilova": "Аня",
        "Kniazev Sergei": "Сергей",
        "Fedor Udalov": "Федя",
        "Sergey Konstantinov": "Сергей",
        "Ashot Gevorgyan": "Ашот",
        "Dmitry Kuznetsov": "Дмитрий",
        "Антирепрессант": "Араик",
        "Артем А": "Артем",
        "N": "Никита красивый",
        "Polina Matveeva": "Полина",
        "Daria Goltsova": "Дарья",
        "Viacheslav": "Слава",
        "Svetlana": "Светлана",
        "Valeriy": "Валерий",
        "Nikita Shabalin": "Никита",
        "Alice Koshechkina": "Алиса",
        "Matvey": "Матвей",
        "Ruslan": "Руслан",
        "Anatoliy Kudrin": "Толя",
        "Ivan": "Ваня",
        "Andrey Beloborodov": "Андрей",
        "Vanya": "Ваня",
        "Sergey Tkachuk": "Сергей",
        "Jek": "Женя",
        "Stas Maltsev": "Стас",
        "Noro Stambolyan": "Норо",
        "Narek Sargsyan": "Нарек",
        "Natali": "Натали",
        "Արարատ Մարտիրոսյան": "Арарат",
        "Artur Hovakanyan": "Артур",
        "Edgar": "Эдгар",
        "Greg": "Гриша",
        "Leonid": "Лёня",
        "Davo Abrahamyan": "Даво",
        "Dronte": "Андрей",
        "Lev Nikolsky": "Лев",
        "Vladimir": "Владимир",
        "Ivan Smirnov": "Иван",
        "Kristina Demirtshyan": "Кристина",
        "Ivan Nikolaev": "Ваня",
        # Добавьте другие соответствия имён по необходимости
    }
    
    # Получаем базовое имя без [2], [3] и т.д.
    base_name = re.sub(r'\s*\[\d+\]$', '', name)
    
    # Получаем персональное обращение или используем полное имя
    personal_name = name_mappings.get(base_name, base_name.split()[0])
    
    # Форматируем даты
    if len(dates) == 1:
        date_str = f"за игру в {dates[0]}"
    else:
        dates_formatted = [d for d in dates[:-1]]
        date_str = f"за игры в {', '.join(dates_formatted)} и {dates[-1]}"
    
    message = f"{personal_name}, привет!\n\nПодскажи, {date_str} картой оплачивал или наличкой?"
    return message

def group_by_player(results):
    """Группировка дат игр по игрокам"""
    player_dates = defaultdict(list)
    for result in results:
        date, weekday, *name_parts = result.split()
        full_name = ' '.join(name_parts)
        
        # Пропускаем исключённых игроков
        base_name = re.sub(r'\s*\[\d+\]$', '', full_name)  # Удаляем [2], [3] и т.д. для проверки в списке исключений
        
        if base_name not in EXCLUDED_PLAYERS:
            player_dates[full_name].append(f"{weekday} {date}")
    return player_dates

def create_excel_report(player_dates):
    """Создание Excel-отчета с результатами"""
    wb = Workbook()
    
    # Создаем первую вкладку с оплатами
    ws_payments = wb.active
    ws_payments.title = "Оплаты"

    # Заголовки столбцов
    headers = ["Дата", "Имя", "Вид оплаты", "Статус"]
    for col, header in enumerate(headers, 1):
        ws_payments.cell(row=1, column=col, value=header)

    # Создаем выпадающие списки
    payment_type_dv = DataValidation(
        type="list",
        formula1='"картой,наличкой"',
        allow_blank=True
    )
    
    status_dv = DataValidation(
        type="list",
        formula1='"Запрос оплаты,Оплачено,Отсутствовал"',
        allow_blank=True
    )

    ws_payments.add_data_validation(payment_type_dv)
    ws_payments.add_data_validation(status_dv)

    # Заполняем данные на первой вкладке
    row = 2
    for player, dates in player_dates.items():
        for date in dates:
            ws_payments.cell(row=row, column=1, value=date)
            ws_payments.cell(row=row, column=2, value=player)
            
            # Применяем валидацию к ячейкам
            payment_type_dv.add(f'C{row}')
            status_dv.add(f'D{row}')
            
            row += 1

    # Автоматическая настройка ширины столбцов
    for column in ws_payments.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws_payments.column_dimensions[column_letter].width = adjusted_width

    # Создаем вторую вкладку с личными сообщениями
    ws_messages = wb.create_sheet(title="Личные сообщения")
    ws_messages.column_dimensions['A'].width = 30
    ws_messages.column_dimensions['B'].width = 70

    # Заголовки для личных сообщений
    ws_messages.cell(row=1, column=1, value="Имя")
    ws_messages.cell(row=1, column=2, value="Сообщение")

    # Заполняем личные сообщения
    row = 2
    for player, dates in player_dates.items():
        message = create_personal_message(player, dates)
        ws_messages.cell(row=row, column=1, value=player)
        ws_messages.cell(row=row, column=2, value=message)
        row += 1

    # Изменяем логику сохранения файла
    try:
        # Получаем путь к директории, где находится исполняемый файл
        if getattr(sys, 'frozen', False):
            # Если это скомпилированный exe
            application_path = os.path.dirname(sys.executable)
        else:
            # Если это python скрипт
            application_path = os.path.dirname(os.path.abspath(__file__))
            
        # Создаем директорию для отчетов, если её нет
        reports_dir = os.path.join(application_path, 'reports')
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
            
        # Предлагаем сохранить файл
        file_path = filedialog.asksaveasfilename(
            initialdir=reports_dir,
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Сохранить отчет как..."
        )
        
        if file_path:
            wb.save(file_path)
            print(f"\nОтчет сохранен в файл: {file_path}")
        else:
            print("\nСохранение отчета отменено")
            
    except Exception as e:
        print(f"\nОшибка при сохранении файла: {e}")

def main():
    # Создаём корневое окно и сразу скрываем его
    root = tk.Tk()
    root.withdraw()

    # Открываем диалоговое окно выбора файла
    print("Выберите текстовый файл с данными события...")
    file_path = filedialog.askopenfilename(
        title="Выберите файл с данными события",
        filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
    )

    if not file_path:
        print("Файл не выбран. Программа завершена.")
        return

    try:
        # Читаем содержимое файла
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()

        # Создаём парсер и обрабатываем текст
        parser = EventParser()
        results = parser.parse_event_text(text)
        
        # Группируем результаты по игрокам
        player_dates = group_by_player(results)
        
        # Выводим результаты и создаём личные сообщения
        print("\nРезультаты обработки и личные сообщения:")
        print("=" * 50)
        for player, dates in player_dates.items():
            print(f"\nИгрок: {player}")
            print(f"Даты игр: {', '.join(dates)}")
            message = create_personal_message(player, dates)
            print("\nЛичное сообщение:")
            print(message)
            print("-" * 30)

        # Создаем Excel-отчет
        create_excel_report(player_dates)

    except FileNotFoundError:
        print("Ошибка: Файл не найден.")
    except Exception as e:
        print(f"Произошла ошибка при чтении файла: {e}")

if __name__ == "__main__":
    main() 