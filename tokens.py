from random import randint, choice
from AST import *
from question import Question
from string import digits, ascii_letters as letters
from math import isclose


class Token:
    def __init__(self, data, shared):
        self.data = data
        self.shared = shared

    def __str__(self):
        return f"Generic({self.data})"

    def __repr__(self):
        return self.__str__()


class Number(Token):
    """Клас, який є поданням токена Number (число)"""

    def __init__(self, data, shared):
        super().__init__(data, shared)
        if type(data) is str:
            self.value = float(data) if '.' in data else int(data)
        elif type(data) in (int, float):
            self.value = data
        else:
            raise TypeError(f"Unable to create a number token from object {self.data} of type {type(self.data)}:")

    def __str__(self):
        return f"Num({self.value})"

    def __repr__(self):
        return self.__str__()

    def get_value(self):
        return self.value


class Text(Token):
    """Клас, який є поданням токена Text (текст)"""

    def __init__(self, data, shared):
        if data[0] == '\"' and data[-1] == '\"':
            data = data[1:-1]
        super().__init__(data, shared)

        self.value = self.data

    def __str__(self):
        return f"Txt({self.data})"

    def __repr__(self):
        return self.__str__()

    def get_value(self):
        return self.data


class Formula(Token):
    """Клас, який є поданням токена Formula (формула)"""

    superscript = {"0": "⁰",
                   "1": "¹",
                   "2": "²",
                   "3": "³",
                   "4": "⁴",
                   "5": "⁵",
                   "6": "⁶",
                   "7": "⁷",
                   "8": "⁸",
                   "9": "⁹"}

    def __init__(self, data, shared):
        super().__init__(data, shared)
        self.flags = set()

    def __str__(self):
        return f"Form({self.data})"

    def __repr__(self):
        return self.__str__()

    def get_value(self):
        formula = self.data

        # Видаляємо квадратні дужки
        formula = formula[1:-1]

        # Екстрагуємо прапорці
        if formula.count("&") == 1 and (formula.index("&") != len(formula) - 1):
            flags_start = formula.index("&")
            flag_line = formula[flags_start + 1:]
            formula = formula[:flags_start]
            self.flags = set("*-^") & set(flag_line)

        # Замінюємо імена змінних на їхні значення
        for name in self.shared.names:
            while name in formula:
                start = formula.index(name)
                stop = start + len(name) - 1
                if (start == 0 or formula[start - 1] not in letters + digits) and (
                        stop == len(formula) - 1 or formula[start - 1] not in letters + digits):
                    formula = formula.replace(name, str(self.shared.names[name]), 1)

        # Видаляємо пробіли
        formula = formula.replace(" ", "")

        # Форматуємо згідно з прапорцями
        if "-" not in self.flags:
            formula = formula.replace("+-", "-")
            formula = formula.replace("--", "+")
            formula = formula.replace("-1*", "-")
            formula = formula.replace("+1*", "+")
            if formula[0] == "+":
                formula = formula[1:]

        # Видаляємо зайві знаки множення
        if "*" not in self.flags and ("*" in formula):
            changes = True
            while changes and ("*" in formula):
                changes = False
                index = formula.index("*")
                if 0 < index < len(formula) - 1:
                    neighbors = formula[index - 1:index + 2:2]
                    if neighbors == ")(" or (neighbors[0] in digits and neighbors[1] in letters + "_("):
                        formula = formula[:index] + formula[index + 1:]
                        changes = True

        # Форматуємо одноцифрові показники степенів як верхній індекс
        if "^" not in self.flags and "^" in formula:
            changes = True
            while changes and ("^" in formula):
                changes = False

                index = formula.index("^")
                if 0 < index < len(formula) - 1:
                    right_neighbors = formula[index + 1:index + 3]
                    if right_neighbors[0] in digits and right_neighbors[1] not in digits:
                        formula = formula[:index] + self.superscript[formula[index + 1]] + formula[index + 2:]
                        changes = True

        # Додаємо пробілів для краси
        if "_" not in self.flags:
            if "+" in formula and formula.index("+") > 0:
                formula = formula.replace("+", " + ")
            if "-" in formula and formula.index("-") > 0:
                formula = formula.replace("-", " - ")
            if "=" in formula:
                formula = formula.replace("=", " = ")
        return formula


