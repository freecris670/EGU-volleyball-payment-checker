from datetime import datetime
import re

class PaymentChecker:
    def __init__(self):
        self.payments = {}
    
    def load_payments(self, filename):
        """Загрузка данных об оплатах из файла"""
        pass
    
    def check_payment(self, student_id):
        """Проверка оплаты для конкретного студента"""
        pass
    
    def add_payment(self, student_id, amount, date):
        """Добавление новой оплаты"""
        pass 

class EventParser:
    def __init__(self):
        self.weekday_map = {
            'Monday': 'пн',
            'Tuesday': 'вт',
            'Wednesday': 'ср',
            'Thursday': 'чт',
            'Friday': 'пт',
            'Saturday': 'сб',
            'Sunday': 'вс'
        }

    def parse_event_text(self, text):
        """Парсинг текста события и получение списка участников"""
        participants = []
        current_date = None
        current_weekday = None
        
        lines = text.split('\n')
        for line in lines:
            # Ищем дату в формате YYYY-MM-DD
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', line)
            if date_match:
                date_str = date_match.group(1)
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                current_date = date_obj.strftime('%d.%m')
                current_weekday = self.weekday_map[date_obj.strftime('%A')]
                continue

            # Ищем участников в формате с votes
            vote_match = re.search(r'[├└]?\s*(?:[\d.]+\s*)?([^(]+)\((\d+)\s*votes\)', line)
            if vote_match and current_date and current_weekday:
                name = vote_match.group(1).strip()
                votes = int(vote_match.group(2))
                for _ in range(votes):
                    participant_str = f"{current_date} {current_weekday} {name}"
                    participants.append(participant_str)
                continue

            # Ищем участников в формате с номером
            numbered_match = re.search(r'[├└]\s*\d+\.\s*([^└├\n]+)', line)
            if numbered_match and current_date and current_weekday:
                name = numbered_match.group(1).strip()
                participant_str = f"{current_date} {current_weekday} {name}"
                participants.append(participant_str)

        return participants