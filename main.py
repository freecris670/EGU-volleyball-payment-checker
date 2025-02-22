from src.payment_checker import EventParser
from src.excluded_players import EXCLUDED_PLAYERS
import tkinter as tk
from tkinter import filedialog
from collections import defaultdict
from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation
import os
import sys

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
        "Viacheslav": "Виачеслав",
        # Добавьте другие соответствия имён по необходимости
    }
    
    # Получаем персональное обращение или используем полное имя
    personal_name = name_mappings.get(name, name.split()[0])
    
    # Форматируем даты
    if len(dates) == 1:
        date_str = f"за игру в {dates[0]}"
    else:
        dates_formatted = [d for d in dates[:-1]]
        date_str = f"за игры в {', '.join(dates_formatted)} и {dates[-1]}"
    
    message = f"{personal_name}, привет!\nПодскажи, {date_str} картой оплачивал(а) или наличкой?"
    return message

def group_by_player(results):
    """Группировка дат игр по игрокам"""
    player_dates = defaultdict(list)
    for result in results:
        date, weekday, *name_parts = result.split()
        name = ' '.join(name_parts)
        # Пропускаем исключённых игроков
        if name not in EXCLUDED_PLAYERS:
            player_dates[name].append(f"{weekday} {date}")
    return player_dates

def create_excel_report(player_dates):
    """Создание Excel-отчета с результатами"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Оплаты"

    # Заголовки столбцов
    headers = ["Дата", "Имя", "Вид оплаты", "Статус"]
    for col, header in enumerate(headers, 1):
        ws.cell(row=1, column=col, value=header)

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

    ws.add_data_validation(payment_type_dv)
    ws.add_data_validation(status_dv)

    # Заполняем данные
    row = 2
    for player, dates in player_dates.items():
        for date in dates:
            ws.cell(row=row, column=1, value=date)
            ws.cell(row=row, column=2, value=player)
            
            # Применяем валидацию к ячейкам
            payment_type_dv.add(f'C{row}')
            status_dv.add(f'D{row}')
            
            row += 1

    # Автоматическая настройка ширины столбцов
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column_letter].width = adjusted_width

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