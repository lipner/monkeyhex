import token_utils
import IPython
from IPython.core.magic import register_line_magic

s = """
x = 3fe20
y = x + 420
z = x + y + 15
j = x * z
j += 0cafe
print(j)
"""

NAME = token_utils.py_tokenize.NAME
NUM = token_utils.py_tokenize.NUMBER
EXPECTED_ORDER = (NUM, NAME, None)
ENABLED = False


def _combine_multiple(to_combine):
    """Combine tokens and convert to a hexadecimal number.
    Works for [Number] (e.g. 12) and [Number, Name] (e.g. 12face)"""
    combined_string = "0x" + "".join(token.string for token in to_combine)
    first_token = to_combine[0]
    last_token = to_combine[-1]
    new_token = token_utils.Token((NUM, combined_string, first_token.start, last_token.end, last_token.line))
    return new_token


def _is_hexnum(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False


def transform_hex(source):
    next_expected = 0
    new_tokens = []
    to_combine = []
    
    for token in token_utils.tokenize(source):
        if token.type != EXPECTED_ORDER[next_expected] or not _is_hexnum(token.string):
            if to_combine:
                new_tokens.append(_combine_multiple(to_combine))
                to_combine = []
                next_expected = 0
            new_tokens.append(token)
        else:
            next_expected += 1
            to_combine.append(token)
    
    if to_combine:
        new_tokens.append(_combine_multiple(to_combine))
    
    return token_utils.untokenize(new_tokens)


def transform_hex_lines(lines):
    if not ENABLED:
        return lines
    return [transform_hex(line) for line in lines]


def test_transform_hex():
    compiled = compile(transform_hex(s), '__main__.py', 'exec')
    exec(compiled)


ipy = IPython.get_ipython()
if ipy:
    ipy.input_transformers_post.append(transform_hex_lines)

    @register_line_magic
    def hexinput(line):
        """turn hexadecimal number input <on> or <off>"""
        global ENABLED
        line = line.strip().lower()

        if not line:
            return ENABLED
        elif line == 'on':
            ENABLED = True
        elif line == 'off':
            ENABLED = False
        else:
            raise AttributeError("argument should be <on> or <off>")
