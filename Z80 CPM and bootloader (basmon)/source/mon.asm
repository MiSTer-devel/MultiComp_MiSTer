;==================================================================================
; Contents of this file are copyright Grant Searle
; HEX routines from Joel Owens.
;
; You have permission to use this for NON COMMERCIAL USE ONLY
; If you wish to use it elsewhere, please include an acknowledgement to myself.
;
; http://searle.hostei.com/grant/index.html
;
; eMail: home.micros01@btinternet.com
;
; If the above don't work, please perform an Internet search to see if I have
; updated the web page hosting service.
;
;==================================================================================

;------------------------------------------------------------------------------
;
; Z80 Monitor Rom
;
;------------------------------------------------------------------------------
; General Equates
;------------------------------------------------------------------------------

;CR		.EQU	0DH
;LF		.EQU	0AH
;ESC		.EQU	1BH
;CTRLC	.EQU	03H
M_CLS		.EQU	0CH


loadAddr	.EQU	0D000h	; CP/M load address
numSecs		.EQU	24	; Number of 512 sectors to be loaded


RTS_HIGH	.EQU	0D5H
RTS_LOW		.EQU	095H

ACIA0_D		.EQU	$81
ACIA0_C		.EQU	$80
ACIA1_D		.EQU	$83
ACIA1_C		.EQU	$82

SD_DATA		.EQU	088H
SD_CONTROL	.EQU	089H
SD_STATUS	.EQU	089H
SD_LBA0		.EQU	08AH
SD_LBA1		.EQU	08BH
SD_LBA2		.EQU	08CH

	.ORG	$3000

primaryIO	.ds	1
secNo		.ds	1
dmaAddr		.ds	2
InitTxtB        .ds     2
	
lba0		.DB	00h
lba1		.DB	00h
lba2		.DB	00h
lba3		.DB	00h

stackSpace	.ds	32
M_STACK   	.EQU    $	; Stack top


;------------------------------------------------------------------------------
;                         START OF MONITOR ROM
;------------------------------------------------------------------------------

MON		.ORG	$0000		; MONITOR ROM RESET VECTOR
;------------------------------------------------------------------------------
; Reset
;------------------------------------------------------------------------------
RST00		DI			;Disable INTerrupts
		JP	M_INIT		;Initialize Hardware and go
		NOP
		NOP
		NOP
		NOP
;------------------------------------------------------------------------------
; TX a character over RS232 wait for TXDONE first.
;------------------------------------------------------------------------------
RST08		JP	conout
		NOP
		NOP
		NOP
		NOP
		NOP
;------------------------------------------------------------------------------
; RX a character from buffer wait until char ready.
;------------------------------------------------------------------------------
RST10		JP	conin
		NOP
		NOP
		NOP
		NOP
		NOP
;------------------------------------------------------------------------------
; Check input buffer status
;------------------------------------------------------------------------------
RST18		JP	CKINCHAR


;------------------------------------------------------------------------------
; Console input routine
; Use the "primaryIO" flag to determine which input port to monitor.
;------------------------------------------------------------------------------
conin:
		LD	A,(primaryIO)
		CP	0
		JR	NZ,coninB
coninA:

waitForCharA:
		call ckincharA
		JR	Z, waitForCharA
		IN   	A,(ACIA0_D)
		RET	; Char ready in A

coninB:

waitForCharB:
		call ckincharB
		JR	Z, waitForCharB
		IN   	A,(ACIA1_D)
		RET	; Char ready in A

;------------------------------------------------------------------------------
; Console output routine
; Use the "primaryIO" flag to determine which output port to send a character.
;------------------------------------------------------------------------------
conout:		PUSH	AF		; Store character
		LD	A,(primaryIO)
		CP	0
		JR	NZ,conoutB1
		JR	conoutA1
conoutA:
		PUSH	AF

conoutA1:	CALL	CKACIA0		; See if ACIA channel A is finished transmitting
		JR	Z,conoutA1	; Loop until ACIA flag signals ready
		POP	AF		; RETrieve character
		OUT	(ACIA0_D),A	; OUTput the character
		RET

conoutB:
		PUSH	AF

conoutB1:	CALL	CKACIA1		; See if ACIA channel B is finished transmitting
		JR	Z,conoutB1	; Loop until ACIA flag signals ready
		POP	AF		; RETrieve character
		OUT	(ACIA1_D),A	; OUTput the character
		RET

;------------------------------------------------------------------------------
; Non blocking console output routine
; On return Z flag is 0, if the character could be written, else 1
; Use the "primaryIO" flag to determine which output port to send a character.
;------------------------------------------------------------------------------
nbconoutB:
         	PUSH	AF

