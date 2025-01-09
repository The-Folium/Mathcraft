class AST_Entry:
    """Клас, що реалізує одну вершину абстрактного синтаксичного дерева"""
    def __init__(self, operator, arguments):
        self.operator = operator
        self.arguments = arguments
        self.value = None

    def __str__(self):
        return f"{self.operator}: {self.arguments}"

    def __repr__(self):
        return self.__str__()

    def calculate(self):
        self.value = self.operator.evaluate(self.arguments)


class AST_Tree:
    """Клас, що реалізує абстрактне синтаксичне дерево"""
    def __init__(self):
        self.entries = []

    def add_entry(self, operator, arguments):
        entry = AST_Entry(operator, arguments)
        self.entries.append(entry)
        return entry

    def evaluate(self):
        for entry in self.entries:
            entry.calculate()
        return self.entries[-1].value if self.entries else None

    def __str__(self):
        result = ""
        for entry in self.entries:
            result += "{" + str(entry) + "} "
        return result + "\n"

    def __repr__(self):
        return self.__str__()

    def disp(self):
        for entry in self.entries:
            print(entry.value)