import code_generator


filename = input("File name [.sig]: ")
if filename[-4:] == ".sig":
    filename = filename[:-4]
try:
    f = open(filename+".sig", "r")
    code_gen = code_generator.CodeGenerator()
    g = open(filename + ".asm", "w")
    code_gen.code_gen(f, g)
    f.close()
    g.close()
    if code_gen.error_list:
        import os
        os.remove(filename+".asm")
        print("Some error occurred: compilation failed")
    else:
        print("%s.asm file has been generated successfully" % filename)
    h = open(filename + ".lst", "w")
    code_gen.listing(h)
    h.close()
    print("Listing is written to %s.lst" % filename)
except FileNotFoundError:
    print("No such file found")