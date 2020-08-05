import re
import csv
from typing import List


_dic = None


def load_dic() -> List[str]:
    global _dic
    if _dic:
        return _dic

    words = []
    with open('dic/ejdict-hand-utf8.txt', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for word, desc in reader:
            if re.match(r'[_a-z][_0-9a-zA-Z]*$', word):
                words.append(word)

    _dic = sorted(words)
    return _dic
