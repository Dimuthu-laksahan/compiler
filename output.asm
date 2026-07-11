; --- DATA SECTION ---
section .data
    str_1 db "Hello World", 0
    t1 dq 0
    t2 dq 0
    t3 dq 0
    t4 dq 0
    w dq 0
    x dq 0
    y dq 0
    z dq 0

; --- TEXT SECTION ---
section .text
global main
extern printf

main:
    push rbp                       ; Setup stack frame
    mov rbp, rsp

    mov rax, 60                    ; Read RHS '60'
    mov [x], rax                   ; Assign to 'x'
    mov rax, 2.5                   ; Load immediate constant 2.5
    neg rax                        ; Negate 2.5
    mov [t1], rax                  ; Store result into t1
    mov rax, [t1]                  ; Read RHS 't1'
    mov [y], rax                   ; Assign to 'y'
    lea rdi, [str_1]               ; Load string address for printing
    mov rax, 0                     ; No vector registers used for printf
    call printf                    ; Print output for "Hello World"
    mov rax, [x]                   ; Load variable x
    mov rbx, 5                     ; Load immediate constant 5
    cmp rax, rbx                   ; Compare x and 5
    setg al                        ; Set AL byte if condition '>' is met
    movzx rax, al                  ; Zero extend AL to RAX
    mov [t2], rax                  ; Store result into t2
    mov rax, [t2]                  ; Load variable t2
    cmp rax, 0                     ; Test condition 't2'
    je L1                          ; Jump to L1 if false
    mov rax, [y]                   ; Load variable y
    mov rbx, [x]                   ; Load variable x
    add rax, rbx                   ; Compute y + x
    mov [t3], rax                  ; Store result into t3
    mov rax, [t3]                  ; Read RHS 't3'
    mov [y], rax                   ; Assign to 'y'
L1:
    mov rax, 5                     ; Read RHS '5'
    mov [w], rax                   ; Assign to 'w'
    mov rax, [w]                   ; Load variable w
    mov rbx, 10                    ; Load immediate constant 10
    add rax, rbx                   ; Compute w + 10
    mov [t4], rax                  ; Store result into t4
    mov rax, [t4]                  ; Read RHS 't4'
    mov [z], rax                   ; Assign to 'z'

    mov rax, 0                     ; Return status 0
    pop rbp                        ; Restore stack frame
    ret