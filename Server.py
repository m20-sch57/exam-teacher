from xmlrpc.server import SimpleXMLRPCServer
import os


class Item:
    """
    Item with fields that should be saved on disk
    """
    def __init__(self, path):
        self.path = path
        if not os.path.exists(path):
            os.makedirs(path)

    def set_attr(self, attr, value):
        """
        Sets value of attribute
        """
        open(os.path.join(self.path, attr), 'w', encoding=ENCODING).write(str(value))

    def get_attr(self, attr):
        """
        Gets value of attribute
        """
        return open(os.path.join(self.path, attr), encoding=ENCODING).read()


def format_str(string):
    """
    Formats string: lowers letters and removes all other symbols except numbers
    """
    string = string.lower()
    string = string.replace('ё', 'е')
    string = ''.join([c for c in string if c.isalnum()])
    return string


def check_connection():
    """
    Verifying connection
    """
    return True


def search_group(group_name):
    """
    Searches for group, using format_str, and returns the name of the group
    """
    for cur_group in os.listdir('groups'):
        if format_str(cur_group) == format_str(group_name):
            return cur_group
    return ''


def search_user(group_name, user_name):
    """
    Searches for user, using format_str, and returns the user name
    """
    for cur_user in os.listdir(os.path.join('groups', group_name, 'users')):
        if format_str(cur_user) == format_str(user_name):
            return cur_user
    return ''


def list_of_exams(group_name):
    """
    Returns list of all available exams in the group
    """
    return os.listdir(os.path.join('groups', group_name, 'exams'))


def number_of_questions(group_name, exam_name):
    """
    Returns number of questions in exam
    """
    return len(os.listdir(os.path.join('groups', group_name, 'exams', exam_name)))


def first_not_passed_question(group_name, user_name, exam_name):
    """
    Finds the first not seen question
    """
    directory = os.path.join('groups', group_name, 'users', user_name, exam_name)
    if not os.path.exists(directory):
        os.makedirs(directory)
    for question_number in range(1, number_of_questions(group_name, exam_name) + 1):
        if not os.path.exists(os.path.join(directory, str(question_number))):
            return question_number
    return number_of_questions(group_name, exam_name) + 1


def get_question(group_name, exam_name, question_number):
    """
    Returns the question data without student's answer
    """
    question_item = Item(os.path.join('groups', group_name, 'exams', exam_name, str(question_number)))
    if question_item.get_attr('type') == 'Тест':
        variants = question_item.get_attr('variants').split('\n')
        return {'statement': question_item.get_attr('statement'),
                'variants': variants,
                'correct': variants[int(question_item.get_attr('correct')) - 1],
                'time': int(question_item.get_attr('time')),
                'type': question_item.get_attr('type'),
                'max': 1}
    elif question_item.get_attr('type') == 'Короткий ответ':
        return {'statement': question_item.get_attr('statement'),
                'correct': question_item.get_attr('correct').split('\n'),
                'time': int(question_item.get_attr('time')),
                'type': question_item.get_attr('type'),
                'max': 1}
    else:
        return {}


def get_answer(group_name, user_name, exam_name, question_number):
    """
    Returns the student's answer
    """
    answer_item = Item(os.path.join('groups', group_name, 'users', user_name, exam_name, str(question_number)))
    return {'answer': answer_item.get_attr('answer'),
            'score': int(answer_item.get_attr('score'))}


def view_question(group_name, user_name, exam_name, question_number):
    """
    Registers that student opened question
    """
    answer_item = Item(os.path.join('groups', group_name, 'users', user_name, exam_name, str(question_number)))
    answer_item.set_attr('answer', '')
    answer_item.set_attr('score', 0)
    return get_question(group_name, exam_name, question_number)


def view_details(group_name, user_name, exam_name, question_number):
    """
    Returns all question info including the student's answer
    """
    return {**get_question(group_name, exam_name, question_number),
            **get_answer(group_name, user_name, exam_name, question_number)}


def test_checker(answer, correct):
    """
    Checker for Test question
    """
    return int(answer == correct)


def short_checker(answer, correct):
    """
    Checker for Short question
    """
    answer = format_str(answer)
    return int(format_str(answer) in list(map(format_str, correct)))


def check(group_name, user_name, exam_name, question_number, answer):
    """
    Checks student's answer and saves it on disk
    """
    question = get_question(group_name, exam_name, question_number)
    reply = {}
    if question['type'] == 'Тест':
        reply = {'score': test_checker(answer, question['correct'])}
    elif question['type'] == 'Короткий ответ':
        reply = {'score': short_checker(answer, question['correct'])}
    elif question['type'] == 'Развёрнутый ответ':
        reply = {'score': -1}
    answer_item = Item(os.path.join('groups', group_name, 'users', user_name, exam_name, str(question_number)))
    answer_item.set_attr('answer', answer)
    answer_item.set_attr('score', reply['score'])
    return reply


ENCODING = 'utf-8-sig'
server = SimpleXMLRPCServer(('', 8000))
server.register_function(check_connection)
server.register_function(search_group)
server.register_function(search_user)
server.register_function(list_of_exams)
server.register_function(number_of_questions)
server.register_function(first_not_passed_question)
server.register_function(get_question)
server.register_function(get_answer)
server.register_function(view_question)
server.register_function(view_details)
server.register_function(check)
server.serve_forever()
