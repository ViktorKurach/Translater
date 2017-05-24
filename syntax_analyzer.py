import lexical_analyzer


class Parser:
    """
    Class for syntax analysis.

    Class contents lists:
    1. token_list - list of tokens. Initially is empty; is filled during
    lexical analysis (see lexical_analyzer.token_list description).
    2. syntax_tree list. Initially is empty. If any lexical or syntax error
    occurs, remains empty. If analysis finishes successfully, is filled with
    elements of three types:
        1) N - integer, token's code, represents terminal symbol;
        2) S - string, represents non-terminal symbol, requires L element
        after itself;
        3) L - list, that represents parsing of non-terminal symbol, that
        stands before this list;
        4) "<EMPTY>".
    3. error_list initially is empty. If analysis finishes successfully,
    remains empty; if not - contains lists of next type: [N, L, P], where
    N is error's number, that occurs in line L, position P. For error's
    numbers see self.process_error description.

    Class contents integer variables:
    1. ct (Current Token) - used for iteration through self.token_list.
    2. max_ct = len(self.token_list) - 1

    Class contents objects:
    1. lex - an instance of class Lexer. Is being created by constructor.

    Class contents methods:
    1. __init__(self)
    2. parser(self, file)
    3-17: methods to parse each rule of given grammar.
    18. process_error(self, n)
    19. find_lexical_errors(self)
    20. listing(self, output=None, only_first_error=True)
    21. pretty_print(self, tree, n=0, output=None)
    """
    token_list = []
    syntax_tree = []
    error_list = []
    ct = 0
    max_ct = 0

    def __init__(self):
        self.lex = lexical_analyzer.Lexer()

    def parser(self, file):
        """
        Main method for syntax analysis.
        Parses the rule #1:
        <SIGNAL-PROGRAM> -> <PROGRAM>

        At first calls lexical analysis and searches for lexical errors in
        self.token_list using self.find_lexical_errors(). If any is found,
        returns []; otherwise starts syntax analysis. If any syntax error is
        found, returns []; otherwise returns self.syntax_tree.

        :param file: file, analysis is performed on.
        """
        self.token_list = self.lex.analysis(file)
        if self.find_lexical_errors():
            return []
        self.max_ct = len(self.token_list) - 1
        res = self.parse_program()
        if not self.error_list:
            self.syntax_tree = ["<SIGNAL-PROGRAM>", res]
        return res

    def parse_program(self):
        """
        Parses the rule #2:
        <PROGRAM> -> PROCEDURE <PROCEDURE-IDENTIFIER> <PARAMETERS-LIST>;
        <BLOCK>;
        """
        if self.ct > self.max_ct or self.token_list[self.ct][0] != 401:
            return self.process_error(0)
        res = list([401])
        self.ct += 1
        res.extend(self.parse_procedure_id())
        res.extend(self.parse_param_list())
        if self.ct > self.max_ct or self.token_list[self.ct][0] != 59:
            return self.process_error(1)
        res.append(59)
        self.ct += 1
        res.extend(self.parse_block())
        if self.ct > self.max_ct or self.token_list[self.ct][0] != 59:
            return self.process_error(1)
        res.append(59)
        return ["<PROGRAM>", res]

    def parse_block(self):
        """
        Parses the rule #3:
        <BLOCK> -> <DECLARATIONS> BEGIN <STATEMENTS-LIST> END
        """
        res = self.parse_declarations()
        if self.ct > self.max_ct or self.token_list[self.ct][0] != 402:
            return self.process_error(2)
        res.append(402)
        self.ct += 1
        res.extend(self.parse_stmt_list())
        if self.ct > self.max_ct or self.token_list[self.ct][0] != 403:
            return self.process_error(3)
        res.append(403)
        self.ct += 1
        return ["<BLOCK>", res]

    def parse_declarations(self):
        """
        Parses the rule #4:
        <DECLARATIONS> -> <LABEL-DECLARATIONS>
        """
        return ["<DECLARATIONS>", self.parse_label_declarations()]

    def parse_label_declarations(self):
        """
        Parses the rule #5:
        <LABEL-DECLARATIONS> ->
            LABEL <UNSIGNED-INTEGER> <LABELS-LIST>; |
            <EMPTY>
        """
        if self.ct <= self.max_ct and self.token_list[self.ct][0] == 402:
            return ["<LABEL-DECLARATIONS>", ["<EMPTY>"]]
        if self.ct > self.max_ct or self.token_list[self.ct][0] != 404:
            return self.process_error(4)
        res = list([404])
        self.ct += 1
        res.extend(self.parse_unsigned())
        res.extend(self.parse_labels_list())
        if self.ct > self.max_ct or self.token_list[self.ct][0] != 59:
            return self.process_error(1)
        res.append(59)
        self.ct += 1
        return ["<LABEL-DECLARATIONS>", res]

    def parse_labels_list(self):
        """
        Parses the rule #6:
        <LABELS-LIST> ->
            , <UNSIGNED-INTEGER> <LABELS-LIST>; |
            <EMPTY>
        """
        if self.ct <= self.max_ct and self.token_list[self.ct][0] == 59:
            return ["<LABELS-LIST>", ["<EMPTY>"]]
        if self.ct > self.max_ct or self.token_list[self.ct][0] != 44:
            return self.process_error(5)
        res = list([44])
        self.ct += 1
        res.extend(self.parse_unsigned())
        res.extend(self.parse_labels_list())
        return ["<LABELS-LIST>", res]

    def parse_param_list(self):
        """
        Parses the rule #7:
        <PARAMETERS-LIST> ->
            (<VARIABLE-IDENTIFIER> <IDENTIFIERS-LIST>) |
            <EMPTY>
        """
        if self.ct <= self.max_ct and self.token_list[self.ct][0] == 59:
            return ["<PARAMETERS-LIST>", ["<EMPTY>"]]
        if self.ct > self.max_ct or self.token_list[self.ct][0] != 40:
            return self.process_error(6)
        res = list([40])
        self.ct += 1
        res.extend(self.parse_variable_id())
        res.extend(self.parse_id_list())
        if self.ct > self.max_ct or self.token_list[self.ct][0] != 41:
            return self.process_error(7)
        res.append(41)
        self.ct += 1
        return ["<PARAMETERS-LIST>", res]

    def parse_id_list(self):
        """
        Parses the rule #8:
        <IDENTIFIERS-LIST> ->
            , <VARIABLE-IDENTIFIER> <IDENTIFIERS-LIST> |
            <EMPTY>
        """
        if self.ct <= self.max_ct and self.token_list[self.ct][0] == 41:
            return ["<IDENTIFIERS-LIST>", ["<EMPTY>"]]
        if self.ct > self.max_ct or self.token_list[self.ct][0] != 44:
            return self.process_error(5)
        res = list([44])
        self.ct += 1
        res.extend(self.parse_variable_id())
        res.extend(self.parse_id_list())
        return ["<IDENTIFIERS-LIST>", res]

    def parse_stmt_list(self):
        """
        Parses rule #9:
        <STATEMENTS-LIST> ->
            <STATEMENT> <STATEMENTS-LIST> |
            <EMPTY>
        """
        if self.ct <= self.max_ct and self.token_list[self.ct][0] == 403:
            return ["<STATEMENTS-LIST>", ["<EMPTY>"]]
        if self.ct <= self.max_ct and self.token_list[self.ct][0] == 41:
            return ["<STATEMENTS-LIST>", ["<EMPTY>"]]
        res = self.parse_statement()
        if self.ct > self.max_ct:
            return self.process_error(3)
        res.extend(self.parse_stmt_list())
        return ["<STATEMENTS-LIST>", res]

    def parse_statement(self):
        """
        Parses rule #10:
        <STATEMENT> ->
            <UNSIGNED-INTEGER>: <STATEMENT> |
            GOTO <UNSIGNED INTEGER>; |
            RETURN; |
            ; |
            ($ <ASSEMBLY-INSERT-FILE-IDENTIFIER> $) |
            IF <CONDITION> THEN (<STATEMENT-LIST>)
            ELSE (<STATEMENT-LIST>);
        """
        if self.ct <= self.max_ct and self.token_list[self.ct][0] == 407:
            res = list([407])
            self.ct += 1
            res.extend(self.parse_condition())
            if self.ct > self.max_ct or self.token_list[self.ct][0] != 408:
                return self.process_error(14)
            res.append(408)
            self.ct += 1
            if self.ct > self.max_ct or self.token_list[self.ct][0] != 40:
                return self.process_error(6)
            res.append(40)
            self.ct += 1
            res.extend(self.parse_stmt_list())
            if self.ct > self.max_ct or self.token_list[self.ct][0] != 41:
                return self.process_error(7)
            res.append(41)
            self.ct += 1
            if self.ct > self.max_ct or self.token_list[self.ct][0] != 409:
                return self.process_error(15)
            res.append(409)
            self.ct += 1
            if self.ct > self.max_ct or self.token_list[self.ct][0] != 40:
                return self.process_error(6)
            res.append(40)
            self.ct += 1
            res.extend(self.parse_stmt_list())
            if self.ct > self.max_ct or self.token_list[self.ct][0] != 41:
                return self.process_error(7)
            res.append(41)
            self.ct += 1
            if self.ct > self.max_ct or self.token_list[self.ct][0] != 59:
                return self.process_error(1)
            res.append(59)
            self.ct += 1
        elif self.ct <= self.max_ct and self.token_list[self.ct][0] == 59:
            res = list([59])
            self.ct += 1
        elif self.ct <= self.max_ct and self.token_list[self.ct][0] == 406:
            res = list([406])
            self.ct += 1
            if self.ct > self.max_ct or self.token_list[self.ct][0] != 59:
                return self.process_error(1)
            res.append(59)
            self.ct += 1
        elif self.ct <= self.max_ct and self.token_list[self.ct][0] == 301:
            res = list([301])
            self.ct += 1
            res.extend(self.parse_asm_file_id())
            if self.ct > self.max_ct or self.token_list[self.ct][0] != 302:
                return self.process_error(8)
            res.append(302)
            self.ct += 1
        elif self.ct <= self.max_ct and self.token_list[self.ct][0] == 405:
            res = list([405])
            self.ct += 1
            res.extend(self.parse_unsigned())
            if self.ct > self.max_ct or self.token_list[self.ct][0] != 59:
                return self.process_error(1)
            res.append(59)
            self.ct += 1
        else:
            res = self.parse_unsigned()
            if self.ct > self.max_ct or self.token_list[self.ct][0] != 58:
                return self.process_error(9)
            res.append(58)
            self.ct += 1
            res.extend(self.parse_statement())
        return ["<STATEMENT>", res]

    def parse_condition(self):
        """
        Parses extra rules:
        <CONDITION> ->
            (<IDENTIFIER> <COMPARISON-OPERATOR> <IDENTIFIER>)
        <COMPARISON-OPERATOR> ->
            > | < | <= | >=
        """
        if self.ct > self.max_ct or self.token_list[self.ct][0] != 40:
            return self.process_error(6)
        res = list([40])
        self.ct += 1
        res.extend(self.parse_identifier())
        if self.ct > self.max_ct or self.token_list[self.ct][0]\
                not in [62, 60, 303, 304]:
            return self.process_error(16)
        res.append(self.token_list[self.ct][0])
        self.ct += 1
        res.extend(self.parse_identifier())
        if self.ct > self.max_ct or self.token_list[self.ct][0] != 41:
            return self.process_error(7)
        res.append(41)
        self.ct += 1
        return ["<CONDITION>", res]

    def parse_variable_id(self):
        """
        Parses the rule #11:
        <VARIABLE-IDENTIFIER> -> <IDENTIFIER>
        """
        return ["<VARIABLE-ID>", self.parse_identifier()]

    def parse_procedure_id(self):
        """
        Parses the rule #12:
        <PROCEDURE-IDENTIFIER> -> <IDENTIFIER>
        """
        return ["<PROCEDURE-ID>", self.parse_identifier()]

    def parse_asm_file_id(self):
        """
        Parses the rule #13:
        <ASSEMBLY-INSERT-FILE-IDENTIFIER> -> <IDENTIFIER>
        """
        return ["<ASSEMBLY-INSERT-FILE-ID>", self.parse_identifier()]

    def parse_identifier(self):
        """
        Parses identifier or calls error #10 (see self.process_error
        description).
        """
        if self.ct > self.max_ct or self.token_list[self.ct][0] <= 1000:
            return self.process_error(10)
        res = [self.token_list[self.ct][0]]
        self.ct += 1
        return ["<IDENTIFIER>", res]

    def parse_unsigned(self):
        """
        Parses unsigned integer or calls error #11 (see self.process_error
        description).
        """
        if self.ct > self.max_ct or self.token_list[self.ct][0]\
                not in range(500, 1001):
            return self.process_error(11)
        res = [self.token_list[self.ct][0]]
        self.ct += 1
        return ["<UNSIGNED-INTEGER>", res]

    def process_error(self, n):
        """
        Appends to self.error_list a list of next type: [N, L, P], where N is
        error's number, that occurs in line L, position P.
        Errors:
            0 - "PROCEDURE" keyword expected, but not found;
            1 - semicolon expected, but not found;
            2 - "BEGIN" keyword expected, but not found;
            3 - "END" keyword expected, but not found;
            4 - "LABEL" keyword expected, but not found;
            5 - comma expected, but not found;
            6 - opening parenthesis expected, but not found;
            7 - closing parenthesis expected, but not found;
            8 - "$)" expected, but not found;
            9 - colon expected, but not found;
            10 - identifier expected, but not found;
            11 - unsigned integer expected, but not found;
            12 - lexical error: unresolved character;
            13 - lexical error: unclosed comment;
            14 (extra) - "THEN" keyword expected, but not found;
            15 (extra) - "ELSE" keyword expected, but not found;
            16 (extra) - comparison operator expected.
        :param n: error's number
        :return: []
        """
        try:
            self.error_list.append([n, self.token_list[self.ct][1],
                                    self.token_list[self.ct][2]])
        except IndexError:
            self.error_list.append([n, self.token_list[self.ct - 1][1],
                                    self.token_list[self.ct - 1][2]])
        return []

    def find_lexical_errors(self):
        """
        Iterates through self.token_list. Returns True if no lexical errors are
        found or False otherwise.
        Side effect: when finds lexical error, writes it to self.error_list
        using self.process_error().
        """
        res = False
        for x in self.token_list:
            if type(x[0]) == str and x[0] == "E1":
                res = True
                self.error_list.append([12, x[2], x[3]])
            elif type(x[0]) == str and x[0] == "E2":
                res = True
                self.error_list.append([13, x[1], x[2]])
        return res

    def listing(self, output=None, only_first_error=True, full=True):
        """
        Writes listing: tables, formed during lexical analysis, all of the
        tokens of source program, lexical and syntax errors.
        :param output: file, listing is written into; if None, writes listing
        on the screen.
        :param only_first_error: if True, writes only the first found error;
        writes all found errors otherwise.
        :param full: if True, writes result of lexical analysis: tables and
        list of tokens.
        """
        if full:
            self.lex.listing(output=output)
        for x in self.error_list:
            if x[0] == 0:
                print("\"PROCEDURE\" keyword expected (line %i, position %i)" %
                      (x[1] + 1, x[2] + 1), file=output)
            elif x[0] == 1:
                print("Semicolon expected (line %i, position %i)" %
                      (x[1] + 1, x[2] + 1), file=output)
            elif x[0] == 2:
                print("\"BEGIN\" keyword expected (line %i, position %i)" %
                      (x[1] + 1, x[2] + 1), file=output)
            elif x[0] == 3:
                print("\"END\" keyword expected (line %i, position %i)" %
                      (x[1] + 1, x[2] + 1), file=output)
            elif x[0] == 4:
                print("\"LABEL\" keyword expected (line %i, position %i)" %
                      (x[1] + 1, x[2] + 1), file=output)
            elif x[0] == 5:
                print("Comma expected (line %i, position %i)" %
                      (x[1] + 1, x[2] + 1), file=output)
            elif x[0] == 6:
                print("Opening parenthesis expected (line %i, position %i)" %
                      (x[1] + 1, x[2] + 1), file=output)
            elif x[0] == 7:
                print("Closing parenthesis expected (line %i, position %i)" %
                      (x[1] + 1, x[2] + 1), file=output)
            elif x[0] == 8:
                print("\"$)\" expected (line %i, position %i)" %
                      (x[1] + 1, x[2] + 1), file=output)
            elif x[0] == 9:
                print("Colon expected (line %i, position %i)" %
                      (x[1] + 1, x[2] + 1), file=output)
            elif x[0] == 10:
                print("Identifier expected (line %i, position %i)" %
                      (x[1] + 1, x[2] + 1), file=output)
            elif x[0] == 11:
                print("Unsigned integer expected (line %i, position %i)" %
                      (x[1] + 1, x[2] + 1), file=output)
            elif x[0] == 12:
                print("Unresolved character (line %i, position %i)" %
                      (x[1] + 1, x[2] + 1), file=output)
            elif x[0] == 13:
                print("Unclosed comment (line %i, position %i)" %
                      (x[1] + 1, x[2] + 1), file=output)
            elif x[0] == 14:
                print("\"THEN\" keyword expected (line %i, position %i)" %
                      (x[1] + 1, x[2] + 1), file=output)
            elif x[0] == 15:
                print("\"ELSE\" keyword expected (line %i, position %i)" %
                      (x[1] + 1, x[2] + 1), file=output)
            elif x[0] == 16:
                print("Comparison operator expected (line %i, position %i)" %
                      (x[1] + 1, x[2] + 1), file=output)
            if only_first_error:
                break

    def pretty_print(self, tree, n=0, output=None):
        """
        Prints self.syntax_tree or its subtree.
        :param tree: self.syntax_tree or its subtree.
        :param n: subtree's level.
        :param output: file, the tree is printed into; if None, prints on the
        screen.
        """
        for x in tree:
            if type(x) == list:
                self.pretty_print(x, n+1, output=output)
            else:
                print("%s" % "|" * n + " " + str(x), file=output)


if __name__ == "__main__":
    filename = input("File name [.sig]: ")
    if filename[-4:] != ".sig":
        filename += ".sig"
    f = open(filename, "r")
    parser = Parser()
    parser.parser(f)
    f.close()
    parser.listing(full=False)
    if parser.syntax_tree:
        print("Syntax tree:")
    parser.pretty_print(parser.syntax_tree)
    input()