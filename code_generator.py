import syntax_analyzer


class CodeGenerator:
    """
    Class for code generation and making listing.

    Class contents lists:
    1. syntax_tree - a syntax tree built by parser. If parsing wasn't
    successful, syntax_tree is empty. See Parser.syntax_tree description.
    2. token_list - a list of tokens created by lexical analysis. See
    Lexer.token_list description.
    3. error_list is filled by parser (see Parser.error_list description) and
    is complemented by code generator. If no lexical, syntax or semantic
    errors found, remains empty. If semantic error occurs, a list of next type
    is appended: [N, T], where N is error's number (see self.process_error
    description), T is a code of token, that caused an error.
    4. parameters - a list of strings, that represent user's identifiers'
    codes. Is used to control duplication of formal parameters.
    5. identifiers - a list of strings, that represent codes of all user's
    identifiers. Is used to control identifiers' re-usage.

    Class contents dictionaries:
    1. labels - keys are strings, that represent codes of labels, that are
    declared; value may be True if label is used in program code at least
    once, or False otherwise.
    2-5. two_char_separators_table, identifiers_table, constants_table and
    keywords_table are created by constructor. They are copies of
    Lexer.two_char_separators, Lexer.identifiers, Lexer.constants and
    Lexer.keywords appropriately.

    Class contents strings:
    1. proc_id - a buffer for a code of identifier - procedure's name.
    2. var_id - a buffer for a code of identifier - procedure parameter's
    name.
    3. asm_file_name - a buffer for a code of identifier - name of file, that
    contains assembler's code for insertion.
    4. id - a buffer for a code of any identifier.
    5. unsigned - a buffer for a code of unsigned integer (label).

    Class contains objects:
    1. parser - an instance of class Parser. Is being created by constructor.
    2. code_file - file object, where generated code is being written.

    Class contents methods:
    1. __init__(self)
    2. code_gen(self, source_file, code_file)
    3-16: methods for code generation according to each rule of given grammar.
    17. process_error(self, n, label=None)
    18. listing(self, output)
    """
    syntax_tree = []
    token_list = []
    error_list = []
    labels = {}
    parameters = []
    identifiers = []
    proc_id = ""
    var_id = ""
    asm_file_name = ""
    id = ""
    unsigned = ""
    code_file = None

    def __init__(self):
        self.parser = syntax_analyzer.Parser()
        self.identifiers_table = self.parser.lex.identifiers
        self.constants_table = self.parser.lex.constants
        self.keywords_table = self.parser.lex.keywords
        self.two_char_separators_table = self.parser.lex.two_char_separators

    def code_gen(self, source_file, code_file):
        """
        Main method for code generation.
        :param source_file: file object, SIGNAL program, that is being
        compiled.
        :param code_file: file object, .asm file, which code is written to.
        :returns 0 in case of success, or 1 if any error (lexical, syntax,
        semantic) occurs.

        Rule #1:
            <SIGNAL-PROGRAM> -> <PROGRAM>
        Semantic definition:
            {[1]}
        """
        self.code_file = code_file
        self.parser.parser(source_file)
        self.syntax_tree = self.parser.syntax_tree
        self.token_list = self.parser.token_list
        self.error_list = self.parser.error_list
        if self.syntax_tree:
            return self.code_gen_program(self.syntax_tree[1][1])
        return 1

    def code_gen_program(self, tree):
        """
        Rule #2:
            <PROGRAM> ->
                PROCEDURE <PROCEDURE-IDENTIFIER> <PARAMETERS-LIST>; <BLOCK>;
        Semantic definition:
            {code segment \n assume cs:code \n [3] PROCID proc \n push ebp \n
            [1] pop ebp \n ret \n PROCID endp \n start: \n mov ax, 0 \n [2]
            mov ax, 4c00h \n int 21h \n code ends \n end start \n}
        """
        print("code segment\nassume cs:code\n", file=self.code_file)
        if self.code_gen_procedure_id(tree[2]) != 0:
            return 1
        print("@%s proc\npush ebp" % self.proc_id, file=self.code_file)
        if self.code_gen_block(tree[7]) != 0:
            return 1
        print("pop ebp\nret\n@%s endp\n\nstart:\nxor ax, ax" % self.proc_id,
              file=self.code_file)
        if self.code_gen_param_list(tree[4]) != 0:
            return 1
        print("mov ax, 4c00h\nint 21h\ncode ends\n\nend start",
              file=self.code_file)
        return 0

    def code_gen_block(self, tree):
        """
        Rule #3:
            <BLOCK> -> <DECLARATIONS> BEGIN <STATEMENTS-LIST> END
        Semantic definition:
            {[2][1]}
        """
        if self.code_gen_declarations(tree[1]) != 0:
            return 1
        return self.code_gen_stmt_list(tree[4])

    def code_gen_declarations(self, tree):
        """
        Rule #4:
            <DECLARATIONS> -> <LABEL-DECLARATIONS>
        Semantic definition:
            {[1]}
        """
        return self.code_gen_label_declarations(tree[1])

    def code_gen_label_declarations(self, tree):
        """
        Rule #5:
            <LABEL-DECLARATIONS> ->
                LABEL <UNSIGNED-INTEGER> <LABELS-LIST>; |
                <EMPTY>
        Semantic definitions:
            {[2][1]}
            {}
        """
        if tree[0] == "<EMPTY>":
            return 0
        self.code_gen_unsigned(tree[2])
        self.labels[self.unsigned] = False
        return self.code_gen_labels_list(tree[4])

    def code_gen_labels_list(self, tree):
        """
        Rule #6:
            <LABELS-LIST> ->
                , <UNSIGNED-INTEGER> <LABELS-LIST>; |
                <EMPTY>
        Semantic definitions:
            {[2][1]}
            {}
        """
        if tree[0] == "<EMPTY>":
            return 0
        self.code_gen_unsigned(tree[2])
        if self.unsigned in self.labels.keys():
            return self.process_error(17)
        self.labels[self.unsigned] = False
        return self.code_gen_labels_list(tree[4])

    def code_gen_param_list(self, tree):
        """
        Rule #7:
            <PARAMETERS-LIST> ->
                (<VARIABLE-IDENTIFIER> <IDENTIFIERS-LIST>) |
                <EMPTY>
        Semantic definitions:
            {[2] push ax \n [1]}
            {}
        """
        if tree[0] == "<EMPTY>":
            return 0
        self.code_gen_variable_id(tree[2])
        print("push ax", file=self.code_file)
        return self.code_gen_id_list(tree[4])

    def code_gen_id_list(self, tree):
        """
        Rule #8:
            <IDENTIFIERS-LIST> ->
                , <VARIABLE-IDENTIFIER> <IDENTIFIERS-LIST> |
                <EMPTY>
        Semantic definitions:
            {[2] push ax \n [1]}
            {}
        """
        if tree[0] == "<EMPTY>":
            return 0
        if self.code_gen_variable_id(tree[2]) != 0:
            return 1
        print("push ax", file=self.code_file)
        return self.code_gen_id_list(tree[4])

    def code_gen_stmt_list(self, tree):
        """
        Rule #9:
            <STATEMENTS-LIST> ->
                <STATEMENT> <STATEMENTS-LIST> |
                <EMPTY>
        Semantic definitions:
            {[2][1]}
            {}
        """
        if tree[0] == "<EMPTY>":
            return 0
        stmt_res = self.code_gen_statement(tree[1])
        if type(stmt_res) == int and stmt_res != 0:
            return 1
        if self.code_gen_stmt_list(tree[3]) != 0:
            return 1
        if type(stmt_res) == str and not self.labels[stmt_res]:
            return self.process_error(19, stmt_res)
        return 0

    def code_gen_statement(self, tree):
        """
        Rule #10:
            <STATEMENT> ->
                <UNSIGNED-INTEGER>: <STATEMENT> |
                GOTO <UNSIGNED INTEGER>; |
                RETURN; |
                ; |
                ($ <ASSEMBLY-INSERT-FILE-IDENTIFIER> $)
        Semantic definitions:
            {[2] @UNSIGNED: \n [1]}
            {[1] jmp @UNSIGNED \n}
            {pop ebp \n ret \n}
            {}
            {[1]<assembler's code from file>}
        """
        if tree[0] == 59:
            return 0
        elif tree[0] == 405:
            self.code_gen_unsigned(tree[2])
            if self.unsigned not in self.labels.keys():
                return self.process_error(22)
            print("jmp @%s" % self.unsigned, file=self.code_file)
            return self.unsigned
        elif tree[0] == 406:
            print("pop ebp\nret", file=self.code_file)
            return 0
        elif tree[0] == 301:
            if self.code_gen_asm_file_id(tree[2]) != 0:
                return 1
            try:
                asm_file_real_name = self.__get_identifier(self.asm_file_name)
                asm = open(asm_file_real_name+".asm")
            except FileNotFoundError:
                return self.process_error(20)
            ch = asm.read(1)
            while ch != "":
                print(ch, file=self.code_file, end="")
                ch = asm.read(1)
            asm.close()
            print(file=self.code_file)
            return 0
        else:
            self.code_gen_unsigned(tree[1])
            if self.unsigned not in self.labels.keys():
                return self.process_error(22)
            print("@%s:" % self.unsigned, file=self.code_file)
            self.labels[self.unsigned] = True
            return self.code_gen_statement(tree[4])

    def code_gen_variable_id(self, tree):
        """
        Rule #11:
            <VARIABLE-IDENTIFIER> -> <IDENTIFIER>
        Semantic definition:
            {[1]}
        """
        if self.code_gen_identifier(tree[1]) != 0:
            return 1
        self.var_id = self.id
        return 0

    def code_gen_procedure_id(self, tree):
        """
        Rule #12:
            <PROCEDURE-IDENTIFIER> -> <IDENTIFIER>
        Semantic definition:
            {[1]}
        """
        if self.code_gen_identifier(tree[1]) != 0:
            return 1
        self.proc_id = self.id
        return 0

    def code_gen_asm_file_id(self, tree):
        """
        Rule #13:
            <ASSEMBLY-INSERT-FILE-IDENTIFIER> -> <IDENTIFIER>
        Semantic definition:
            {[1]}
        """
        if self.code_gen_identifier(tree[1]) != 0:
            return 1
        self.asm_file_name = self.id
        return 0

    def code_gen_identifier(self, tree):
        """
        Returns a string containing identifier's code or calls error #22, #18
        or #21 (see self.process_error description).
        """
        self.id = str(tree[0])
        if self.id in self.keywords_table.keys():
            return self.process_error(22)
        if self.id in self.parameters:
            return self.process_error(18)
        if self.id in self.identifiers:
            return self.process_error(21)
        self.identifiers.append(self.id)
        return 0

    def code_gen_unsigned(self, tree):
        """
        Returns a string containing label's code or calls error #22, #18 or
        #21 (see self.process_error description).
        """
        self.unsigned = str(tree[0])
        return 0

    def process_error(self, n, label=None):
        """
        Appends to self.error_list a list of next type: [N, T], where N is
        error's number, T is a code of token, that caused an error.
        Errors:
            17 - twice declared label;
            18 - duplicating formal parameter;
            19 - reference to non-existing label in GOTO statement;
            20 - assembly insertion file not found;
            21 - re-used identifier;
            22 - reference to undeclared label.
        :param n: error's number
        :param label: non-existing label's code. Is used only for error #19.
        :returns 1
        """
        if n == 17:
            self.error_list.append([n, self.__get_constant(self.unsigned)])
        elif n == 18:
            self.error_list.append([n, self.__get_identifier(self.id)])
        elif n == 19:
            self.error_list.append([n, self.__get_constant(label)])
        elif n == 20:
            self.error_list.append([n, self.__get_identifier(
                self.asm_file_name)])
        elif n == 21:
            self.error_list.append([n, self.__get_identifier(self.id)])
        elif n == 22:
            self.error_list.append([n, self.__get_constant(self.unsigned)])
        return 1

    def __get_identifier(self, code):
        res = ""
        for key in self.identifiers_table.keys():
            if self.identifiers_table[key] == int(code):
                res = key
                break
        return res

    def __get_constant(self, code):
        res = ""
        for key in self.constants_table.keys():
            if self.constants_table[key] == int(code):
                res = key
                break
        return res

    def __get_two_char_separator(self, code):
        res = ""
        for key in self.two_char_separators_table.keys():
            if self.two_char_separators_table[key] == int(code):
                res = key
                break
        return res

    def __get_keyword(self, code):
        res = ""
        for key in self.keywords_table.keys():
            if self.keywords_table[key] == int(code):
                res = key
                break
        return res

    def listing(self, output):
        """
        Prints source program's listing: all of the tokens and first found
        error (lexical, syntax or semantic).
        :param output: file object, .lst file, where listing is written.
        """
        line = 0
        pos = 0
        print("1.\t| ", file=output, end="")
        for token in self.token_list:
            if token[0] == "E1" and token[2] > line or token[0]\
                    != "E1" and token[1] > line:
                line += 1
                pos = 0
                print("\n%d.\t| " % (line + 1), file=output, end="")
            if token[0] == "E1":
                while pos < token[3]:
                    pos += 1
                    print(" ", file=output, end="")
                print("%s" % token[1], file=output, end="")
                pos += 1
            else:
                while pos < token[2]:
                    pos += 1
                    print(" ", file=output, end="")
                if token[0] == "E2":
                    break
                elif token[0] in range(0, 256):
                    print("%s" % chr(token[0]), file=output, end="")
                    pos += 1
                elif token[0] in range(301, 401):
                    print("%s" % self.__get_two_char_separator(token[0]),
                          file=output, end="")
                    pos += 2
                elif token[0] in range(401, 501):
                    buf = self.__get_keyword(token[0])
                    print("%s" % buf, file=output, end="")
                    pos += len(buf)
                elif token[0] in range(501, 1001):
                    buf = self.__get_constant(token[0])
                    print("%s" % buf, file=output, end="")
                    pos += len(buf)
                else:  # token[0] > 1000
                    buf = self.__get_identifier(token[0])
                    print("%s" % buf, file=output, end="")
                    pos += len(buf)
        if self.error_list:
            print("\n\nError occurred:", file=output)
            error_case = self.error_list[0]
            if error_case[0] == 0:
                print("\"PROCEDURE\" keyword expected (line %i, position %i)"
                      % (error_case[1] + 1, error_case[2] + 1), file=output)
            elif error_case[0] == 1:
                print("Semicolon expected (line %i, position %i)" %
                      (error_case[1] + 1, error_case[2] + 1), file=output)
            elif error_case[0] == 2:
                print("\"BEGIN\" keyword expected (line %i, position %i)" %
                      (error_case[1] + 1, error_case[2] + 1), file=output)
            elif error_case[0] == 3:
                print("\"END\" keyword expected (line %i, position %i)" %
                      (error_case[1] + 1, error_case[2] + 1), file=output)
            elif error_case[0] == 4:
                print("\"LABEL\" keyword expected (line %i, position %i)" %
                      (error_case[1] + 1, error_case[2] + 1), file=output)
            elif error_case[0] == 5:
                print("Comma expected (line %i, position %i)" %
                      (error_case[1] + 1, error_case[2] + 1), file=output)
            elif error_case[0] == 6:
                print("Opening parenthesis expected (line %i, position %i)" %
                      (error_case[1] + 1, error_case[2] + 1), file=output)
            elif error_case[0] == 7:
                print("Closing parenthesis expected (line %i, position %i)" %
                      (error_case[1] + 1, error_case[2] + 1), file=output)
            elif error_case[0] == 8:
                print("\"$)\" expected (line %i, position %i)" %
                      (error_case[1] + 1, error_case[2] + 1), file=output)
            elif error_case[0] == 9:
                print("Colon expected (line %i, position %i)" %
                      (error_case[1] + 1, error_case[2] + 1), file=output)
            elif error_case[0] == 10:
                print("Identifier expected (line %i, position %i)" %
                      (error_case[1] + 1, error_case[2] + 1), file=output)
            elif error_case[0] == 11:
                print("Unsigned integer expected (line %i, position %i)" %
                      (error_case[1] + 1, error_case[2] + 1), file=output)
            elif error_case[0] == 12:
                print("Unresolved character (line %i, position %i)" %
                      (error_case[1] + 1, error_case[2] + 1), file=output)
            elif error_case[0] == 13:
                print("Unclosed comment (line %i, position %i)" %
                      (error_case[1] + 1, error_case[2] + 1), file=output)
            elif error_case[0] == 17:
                print("Twice declared label: %s" % error_case[1],
                      file=output)
            elif error_case[0] == 18:
                print("Duplicating formal parameter: %s" % error_case[1],
                      file=output)
            elif error_case[0] == 19:
                print("Reference to non-existing label %s in GOTO statement" %
                      error_case[1], file=output)
            elif error_case[0] == 20:
                print("File not found: %s.asm" % error_case[1], file=output)
            elif error_case[0] == 21:
                print("Re-used identifier: %s" % error_case[1], file=output)
            elif error_case[0] == 22:
                print("Reference to undeclared label %s"
                      % error_case[1], file=output)


if __name__ == "__main__":
    filename = input("File name [.sig]: ")
    if filename[-4:] == ".sig":
        filename = filename[:-4]
    f = open(filename+".sig", "r")
    code_gen = CodeGenerator()
    g = open(filename+".asm", "w")
    print(code_gen.code_gen(f, g))
    if code_gen.error_list:
        print(code_gen.error_list)
    f.close()
    g.close()
    h = open(filename+".lst", "w")
    code_gen.listing(h)
    h.close()
