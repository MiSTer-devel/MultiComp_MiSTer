;------------------------------------------------------------------------------
; Dummy interpreter
; Just say sorry.
;------------------------------------------------------------------------------
      LD   HL,M_SORRY	; Print Sorry message
      CALL M_PRINT
SORRY_GETC:	 CALL RDCHR
      CP   ' '
      JR   NZ, SORRY_GETC
      JP   M_INIT

M_SORRY:
      .BYTE	$0D,$0A
      .TEXT	"Sorry. No interpreter has been installed."
      .BYTE	$0D,$0A
      .TEXT "Press [space] ..." 
      .BYTE $00
 

 
