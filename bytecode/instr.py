import opcode

UNSET = object()


def const_key(obj):
    # FIXME: don't use == but a key function, 1 and 1.0 are not the same
    # constant, see _PyCode_ConstantKey() in Objects/codeobject.c
    return (type(obj), obj)


class Label:
    __slots__ = ()


class BaseInstr:
    __slots__ = ('_lineno', '_name', '_arg', '_op')

    def __init__(self, lineno, name, arg=UNSET):
        self._set_lineno(lineno)
        self._set_name(name)
        self._arg = arg

    # FIXME: stack effect

    def _set_lineno(self, lineno):
        if not isinstance(lineno, int):
            raise TypeError("lineno must be an int")
        if lineno < 1:
            raise ValueError("invalid lineno")
        self._lineno = lineno

    def _set_name(self, name):
        if not isinstance(name, str):
            raise TypeError("name must be a str")
        try:
            op = opcode.opmap[name]
        except KeyError:
            raise ValueError("invalid operation name")
        self._name = name
        self._op = op

    @property
    def op(self):
        return self._op

    @op.setter
    def op(self, op):
        if not isinstance(op, int):
            raise TypeError("operator must be an int")
        if 0 <= op <= 255:
            name = opcode.opname[op]
            valid = (name != '<%r>' % op)
        else:
            valid = False
        if not valid:
            raise ValueError("invalid operator")

        self._name = name
        self._op = op

    def format(self, labels):
        text = self.name
        arg = self._arg
        if arg is not UNSET:
            if isinstance(arg, Label):
                arg = '<%s>' % labels[arg]
            else:
                arg = repr(arg)
            text = '%s %s' % (text, arg)
        return text

    def __repr__(self):
        if self._arg is not UNSET:
            return '<%s arg=%r lineno=%s>' % (self._name, self._arg, self._lineno)
        else:
            return '<%s lineno=%s>' % (self._name, self._lineno)

    def _cmp_key(self, labels=None):
        arg = self._arg
        if self._op in opcode.hasconst:
            arg = const_key(arg)
        elif isinstance(arg, Label) and labels is not None:
            arg = labels[arg]
        return (self._lineno, self._name, arg)

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self._cmp_key() == other._cmp_key()

    def is_jump(self):
        return (self._op in opcode.hasjrel or self._op in opcode.hasjabs)

    def is_cond_jump(self):
        # Ex: POP_JUMP_IF_TRUE, JUMP_IF_FALSE_OR_POP
        return ('JUMP_IF_' in self._name)


class Instr(BaseInstr):
    """Abstract instruction.

    lineno, name, op and arg attributes can be modified.

    arg is not checked.
    """

    __slots__ = ()

    @property
    def lineno(self):
        return self._lineno

    @lineno.setter
    def lineno(self, lineno):
        self._set_lineno(lineno)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._set_name(name)

    @property
    def arg(self):
        return self._arg

    @arg.setter
    def arg(self, arg):
        self._arg = arg