import re


class ValidationUtil:

    @staticmethod
    def is_integer(src, allow_zero=False):

        if allow_zero and src == '0':
            return True

        pattern = re.compile(r'^[1-9][0-9]*$')
        match = pattern.match(src)

        if match is None:
            return False
        return True
