import json

def get_questions(number):
    file_name = f'questions/{number}.json'
    with open(file_name, 'r', encoding='utf-8') as f:
        templates = json.load(f)
        f.close()
        return templates  # печать нового списка