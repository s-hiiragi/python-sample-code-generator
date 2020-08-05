# coding: utf-8


# TODO ネストレベルに応じて識別子の長さを短くしたい
# TODO ネストレベルに応じてブロックの長さを短くしたい
# TODO 直近のスコープに定義された変数を優先して使いたい
# TODO ヨーダ記法に対応したい


import keyword
import itertools
import contextlib
from typing import Optional
from random import randint, choice, choices
from dic_loader import load_dic


class SampleCodeGenerator():

    KEYWORDS = keyword.kwlist

    ID_CHARS_HEAD   = '_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    ID_CHARS_LEAST  = ID_CHARS_HEAD + '0123456789'
    VAR_CHARS_HEAD  = '_abcdefghijklmnopqrstuvwxyz'
    VAR_CHARS_LEAST = VAR_CHARS_HEAD + '0123456789'

    def __init__(self, indent=None, newline=None, encoding=None):

        if isinstance(indent, int):
            self.INDENT = ' ' * indent
        elif isinstance(indent, str):
            self.INDENT = indent
        else:
            self.INDENT = '\t'

        if isinstance(newline, str):
            self.NEWLINE = newline
        else:
            self.NEWLINE = '\n'

        if isinstance(encoding, str):
            self.FILE_ENCODING = encoding
        else:
            self.FILE_ENCODING = 'UTF-8'

        self._dic = [word for word in load_dic() if word not in self.KEYWORDS]

        self.MAX_NEST_LEVEL = 4
        self._nest_level = 0

        # for class, def
        self._scopes = []

    # Internal functions

    @contextlib.contextmanager
    def _indent(self):
        self._nest_level += 1
        try:
            yield None
        finally:
            self._nest_level -= 1

    def _add_scope(self):
        self._scopes.append({})

    def _remove_scope(self):
        self._scopes.pop()

    def _add_var(self, name, type=None):
        self._scopes[-1][name] = {
            'type': type,
            'nest_level': self._nest_level,
        }

    def _remove_trailing_empty_lines(self, lines):
        while lines:
            if lines[-1] == '':
                lines.pop()
            else:
                break
        return lines

    # Functions that returns a string

    def generate_var_by_dic(self, min_length=1, max_length=2):
        k = randint(min_length, max_length)
        s = '_'.join(choices(self._dic, k=k))
        return s

    def def_var_by_dic(self, min_length=1, max_length=2, type=None):
        s = self.generate_var_by_dic(min_length, max_length)
        self._add_var(s, type)
        return s

    def def_specified_var(self, name, type=None):
        self._add_var(name, type)
        return name

    def def_random_var(self, min_length=1, max_length=7, type=None):
        k = randint(min_length, max_length)
        s = choice(self.VAR_CHARS_HEAD)
        if k > 1:
            s += ''.join(choices(self.VAR_CHARS_LEAST, k=k-1))
        self._add_var(s, type)
        return s

    def is_func_defined(self):
        for scope in self._scopes:
            for _, info in scope.items():
                if info['type'] == 'function' and info['nest_level'] <= self._nest_level:
                    return True
        return False

    def use_valname(self) -> str:
        non_valtypes = ['module', 'class', 'function']
        items = []
        for scope in self._scopes:
            for name, info in scope.items():
                if info['type'] not in non_valtypes and info['nest_level'] <= self._nest_level:
                    items.append(name)
        name = choice(items)
        return name

    def use_funcname(self) -> str:
        items = []
        for scope in self._scopes:
            for name, info in scope.items():
                if info['type'] == 'function' and info['nest_level'] <= self._nest_level:
                    items.append(name)
        name = choice(items)
        return name

    def use_name(self) -> str:
        items = []
        for scope in self._scopes:
            for name, info in scope.items():
                if info['nest_level'] <= self._nest_level:
                    items.append(name)
        name = choice(items)
        return name

    def get_var_type(self, name) -> Optional[str]:
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]['type']
        return None

    def def_funcname_by_dic(self, min_length=1, max_length=3):
        k = randint(min_length, max_length)
        s = '_'.join(choices(self._dic, k=k))
        self._add_var(s, type='function')
        return s

    def generate_boundary_int(self):
        return choice([-1, 0, 1])

    def generate_int(self):
        return randint(-254, 255)

    def generate_literal(self):
        valtypes = {
            'None'  : 'NoneType',
            'False' : 'bool',
            'True'  : 'bool',
            '0'     : 'int',
            '0.0'   : 'float',
            '""'    : 'str',
            '[]'    : 'list',
            '{}'    : 'dict',
        }
        k = choice(list(valtypes.keys()))
        return k, valtypes[k]

    def generate_display(self):
        self._add_scope()
        iterable = self.use_valname()  # ループ変数を選択しないよう、先にiterableの名前を決める必要がある
        loop_var = self.def_random_var(max_length=1)
        expr, expr_type = self.generate_expr()  # ループ変数を使用できるよう、後に式を生成する必要がある
        v, t = '[{} for {} in {}]'.format(expr, loop_var, iterable), 'list'
        self._remove_scope()
        return (v, t)

    def generate_default_value(self):
        type_by_val = {
            'None'  : 'NoneType',
            'False' : 'bool',
            '0'     : 'int',
            '0.0'   : 'float',
            '""'    : 'str',
            '[]'    : 'list',
            '{}'    : 'dict',
        }
        v = choice(list(type_by_val.keys()))
        return v, type_by_val[v]

    def generate_expr(self):
        k = choice(['literal', 'display', 'var'])
        if k == 'literal':
            v, t = self.generate_literal()
        elif k == 'display':
            v, t = self.generate_display()
        elif k == 'var':
            v = self.use_valname()
            t = self.get_var_type(v)
        else:
            assert False, k
        return v, t

    # Functions that returns an array of string

    def indent_lines(self, lines, level=1):
        indent = self.INDENT * level
        s = []
        for line in lines:
            if line:
                s.append(indent + line)
            else:
                s.append(line)
        return s

    def generate_file_header(self):
        enc = self.FILE_ENCODING.lower()
        headerstyle = [
            '# coding: {}'.format(enc),
            '# -- vim: fileencoding={} --'.format(enc),
            '# -*- coding: {} -*-'.format(enc)
        ]
        return [choice(headerstyle)]

    def generate_import(self):
        s = []
        k = choice(['import', 'from_import'])
        if k == 'import':
            if randint(0, 1) == 0:
                mod = self.def_var_by_dic(max_length=1, type='module')
                s += ['import {}'.format(mod)]
            else:
                mod = self.generate_var_by_dic(max_length=1)
                alias = self.def_var_by_dic(max_length=1, type='module')
                s += ['import {} as {}'.format(mod, alias)]
        elif k == 'from_import':
            mod = self.def_var_by_dic(max_length=1, type='module')
            if randint(0, 1) == 0:
                if randint(0, 1) == 0:
                    mod2 = self.def_var_by_dic(max_length=1, type='module')
                    s += ['from {} import {}'.format(mod, mod2)]
                else:
                    mod2 = self.generate_var_by_dic(max_length=1)
                    alias = self.def_var_by_dic(max_length=1)
                    s += ['from {} import {} as {}'.format(mod, mod2, alias)]
            else:
                if randint(0, 1) == 0:
                    id = self.def_var_by_dic(max_length=1)
                    s += ['from {} import {}'.format(mod, id)]
                else:
                    id = self.generate_var_by_dic(max_length=1)
                    alias = self.def_var_by_dic(max_length=1)
                    s += ['from {} import {} as {}'.format(mod, id, alias)]
        else:
            assert False, k
        return s

    def generate_stmt(self):
        candidates = {
            'assign': 4,
#            'call': 3,  # 再帰呼出しが発生するので一時的にコメントアウト
            'if': 2,
            'for': 1,
        }

        if self._nest_level >= self.MAX_NEST_LEVEL:
            del candidates['if']
            del candidates['for']

