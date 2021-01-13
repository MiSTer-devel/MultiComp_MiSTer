LF	.EQU	0AH		;line feed
FF	.EQU	0CH		;form feed
CR	.EQU	0DH		;carriage RETurn
DOT .EQU     '.'
CH375_CMD_CHECK_EXIST .EQU 06H
CH375_CMD_RESET_ALL .EQU 05H

    .ORG 4000H

    CALL	printInline
    .TEXT "Check CH376s communication"
    .DB CR,LF,0

    CALL	printInline
    .TEXT "Send A"
    .DB CR,LF,0

    ;ld a, CH375_CMD_RESET_ALL
    ;out (20h),a

    ;ld a, CH375_CMD_CHECK_EXIST
    ;out (20h),a
    ld b, 10
    ld a, 0AAH
_again:
    out (20h),a
    push bc
    ld b, 50
_again2:
    djnz _again2
    pop bc
    djnz _again
    ; receive result
    ;xor a
    ;out (20h),a
    ;in a, (20h)
    ;xor 255

    CALL	printInline
    .TEXT "Received "
    .DB 0

    RST 08H ; print contents of A

    CALL	printInline
    .DB CR,LF,0

    ret

    ; LOOPBACK TEST

    ld b, 39h
outer:
    ld a, b
    cp 2fh
    ret z
    ; send out
    out (20h),a
;inner:
;    ld a, DOT
;    rst 08h
;    in a, (21h)
;    bit 0,a
;    jr z, inner
    xor a

    ; read back
    in a, (20h)
    rst 08h ; should be 30h => 0..9

    dec b
    jr outer

    ret

printInline:
    EX 	(SP),HL 	; PUSH HL and put RET ADDress into HL
    PUSH 	AF
    PUSH 	BC
nextILChar:	LD 	A,(HL)
    CP	0
    JR	Z,endOfPrint
    RST 08H
    INC HL
    JR	nextILChar
endOfPrint:	INC 	HL 		; Get past "null" terminator
    POP 	BC
    POP 	AF
    EX 	(SP),HL 	; PUSH new RET ADDress on stack and restore HL
    RET


    .END
