import syntax_analyzer


class CodeGenerator:

    def __init__(self):
        self.parser = syntax_analyzer.Parser()
        self.syntax_tree = []
        self.token_list = []
        self.error_list = []
        self.labels = {}
        self.code_gen_identifiers = []
        self.identifiers_table = self.parser.lex.identifiers
        self.proc_id = ""
        self.var_id = ""
        self.asm_file_name = ""
        self.id = ""
        self.unsigned = ""
        self.code_file = None

    def code_gen(self, source_file, code_file):
        """
        <SIGNAL-PROGRAM> -> <PROGRAM>
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
        <PROGRAM> -> PROCEDURE <PROCEDURE-IDENTIFIER> <PARAMETERS-LIST>;
        <BLOCK>;
        {code segment \n assume cs:code \n [3] PROCID proc \n push ebp \n [1]
        pop ebp \n ret \n PROCID endp \n start: \n mov ax, 0 \n [2] mov ax,
        4c00h \n int 21h \n code ends \n end start \n}
        """
        print("Program:\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n" %
              (tree[0], tree[1], tree[2], tree[3], tree[4], tree[5], tree[6], tree[7], tree[8]))
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
        <BLOCK> -> <DECLARATIONS> BEGIN <STATEMENTS-LIST> END
        {[2][1]}
        """
        print("Block:\n%s\n%s\n%s\n%s\n%s\n%s\n" %
              (tree[0], tree[1], tree[2], tree[3], tree[4], tree[5]))
        if self.code_gen_declarations(tree[1]) != 0:
            return 1
        return self.code_gen_stmt_list(tree[4])

    def code_gen_declarations(self, tree):
        """
        <DECLARATIONS> -> <LABEL-DECLARATIONS>
        {[1]}
        """
        print("Declarations:\n%s\n%s\n" % (tree[0], tree[1]))
        return self.code_gen_label_declarations(tree[1])

    def code_gen_label_declarations(self, tree):
        """
        <LABEL-DECLARATIONS> ->
            LABEL <UNSIGNED-INTEGER> <LABELS-LIST>; |
            <EMPTY>
        {[2][1]} | {}
        """
        print("Label declarations:")
        if tree[0] == "<EMPTY>":
            print("%s\n" % tree[0])
            return 0
        print("%s\n%s\n%s\n%s\n%s\n%s\n" % (tree[0], tree[1], tree[2], tree[3], tree[4], tree[5]))
        self.code_gen_unsigned(tree[2])
        self.labels[self.unsigned] = False
        return self.code_gen_labels_list(tree[4])

    def code_gen_labels_list(self, tree):
        """
        <LABELS-LIST> ->
            , <UNSIGNED-INTEGER> <LABELS-LIST>; |
            <EMPTY>
        {[2][1]} | {}
        """
        print("Labels list:")
        if tree[0] == "<EMPTY>":
            print("%s\n" % tree[0])
            return 0
        print("%s\n%s\n%s\n%s\n%s\n" % (tree[0], tree[1], tree[2], tree[3], tree[4]))
        self.code_gen_unsigned(tree[2])
        if self.unsigned in self.labels.keys():
            return self.process_error(17)
        self.labels[self.unsigned] = False
        return self.code_gen_labels_list(tree[4])

    def code_gen_param_list(self, tree):
        """
        <PARAMETERS-LIST> ->
            (<VARIABLE-IDENTIFIER> <IDENTIFIERS-LIST>) |
            <EMPTY>
        {[2] push ax \n [1]} | {}
        """
        print("Parameters list:")
        if tree[0] == "<EMPTY>":
            print("%s\n" % tree[0])
            return 0
        print("%s\n%s\n%s\n%s\n%s\n%s\n" % (tree[0], tree[1], tree[2], tree[3], tree[4], tree[5]))
        self.code_gen_variable_id(tree[2])
        print("push ax", file=self.code_file)
        return self.code_gen_id_list(tree[4])

    def code_gen_id_list(self, tree):
        """
        <IDENTIFIERS-LIST> ->
            , <VARIABLE-IDENTIFIER> <IDENTIFIERS-LIST> |
            <EMPTY>
        {[2] push ax \n [1]} | {}
        """
        print("Identifiers list:")
        if tree[0] == "<EMPTY>":
            print("%s\n" % tree[0])
            return 0
        print("%s\n%s\n%s\n%s\n%s\n" % (tree[0], tree[1], tree[2], tree[3], tree[4]))
        if self.code_gen_variable_id(tree[2]) != 0:
            return self.process_error(18)
        print("push ax", file=self.code_file)
        return self.code_gen_id_list(tree[4])

    def code_gen_stmt_list(self, tree):
        """
        <STATEMENTS-LIST> ->
            <STATEMENT> <STATEMENTS-LIST> |
            <EMPTY>
        {[2][1]} | {}
        """
        print("Statements list:")
        if tree[0] == "<EMPTY>":
            print("%s\n" % tree[0])
            return 0
        print("%s\n%s\n%s\n%s\n" % (tree[0], tree[1], tree[2], tree[3]))
        stmt_res = self.code_gen_statement(tree[1])
        if type(stmt_res) == int and stmt_res != 0:
            return 1
        if self.code_gen_stmt_list(tree[3]) != 0:
            return 1
        if type(stmt_res) == str and not self.labels[stmt_res]:
            return self.process_error(19)
        return 0

    def code_gen_statement(self, tree):
        """
        <STATEMENT> ->
            <UNSIGNED-INTEGER>: <STATEMENT> |
            GOTO <UNSIGNED INTEGER>; |
            RETURN; |
            ; |
            ($ <ASSEMBLY-INSERT-FILE-IDENTIFIER> $)
        {[2] @UNSIGNED: \n [1]} | {[1] jmp @UNSIGNED \n} |
        {pop ebp \n ret \n} | {} | {[1]ASM-CODE-FROM-FILE}
        """
        print("Statement:")
        if tree[0] == 59:
            print("%s\n" % tree[0])
            return 0
        elif tree[0] == 405:
            print("%s\n%s\n%s\n%s\n" % (tree[0], tree[1], tree[2], tree[3]))
            self.code_gen_unsigned(tree[2])
            if self.unsigned not in self.labels.keys():
                return self.process_error(18)
            print("jmp @%s" % self.unsigned, file=self.code_file)
            return self.unsigned
        elif tree[0] == 406:
            print("%s\n%s\n" % (tree[0], tree[1]))
            print("pop ebp\nret", file=self.code_file)
            return 0
        elif tree[0] == 301:
            print("%s\n%s\n%s\n%s\n" % (tree[0], tree[1], tree[2], tree[3]))
            if self.code_gen_asm_file_id(tree[2]) != 0:
                return 1
            try:
                asm_file_real_name = ""
                for key in self.identifiers_table.keys():
                    if self.identifiers_table[key] == self.asm_file_name:
                        asm_file_real_name = key
                        break
                asm = open(asm_file_real_name+".asm")
            except FileNotFoundError:
                return self.process_error(20)
            ch = asm.read(1)
            while ch != "":
                print(ch, file=self.code_file, end="")
                ch = asm.read(1)
            asm.close()
            return 0
        else:
            print("%s\n%s\n%s\n%s\n%s\n" % (tree[0], tree[1], tree[2], tree[3], tree[4]))
            self.code_gen_unsigned(tree[1])
            if self.unsigned not in self.labels.keys():
                return self.process_error(18)
            print("@%s:" % self.unsigned, file=self.code_file)
            self.labels[self.unsigned] = True
            return self.code_gen_statement(tree[4])

    def code_gen_variable_id(self, tree):
        """
        <VARIABLE-IDENTIFIER> -> <IDENTIFIER>
        {[1]}
        """
        print("Variable id:\n%s\n%s\n" % (tree[0], tree[1]))
        if self.code_gen_identifier(tree[1]) != 0:
            return 1
        self.var_id = self.id
        return 0

    def code_gen_procedure_id(self, tree):
        """
        <PROCEDURE-IDENTIFIER> -> <IDENTIFIER>
        {[1]}
        """
        print("Procedure id:\n%s\n%s\n" % (tree[0], tree[1]))
        if self.code_gen_identifier(tree[1]) != 0:
            return 1
        self.proc_id = self.id
        return 0

    def code_gen_asm_file_id(self, tree):
        """
        <ASSEMBLY-INSERT-FILE-IDENTIFIER> -> <IDENTIFIER>
        {[1]}
        """
        print("Asm insert file id:\n%s\n%s\n" % (tree[0], tree[1]))
        if self.code_gen_identifier(tree[1]) != 0:
            return 1
        self.asm_file_name = self.id
        return 0

    def code_gen_identifier(self, tree):
        print("Identifier: %s\n" % tree)
        if tree[0] in self.code_gen_identifiers:
            return self.process_error(21)
        self.id = tree[0]
        self.code_gen_identifiers.append(self.id)
        return 0

    def code_gen_unsigned(self, tree):
        print("Unsigned: %s\n" % tree)
        self.unsigned = str(tree[0])
        return 0

    def process_error(self, n):
        self.error_list.append(n)
        return 1


if __name__ == "__main__":
    filename = input("File name [.sig]: ")
    if filename[-4:] == ".sig":
        filename = filename[:-4]
    f = open(filename+".sig", "r")
    code_gen = CodeGenerator()
    g = open(filename+".asm", "w")
    print(code_gen.code_gen(f, g))
    f.close()
    g.close()