nbconoutB1:	CALL	CKACIA1		; See if ACIA channel B has finished transmitting
		JR      NZ, nbconoutB2  ; Ready to write
		POP	AF	        ; Remove the parameter we don't need 
	        AND     $00             ; Indicate failure
		RET	        	; Return if ACIA flag signals not ready
nbconoutB2:	
	        POP	AF		; RETrieve character
		OUT	(ACIA1_D),A	; OUTput the character
	        OR      $ff             ; Indicate success
		RET

;------------------------------------------------------------------------------
; I/O status check routine
; Use the "primaryIO" flag to determine which port to check.
;------------------------------------------------------------------------------
CKACIA0
		IN   	A,(ACIA0_C)	; Status byte D1=TX Buff Empty, D0=RX char ready	
		RRCA			; Rotates RX status into Carry Flag,	
		BIT  	0,A		; Set Zero flag if still transmitting character	
        RET

CKACIA1
		IN   	A,(ACIA1_C)	; Status byte D1=TX Buff Empty, D0=RX char ready	
		RRCA			; Rotates RX status into Carry Flag,	
		BIT  	0,A		; Set Zero flag if still transmitting character	
        RET

;------------------------------------------------------------------------------
; Check if there is a character in the input buffer
; Use the "primaryIO" flag to determine which port to check.
;------------------------------------------------------------------------------
CKINCHAR
		LD	A,(primaryIO)
		CP	0
		JR	NZ,ckincharB

ckincharA:

		IN   A,(ACIA0_C)		; Status byte
		AND  $01
		CP   $0			; Z flag set if no char
		RET

ckincharB:

		IN   A,(ACIA1_C)		; Status byte
		AND  $01
		CP   $0			; Z flag set if no char
		RET

;------------------------------------------------------------------------------
; Filtered Character I/O
;------------------------------------------------------------------------------

RDCHR		RST	10H
		CP	LF
		JR	Z,RDCHR		; Ignore LF
		CP	ESC
		JR	NZ,RDCHR1
		LD	A,CTRLC		; Change ESC to CTRL-C
RDCHR1		RET

WRCHR		CP	CR
		JR	Z,WRCRLF	; When CR, write CRLF
		CP	M_CLS
		JR	Z,WR		; Allow write of "CLS"
		CP	' '		; Don't write out any other control codes
		JR	C,NOWR		; ie. < space
WR		RST	08H
NOWR		RET

WRCRLF		LD	A,CR
		RST	08H
		LD	A,LF
		RST	08H
		LD	A,CR
		RET


;------------------------------------------------------------------------------
; Initialise hardware and start main loop
;------------------------------------------------------------------------------
M_INIT		LD   SP,M_STACK		; Set the Stack Pointer

		LD        A,RTS_LOW
		OUT       (ACIA0_C),A         ; Initialise ACIA0
		OUT       (ACIA1_C),A         ; Initialise ACIA1
		; Display the "Press space to start" message on both consoles
		LD	A,$00
		LD	(primaryIO),A
    		LD   	HL,INITTXT
		CALL 	M_PRINT
		; On Display B we need to take care that it does not hang. 	
		LD   	HL,INITTXT
		LD      (InitTxtB),HL

printInitB:	LD   	HL,(InitTxtB)
		LD   	A,(HL)	; Get character
		OR   	A	; Is it $00 ?
		JR      Z, waitForSpace
        	CALL    nbconoutB	; Print it
		JR      Z, waitForSpace ; If we can't write, don't increment
		INC	HL
		LD 	(InitTxtB),HL   ; Store pointer into message for next round 
                JP      printInitB
		; Wait until space is in one of the buffers to determine the active console
waitForSpace:
		CALL    ckincharA
		JR	Z,chkSpaceB
		LD	A,$00
		LD	(primaryIO),A
		CALL	conin
		CP	' '
		JP	NZ, waitForSpace
		JR	spacePressed

chkSpaceB:	
		CALL 	ckincharB
	        JR	Z,printInitB ; If no key pressed, try to continue writing the init message on B
		LD	A,$01
		LD	(primaryIO),A
		CALL	conin
		CP	' '
		JP	NZ, printInitB ; If space not pressed, try to continue writing the init message on B

spacePressed:

		; Clear message on both consoles
		LD	A,$0C
		CALL	conoutA
	        CALL	nbconoutB

		;; We only clear the message on the active console,
		;; because trying to write on a console not connected could
		;; make the system freeze.

		; primaryIO is now set to the channel where SPACE was pressed	
		CALL TXCRLF	; TXCRLF
		LD   HL,M_SIGNON	; Print SIGNON message
		CALL M_PRINT

