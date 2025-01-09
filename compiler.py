from token_features import *
from shared import Shared
from AST import *
from settings import *

# Імпортуємо модуль інтеграції тільки якщо у settings.py параметр send_to_drive == True
if send_to_drive:
    from sender import *

# Спроба завантажити вихідний код мовою Mathcraft
try:
    with open(source_file, 'r', encoding="UTF-8") as source:
        source_code = source.readlines()
except FileNotFoundError as e:
    raise FileNotFoundError(f"Source file {source_file} not found. Try to fix path in settings.py")

log_stream = None  # None для логу в консоль, file_object для логу у файл
shared = Shared()  # створюємо об'єкт shared data (names and questions)


# ОСНОВНІ ФУНКЦІЇ КОМПІЛЯТОРА
# ---------------------------
def compile(source_code: list):
    """Функція, яка виконує компіляцію вихідного коду згідно з налаштуваннями"""
    # Препроцесінг
    preprocessed_source = preprocess(source_code)
    if preprocessed_source_log:
        logger("Preprocessed source", preprocessed_source, log_stream)

    # Лексичний аналіз
    tokenized_source = tokenize(preprocessed_source)
    if tokenized_source_log:
        logger("Tokenized source", tokenized_source, log_stream)

    # Синтаксичний аналіз
    AST_forest = build_AST(tokenized_source)

    # Семантичний аналіз і інтерпретація
    evaluate(AST_forest)

    # Формування продукту компіляції - результуючих файлів
    if csv_output:
        with open(output_filename + ".csv", "w", encoding="UTF-8") as output_file:
            for question in shared.questions:
                print(question, file=output_file)

    if txt_output:
        with open(output_filename + ".txt", "w", encoding="UTF-8") as output_file:
            for question in shared.questions:
                print(question.get_txt() + '\n', file=output_file)

    # Відправка CSV-файлу на диск
    if csv_output and send_to_drive:
        upload_and_share(output_filename + ".csv", "task.csv")


def preprocess(raw_source: list) -> list:
    """Функція виконує попередню обробку вихідного файлу мовою Mathcraft"""
    preprocessed_source = []

    new_line = ""
    quote_state = None
    for line in raw_source:
        index = -1
        while index < len(line) - 1:
            index += 1
            ch = line[index]
            quote_state = quote_state_analyzer(quote_state, ch)

            if ch in "{}" and quote_state is None:
                raise SyntaxError("Curly braces outside of the text/formula")

            # Ігнорування подвійних пробілів: "  " -> " "
            if quote_state is None and index > 0 and ch == " " and line[index - 1] == " ":
                continue
            new_line += ch

        # Конкатенація
        if quote_state is None:
            # Заміна фігурних дужок у текстах і формулах на конкатенацію
            curly_start, curly_stop = get_innermost_curly_braces_indices(new_line)
            while curly_start is not None:
                new_line = new_line[:curly_start] + "\"+(" + new_line[curly_start + 1:curly_stop] + ")+\"" + new_line[
                                                                                                             curly_stop + 1:]
                curly_start, curly_stop = get_innermost_curly_braces_indices(new_line)

            # Заміна двохсимвольного оператора .. на його односимвольну версію ~
            final_line = ""
            subindex = -1
            while subindex < len(new_line) - 1:
                subindex += 1
                ch = new_line[subindex]
                quote_state = quote_state_analyzer(quote_state, ch)
                if subindex < len(new_line) - 1 and new_line[subindex:subindex + 2] == ".." and quote_state is None:
                    final_line += "~"
                    subindex += 1
                    continue
                final_line += ch

            preprocessed_source.append(final_line + " ")  # додаємо один кінцевий пробіл (потрібен для парсера)
            new_line = ""
            quote_state = None

    # Вихідний код не може закінчитись, коли відкриті лапки чи квадратні дужки
    if quote_state is not None:
        raise SyntaxError(f"ERROR! qoute_state {quote_state}")

    return preprocessed_source


def tokenize(preprocessed_source: list) -> list:
    """Функція виконує лексичний аналіз вихідного коду"""
    tokenized_source = []
    for line in preprocessed_source:
        token_sequence = tokenize_line(line)
        tokenized_source.append(token_sequence)
    return tokenized_source


def tokenize_line(line: str) -> list:
    """Функція-лексер, яка перетворює рядок символів вихідного коду на послідовність токенів"""
    token_sequence = []
    token_list = syntax.keys()
    index = -1
    pattern = None
    character_buffer = ""
    current_token = None
    while index < len(line) - 2:
        index += 1
        current_character, next_character = line[index:index + 2]
        if current_token is None:  # визначаємо тип токена, якщо наразі ніякий токен не зчитується
            for token in token_list:
                pattern = syntax[token]
                if current_character in pattern["First"] and (pattern["Second"] is None or
                                                              (next_character not in pattern["Last"] and pattern[
                                                                  "First"] not in "\"[")):
                    token_sequence.append(pattern["TokenClass"](current_character, shared))
                    break
                elif current_character in pattern["First"] and ((pattern["Second"] is True) or
                                                                (next_character in pattern["Second"])):
                    current_token = token
                    pattern = syntax[token]
                    character_buffer = current_character
                    break

        else:  # збирання символів токена у буфер
            if pattern["Inner"] is True:
                if current_character in pattern["Last"]:
                    character_buffer += current_character
                    token_sequence.append(pattern["TokenClass"](character_buffer, shared))
                    current_token = None
                else:
                    character_buffer += current_character
            elif current_character in pattern["Inner"]:
                if next_character not in pattern["Inner"]:
                    character_buffer += current_character
                    token_sequence.append(pattern["TokenClass"](character_buffer, shared))
                    current_token = None
                else:
                    character_buffer += current_character
        if token_sequence and token_sequence[-1].data == "#":  # зупинка зчитування, якщо знайдено оператор #
            token_sequence.pop(-1)
            break
    return token_sequence


