class Lexer:
    """
    Class for lexical analysis

    Class contents dictionaries (tables):
    1. 'attributes' dictionary: keys are 255 ASCII characters, values are their
    attributes:
        0 - whitespaces;
        1 - small and capital latin letters;
        2 - digits;
        3 - one-char separators;
        4 - characters, two-char separators may begin with;
        5 - other characters (unresolved).
    2. 'two_char_separators' dictionary: keys are two-char separators, values
    are their codes.
    3. 'keywords' dictionary: keys are SIGNAL language's reserved words,
    values their codes.
    4. 'constants' dictionary: keys are numerical constants appearing in
    analysed program code, values are their codes.
    Initially dictionary is empty, it is filled during lexical analysis.
    5. 'identifiers' dictionary: keys are user's identifiers appearing in
    analysed program code, values are their codes.
    Initially dictionary is empty, it is filled during lexical analysis.
    6. 'token_list' is a list of tokens. During lexical analysis is filled
    with elements of three types:
        1) [N, L, P] - a token with code N, standing in line L of source code
        starting from position P;
        2) ['E1', S, L, P] - lexical error #1: unresolved character S, standing
        in line L, position P;
        3) ['E2', L, P] - lexical error #2: unclosed comment starting at
        line L, position P.

    Class contents methods:
    1. __init__(self)
    2. attributes_initial(self)
    3. analysis(self, file)
    4. table_print(self, table, table_name, output=None)
    5. listing(self, only_errors=True, output=None)
    """
    attributes = {}
    two_char_separators = {'($': 301, '$)': 302, '>=': 303, '<=': 304}
    keywords = {'PROCEDURE': 401, 'BEGIN': 402, 'END': 403,
                'LABEL': 404, 'GOTO': 405, 'RETURN': 406,
                'IF': 407, 'THEN': 408, 'ELSE': 409}
    constants = {}
    identifiers = {}
    token_list = []

    def __init__(self):
        self.attributes = self.attributes_initial()

    def attributes_initial(self):
        """
        Fills self.attributes dictionary.
        Returns self.attributes.
        """
        self.attributes = {}
        for i in range(0, 256):
            if i in [8, 9, 10, 13, 32]:
                # \b, \t, \n, return, space
                self.attributes[chr(i)] = 0
            elif i in range(65, 91) or i in range(97, 123):
                # A..Z, a..z
                self.attributes[chr(i)] = 1
            elif i in range(48, 58):
                # 0..9
                self.attributes[chr(i)] = 2
            elif i in [41, 44, 58, 59, 61]:
                # ) , : ; =
                self.attributes[chr(i)] = 3
            elif i in [36, 40, 60, 62]:
                # $ ( < >
                self.attributes[chr(i)] = 4
            else:
                self.attributes[chr(i)] = 5
        return self.attributes

    def analysis(self, file):
        """
        Performs lexical analysis on 'file'.
        Returns self.token_list.
        """
        self.token_list, token, line_count, pos_count = [], '', 0, 0
        ch = file.read(1)
        while ch != "":
            if ch not in self.attributes.keys() or self.attributes[ch] == 5:
                # Wrong character, not form ASCII: error #1
                self.token_list.append(['E1', ch, line_count, pos_count])
                ch = file.read(1)
                pos_count += 1
            elif self.attributes[ch] == 0:
                # Spaces, tabs, newlines etc.
                if ch == "\n":
                    line_count += 1
                    pos_count = 0
                else:
                    pos_count += 1
                ch = file.read(1)
            elif self.attributes[ch] == 1:
                # Identifiers and reserved words
                while ch != "" and self.attributes[ch] in [1, 2]:
                    token += ch.capitalize()
                    ch = file.read(1)
                    pos_count += 1
                if token in self.keywords.keys():
                    self.token_list.append([self.keywords[token], line_count,
                                            pos_count - len(token)])
                else:
                    if not self.identifiers.keys():
                        self.identifiers[token] = 1001
                    elif token in self.identifiers.keys():
                        pass
                    else:
                        self.identifiers[token] = max(self.identifiers.
                                                      values()) + 1
                    self.token_list.append([self.identifiers[token],
                                            line_count,
                                            pos_count - len(token)])
                token = ''
            elif self.attributes[ch] == 2:
                # Numeric constants
                while ch != "" and self.attributes[ch] == 2:
                    token += ch
                    ch = file.read(1)
                    pos_count += 1
                if not self.constants.keys():
                    self.constants[token] = 501
                if token in self.constants.keys():
                    pass
                else:
                    self.constants[token] = max(self.constants.values()) + 1
                self.token_list.append([self.constants[token], line_count,
                                        pos_count - len(token)])
                token = ''
            elif self.attributes[ch] == 3:
                # One-char delimiters: ',' ';' ':' ')'
                self.token_list.append([ord(ch), line_count, pos_count])
                ch = file.read(1)
                pos_count += 1
            elif self.attributes[ch] == 4:
                # ($ file-insertion $), one-char delimiter '(', (*comment*),
                # or '<=', '>=', '<', '>'
                if ch == '(':
                    ch = file.read(1)
                    pos_count += 1
                    if ch == '$':
                        # File insertion begins
                        self.token_list.append([self.two_char_separators["($"],
                                                line_count, pos_count-1])
                        ch = file.read(1)
                        pos_count += 1
                    elif ch == '*':
                        # (*Comment*)
                        ch = file.read(1)
                        pos_count += 1
                        end_comment = False
                        comm_beg_line = line_count
                        comm_beg_pos = pos_count - 2
                        while not (end_comment and ch == ')'):
                            if ch == "":
                                self.token_list.append(['E2', comm_beg_line,
                                                        comm_beg_pos])
                                break
                            elif ch == '*':
                                end_comment = True
                            elif end_comment and ch != '*':
                                end_comment = False
                            ch = file.read(1)
                            pos_count += 1
                        ch = file.read(1)
                        pos_count += 1
                    else:
                        # Just '(' character
                        self.token_list.append([ord('('), line_count,
                                                pos_count-1])
                elif ch == '>':
                    # '>=' or '>'
                    ch = file.read(1)
                    pos_count += 1
                    if ch == '=':
                        self.token_list.append([self.two_char_separators[">="],
                                                line_count, pos_count - 1])
                        ch = file.read(1)
                        pos_count += 1
                    else:
                        self.token_list.append([ord('>'), line_count,
                                                pos_count-1])
                elif ch == '<':
                    # '<=' or '<'
                    ch = file.read(1)
                    pos_count += 1
                    if ch == '=':
                        self.token_list.append([self.two_char_separators["<="],
                                                line_count, pos_count - 1])
                        ch = file.read(1)
                        pos_count += 1
                    else:
                        self.token_list.append([ord('<'), line_count,
                                                pos_count - 1])
                elif ch == '$':
                    # File insertion ends
                    ch = file.read(1)
                    pos_count += 1
                    if ch == ')':
                        self.token_list.append([self.two_char_separators["$)"],
                                                line_count, pos_count-1])
                        ch = file.read(1)
                        pos_count += 1
                    else:
                        self.token_list.append(['E1', '$', line_count,
                                                pos_count-1])
        return self.token_list

    @staticmethod
    def table_print(table, table_name, output=None):
        """
        Prints one of lexer's tables.
        """
        print("%s:" % table_name, file=output)
        for x in table:
            print("#%s: %s" % (table[x], x), file=output)
        print(file=output)

    def listing(self, output=None, only_errors=True):
        """
        Prints the result of lexical analysis: tables, errors and tokens'
        codes with their positions in source code file.
        If only_errors=True, prints only error messages; otherwise prints
        tokens too.
        The parameter 'output' takes a file, which analysis results are
        printed into; if output=None, listing is printed on the screen.
        """
        if not only_errors:
            self.table_print(self.keywords, "Keywords", output)
            self.table_print(self.two_char_separators, "Two-char separators",
                             output)
            self.table_print(self.identifiers, "Identifiers", output)
            self.table_print(self.constants, "Constants", output)
            print("Lexical analysis:")
        for x in self.token_list:
            if x[0] == 'E1':
                print("%s (line %i, position %i)"
                      % (x[1], x[2]+1, x[3]+1), file=output)
            elif x[0] == 'E2':
                pass
            elif x[0] in range(0, 256) and not only_errors:
                print("%s (line %i, position %i)"
                      % (chr(x[0]), x[1]+1, x[2]+1), file=output)
            elif x[0] in range(301, 401) and not only_errors:
                print("#%s (line %i, position %i)"
                      % (x[0], x[1] + 1, x[2] + 1), file=output)
            elif x[0] in range(401, 501) and not only_errors:
                print("#%s (line %i, position %i)"
                      % (x[0], x[1] + 1, x[2] + 1), file=output)
            elif x[0] in range(501, 1001) and not only_errors:
                print("#%s (line %i, position %i)"
                      % (x[0], x[1] + 1, x[2] + 1), file=output)
            elif x[0] >= 1001 and not only_errors:
                print("#%s (line %i, position %i)"
                      % (x[0], x[1] + 1, x[2] + 1), file=output)
            else:
                continue
        print(file=output)


if __name__ == "__main__":
    filename = input("File name [.sig]: ")
    if filename[-4:] != ".sig":
        filename += ".sig"
    f = open(filename, "r")
    lexer = Lexer()
    lexer.analysis(f)
    f.close()
    lexer.listing(only_errors=False)
    input()