;------------------------------------------------------------------------------
; Monitor command loop
;------------------------------------------------------------------------------
MAIN  		LD   HL,MAIN	; Save entry point for Monitor	
		PUSH HL		; This is the return address
MAIN0		CALL TXCRLF	; Entry point for Monitor, Normal	
		LD   A,'>'	; Get a ">"	
		RST 08H		; print it

MAIN1		CALL RDCHR	; Get a character from the input port
		CP   ' '	; <spc> or less? 	
		JR   C,MAIN1	; Go back
	
		CP   ':'	; ":"?
		JP   Z,LOAD	; First character of a HEX load

		CALL WRCHR	; Print char on console

		AND  $5F	; Make character uppercase

		CP   'I'	
		JP   Z,INTERPRT

		CP   'G'
		JP   Z,M_GOTO

		CP   'X'
		JP   Z,CPMLOAD

		LD   A,'?'	; Get a "?"	
		RST 08H		; Print it
		JR   MAIN0
	
;------------------------------------------------------------------------------
; Print string of characters to Serial A until byte=$00, WITH CR, LF
;------------------------------------------------------------------------------
M_PRINT		LD   A,(HL)	; Get character
		OR   A		; Is it $00 ?
		RET  Z		; Then RETurn on terminator
		RST  08H	; Print it
		INC  HL		; Next Character
		JR   M_PRINT	; Continue until $00


TXCRLF		LD   A,$0D	; 
		RST  08H	; Print character 
		LD   A,$0A	; 
		RST  08H	; Print character
		RET

;------------------------------------------------------------------------------
; Get a character from the console, must be $20-$7F to be valid (no control characters)
; <Ctrl-c> and <SPACE> breaks with the Zero Flag set
;------------------------------------------------------------------------------	
M_GETCHR		CALL RDCHR	; RX a Character
		CP   $03	; <ctrl-c> User break?
		RET  Z			
		CP   $20	; <space> or better?
		JR   C,M_GETCHR	; Do it again until we get something usable
		RET
;------------------------------------------------------------------------------
; Gets two ASCII characters from the console (assuming them to be HEX 0-9 A-F)
; Moves them into B and C, converts them into a byte value in A and updates a
; Checksum value in E
;------------------------------------------------------------------------------
GET2		CALL M_GETCHR	; Get us a valid character to work with
		LD   B,A	; Load it in B
		CALL M_GETCHR	; Get us another character
		LD   C,A	; load it in C
		CALL BCTOA	; Convert ASCII to byte
		LD   C,A	; Build the checksum
		LD   A,E
		SUB  C		; The checksum should always equal zero when checked
		LD   E,A	; Save the checksum back where it came from
		LD   A,C	; Retrieve the byte and go back
		RET
;------------------------------------------------------------------------------
; Gets four Hex characters from the console, converts them to values in HL
;------------------------------------------------------------------------------
GETHL		LD   HL,$0000	; Gets xxxx but sets Carry Flag on any Terminator
		CALL ECHO	; RX a Character
		CP   $0D	; <CR>?
		JR   NZ,GETX2	; other key		
SETCY		SCF		; Set Carry Flag
		RET             ; and Return to main program		
;------------------------------------------------------------------------------
; This routine converts last four hex characters (0-9 A-F) user types into a value in HL
; Rotates the old out and replaces with the new until the user hits a terminating character
;------------------------------------------------------------------------------
GETX		LD   HL,$0000	; CLEAR HL
GETX1		CALL ECHO	; RX a character from the console
		CP   $0D	; <CR>
		RET  Z		; quit
		CP   $2C	; <,> can be used to safely quit for multiple entries
		RET  Z		; (Like filling both DE and HL from the user)
GETX2		CP   $03	; Likewise, a <ctrl-C> will terminate clean, too, but
		JR   Z,SETCY	; It also sets the Carry Flag for testing later.
		ADD  HL,HL	; Otherwise, rotate the previous low nibble to high
		ADD  HL,HL	; rather slowly
		ADD  HL,HL	; until we get to the top
		ADD  HL,HL	; and then we can continue on.
		SUB  $30	; Convert ASCII to byte	value
		CP   $0A	; Are we in the 0-9 range?
		JR   C,GETX3	; Then we just need to sub $30, but if it is A-F
		SUB  $07	; We need to take off 7 more to get the value down to
GETX3		AND  $0F	; to the right hex value
		ADD  A,L	; Add the high nibble to the low
		LD   L,A	; Move the byte back to A
		JR   GETX1	; and go back for next character until he terminates