def evaluate(forest: list):
    """Функція запускає семантичний аналіз і інтерпретацію кожного AST"""
    for tree in forest:
        tree.evaluate()


def build_AST(tokenized_source: list) -> list:
    """Функція-парсер, виконує синтаксичний аналіз токенізованого коду"""
    forest = []     # Ліс - список абстрактних синтаксичних дерев
    for tokenized_line in tokenized_source:
        # Увесь рядок розміщується всередині круглих лапок для уніфікації процедури парсингу
        tokenized_line = [Parenthesis("(", shared)] + tokenized_line + [Parenthesis(")", shared)]
        tree = AST_Tree()
        while len(tokenized_line) > 1:
            # Пошук найбільш вкладених лапок
            start, stop = get_innermost_tokenized_line_indices(tokenized_line)
            # Формування дерева
            subline = tokenized_line[start + 1: stop]
            while len(subline) > 1:
                # Пошук найбільш пріоритетного оператора
                poi = get_prioritized_operator_index(subline)  # poi - prioritized_operator_index
                if poi == len(subline) - 1:
                    raise SyntaxError("Operator at the end of the line")
                right_operand = subline[poi + 1]
                right_bound = poi + 1
                if poi == 0 or isinstance(subline[poi - 1], Operator):
                    left_operand = None
                    left_bound = poi
                else:
                    left_operand = subline[poi - 1]
                    left_bound = poi - 1
                tree.add_entry(subline[poi], (left_operand, right_operand))
                subline = subline[:left_bound] + [tree.entries[-1]] + subline[right_bound + 1:]
            tokenized_line = tokenized_line[:start] + subline + tokenized_line[stop + 1:]

        forest.append(tree)
    return forest

# ДОПОМІЖНІ ФУНКЦІЇ
# -----------------
def quote_state_analyzer(quote_state, ch):
    """Функція, яка відслідковує стан дужок під час препроцесінгу, імплементує машину станів"""
    if ch == "\"":
        if quote_state is None:
            quote_state = "Text"
        elif quote_state == "Text":
            quote_state = None
    elif ch == "[" and quote_state is None:
        quote_state = "Formula"
    elif ch == "]" and quote_state == "Formula":
        quote_state = None
    return quote_state


def get_innermost_tokenized_line_indices(tokenized_line: list) -> tuple:
    """Функція знаходить індекси найбільш вкладених лівої і правої дужки у списку токенів"""
    current_depth = max_depth = 0
    start, stop = None, None
    parentheses_are_open = False

    for index, token in enumerate(tokenized_line):
        if isinstance(token, Parenthesis):
            if token.data == "(" and isinstance(token, Parenthesis):
                current_depth += 1
                if current_depth > max_depth:
                    parentheses_are_open = True
                    max_depth = current_depth
                    start = index
            elif token.data == ")" and isinstance(token, Parenthesis):
                if current_depth == max_depth and parentheses_are_open:
                    parentheses_are_open = False
                    stop = index
                current_depth -= 1
            else:
                raise SyntaxError(f"Unknown parenthesis type: \"{token.data}\"")
    return start, stop


def get_innermost_curly_braces_indices(line: str):
    """Функція знаходить індекси найбільш вкладених лівої і правої фігурної дужки в рядку"""
    current_depth = max_depth = 0
    start, stop = None, None
    parentheses_are_open = False

    for index, symbol in enumerate(line):
        if symbol == "{":
            current_depth += 1
            if current_depth > max_depth:
                parentheses_are_open = True
                max_depth = current_depth
                start = index
        elif symbol == "}":
            if current_depth == max_depth and parentheses_are_open:
                parentheses_are_open = False
                stop = index
            current_depth -= 1
        if current_depth < 0:
            raise SyntaxError(f"Invalid curly braces sequence in line: {line}")
    if current_depth != 0:
        raise SyntaxError(f"Invalid curly braces sequence in line: {line}")
    return start, stop


def get_prioritized_operator_index(subline) -> int:
    """Функція повертає індекс токена, що відповідає найпріоритетнішому оператору в рядку без дужок"""
    high_priority_found = max(Operator.operator_priority.values()) + 1 # починаємо з найменшого пріоритету (більше число означає менший пріоритет)
    index_found = None
    for index, token in enumerate(subline):
        if isinstance(token, Operator) and token.get_priority() < high_priority_found:
            high_priority_found = token.get_priority()
            index_found = index
    return index_found


def logger(text, data, log_stream):
    """Функція друкує лог у зазначений потік"""
    print(text + "\n" + "-" * len(text) + "\n" + str(data) + "\n\n", file=log_stream)


# Запуск компілятора при запуску файлу compiler.py
if __name__ == "__main__":
    compile(source_code)