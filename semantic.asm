code segment
assume cs:code

@1001 proc
push ebp
@501:
@502:
@504:
jmp @505
@505:
xor ax, ax
mov cx, 6
add ax, cx
nop
pop ebp
ret
pop ebp
ret
@1001 endp

start:
xor ax, ax
push ax
push ax
push ax
mov ax, 4c00h
int 21h
code ends

end start
