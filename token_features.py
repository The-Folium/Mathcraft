# Цей файл містить ознаки токенів, що дозволяє лексеру екстрагувати їх з вихідного коду

from tokens import *
from string import digits, ascii_letters as letters

syntax = {
    "Number":     {"First": "." + digits,
                   "Second": "." + digits,
                   "Inner": "." + digits,
                   "Last": "." + digits,
                   "Unique": ".",
                   "TokenClass": Number
                   },
    "Text":       {"First": "\"",
                   "Second": True,
                   "Inner": True,
                   "Last": "\"",
                   "Unique": None,
                   "TokenClass": Text
                   },
    "Formula":    {"First": "[",
                   "Second": True,
                   "Inner": True,
                   "Last": "]",
                   "Unique": None,
                   "TokenClass": Formula
                   },

    "Name":       {"First": letters + "_",
                   "Second": letters + digits + "_",
                   "Inner": letters + digits + "_",
                   "Last": letters + digits + "_",
                   "Unique": None,
                   "TokenClass": Name
                   },

    "Operator":   {"First": "=~,;\\+-*/^@$#",
                   "Second": None,
                   "Inner": None,
                   "Last": "=~,;\\+-*/^@$#",
                   "Unique": "=~,;\\+-*/^",
                   "TokenClass": Operator
                   },

    "Parethesis": {"First": "()",
                   "Second": None,
                   "Inner": None,
                   "Last": "()",
                   "Unique": "()",
                   "TokenClass": Parenthesis
                   }
}
