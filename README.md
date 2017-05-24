# Signal-Compiler
Labworks for 'Theory Of Translaters' discipline

Instruments:
 - JetBrains PyCharm Community Edition 2016.2.3

The program parses and translates to Assembler's code a subset of SIGNAL(c) programming language:
1. \<signal-program\> --> \<program\>
2. \<program\> --> PROCEDURE \<procedure-identifier\>\<parameters-list\>; \<block\>;
3. \<block\> --> \<declarations\> BEGIN \<statements-list\> END
4. \<declarations\> --> \<label-declarations\>
5. \<label-declarations\> --> LABEL \<unsigned-integer\>\<labels-list\>; | \<empty\>
6. \<labels-list\> --> , \<unsigned-integer\>\<labels-list\> | \<empty\>
7. \<parameters-list\> --> ( \<variable-identifier\>\<identifiers-list\> ) | \<empty\>
8. \<identifiers-list\> --> , \<variable-integer\>\<identifiers-list\> | \<empty\>
9. \<statements-list\> --> \<statement\>\<statements-list\> | \<empty\>
10. \<statement\> --> \<unsigned-integer\> : \<statement\> | GOTO \<unsigned-integer\>; | RETURN; | ; | ($ \<assembly-insert-file-identifier> $)
11. \<variable-identifier\> --> \<identifier\>
12. \<procedure-identifier\> --> \<identifier\>
13. \<assembly-insert-file-identifier\> --> \<identifier\>
14. \<identifier\> --> \<letter\>\<string\>
15. \<string\> --> \<letter\>\<string\> | \<digit\>\<string\> | \<empty\>
16. \<unsigned-integer\> --> \<digit\>\<digits-string\>
17. \<digits-string\> --> \<digit\>\<digits-string\> | \<empty\>
18. \<digit\> --> 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
19. \<letter\> --> A | B | C | D | ... | Z