;------------------------------------------------------------------------------
; Convert ASCII characters in B C registers to a byte value in A
;------------------------------------------------------------------------------
BCTOA		LD   A,B	; Move the hi order byte to A
		SUB  $30	; Take it down from Ascii
		CP   $0A	; Are we in the 0-9 range here?
		JR   C,BCTOA1	; If so, get the next nybble
		SUB  $07	; But if A-F, take it down some more
BCTOA1		RLCA		; Rotate the nybble from low to high
		RLCA		; One bit at a time
		RLCA		; Until we
		RLCA		; Get there with it
		LD   B,A	; Save the converted high nybble
		LD   A,C	; Now get the low order byte
		SUB  $30	; Convert it down from Ascii
		CP   $0A	; 0-9 at this point?
		JR   C,BCTOA2	; Good enough then, but
		SUB  $07	; Take off 7 more if it's A-F
BCTOA2		ADD  A,B	; Add in the high order nybble
		RET

;------------------------------------------------------------------------------
; Get a character and echo it back to the user
;------------------------------------------------------------------------------
ECHO		CALL	RDCHR
		CALL	WRCHR
		RET

;------------------------------------------------------------------------------
; GOTO command
;------------------------------------------------------------------------------
M_GOTO		CALL GETHL		; ENTRY POINT FOR <G>oto addr. Get XXXX from user.
		RET  C			; Return if invalid       	
		PUSH HL
		RET			; Jump to HL address value

;------------------------------------------------------------------------------
; LOAD Intel Hex format file from the console.
; [Intel Hex Format is:
; 1) Colon (Frame 0)
; 2) Record Length Field (Frames 1 and 2)
; 3) Load Address Field (Frames 3,4,5,6)
; 4) Record Type Field (Frames 7 and 8)
; 5) Data Field (Frames 9 to 9+2*(Record Length)-1
; 6) Checksum Field - Sum of all byte values from Record Length to and 
;   including Checksum Field = 0 ]
;------------------------------------------------------------------------------	
LOAD		LD   E,0	; First two Characters is the Record Length Field
		CALL GET2	; Get us two characters into BC, convert it to a byte <A>
		LD   D,A	; Load Record Length count into D
		CALL GET2	; Get next two characters, Memory Load Address <H>
		LD   H,A	; put value in H register.
		CALL GET2	; Get next two characters, Memory Load Address <L>
		LD   L,A	; put value in L register.
		CALL GET2	; Get next two characters, Record Field Type
		CP   $01	; Record Field Type 00 is Data, 01 is End of File
		JR   NZ,LOAD2	; Must be the end of that file
		CALL GET2	; Get next two characters, assemble into byte
		LD   A,E	; Recall the Checksum byte
		AND  A		; Is it Zero?
		JR   Z,LOAD00	; Print footer reached message
		JR   LOADERR	; Checksums don't add up, Error out
		
LOAD2		LD   A,D	; Retrieve line character counter	
		AND  A		; Are we done with this line?
		JR   Z,LOAD3	; Get two more ascii characters, build a byte and checksum
		CALL GET2	; Get next two chars, convert to byte in A, checksum it
		LD   (HL),A	; Move converted byte in A to memory location
		INC  HL		; Increment pointer to next memory location	
		LD   A,'.'	; Print out a "." for every byte loaded
		RST  08H	;
		DEC  D		; Decrement line character counter
		JR   LOAD2	; and keep loading into memory until line is complete
		
LOAD3		CALL GET2	; Get two chars, build byte and checksum
		LD   A,E	; Check the checksum value
		AND  A		; Is it zero?
		RET  Z

LOADERR		LD   HL,CKSUMERR  ; Get "Checksum Error" message
		CALL M_PRINT	; Print Message from (HL) and terminate the load
		RET

LOAD00  	LD   HL,LDETXT	; Print load complete message
		CALL M_PRINT
		RET

;------------------------------------------------------------------------------
; Start Interpreter
;------------------------------------------------------------------------------
INTERPRT
		JP  STARTINT
		RET

;------------------------------------------------------------------------------
; CP/M load command
;------------------------------------------------------------------------------
CPMLOAD

    	LD HL,CPMTXT
		CALL M_PRINT
		CALL M_GETCHR
		RET Z	; Cancel if CTRL-C
		AND  $5F ; uppercase
		CP 'Y'
		JP  Z,CPMLOAD2
		RET
CPMTXT
		.BYTE	$0D,$0A
		.TEXT	"Boot CP/M?"
		.BYTE	$00