#        if not self.is_func_defined():
#            del candidates['call']

        k = choices(list(candidates.keys()), k=1, weights=list(candidates.values()))[0]

        if k == 'assign':
            s = self.generate_assign()
        elif k == 'call':
            s = self.generate_call()
        elif k == 'if':
            s = self.generate_if()
        elif k == 'for':
            s = self.generate_for()
        elif k == 'blank':
            s = ['']
        else:
            assert False, k
        return s

    def generate_assign(self, var=None, expr=None, expr_type=None):
        if not expr:
            expr, expr_type = self.generate_expr()

        if not var:
            var = self.def_var_by_dic(type=expr_type)

        return ['{} = {}'.format(var, expr)]

    def generate_call(self, funcname=None):
        if not funcname:
            funcname = self.use_funcname()

        return ['{}()'.format(funcname)]

    def generate_if(self, var1=None, var2=None, body_length=None):
        s = []

        if not var1:
            var1 = self.use_valname()

        if not var2:
            var2 = self.generate_literal()[0] if randint(0, 1) == 0 else self.use_valname()

        if not body_length:
            body_length = randint(1, 3)

        # condition part
        num_operands = randint(1, 3)

        if num_operands == 1:
            if randint(0, 1) == 0:
                s += ['if {}:'.format(var1)]
            else:
                s += ['if not {}:'.format(var1)]

        elif num_operands == 2:
            if randint(0, 1) == 0:
                op = choice(['==', '!='])
                s += ['if {} {} {}:'.format(var1, op, var2)]
            else:
                op = choice(['in', 'not in'])
                s += ['if {} {} {}:'.format(var1, op, var2)]

        elif num_operands == 3:
            arg1 = self.generate_int()
            arg3 = self.generate_int()
            if arg1 > arg3:
                arg1, arg3 = arg3, arg1
            s += ['if {} < {} < {}:'.format(arg1, var1, arg3)]

        # body part
        with self._indent():
            for _ in range(body_length):
                s += self.indent_lines(self.generate_stmt())
            self._remove_trailing_empty_lines(s)

        s += ['']
        return s

    def generate_for(self, body_length=None):
        if not body_length:
            body_length = randint(1, 3)

        c = self.use_valname()  # ループ変数を使用しないよう、先にコレクション名を取得する
        s = ['for {} in {}:'.format(self.def_random_var(max_length=1), c)]
        with self._indent():
            for _ in range(body_length):
                s += self.indent_lines(self.generate_stmt())
            self._remove_trailing_empty_lines(s)

        s += ['']
        return s

    def def_func(self, name=None, args=None):
        if not name:
            name = self.def_funcname_by_dic()

        s = []
        self._add_scope()

        if args is None:
            args = []

            # positional args
            for _ in range(randint(0, 3)):
                args.append(self.def_var_by_dic())

            # variable args
            if randint(0, 1):
                args += ['*' + self.def_specified_var('args', type='tuple')]

            # keyword args
            for _ in range(randint(0, 3)):
                def_val, def_type = self.generate_default_value()
                args += [self.def_var_by_dic(type=def_type) + '=' + def_val]

            # dict args
            if randint(0, 1):
                args += ['**' + self.def_specified_var('kwargs', type='dict')]

            args = ', '.join(args)

        s += ['def {}({}):'.format(name, args)]
        with self._indent():
            k = randint(0, 7)
            if k:
                for _ in range(k):
                    s += self.indent_lines(self.generate_stmt())
                self._remove_trailing_empty_lines(s)
            else:
                s += self.indent_lines(['pass'])

        self._remove_scope()
        s += ['']
        s += ['']
        return s

    def generate_file(self):
        s = []
        self._add_scope()

        k = randint(0, 1)
        if k:
            s.extend(self.generate_file_header())
            s.append('')
            s.append('')

        k = randint(0, 10)
        if k:
            for _ in range(k):
                s.extend(self.generate_import())
            s.append('')
            s.append('')

        k = randint(0, 3)
        if k:
            for _ in range(k):
                s.extend(self.def_func())

        k = randint(0, 1)
        if k:
            s.extend(self.def_func(name='main', args=''))
            s.extend([
                "if __name__ == '__main__':",
                self.INDENT + 'main()'
            ])
            s.append('')

        self._remove_scope()

        self._remove_trailing_empty_lines(s)
        code = '\n'.join(s)

        assert self._nest_level == 0
        assert len(self._scopes) == 0

        return code
