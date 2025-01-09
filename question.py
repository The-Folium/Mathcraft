class Question:
    """Клас-контейнер для питання, яке створюється мовою Mathcraft"""
    def __init__(self, question="", answer_list=None):
        self.question = question
        if answer_list is None:
            self.answer_list = []
        else:
            self.answer_list = answer_list

    def add_answer(self, new_answer):
        self.answer_list.append("\""+str(new_answer)+"\"")

    def __str__(self):
        return f"\"{self.question}\"" + "," + ",".join(map(str, self.answer_list))

    def get_txt(self):
        answers = ""
        for number, answer in enumerate(self.answer_list, 1):
            answers += ("  " + str(number) + ") " + answer[1:-1] + '\n')
        return (f"{self.question}\n{answers}")

    def __repr__(self):
        return self.__str__()