class Name(Token):
    """Клас, який є поданням токена Name (змінна)"""

    def __init__(self, data, shared):
        super().__init__(data, shared)

    def __str__(self):
        return f"Name({self.data})"

    def __repr__(self):
        return self.__str__()

    def __bool__(self):
        return self.data in self.shared.names

    def get_value(self):
        if self:
            return self.shared.names[self.data]
        else:
            raise NameError(f"Name {self.data} is undefined.")

    def set_value(self, value):
        self.shared.names[self.data] = value
        return value

    def get_type(self):
        obj = self.shared.names[self.data]
        if isinstance(obj, (int, float)):
            return Number
        if isinstance(obj, str):
            return Text


class Operator(Token):
    """Клас, який є поданням токена Operator (оператор). Містить реалізації усіх операторів мови"""

    operator_priority = {"^": 1,
                         "*": 2,
                         "/": 2,
                         "+": 3,
                         "-": 3,
                         "~": 4,
                         ",": 5,
                         "\\": 6,
                         ";": 7,
                         "=": 8,
                         "@": 9,
                         "$": 10}

    def __init__(self, data, shared):
        super().__init__(data, shared)

    def __str__(self):
        return f"Op{self.data}"

    def __repr__(self):
        return self.__str__()

    def get_priority(self):
        return self.operator_priority[self.data]

    @staticmethod
    def is_whole(x):
        return isclose(x - round(x), 0)

    @staticmethod
    def get_final_value(obj):
        while not isinstance(obj, (int, float, str)):
            obj = obj.get_value()
        return obj

    def evaluate(self, arguments):
        a, b = arguments
        if isinstance(a, AST_Entry):
            a = a.value

        if isinstance(b, AST_Entry):
            b = b.value

        Number_Producing_Tokens = (Number, Name, Randomizer, Selector)

        match self.data:
            case '+':
                if isinstance(a, Tuple) or isinstance(b, Tuple):
                    raise TypeError(f"Conjunction does not support addition")
                a_value, b_value = self.get_final_value(a), self.get_final_value(b)
                if isinstance(a_value, str) or isinstance(b_value, str):
                    return Text(str(a_value) + str(b_value), self.shared)

                return Number(a_value + b_value, self.shared)

            case '-':
                if isinstance(a, Number_Producing_Tokens) and isinstance(b, Number_Producing_Tokens):
                    return Number(self.get_final_value(a) - self.get_final_value(b), self.shared)
                elif isinstance(b, Number_Producing_Tokens):
                    return Number(-self.get_final_value(b), self.shared)
                else:
                    raise TypeError(f"Unable to evaluate {a} - {b}")

            case '*':
                if isinstance(a, Number_Producing_Tokens) and isinstance(b, Number_Producing_Tokens):
                    return Number(self.get_final_value(a) * self.get_final_value(b), self.shared)
                else:
                    raise TypeError(f"Unable to evaluate {a} * {b}")

            case '/':
                if isinstance(a, Number_Producing_Tokens) and isinstance(b, Number_Producing_Tokens):
                    a_value, b_value = self.get_final_value(a), self.get_final_value(b)
                    if not isinstance(a_value, (int, float)) or not isinstance(b_value, (int, float)):
                        raise ValueError(f"Unable to divide non-numerical values")
                    if isclose(b_value, 0):
                        raise ZeroDivisionError("Division bu zero.")
                    result = a_value / b_value
                    if self.is_whole(result):
                        result = round(result)
                    return Number(result, self.shared)
                else:
                    raise TypeError(f"Unable to evaluate {a} / {b}")

            case '^':
                if isinstance(a, Number_Producing_Tokens) and isinstance(b, Number_Producing_Tokens):
                    result = self.get_final_value(a) ** self.get_final_value(b)
                    if self.is_whole(result):
                        result = round(result)
                    return Number(result, self.shared)
                else:
                    raise TypeError(f"Unable to evaluate {a} ^ {b}")

            case '=':
                if isinstance(a, Name):
                    return a.set_value(self.get_final_value(b))

                elif isinstance(a, Tuple):
                    for element in a.get_value():
                        if isinstance(element, Name):
                            element.set_value(self.get_final_value(b))
                        else:
                            raise TypeError(f"Unable to assign to {element}")
                else:
                    raise TypeError(f"Unable to assign to the object {a} which is not a Name")

            case '\\':
                if isinstance(a, Randomizer) and isinstance(b, Number_Producing_Tokens):
                    return Randomizer(a.left_bound, a.right_bound, [b], self.shared)

                if isinstance(a, Randomizer) and isinstance(b, Tuple):
                    return Randomizer(a.left_bound, a.right_bound, b.get_value(), self.shared)

                else:
                    raise TypeError(f"\\ error: {a}, {b}")

            case '~':
                if isinstance(a, Number_Producing_Tokens) and isinstance(b, Number_Producing_Tokens):
                    return Randomizer(self.get_final_value(a), self.get_final_value(b), [], self.shared)

                else:
                    raise TypeError(f"~ error: {a}..{b}")

            case ',':
                if isinstance(a, (Number, Name)) and isinstance(b, (Number, Name)):
                    return Tuple([a, b], self.shared)
                elif isinstance(a, Tuple) and isinstance(b, (Number, Name)):
                    return Tuple(a.objects + [b], self.shared)
                else:
                    raise TypeError(f"Tuple error")

            case ';':
                if isinstance(a, (Text, Formula, Name, Number, Randomizer)) and isinstance(b, (
                        Text, Formula, Name, Number, Randomizer)):
                    return Selector([a.get_value(), b.get_value()], self.shared)
                elif isinstance(a, (Text, Formula, Name, Number, Randomizer)) and isinstance(b, Selector):
                    return Selector([a.get_value()] + b.values, self.shared)
                elif isinstance(a, Selector) and isinstance(b, (Text, Formula, Name, Number, Randomizer)):
                    return Selector(a.values + [b.get_value()], self.shared)
                else:
                    raise SyntaxError("Selector error")

            case '@':
                if isinstance(b, (Text, Formula, Name, Number, Randomizer, Selector)):
                    question = Question(question=b.get_value())
                    self.shared.questions.append(question)

            case '$':
                if isinstance(b, (Text, Formula, Name, Number, Randomizer, Selector)):
                    question = self.shared.questions[-1]
                    question.add_answer(b.get_value())


