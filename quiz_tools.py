def get_questions():
    with open('mkm17.txt', 'r', encoding='KOI8-R') as file:
        quiz = file.read()

    question = answer = ''
    questions = {}
    for blob in quiz.split('\n\n'):
        if blob.find('Вопрос ') == 0:
            question = ' '.join(blob.split('\n')[1:])
            continue
        if blob.find('Ответ:') == 0:
            answer = ' '.join(blob.split('\n')[1:])
            if answer[-1] == '.':
                answer = answer[:-1]
            questions[question.strip()] = answer.strip()

    return questions