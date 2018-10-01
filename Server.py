from xmlrpc.server import SimpleXMLRPCServer
import os


def format_str(s):
    s = s.lower()
    s = s.replace('ё', 'е')
    s = ''.join([c for c in s if c.isalnum()])
    return s


def check_connection():
    return True


def search_group(group_name):
    for cur_group in os.listdir('groups'):
        if format_str(cur_group) == format_str(group_name):
            return cur_group
    return ''


def search_user(group_name, user_name):
    for cur_user in os.listdir(os.path.join('groups', group_name, 'users')):
        if format_str(cur_user) == format_str(user_name):
            return cur_user
    return ''


def list_of_exams(group_name):
    return os.listdir(os.path.join('groups', group_name, 'exams'))


def number_of_questions(group_name, exam_name):
    return len(os.listdir(os.path.join('groups', group_name, 'exams', exam_name)))


def get_question(group_name, exam_name, question_number):
    directory = os.path.join('groups', group_name, 'exams', exam_name, str(question_number))
    question_type = open(os.path.join(directory, 'type'), encoding=encoding).read()
    if question_type == 'Тест':
        return {'statement': open(os.path.join(directory, 'statement'), encoding=encoding).read(),
                'variants': open(os.path.join(directory, 'variants'), encoding=encoding).read().split('\n'),
                'time': int(open(os.path.join(directory, 'time'), encoding=encoding).read()),
                'type': question_type}
    elif question_type == 'Короткий ответ':
        return {'statement': open(os.path.join(directory, 'statement'), encoding=encoding).read(),
                'time': int(open(os.path.join(directory, 'time'), encoding=encoding).read()),
                'type': question_type}
    else:
        return {}


def get_question_protected(group_name, exam_name, question_number):
    directory = os.path.join('groups', group_name, 'exams', exam_name, str(question_number))
    question_type = open(os.path.join(directory, 'type'), encoding=encoding).read()
    if question_type == 'Тест':
        return {'correct': int(open(os.path.join(directory, 'correct'), encoding=encoding).read())}
    elif question_type == 'Короткий ответ':
        return {'correct': open(os.path.join(directory, 'correct'), encoding=encoding).read().split('\n')}
    elif question_type == 'Развёрнутый ответ':
        return {}
    else:
        return {}


def test_checker(answer, correct):
    return int(answer == correct)


def short_checker(answer, correct):
    answer = format_str(answer)
    return int(format_str(answer) in list(map(format_str, correct)))


def check(group_name, user_name, exam_name, question_number, answer):
    question = get_question(group_name, exam_name, question_number)
    question_protected = get_question_protected(group_name, exam_name, question_number)
    if question['type'] == 'Тест':
        return {'score': test_checker(answer, question_protected['correct']),
                'maximum': 1}
    elif question['type'] == 'Короткий ответ':
        return {'score': short_checker(answer, question_protected['correct']),
                'maximum': 1}
    elif question['type'] == 'Развёрнутый ответ':
        return {'score': -1,
                'maximum': question_protected['maximum']}
    else:
        return {}


encoding = 'utf-8-sig'
server = SimpleXMLRPCServer(('', 8000))
server.register_function(check_connection)
server.register_function(search_group)
server.register_function(search_user)
server.register_function(list_of_exams)
server.register_function(number_of_questions)
server.register_function(get_question)
server.register_function(get_question_protected)
server.register_function(check)
server.serve_forever()