class Parenthesis(Token):
    """Клас, який є поданням токена Parenthesis (кругла дужка)"""

    def __init__(self, data, shared):
        super().__init__(data, shared)

    def __str__(self):
        return f"P{self.data}"

    def __repr__(self):
        return self.__str__()


class Randomizer(Token):
    """Клас, який є поданням токена Randomizer (генератор випадкових чисел)"""
    max_attempts = 100  # Кількість спроб генерації випадкового числа

    def __init__(self, left_bound, right_bound, except_for, shared):
        super().__init__(None, shared)
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.except_for = except_for

    def get_value(self):
        for _ in range(self.max_attempts):
            value = randint(self.left_bound, self.right_bound)
            exception_list = map(lambda x: x.get_value(), self.except_for)
            if value not in exception_list:
                return value
        raise ValueError("Unable to generate Random value")


class Tuple(Token):
    """Клас, який є поданням токена Tuple (кортеж)"""

    def __init__(self, objects: list, shared):
        super().__init__(None, shared)
        self.objects = objects

    def get_value(self):
        return self.objects


class Selector(Token):
    """Клас, який є поданням токена Selector (селектор)"""

    def __init__(self, values: list, shared):
        super().__init__(None, shared)
        self.values = values

    def get_value(self):
        return choice(self.values)