CPMTXT2
		.BYTE	$0D,$0A
		.TEXT	"Loading CP/M"
		.BYTE	$0D,$0A,$00

CPMLOAD2
    	LD HL,CPMTXT2
		CALL M_PRINT
		
		LD	B,numSecs

		LD	A,0
		LD	(lba0),A
		ld 	(lba1),A
		ld 	(lba2),A
		ld 	(lba3),A
		
		LD	HL,loadAddr
		LD	(dmaAddr),HL
processSectors:

		call	readhst

		LD	DE,0200H
		LD	HL,(dmaAddr)
		ADD	HL,DE
		LD	(dmaAddr),HL
		LD	A,(lba0)
		INC	A
		LD	(lba0),A

		djnz	processSectors

; Start CP/M using entry at top of BIOS
; The current active console stream ID is pushed onto the stack
; to allow the CBIOS to pick it up
; 0 = ACIA0, 1 = ACIA1
		
		ld	A,(primaryIO)
		PUSH	AF
		ld	HL,($FFFE)
		jp	(HL)


;------------------------------------------------------------------------------
; ROUTINES AS USED IN BIOS
;------------------------------------------------------------------------------

;================================================================================================
; Convert track/head/sector into LBA for physical access to the disk
;================================================================================================
setLBAaddr:	
		; Transfer LBA to disk (LBA3 not used on SD card)
		LD	A,(lba2)
		OUT	(SD_LBA2),A
		LD	A,(lba1)
		OUT	(SD_LBA1),A
		LD	A,(lba0)
		OUT	(SD_LBA0),A
		RET
		
;================================================================================================
; Read physical sector from host
;================================================================================================

readhst:
		PUSH 	AF
		PUSH 	BC
		PUSH 	HL

rdWait1: IN	A,(SD_STATUS)
		CP	128
		JR	NZ,rdWait1
		
		CALL 	setLBAaddr
		
		LD	A,$00	; 00 = Read block
		OUT	(SD_CONTROL),A

		LD 	c,4
;		LD 	HL,hstbuf
rd4secs:
		LD 	b,128
rdByte:

rdWait2: IN	A,(SD_STATUS)
		CP	224	; Read byte waiting
		JR	NZ,rdWait2

		IN	A,(SD_DATA)

		LD 	(HL),A
		INC 	HL
		dec 	b
		JR 	NZ, rdByte
		dec 	c
		JR 	NZ,rd4secs

		POP 	HL
		POP 	BC
		POP 	AF

;		XOR 	a
;		ld	(erflag),a
		RET

;------------------------------------------------------------------------------
; END OF ROUTINES AS USED IN BIOS
;------------------------------------------------------------------------------


M_SIGNON	.BYTE	"CP/M Boot ROM 2.0"
		.BYTE	" based on design by G. Searle"
		.BYTE	$0D,$0A
		.BYTE	$0D,$0A
		.TEXT	"I        - Start Interpreter"
		.BYTE	$0D,$0A
		.TEXT	"X        - Boot CP/M (load $D000-$FFFF)"
		.BYTE	$0D,$0A
		.TEXT	":nnnn... - Load Intel-Hex file record"
		.BYTE	$0D,$0A
		.TEXT	"Gnnnn    - Run loc nnnn"
		.BYTE	$0D,$0A
       	.BYTE   $00

CKSUMERR	.BYTE	"Checksum error"
		.BYTE	$0D,$0A,$00

INITTXT  
		.BYTE	$0C
		.TEXT	"Press [space] to activate console."
		.BYTE	$0D,$0A, $00

LDETXT  
		.TEXT	"Complete"
		.BYTE	$0D,$0A, $00

; ==========================================================================================================================
; GENERAL EQUATES

CTRLC   .EQU    03H             ; Control "C"
CTRLG   .EQU    07H             ; Control "G"
BKSP    .EQU    08H             ; Back space
LF      .EQU    0AH             ; Line feed
CS      .EQU    0CH             ; Clear screen
CR      .EQU    0DH             ; Carriage return
CTRLO   .EQU    0FH             ; Control "O"
CTRLQ	.EQU	11H		; Control "Q"
CTRLR   .EQU    12H             ; Control "R"
CTRLS   .EQU    13H             ; Control "S"
CTRLU   .EQU    15H             ; Control "U"
ESC     .EQU    1BH             ; Escape
DEL     .EQU    7FH             ; Delete


;===========================================================================================================================

; NASCOM ROM BASIC Ver 4.7, 
; used to be here, removed to get rid of the '(C) 1978 Microsoft'

STARTINT:							  
#INCLUDE "SOURCE\\INTPRT.ASM"
.end
