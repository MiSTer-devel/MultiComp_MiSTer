#!/usr/bin/python

import array
import sys

NULL = 0
OP_NONE = 0
OP_BYTE = 1
OP_WORD = 2
OP_OFFSET = 3
OP_JUMP = 4
OP_CB = 5
OP_DD = 6
OP_ED = 7
OP_FD = 8
OP_BYTE_OFF = 9
OP_BYTE_OFF_2 = 10
OP_DDCB = 11
OP_FDCB = 12
OP_BYTE_OFF_3 = 13

hexadecimal = False
second = False
show_address = False

opcodes_main = (
	(  OP_NONE  , "nop"        ), #   0 nop
	(  OP_WORD  , "ld bc,%s"   ), #   1 ld_bc_nn
	(  OP_NONE  , "ld (bc),a"  ), #   2 ld_off_bc_A
	(  OP_NONE  , "inc bc"     ), #   3 inc_bc
	(  OP_NONE  , "inc b"      ), #   4 inc_B
	(  OP_NONE  , "dec b"      ), #   5 dec_B
	(  OP_BYTE  , "ld b,%s"    ), #   6 ld_B_n
	(  OP_NONE  , "rlca"       ), #   7 rlca
	(  OP_NONE  , "ex af,af'"  ), #   8 EX_af_af_
	(  OP_NONE  , "add hl,bc"  ), #   9 add_hl_bc
	(  OP_NONE  , "ld a,(bc)"  ), #  10 ld_A_off_bc
	(  OP_NONE  , "dec bc"     ), #  11 dec_bc
	(  OP_NONE  , "inc c"      ), #  12 inc_C
	(  OP_NONE  , "dec c"      ), #  13 dec_C
	(  OP_BYTE  , "ld c,%s"    ), #  14 ld_C_n
	(  OP_NONE  , "rrca"       ), #  15 rrca
	(  OP_OFFSET, "djnz %s"    ), #  16 djnz_off_PC_e
	(  OP_WORD  , "ld de,%s"   ), #  17 ld_de_nn
	(  OP_NONE  , "ld (de),a"  ), #  18 ld_off_de_A
	(  OP_NONE  , "inc de"     ), #  19 inc_de
	(  OP_NONE  , "inc d"      ), #  20 inc_D
	(  OP_NONE  , "dec d"      ), #  21 dec_D
	(  OP_BYTE  , "ld d,%s"    ), #  22 ld_D_n
	(  OP_NONE  , "rla"        ), #  23 rla
	(  OP_OFFSET, "jr %s"      ), #  24 jr_off_PC_e
	(  OP_NONE  , "add hl,de"  ), #  25 add_hl_de
	(  OP_NONE  , "ld a,(de)"  ), #  26 ld_A_off_de
	(  OP_NONE  , "dec de"     ), #  27 dec_de
	(  OP_NONE  , "inc e"      ), #  28 inc_E
	(  OP_NONE  , "dec e"      ), #  29 dec_E
	(  OP_BYTE  , "ld e,%s"    ), #  30 ld_E_n
	(  OP_NONE  , "rra"        ), #  31 rra
	(  OP_OFFSET, "jr nz,%s"   ), #  32 jr_NZ_off_PC_e
	(  OP_WORD  , "ld hl,%s"   ), #  33 ld_hl_nn
	(  OP_WORD  , "ld (%s),hl" ), #  34 ld_off_nn_hl
	(  OP_NONE  , "inc hl"     ), #  35 inc_hl
	(  OP_NONE  , "inc h"      ), #  36 inc_H
	(  OP_NONE  , "dec h"      ), #  37 dec_H
	(  OP_BYTE  , "ld h,%s"    ), #  38 ld_H_n
	(  OP_NONE  , "daa"        ), #  39 daa
	(  OP_OFFSET, "jr z,%s"    ), #  40 jr_Z_off_PC_e
	(  OP_NONE  , "add hl,hl"  ), #  41 add_hl_hl
	(  OP_WORD  , "ld hl,(%s)" ), #  42 ld_hl_off_nn
	(  OP_NONE  , "dec hl"     ), #  43 dec_hl
	(  OP_NONE  , "inc l"      ), #  44 inc_L
	(  OP_NONE  , "dec l"      ), #  45 dec_L
	(  OP_BYTE  , "ld l,%s"    ), #  46 ld_L_n
	(  OP_NONE  , "cpl"        ), #  47 cpl
	(  OP_OFFSET, "jr nc,%s"   ), #  48 jr_NC_off_PC_e
	(  OP_WORD  , "ld sp,%s"   ), #  49 ld_sp_nn
	(  OP_WORD  , "ld (%s),a"  ), #  50 ld_off_nn_A
	(  OP_NONE  , "inc sp"     ), #  51 inc_sp
	(  OP_NONE  , "inc (hl)"   ), #  52 inc_off_hl
	(  OP_NONE  , "dec (hl)"   ), #  53 dec_off_hl
	(  OP_BYTE  , "ld (hl),%s" ), #  54 ld_off_hl_n
	(  OP_NONE  , "scf"        ), #  55 scf
	(  OP_OFFSET, "jr c,%s"    ), #  56 jr_C_off_PC_e
	(  OP_NONE  , "add hl,sp"  ), #  57 add_hl_sp
	(  OP_WORD  , "ld a,(%s)"  ), #  58 ld_A_off_nn
	(  OP_NONE  , "dec sp"     ), #  59 dec_sp
	(  OP_NONE  , "inc a"      ), #  60 inc_A
	(  OP_NONE  , "dec a"      ), #  61 dec_A
	(  OP_BYTE  , "ld a,%s"    ), #  62 ld_A_n
	(  OP_NONE  , "ccf"        ), #  63 ccf
	(  OP_NONE  , "ld b,b"     ), #  64 ld_B_B
	(  OP_NONE  , "ld b,c"     ), #  65 ld_B_C
	(  OP_NONE  , "ld b,d"     ), #  66 ld_B_D
	(  OP_NONE  , "ld b,e"     ), #  67 ld_B_E
	(  OP_NONE  , "ld b,h"     ), #  68 ld_B_H
	(  OP_NONE  , "ld b,l"     ), #  69 ld_B_L
	(  OP_NONE  , "ld b,(hl)"  ), #  70 ld_B_off_hl
	(  OP_NONE  , "ld b,a"     ), #  71 ld_B_A
	(  OP_NONE  , "ld c,b"     ), #  72 ld_C_B
	(  OP_NONE  , "ld c,c"     ), #  73 ld_C_C
	(  OP_NONE  , "ld c,d"     ), #  74 ld_C_D
	(  OP_NONE  , "ld c,e"     ), #  75 ld_C_E
	(  OP_NONE  , "ld c,h"     ), #  76 ld_C_H
	(  OP_NONE  , "ld c,l"     ), #  77 ld_C_L
	(  OP_NONE  , "ld c,(hl)"  ), #  78 ld_C_off_hl
	(  OP_NONE  , "ld c,a"     ), #  79 ld_C_A
	(  OP_NONE  , "ld d,b"     ), #  80 ld_D_B
	(  OP_NONE  , "ld d,c"     ), #  81 ld_D_C
	(  OP_NONE  , "ld d,d"     ), #  82 ld_D_D
	(  OP_NONE  , "ld d,e"     ), #  83 ld_D_E
	(  OP_NONE  , "ld d,h"     ), #  84 ld_D_H
	(  OP_NONE  , "ld d,l"     ), #  85 ld_D_L
	(  OP_NONE  , "ld d,(hl)"  ), #  86 ld_D_off_hl
	(  OP_NONE  , "ld d,a"     ), #  87 ld_D_A
	(  OP_NONE  , "ld e,b"     ), #  88 ld_E_B
	(  OP_NONE  , "ld e,c"     ), #  89 ld_E_C
	(  OP_NONE  , "ld e,d"     ), #  90 ld_E_D
	(  OP_NONE  , "ld e,e"     ), #  91 ld_E_E
	(  OP_NONE  , "ld e,h"     ), #  92 ld_E_H
	(  OP_NONE  , "ld e,l"     ), #  93 ld_E_L
	(  OP_NONE  , "ld e,(hl)"  ), #  94 ld_E_off_hl
	(  OP_NONE  , "ld e,a"     ), #  95 ld_E_A
	(  OP_NONE  , "ld h,b"     ), #  96 ld_H_B
	(  OP_NONE  , "ld h,c"     ), #  97 ld_H_C
	(  OP_NONE  , "ld h,d"     ), #  98 ld_H_D
	(  OP_NONE  , "ld h,e"     ), #  99 ld_H_E
	(  OP_NONE  , "ld h,h"     ), # 100 ld_H_H
	(  OP_NONE  , "ld h,l"     ), # 101 ld_H_L
	(  OP_NONE  , "ld h,(hl)"  ), # 102 ld_H_off_hl
	(  OP_NONE  , "ld h,a"     ), # 103 ld_H_A
	(  OP_NONE  , "ld l,b"     ), # 104 ld_L_B
	(  OP_NONE  , "ld l,c"     ), # 105 ld_L_C
	(  OP_NONE  , "ld l,d"     ), # 106 ld_L_D
	(  OP_NONE  , "ld l,e"     ), # 107 ld_L_E
	(  OP_NONE  , "ld l,h"     ), # 108 ld_L_H
	(  OP_NONE  , "ld l,l"     ), # 109 ld_L_L
	(  OP_NONE  , "ld l,(hl)"  ), # 110 ld_L_off_hl
	(  OP_NONE  , "ld l,a"     ), # 111 ld_L_A
	(  OP_NONE  , "ld (hl),b"  ), # 112 ld_off_hl_B
	(  OP_NONE  , "ld (hl),c"  ), # 113 ld_off_hl_C
	(  OP_NONE  , "ld (hl),d"  ), # 114 ld_off_hl_D
	(  OP_NONE  , "ld (hl),e"  ), # 115 ld_off_hl_E
	(  OP_NONE  , "ld (hl),h"  ), # 116 ld_off_hl_H
	(  OP_NONE  , "ld (hl),l"  ), # 117 ld_off_hl_L
	(  OP_NONE  , "halt"       ), # 118 halt
	(  OP_NONE  , "ld (hl),a"  ), # 119 ld_off_hl_A
	(  OP_NONE  , "ld a,b"     ), # 120 ld_A_B
	(  OP_NONE  , "ld a,c"     ), # 121 ld_A_C
	(  OP_NONE  , "ld a,d"     ), # 122 ld_A_D
	(  OP_NONE  , "ld a,e"     ), # 123 ld_A_E
	(  OP_NONE  , "ld a,h"     ), # 124 ld_A_H
	(  OP_NONE  , "ld a,l"     ), # 125 ld_A_L
	(  OP_NONE  , "ld a,(hl)"  ), # 126 ld_A_off_hl
	(  OP_NONE  , "ld a,a"     ), # 127 ld_A_A
	(  OP_NONE  , "add a,b"    ), # 128 add_A_B
	(  OP_NONE  , "add a,c"    ), # 129 add_A_C
	(  OP_NONE  , "add a,d"    ), # 130 add_A_D
	(  OP_NONE  , "add a,e"    ), # 131 add_A_E
	(  OP_NONE  , "add a,h"    ), # 132 add_A_H
	(  OP_NONE  , "add a,l"    ), # 133 add_A_L
	(  OP_NONE  , "add a,(hl)" ), # 134 add_A_off_hl
	(  OP_NONE  , "add a,a"    ), # 135 add_A_A
	(  OP_NONE  , "adc a,b"    ), # 136 adc_A_B
	(  OP_NONE  , "adc a,c"    ), # 137 adc_A_C
	(  OP_NONE  , "adc a,d"    ), # 138 adc_A_D
	(  OP_NONE  , "adc a,e"    ), # 139 adc_A_E
	(  OP_NONE  , "adc a,h"    ), # 140 adc_A_H
	(  OP_NONE  , "adc a,l"    ), # 141 adc_A_L
	(  OP_NONE  , "adc a,(hl)" ), # 142 adc_A_off_hl
	(  OP_NONE  , "adc a,a"    ), # 143 adc_A_A
	(  OP_NONE  , "sub a,b"    ), # 144 sub_A_B
	(  OP_NONE  , "sub a,c"    ), # 145 sub_A_C
	(  OP_NONE  , "sub a,d"    ), # 146 sub_A_D
	(  OP_NONE  , "sub a,e"    ), # 147 sub_A_E
	(  OP_NONE  , "sub a,h"    ), # 148 sub_A_H
	(  OP_NONE  , "sub a,l"    ), # 149 sub_A_L
	(  OP_NONE  , "sub a,(hl)" ), # 150 sub_A_off_hl
	(  OP_NONE  , "sub a,a"    ), # 151 sub_A_A
	(  OP_NONE  , "sbc a,b"    ), # 152 sbc_A_B
	(  OP_NONE  , "sbc a,c"    ), # 153 sbc_A_C
	(  OP_NONE  , "sbc a,d"    ), # 154 sbc_A_D
	(  OP_NONE  , "sbc a,e"    ), # 155 sbc_A_E
	(  OP_NONE  , "sbc a,h"    ), # 156 sbc_A_H
	(  OP_NONE  , "sbc a,l"    ), # 157 sbc_A_L
	(  OP_NONE  , "sbc a,(hl)" ), # 158 sbc_A_off_hl
	(  OP_NONE  , "sbc a,a"    ), # 159 sbc_A_A
	(  OP_NONE  , "and b"      ), # 160 and_B
	(  OP_NONE  , "and c"      ), # 161 and_C
	(  OP_NONE  , "and d"      ), # 162 and_D
	(  OP_NONE  , "and e"      ), # 163 and_E
	(  OP_NONE  , "and h"      ), # 164 and_H
	(  OP_NONE  , "and l"      ), # 165 and_L
	(  OP_NONE  , "and (hl)"   ), # 166 and_off_hl
	(  OP_NONE  , "and a"      ), # 167 and_A
	(  OP_NONE  , "xor b"      ), # 168 xor_B
	(  OP_NONE  , "xor c"      ), # 169 xor_C
	(  OP_NONE  , "xor d"      ), # 170 xor_D
	(  OP_NONE  , "xor e"      ), # 171 xor_E
	(  OP_NONE  , "xor h"      ), # 172 xor_H
	(  OP_NONE  , "xor l"      ), # 173 xor_L
	(  OP_NONE  , "xor (hl)"   ), # 174 xor_off_hl
	(  OP_NONE  , "xor a"      ), # 175 xor_A
	(  OP_NONE  , "or b"       ), # 176 OR_B
	(  OP_NONE  , "or c"       ), # 177 OR_C
	(  OP_NONE  , "or d"       ), # 178 OR_D
	(  OP_NONE  , "or e"       ), # 179 OR_E
	(  OP_NONE  , "or h"       ), # 180 OR_H
	(  OP_NONE  , "or l"       ), # 181 OR_L
	(  OP_NONE  , "or (hl)"    ), # 182 OR_off_hl
	(  OP_NONE  , "or a"       ), # 183 OR_A
	(  OP_NONE  , "cp b"       ), # 184 cP_B
	(  OP_NONE  , "cp c"       ), # 185 cP_C
	(  OP_NONE  , "cp d"       ), # 186 cP_D
	(  OP_NONE  , "cp e"       ), # 187 cP_E
	(  OP_NONE  , "cp h"       ), # 188 cP_H
	(  OP_NONE  , "cp l"       ), # 189 cP_L
	(  OP_NONE  , "cp (hl)"    ), # 190 cP_off_hl
	(  OP_NONE  , "cp a"       ), # 191 cP_A
	(  OP_NONE  , "ret nz"     ), # 192 ret_NZ
	(  OP_NONE  , "pop bc"     ), # 193 pop_bc
	(  OP_JUMP  , "jp nz,%s"   ), # 194 jp_NZ_off_nn
	(  OP_JUMP  , "jp %s"      ), # 195 jp_off_nn
	(  OP_JUMP  , "call nz,%s" ), # 196 call_NZ_off_nn
	(  OP_NONE  , "push bc"    ), # 197 push_bc
	(  OP_BYTE  , "add a,%s"   ), # 198 add_A_n
	(  OP_NONE  , "rst 0"      ), # 199 rst_0H
	(  OP_NONE  , "ret z"      ), # 200 ret_Z
	(  OP_NONE  , "ret"        ), # 201 ret
	(  OP_JUMP  , "jp z,%s"    ), # 202 jp_Z_off_nn
	(  OP_CB  ,  NULL,         ), # 203 NULL
	(  OP_JUMP  , "call z,%s"  ), # 204 call_Z_off_nn
	(  OP_JUMP  , "call %s"    ), # 205 call_off_nn
	(  OP_BYTE  , "adc a,%s"   ), # 206 adc_A_n
	(  OP_NONE  , "rst 8"      ), # 207 rst_8H
	(  OP_NONE  , "ret nc"     ), # 208 ret_NC
	(  OP_NONE  , "pop de"     ), # 209 pop_de
	(  OP_JUMP  , "jp nc,%s"   ), # 210 jp_NC_off_nn
	(  OP_BYTE  , "out (%s),a" ), # 211 out_off_n_A
	(  OP_JUMP  , "call nc,%s" ), # 212 call_NC_off_nn
	(  OP_NONE  , "push de"    ), # 213 push_de
	(  OP_BYTE  , "sub %s"     ), # 214 sub_A_n
	(  OP_NONE  , "rst 16"     ), # 215 rst_10H
	(  OP_NONE  , "ret c"      ), # 216 ret_C
	(  OP_NONE  , "exx"        ), # 217 exx
	(  OP_JUMP  , "jp c,%s"    ), # 218 jp_C_off_nn
	(  OP_BYTE  , "in a,(%s)"  ), # 219 in_A_off_n
	(  OP_JUMP  , "call c,%s"  ), # 220 call_C_off_nn
	(  OP_DD  ,  NULL,         ), # 221 NULL
	(  OP_BYTE  , "sbc %s"     ), # 222 sbc_A_n
	(  OP_NONE  , "rst 24"     ), # 223 rst_18H
	(  OP_NONE  , "ret po"     ), # 224 ret_PO
	(  OP_NONE  , "pop hl"     ), # 225 pop_hl
	(  OP_JUMP  , "jp po,%s"   ), # 226 jp_PO_off_nn
	(  OP_NONE  , "ex (sp),hl" ), # 227 EX_off_sp_hl
	(  OP_JUMP  , "call po,%s" ), # 228 call_PO_off_nn
	(  OP_NONE  , "push hl"    ), # 229 push_hl
	(  OP_BYTE  , "and %s"     ), # 230 and_n
	(  OP_NONE  , "rst 32"     ), # 231 rst_20H
	(  OP_NONE  , "ret pe"     ), # 232 ret_PE
	(  OP_NONE  , "jp (hl)"    ), # 233 jp_off_hl
	(  OP_JUMP  , "jp pe,%s"   ), # 234 jp_PE_off_nn
	(  OP_NONE  , "ex de,hl"   ), # 235 EX_de_hl
	(  OP_JUMP  , "call pe,%s" ), # 236 call_PE_off_nn
	(  OP_ED  ,  NULL,         ), # 237 NULL
	(  OP_BYTE  , "xor %s"     ), # 238 xor_n
	(  OP_NONE  , "rst 40"     ), # 239 rst_28H
	(  OP_NONE  , "ret p"      ), # 240 ret_P
	(  OP_NONE  , "pop af"     ), # 241 pop_af
	(  OP_JUMP  , "jp p,%s"    ), # 242 jp_P_off_nn
	(  OP_NONE  , "di"         ), # 243 di
	(  OP_JUMP  , "call p,%s"  ), # 244 call_P_off_nn
	(  OP_NONE  , "push af"    ), # 245 push_af
	(  OP_BYTE  , "or %s"      ), # 246 OR_n
	(  OP_NONE  , "rst 48"     ), # 247 rst_30H
	(  OP_NONE  , "ret m"      ), # 248 ret_M
	(  OP_NONE  , "ld sp,hl"   ), # 249 ld_sp_hl
	(  OP_JUMP  , "jp m,%s"    ), # 250 jp_M_off_nn
	(  OP_NONE  , "ei"         ), # 251 ei
	(  OP_JUMP  , "call m,%s"  ), # 252 call_M_off_nn
	(  OP_FD  ,  NULL,         ), # 253 NULL
	(  OP_BYTE  , "cp %s"      ), # 254 cP_n
	(  OP_NONE  , "rst 56"     ) # 255 rst_38H
)

opcodes_CB = (
	(  OP_NONE  , "rlc b"      ), #   0 rlc_B
	(  OP_NONE  , "rlc c"      ), #   1 rlc_C
	(  OP_NONE  , "rlc d"      ), #   2 rlc_D
	(  OP_NONE  , "rlc e"      ), #   3 rlc_E
	(  OP_NONE  , "rlc h"      ), #   4 rlc_H
	(  OP_NONE  , "rlc l"      ), #   5 rlc_L
	(  OP_NONE  , "rlc (hl)"   ), #   6 rlc_off_hl
	(  OP_NONE  , "rlc a"      ), #   7 rlc_A
	(  OP_NONE  , "rrc b"      ), #   8 rrc_B
	(  OP_NONE  , "rrc c"      ), #   9 rrc_C
	(  OP_NONE  , "rrc d"      ), #  10 rrc_D
	(  OP_NONE  , "rrc e"      ), #  11 rrc_E
	(  OP_NONE  , "rrc h"      ), #  12 rrc_H
	(  OP_NONE  , "rrc l"      ), #  13 rrc_L
	(  OP_NONE  , "rrc (hl)"   ), #  14 rrc_off_hl
	(  OP_NONE  , "rrc a"      ), #  15 rrc_A
	(  OP_NONE  , "rl b"       ), #  16 rl_B
	(  OP_NONE  , "rl c"       ), #  17 rl_C
	(  OP_NONE  , "rl d"       ), #  18 rl_D
	(  OP_NONE  , "rl e"       ), #  19 rl_E
	(  OP_NONE  , "rl h"       ), #  20 rl_H
	(  OP_NONE  , "rl l"       ), #  21 rl_L
	(  OP_NONE  , "rl (hl)"    ), #  22 rl_off_hl
	(  OP_NONE  , "rl a"       ), #  23 rl_A
	(  OP_NONE  , "rr b"       ), #  24 rr_B
	(  OP_NONE  , "rr c"       ), #  25 rr_C
	(  OP_NONE  , "rr d"       ), #  26 rr_D
	(  OP_NONE  , "rr e"       ), #  27 rr_E
	(  OP_NONE  , "rr h"       ), #  28 rr_H
	(  OP_NONE  , "rr l"       ), #  29 rr_L
	(  OP_NONE  , "rr (hl)"    ), #  30 rr_off_hl
	(  OP_NONE  , "rr a"       ), #  31 rr_A
	(  OP_NONE  , "sla b"      ), #  32 sla_B
	(  OP_NONE  , "sla c"      ), #  33 sla_C
	(  OP_NONE  , "sla d"      ), #  34 sla_D
	(  OP_NONE  , "sla e"      ), #  35 sla_E
	(  OP_NONE  , "sla h"      ), #  36 sla_H
	(  OP_NONE  , "sla l"      ), #  37 sla_L
	(  OP_NONE  , "sla (hl)"   ), #  38 sla_off_hl
	(  OP_NONE  , "sla a"      ), #  39 sla_A
	(  OP_NONE  , "sra b"      ), #  40 sra_B
	(  OP_NONE  , "sra c"      ), #  41 sra_C
	(  OP_NONE  , "sra d"      ), #  42 sra_D
	(  OP_NONE  , "sra e"      ), #  43 sra_E
	(  OP_NONE  , "sra h"      ), #  44 sra_H
	(  OP_NONE  , "sra l"      ), #  45 sra_L
	(  OP_NONE  , "sra (hl)"   ), #  46 sra_off_hl
	(  OP_NONE  , "sra a"      ), #  47 sra_A
	(  OP_NONE  , "sll b"      ), #  48 sll_B
	(  OP_NONE  , "sll c"      ), #  49 sll_C
	(  OP_NONE  , "sll d"      ), #  50 sll_D
	(  OP_NONE  , "sll e"      ), #  51 sll_E
	(  OP_NONE  , "sll h"      ), #  52 sll_H
	(  OP_NONE  , "sll l"      ), #  53 sll_L
	(  OP_NONE  , "sll (hl)"   ), #  54 sll_off_hl
	(  OP_NONE  , "sll a"      ), #  55 sll_A
	(  OP_NONE  , "srl b"      ), #  56 srl_B
	(  OP_NONE  , "srl c"      ), #  57 srl_C
	(  OP_NONE  , "srl d"      ), #  58 srl_D
	(  OP_NONE  , "srl e"      ), #  59 srl_E
	(  OP_NONE  , "srl h"      ), #  60 srl_H
	(  OP_NONE  , "srl l"      ), #  61 srl_L
	(  OP_NONE  , "srl (hl)"   ), #  62 srl_off_hl
	(  OP_NONE  , "srl a"      ), #  63 srl_A
	(  OP_NONE  , "bit 0,b"    ), #  64 bit_0_B
	(  OP_NONE  , "bit 0,c"    ), #  65 bit_0_C
	(  OP_NONE  , "bit 0,d"    ), #  66 bit_0_D
	(  OP_NONE  , "bit 0,e"    ), #  67 bit_0_E
	(  OP_NONE  , "bit 0,h"    ), #  68 bit_0_H
	(  OP_NONE  , "bit 0,l"    ), #  69 bit_0_L
	(  OP_NONE  , "bit 0,(hl)" ), #  70 bit_0_off_hl
	(  OP_NONE  , "bit 0,a"    ), #  71 bit_0_A
	(  OP_NONE  , "bit 1,b"    ), #  72 bit_1_B
	(  OP_NONE  , "bit 1,c"    ), #  73 bit_1_C
	(  OP_NONE  , "bit 1,d"    ), #  74 bit_1_D
	(  OP_NONE  , "bit 1,e"    ), #  75 bit_1_E
	(  OP_NONE  , "bit 1,h"    ), #  76 bit_1_H
	(  OP_NONE  , "bit 1,l"    ), #  77 bit_1_L
	(  OP_NONE  , "bit 1,(hl)" ), #  78 bit_1_off_hl
	(  OP_NONE  , "bit 1,a"    ), #  79 bit_1_A
	(  OP_NONE  , "bit 2,b"    ), #  80 bit_2_B
	(  OP_NONE  , "bit 2,c"    ), #  81 bit_2_C
	(  OP_NONE  , "bit 2,d"    ), #  82 bit_2_D
	(  OP_NONE  , "bit 2,e"    ), #  83 bit_2_E
	(  OP_NONE  , "bit 2,h"    ), #  84 bit_2_H
	(  OP_NONE  , "bit 2,l"    ), #  85 bit_2_L
	(  OP_NONE  , "bit 2,(hl)" ), #  86 bit_2_off_hl
	(  OP_NONE  , "bit 2,a"    ), #  87 bit_2_A
	(  OP_NONE  , "bit 3,b"    ), #  88 bit_3_B
	(  OP_NONE  , "bit 3,c"    ), #  89 bit_3_C
	(  OP_NONE  , "bit 3,d"    ), #  90 bit_3_D
	(  OP_NONE  , "bit 3,e"    ), #  91 bit_3_E
	(  OP_NONE  , "bit 3,h"    ), #  92 bit_3_H
	(  OP_NONE  , "bit 3,l"    ), #  93 bit_3_L
	(  OP_NONE  , "bit 3,(hl)" ), #  94 bit_3_off_hl
	(  OP_NONE  , "bit 3,a"    ), #  95 bit_3_A
	(  OP_NONE  , "bit 4,b"    ), #  96 bit_4_B
	(  OP_NONE  , "bit 4,c"    ), #  97 bit_4_C
	(  OP_NONE  , "bit 4,d"    ), #  98 bit_4_D
	(  OP_NONE  , "bit 4,e"    ), #  99 bit_4_E
	(  OP_NONE  , "bit 4,h"    ), # 100 bit_4_H
	(  OP_NONE  , "bit 4,l"    ), # 101 bit_4_L
	(  OP_NONE  , "bit 4,(hl)" ), # 102 bit_4_off_hl
	(  OP_NONE  , "bit 4,a"    ), # 103 bit_4_A
	(  OP_NONE  , "bit 5,b"    ), # 104 bit_5_B
	(  OP_NONE  , "bit 5,c"    ), # 105 bit_5_C
	(  OP_NONE  , "bit 5,d"    ), # 106 bit_5_D
	(  OP_NONE  , "bit 5,e"    ), # 107 bit_5_E
	(  OP_NONE  , "bit 5,h"    ), # 108 bit_5_H
	(  OP_NONE  , "bit 5,l"    ), # 109 bit_5_L
	(  OP_NONE  , "bit 5,(hl)" ), # 110 bit_5_off_hl
	(  OP_NONE  , "bit 5,a"    ), # 111 bit_5_A
	(  OP_NONE  , "bit 6,b"    ), # 112 bit_6_B
	(  OP_NONE  , "bit 6,c"    ), # 113 bit_6_C
	(  OP_NONE  , "bit 6,d"    ), # 114 bit_6_D
	(  OP_NONE  , "bit 6,e"    ), # 115 bit_6_E
	(  OP_NONE  , "bit 6,h"    ), # 116 bit_6_H
	(  OP_NONE  , "bit 6,l"    ), # 117 bit_6_L
	(  OP_NONE  , "bit 6,(hl)" ), # 118 bit_6_off_hl
	(  OP_NONE  , "bit 6,a"    ), # 119 bit_6_A
	(  OP_NONE  , "bit 7,b"    ), # 120 bit_7_B
	(  OP_NONE  , "bit 7,c"    ), # 121 bit_7_C
	(  OP_NONE  , "bit 7,d"    ), # 122 bit_7_D
	(  OP_NONE  , "bit 7,e"    ), # 123 bit_7_E
	(  OP_NONE  , "bit 7,h"    ), # 124 bit_7_H
	(  OP_NONE  , "bit 7,l"    ), # 125 bit_7_L
	(  OP_NONE  , "bit 7,(hl)" ), # 126 bit_7_off_hl
	(  OP_NONE  , "bit 7,a"    ), # 127 bit_7_A
	(  OP_NONE  , "res 0,b"    ), # 128 res_0_B
	(  OP_NONE  , "res 0,c"    ), # 129 res_0_C
	(  OP_NONE  , "res 0,d"    ), # 130 res_0_D
	(  OP_NONE  , "res 0,e"    ), # 131 res_0_E
	(  OP_NONE  , "res 0,h"    ), # 132 res_0_H
	(  OP_NONE  , "res 0,l"    ), # 133 res_0_L
	(  OP_NONE  , "res 0,(hl)" ), # 134 res_0_off_hl
	(  OP_NONE  , "res 0,a"    ), # 135 res_0_A
	(  OP_NONE  , "res 1,b"    ), # 136 res_1_B
	(  OP_NONE  , "res 1,c"    ), # 137 res_1_C
	(  OP_NONE  , "res 1,d"    ), # 138 res_1_D
	(  OP_NONE  , "res 1,e"    ), # 139 res_1_E
	(  OP_NONE  , "res 1,h"    ), # 140 res_1_H
	(  OP_NONE  , "res 1,l"    ), # 141 res_1_L
	(  OP_NONE  , "res 1,(hl)" ), # 142 res_1_off_hl
	(  OP_NONE  , "res 1,a"    ), # 143 res_1_A
	(  OP_NONE  , "res 2,b"    ), # 144 res_2_B
	(  OP_NONE  , "res 2,c"    ), # 145 res_2_C
	(  OP_NONE  , "res 2,d"    ), # 146 res_2_D
	(  OP_NONE  , "res 2,e"    ), # 147 res_2_E
	(  OP_NONE  , "res 2,h"    ), # 148 res_2_H
	(  OP_NONE  , "res 2,l"    ), # 149 res_2_L
	(  OP_NONE  , "res 2,(hl)" ), # 150 res_2_off_hl
	(  OP_NONE  , "res 2,a"    ), # 151 res_2_A
	(  OP_NONE  , "res 3,b"    ), # 152 res_3_B
	(  OP_NONE  , "res 3,c"    ), # 153 res_3_C
	(  OP_NONE  , "res 3,d"    ), # 154 res_3_D
	(  OP_NONE  , "res 3,e"    ), # 155 res_3_E
	(  OP_NONE  , "res 3,h"    ), # 156 res_3_H
	(  OP_NONE  , "res 3,l"    ), # 157 res_3_L
	(  OP_NONE  , "res 3,(hl)" ), # 158 res_3_off_hl
	(  OP_NONE  , "res 3,a"    ), # 159 res_3_A
	(  OP_NONE  , "res 4,b"    ), # 160 res_4_B
	(  OP_NONE  , "res 4,c"    ), # 161 res_4_C
	(  OP_NONE  , "res 4,d"    ), # 162 res_4_D
	(  OP_NONE  , "res 4,e"    ), # 163 res_4_E
	(  OP_NONE  , "res 4,h"    ), # 164 res_4_H
	(  OP_NONE  , "res 4,l"    ), # 165 res_4_L
	(  OP_NONE  , "res 4,(hl)" ), # 166 res_4_off_hl
	(  OP_NONE  , "res 4,a"    ), # 167 res_4_A
	(  OP_NONE  , "res 5,b"    ), # 168 res_5_B
	(  OP_NONE  , "res 5,c"    ), # 169 res_5_C
	(  OP_NONE  , "res 5,d"    ), # 170 res_5_D
	(  OP_NONE  , "res 5,e"    ), # 171 res_5_E
	(  OP_NONE  , "res 5,h"    ), # 172 res_5_H
	(  OP_NONE  , "res 5,l"    ), # 173 res_5_L
	(  OP_NONE  , "res 5,(hl)" ), # 174 res_5_off_hl
	(  OP_NONE  , "res 5,a"    ), # 175 res_5_A
	(  OP_NONE  , "res 6,b"    ), # 176 res_6_B
	(  OP_NONE  , "res 6,c"    ), # 177 res_6_C
	(  OP_NONE  , "res 6,d"    ), # 178 res_6_D
	(  OP_NONE  , "res 6,e"    ), # 179 res_6_E
	(  OP_NONE  , "res 6,h"    ), # 180 res_6_H
	(  OP_NONE  , "res 6,l"    ), # 181 res_6_L
	(  OP_NONE  , "res 6,(hl)" ), # 182 res_6_off_hl
	(  OP_NONE  , "res 6,a"    ), # 183 res_6_A
	(  OP_NONE  , "res 7,b"    ), # 184 res_7_B
	(  OP_NONE  , "res 7,c"    ), # 185 res_7_C
	(  OP_NONE  , "res 7,d"    ), # 186 res_7_D
	(  OP_NONE  , "res 7,e"    ), # 187 res_7_E
	(  OP_NONE  , "res 7,h"    ), # 188 res_7_H
	(  OP_NONE  , "res 7,l"    ), # 189 res_7_L
	(  OP_NONE  , "res 7,(hl)" ), # 190 res_7_off_hl
	(  OP_NONE  , "res 7,a"    ), # 191 res_7_A
	(  OP_NONE  , "set 0,b"    ), # 192 SET_0_B
	(  OP_NONE  , "set 0,c"    ), # 193 SET_0_C
	(  OP_NONE  , "set 0,d"    ), # 194 SET_0_D
	(  OP_NONE  , "set 0,e"    ), # 195 SET_0_E
	(  OP_NONE  , "set 0,h"    ), # 196 SET_0_H
	(  OP_NONE  , "set 0,l"    ), # 197 SET_0_L
	(  OP_NONE  , "set 0,(hl)" ), # 198 SET_0_off_hl
	(  OP_NONE  , "set 0,a"    ), # 199 SET_0_A
	(  OP_NONE  , "set 1,b"    ), # 200 SET_1_B
	(  OP_NONE  , "set 1,c"    ), # 201 SET_1_C
	(  OP_NONE  , "set 1,d"    ), # 202 SET_1_D
	(  OP_NONE  , "set 1,e"    ), # 203 SET_1_E
	(  OP_NONE  , "set 1,h"    ), # 204 SET_1_H
	(  OP_NONE  , "set 1,l"    ), # 205 SET_1_L
	(  OP_NONE  , "set 1,(hl)" ), # 206 SET_1_off_hl
	(  OP_NONE  , "set 1,a"    ), # 207 SET_1_A
	(  OP_NONE  , "set 2,b"    ), # 208 SET_2_B
	(  OP_NONE  , "set 2,c"    ), # 209 SET_2_C
	(  OP_NONE  , "set 2,d"    ), # 210 SET_2_D
	(  OP_NONE  , "set 2,e"    ), # 211 SET_2_E
	(  OP_NONE  , "set 2,h"    ), # 212 SET_2_H
	(  OP_NONE  , "set 2,l"    ), # 213 SET_2_L
	(  OP_NONE  , "set 2,(hl)" ), # 214 SET_2_off_hl
	(  OP_NONE  , "set 2,a"    ), # 215 SET_2_A
	(  OP_NONE  , "set 3,b"    ), # 216 SET_3_B
	(  OP_NONE  , "set 3,c"    ), # 217 SET_3_C
	(  OP_NONE  , "set 3,d"    ), # 218 SET_3_D
	(  OP_NONE  , "set 3,e"    ), # 219 SET_3_E
	(  OP_NONE  , "set 3,h"    ), # 220 SET_3_H
	(  OP_NONE  , "set 3,l"    ), # 221 SET_3_L
	(  OP_NONE  , "set 3,(hl)" ), # 222 SET_3_off_hl
	(  OP_NONE  , "set 3,a"    ), # 223 SET_3_A
	(  OP_NONE  , "set 4,b"    ), # 224 SET_4_B
	(  OP_NONE  , "set 4,c"    ), # 225 SET_4_C
	(  OP_NONE  , "set 4,d"    ), # 226 SET_4_D
	(  OP_NONE  , "set 4,e"    ), # 227 SET_4_E
	(  OP_NONE  , "set 4,h"    ), # 228 SET_4_H
	(  OP_NONE  , "set 4,l"    ), # 229 SET_4_L
	(  OP_NONE  , "set 4,(hl)" ), # 230 SET_4_off_hl
	(  OP_NONE  , "set 4,a"    ), # 231 SET_4_A
	(  OP_NONE  , "set 5,b"    ), # 232 SET_5_B
	(  OP_NONE  , "set 5,c"    ), # 233 SET_5_C
	(  OP_NONE  , "set 5,d"    ), # 234 SET_5_D
	(  OP_NONE  , "set 5,e"    ), # 235 SET_5_E
	(  OP_NONE  , "set 5,h"    ), # 236 SET_5_H
	(  OP_NONE  , "set 5,l"    ), # 237 SET_5_L
	(  OP_NONE  , "set 5,(hl)" ), # 238 SET_5_off_hl
	(  OP_NONE  , "set 5,a"    ), # 239 SET_5_A
	(  OP_NONE  , "set 6,b"    ), # 240 SET_6_B
	(  OP_NONE  , "set 6,c"    ), # 241 SET_6_C
	(  OP_NONE  , "set 6,d"    ), # 242 SET_6_D
	(  OP_NONE  , "set 6,e"    ), # 243 SET_6_E
	(  OP_NONE  , "set 6,h"    ), # 244 SET_6_H
	(  OP_NONE  , "set 6,l"    ), # 245 SET_6_L
	(  OP_NONE  , "set 6,(hl)" ), # 246 SET_6_off_hl
	(  OP_NONE  , "set 6,a"    ), # 247 SET_6_A
	(  OP_NONE  , "set 7,b"    ), # 248 SET_7_B
	(  OP_NONE  , "set 7,c"    ), # 249 SET_7_C
	(  OP_NONE  , "set 7,d"    ), # 250 SET_7_D
	(  OP_NONE  , "set 7,e"    ), # 251 SET_7_E
	(  OP_NONE  , "set 7,h"    ), # 252 SET_7_H
	(  OP_NONE  , "set 7,l"    ), # 253 SET_7_L
	(  OP_NONE  , "set 7,(hl)" ), # 254 SET_7_off_hl
	(  OP_NONE  , "set 7,a"    )  # 255 SET_7_A
)

opcodes_DD = (
	(  OP_NONE  , NULL         ), #   0 NULL
	(  OP_NONE  , NULL         ), #   1 NULL
	(  OP_NONE  , NULL         ), #   2 NULL
	(  OP_NONE  , NULL         ), #   3 NULL
	(  OP_NONE  , NULL         ), #   4 NULL
	(  OP_NONE  , NULL         ), #   5 NULL
	(  OP_NONE  , NULL         ), #   6 NULL
	(  OP_NONE  , NULL         ), #   7 NULL
	(  OP_NONE  , NULL         ), #   8 NULL
	(  OP_NONE  , "add ix,bc"  ), #   9 add_ix_bc
	(  OP_NONE  , NULL         ), #  10 NULL
	(  OP_NONE  , NULL         ), #  11 NULL
	(  OP_NONE  , NULL         ), #  12 NULL
	(  OP_NONE  , NULL         ), #  13 NULL
	(  OP_NONE  , NULL         ), #  14 NULL
	(  OP_NONE  , NULL         ), #  15 NULL
	(  OP_NONE  , NULL         ), #  16 NULL
	(  OP_NONE  , NULL         ), #  17 NULL
	(  OP_NONE  , NULL         ), #  18 NULL
	(  OP_NONE  , NULL         ), #  19 NULL
	(  OP_NONE  , NULL         ), #  20 NULL
	(  OP_NONE  , NULL         ), #  21 NULL
	(  OP_NONE  , NULL         ), #  22 NULL
	(  OP_NONE  , NULL         ), #  23 NULL
	(  OP_NONE  , NULL         ), #  24 NULL
	(  OP_NONE  , "add ix,de"  ), #  25 add_ix_de
	(  OP_NONE  , NULL         ), #  26 NULL
	(  OP_NONE  , NULL         ), #  27 NULL
	(  OP_NONE  , NULL         ), #  28 NULL
	(  OP_NONE  , NULL         ), #  29 NULL
	(  OP_NONE  , NULL         ), #  30 NULL
	(  OP_NONE  , NULL         ), #  31 NULL
	(  OP_NONE  , NULL         ), #  32 NULL
	(  OP_WORD  , "ld ix,%s"   ), #  33 ld_ix_nn
	(  OP_WORD  , "ld (%s),ix" ), #  34 ld_off_nn_ix
	(  OP_NONE  , "inc ix"     ), #  35 inc_ix
	(  OP_NONE  , "inc ixh"    ), #  36 inc_ixh
	(  OP_NONE  , "dec ixh"    ), #  37 dec_ixh
	(  OP_BYTE  , "ld ixh,%s"  ), #  38 ld_ixh_n
	(  OP_NONE  , NULL         ), #  39 NULL
	(  OP_NONE  , NULL         ), #  40 NULL
	(  OP_NONE  , "add ix,ix"  ), #  41 add_ix_ix
	(  OP_WORD  , "ld ix,(%s)" ), #  42 ld_ix_off_nn
	(  OP_NONE  , "dec ix"     ), #  43 dec_ix
	(  OP_NONE  , "inc ixl"    ), #  44 inc_ixl
	(  OP_NONE  , "dec ixl"    ), #  45 dec_ixl
	(  OP_BYTE  , "ld ixl,%s"  ), #  46 ld_ixl_n
	(  OP_NONE  , NULL         ), #  47 NULL
	(  OP_NONE  , NULL         ), #  48 NULL
	(  OP_NONE  , NULL         ), #  49 NULL
	(  OP_NONE  , NULL         ), #  50 NULL
	(  OP_NONE  , NULL         ), #  51 NULL
	(  OP_BYTE_OFF, "inc (ix%s)"), #  52 inc_off_ix_d
	(  OP_BYTE_OFF, "dec (ix%s)"), #  53 dec_off_ix_d
	(  OP_BYTE_OFF_2, "ld (ix%s),%s"), #  54 ld_off_ix_d_n
	(  OP_NONE  , NULL         ), #  55 NULL
	(  OP_NONE  , NULL         ), #  56 NULL
	(  OP_NONE  , "add ix,sp"  ), #  57 add_ix_sp
	(  OP_NONE  , NULL         ), #  58 NULL
	(  OP_NONE  , NULL         ), #  59 NULL
	(  OP_NONE  , NULL         ), #  60 NULL
	(  OP_NONE  , NULL         ), #  61 NULL
	(  OP_NONE  , NULL         ), #  62 NULL
	(  OP_NONE  , NULL         ), #  63 NULL
	(  OP_NONE  , NULL         ), #  64 NULL
	(  OP_NONE  , NULL         ), #  65 NULL
	(  OP_NONE  , NULL         ), #  66 NULL
	(  OP_NONE  , NULL         ), #  67 NULL
	(  OP_NONE  , "ld b,ixh"   ), #  68 ld_B_ixh
	(  OP_NONE  , "ld b,ixl"   ), #  69 ld_B_ixl
	(  OP_BYTE_OFF  , "ld b,(ix%s)"), #  70 ld_B_off_ix_d
	(  OP_NONE  , NULL         ), #  71 NULL
	(  OP_NONE  , NULL         ), #  72 NULL
	(  OP_NONE  , NULL         ), #  73 NULL
	(  OP_NONE  , NULL         ), #  74 NULL
	(  OP_NONE  , NULL         ), #  75 NULL
	(  OP_NONE  , "ld c,ixh"   ), #  76 ld_C_ixh
	(  OP_NONE  , "ld c,ixl"   ), #  77 ld_C_ixl
	(  OP_BYTE_OFF, "ld c,(ix%s)"), #  78 ld_C_off_ix_d
	(  OP_NONE  , NULL         ), #  79 NULL
	(  OP_NONE  , NULL         ), #  80 NULL
	(  OP_NONE  , NULL         ), #  81 NULL
	(  OP_NONE  , NULL         ), #  82 NULL
	(  OP_NONE  , NULL         ), #  83 NULL
	(  OP_NONE  , "ld d,ixh"   ), #  84 ld_D_ixh
	(  OP_NONE  , "ld d,ixl"   ), #  85 ld_D_ixl
	(  OP_BYTE_OFF, "ld d,(ix%s)"), #  86 ld_D_off_ix_d
	(  OP_NONE  , NULL         ), #  87 NULL
	(  OP_NONE  , NULL         ), #  88 NULL
	(  OP_NONE  , NULL         ), #  89 NULL
	(  OP_NONE  , NULL         ), #  90 NULL
	(  OP_NONE  , NULL         ), #  91 NULL
	(  OP_NONE  , "ld e,ixh"   ), #  92 ld_E_ixh
	(  OP_NONE  , "ld e,ixl"   ), #  93 ld_E_ixl
	(  OP_BYTE_OFF, "ld e,(ix%s)"), #  94 ld_E_off_ix_d
	(  OP_NONE  , NULL         ), #  95 NULL
	(  OP_NONE  , "ld ixh,b"   ), #  96 ld_ixh_B
	(  OP_NONE  , "ld ixh,c"   ), #  97 ld_ixh_C
	(  OP_NONE  , "ld ixh,d"   ), #  98 ld_ixh_D
	(  OP_NONE  , "ld ixh,e"   ), #  99 ld_ixh_E
	(  OP_NONE  , "ld ixh,ixh" ), # 100 ld_ixh_ixh
	(  OP_NONE  , "ld ixh,ixl" ), # 101 ld_ixh_ixl
	(  OP_BYTE_OFF,"ld h,(ix%s)"), # 102 ld_H_off_ix_d
	(  OP_NONE  , "ld ixh,a"   ), # 103 ld_ixh_A
	(  OP_NONE  , "ld ixl,b"   ), # 104 ld_ixl_B
	(  OP_NONE  , "ld ixl,c"   ), # 105 ld_ixl_C
	(  OP_NONE  , "ld ixl,d"   ), # 106 ld_ixl_D
	(  OP_NONE  , "ld ixl,e"   ), # 107 ld_ixl_E
	(  OP_NONE  , "ld ixl,ixh" ), # 108 ld_ixl_ixh
	(  OP_NONE  , "ld ixl,ixl" ), # 109 ld_ixl_ixl
	(  OP_BYTE_OFF, "ld l,(ix%s)"), # 110 ld_L_off_ix_d
	(  OP_NONE  , "ld ixl,a"   ), # 111 ld_ixl_A
	(  OP_BYTE_OFF, "ld (ix%s),b"), # 112 ld_off_ix_d_B
	(  OP_BYTE_OFF, "ld (ix%s),c"), # 113 ld_off_ix_d_C
	(  OP_BYTE_OFF, "ld (ix%s),d"), # 114 ld_off_ix_d_D
	(  OP_BYTE_OFF, "ld (ix%s),e"), # 115 ld_off_ix_d_E
	(  OP_BYTE_OFF, "ld (ix%s),h"), # 116 ld_off_ix_d_H
	(  OP_BYTE_OFF, "ld (ix%s),l"), # 117 ld_off_ix_d_L
	(  OP_NONE  , NULL         ), # 118 NULL
	(  OP_BYTE_OFF, "ld (ix%s),a"), # 119 ld_off_ix_d_A
	(  OP_NONE  , NULL         ), # 120 NULL
	(  OP_NONE  , NULL         ), # 121 NULL
	(  OP_NONE  , NULL         ), # 122 NULL
	(  OP_NONE  , NULL         ), # 123 NULL
	(  OP_NONE  , "ld a,ixh"   ), # 124 ld_A_ixh
	(  OP_NONE  , "ld a,ixl"   ), # 125 ld_A_ixl
	(  OP_BYTE_OFF, "ld a,(ix%s)"), # 126 ld_A_off_ix_d
	(  OP_NONE  , NULL         ), # 127 NULL
	(  OP_NONE  , NULL         ), # 128 NULL
	(  OP_NONE  , NULL         ), # 129 NULL
	(  OP_NONE  , NULL         ), # 130 NULL
	(  OP_NONE  , NULL         ), # 131 NULL
	(  OP_NONE  , "add a,ixh"  ), # 132 add_A_ixh
	(  OP_NONE  , "add a,ixl"  ), # 133 add_A_ixl
	(  OP_BYTE_OFF, "add a,(ix%s)"), # 134 add_A_off_ix_d
	(  OP_NONE  , NULL         ), # 135 NULL
	(  OP_NONE  , NULL         ), # 136 NULL
	(  OP_NONE  , NULL         ), # 137 NULL
	(  OP_NONE  , NULL         ), # 138 NULL
	(  OP_NONE  , NULL         ), # 139 NULL
	(  OP_NONE  , "adc a,ixh"  ), # 140 adc_A_ixh
	(  OP_NONE  , "adc a,ixl"  ), # 141 adc_A_ixl
	(  OP_BYTE_OFF, "adc a,(ix%s)"), # 142 adc_A_off_ix_d
	(  OP_NONE  , NULL         ), # 143 NULL
	(  OP_NONE  , NULL         ), # 144 NULL
	(  OP_NONE  , NULL         ), # 145 NULL
	(  OP_NONE  , NULL         ), # 146 NULL
	(  OP_NONE  , NULL         ), # 147 NULL
	(  OP_NONE  , "sub a,ixh"  ), # 148 sub_A_ixh
	(  OP_NONE  , "sub a,ixl"  ), # 149 sub_A_ixl
	(  OP_BYTE_OFF, "sub a,(ix%s)"), # 150 sub_A_off_ix_d
	(  OP_NONE  , NULL         ), # 151 NULL
	(  OP_NONE  , NULL         ), # 152 NULL
	(  OP_NONE  , NULL         ), # 153 NULL
	(  OP_NONE  , NULL         ), # 154 NULL
	(  OP_NONE  , NULL         ), # 155 NULL
	(  OP_NONE  , "sbc a,ixh"  ), # 156 sbc_A_ixh
	(  OP_NONE  , "sbc a,ixl"  ), # 157 sbc_A_ixl
	(  OP_BYTE_OFF, "sbc a,(ix%s)"), # 158 sbc_A_off_ix_d
	(  OP_NONE  , NULL         ), # 159 NULL
	(  OP_NONE  , NULL         ), # 160 NULL
	(  OP_NONE  , NULL         ), # 161 NULL
	(  OP_NONE  , NULL         ), # 162 NULL
	(  OP_NONE  , NULL         ), # 163 NULL
	(  OP_NONE  , "and ixh"    ), # 164 and_ixh
	(  OP_NONE  , "and ixl"    ), # 165 and_ixl
	(  OP_BYTE_OFF, "and (ix%s)"), # 166 and_off_ix_d
	(  OP_NONE  , NULL         ), # 167 NULL
	(  OP_NONE  , NULL         ), # 168 NULL
	(  OP_NONE  , NULL         ), # 169 NULL
	(  OP_NONE  , NULL         ), # 170 NULL
	(  OP_NONE  , NULL         ), # 171 NULL
	(  OP_NONE  , "xor ixh"    ), # 172 xor_ixh
	(  OP_NONE  , "xor ixl"    ), # 173 xor_ixl
	(  OP_BYTE_OFF, "xor (ix%s)"), # 174 xor_off_ix_d
	(  OP_NONE  , NULL         ), # 175 NULL
	(  OP_NONE  , NULL         ), # 176 NULL
	(  OP_NONE  , NULL         ), # 177 NULL
	(  OP_NONE  , NULL         ), # 178 NULL
	(  OP_NONE  , NULL         ), # 179 NULL
	(  OP_NONE  , "or ixh"     ), # 180 OR_ixh
	(  OP_NONE  , "or ixl"     ), # 181 OR_ixl
	(  OP_BYTE_OFF, "or (ix%s)" ), # 182 OR_off_ix_d
	(  OP_NONE  , NULL         ), # 183 NULL
	(  OP_NONE  , NULL         ), # 184 NULL
	(  OP_NONE  , NULL         ), # 185 NULL
	(  OP_NONE  , NULL         ), # 186 NULL
	(  OP_NONE  , NULL         ), # 187 NULL
	(  OP_NONE  , "cp ixh"     ), # 188 cP_ixh
	(  OP_NONE  , "cp ixl"     ), # 189 cP_ixl
	(  OP_BYTE_OFF, "cp (ix%s)" ), # 190 cP_off_ix_d
	(  OP_NONE  , NULL         ), # 191 NULL
	(  OP_NONE  , NULL         ), # 192 NULL
	(  OP_NONE  , NULL         ), # 193 NULL
	(  OP_NONE  , NULL         ), # 194 NULL
	(  OP_NONE  , NULL         ), # 195 NULL
	(  OP_NONE  , NULL         ), # 196 NULL
	(  OP_NONE  , NULL         ), # 197 NULL
	(  OP_NONE  , NULL         ), # 198 NULL
	(  OP_NONE  , NULL         ), # 199 NULL
	(  OP_NONE  , NULL         ), # 200 NULL
	(  OP_NONE  , NULL         ), # 201 NULL
	(  OP_NONE  , NULL         ), # 202 NULL
	(  OP_DDCB  , NULL         ), # 203 NULL
	(  OP_NONE  , NULL         ), # 204 NULL
	(  OP_NONE  , NULL         ), # 205 NULL
	(  OP_NONE  , NULL         ), # 206 NULL
	(  OP_NONE  , NULL         ), # 207 NULL
	(  OP_NONE  , NULL         ), # 208 NULL
	(  OP_NONE  , NULL         ), # 209 NULL
	(  OP_NONE  , NULL         ), # 210 NULL
	(  OP_NONE  , NULL         ), # 211 NULL
	(  OP_NONE  , NULL         ), # 212 NULL
	(  OP_NONE  , NULL         ), # 213 NULL
	(  OP_NONE  , NULL         ), # 214 NULL
	(  OP_NONE  , NULL         ), # 215 NULL
	(  OP_NONE  , NULL         ), # 216 NULL
	(  OP_NONE  , NULL         ), # 217 NULL
	(  OP_NONE  , NULL         ), # 218 NULL
	(  OP_NONE  , NULL         ), # 219 NULL
	(  OP_NONE  , NULL         ), # 220 NULL
	(  OP_DD    , NULL         ), # 221 NULL
	(  OP_NONE  , NULL         ), # 222 NULL
	(  OP_NONE  , NULL         ), # 223 NULL
	(  OP_NONE  , NULL         ), # 224 NULL
	(  OP_NONE  , "pop ix"     ), # 225 pop_ix
	(  OP_NONE  , NULL         ), # 226 NULL
	(  OP_NONE  , "ex (sp),ix" ), # 227 EX_off_sp_ix
	(  OP_NONE  , NULL         ), # 228 NULL
	(  OP_NONE  , "push ix"    ), # 229 push_ix
	(  OP_NONE  , NULL         ), # 230 NULL
	(  OP_NONE  , NULL         ), # 231 NULL
	(  OP_NONE  , NULL         ), # 232 NULL
	(  OP_NONE  , "jp (ix)"    ), # 233 jp_off_ix
	(  OP_NONE  , NULL         ), # 234 NULL
	(  OP_NONE  , NULL         ), # 235 NULL
	(  OP_NONE  , NULL         ), # 236 NULL
	(  OP_NONE  , NULL         ), # 237 NULL
	(  OP_NONE  , NULL         ), # 238 NULL
	(  OP_NONE  , NULL         ), # 239 NULL
	(  OP_NONE  , NULL         ), # 240 NULL
	(  OP_NONE  , NULL         ), # 241 NULL
	(  OP_NONE  , NULL         ), # 242 NULL
	(  OP_NONE  , NULL         ), # 243 NULL
	(  OP_NONE  , NULL         ), # 244 NULL
	(  OP_NONE  , NULL         ), # 245 NULL
	(  OP_NONE  , NULL         ), # 246 NULL
	(  OP_NONE  , NULL         ), # 247 NULL
	(  OP_NONE  , NULL         ), # 248 NULL
	(  OP_NONE  , "ld sp,ix"   ), # 249 ld_sp_ix
	(  OP_NONE  , NULL         ), # 250 NULL
	(  OP_NONE  , NULL         ), # 251 NULL
	(  OP_NONE  , NULL         ), # 252 NULL
	(  OP_NONE  , NULL         ), # 253 NULL
	(  OP_NONE  , NULL         ), # 254 NULL
	(  OP_NONE  , NULL         ), # 255 NULL
)

opcodes_DDCB = (
	(  OP_BYTE_OFF_3  , "ld b,rlc (ix%s)"), #   0 ld_B_rlc_off_ix_d
	(  OP_BYTE_OFF_3  , "ld c,rlc (ix%s)"), #   1 ld_C_rlc_off_ix_d
	(  OP_BYTE_OFF_3  , "ld d,rlc (ix%s)"), #   2 ld_D_rlc_off_ix_d
	(  OP_BYTE_OFF_3  , "ld e,rlc (ix%s)"), #   3 ld_E_rlc_off_ix_d
	(  OP_BYTE_OFF_3  , "ld h,rlc (ix%s)"), #   4 ld_H_rlc_off_ix_d
	(  OP_BYTE_OFF_3  , "ld l,rlc (ix%s)"), #   5 ld_L_rlc_off_ix_d
	(  OP_BYTE_OFF_3  , "rlc (ix%s)"     ), #   6 rlc_off_ix_d
	(  OP_BYTE_OFF_3  , "ld a,rlc (ix%s)"), #   7 ld_A_rlc_off_ix_d
	(  OP_BYTE_OFF_3  , "ld b,rrc (ix%s)"), #   8 ld_B_rrc_off_ix_d
	(  OP_BYTE_OFF_3  , "ld c,rrc (ix%s)"), #   9 ld_C_rrc_off_ix_d
	(  OP_BYTE_OFF_3  , "ld d,rrc (ix%s)"), #  10 ld_D_rrc_off_ix_d
	(  OP_BYTE_OFF_3  , "ld e,rrc (ix%s)"), #  11 ld_E_rrc_off_ix_d
	(  OP_BYTE_OFF_3  , "ld h,rrc (ix%s)"), #  12 ld_H_rrc_off_ix_d
	(  OP_BYTE_OFF_3  , "ld l,rrc (ix%s)"), #  13 ld_L_rrc_off_ix_d
	(  OP_BYTE_OFF_3  , "rrc (ix%s)"     ), #  14 rrc_off_ix_d
	(  OP_BYTE_OFF_3  , "ld a,rrc (ix%s)"), #  15 ld_A_rrc_off_ix_d
	(  OP_BYTE_OFF_3  , "ld b,rl (ix%s)"), #  16 ld_B_rl_off_ix_d
	(  OP_BYTE_OFF_3  , "ld c,rl (ix%s)"), #  17 ld_C_rl_off_ix_d
	(  OP_BYTE_OFF_3  , "ld d,rl (ix%s)"), #  18 ld_D_rl_off_ix_d
	(  OP_BYTE_OFF_3  , "ld e,rl (ix%s)"), #  19 ld_E_rl_off_ix_d
	(  OP_BYTE_OFF_3  , "ld h,rl (ix%s)"), #  20 ld_H_rl_off_ix_d
	(  OP_BYTE_OFF_3  , "ld l,rl (ix%s)"), #  21 ld_L_rl_off_ix_d
	(  OP_BYTE_OFF_3  , "rl (ix%s)"     ), #  22 rl_off_ix_d
	(  OP_BYTE_OFF_3  , "ld a,rl (ix%s)"), #  23 ld_A_rl_off_ix_d
	(  OP_BYTE_OFF_3  , "ld b,rr (ix%s)"), #  24 ld_B_rr_off_ix_d
	(  OP_BYTE_OFF_3  , "ld c,rr (ix%s)"), #  25 ld_C_rr_off_ix_d
	(  OP_BYTE_OFF_3  , "ld d,rr (ix%s)"), #  26 ld_D_rr_off_ix_d
	(  OP_BYTE_OFF_3  , "ld e,rr (ix%s)"), #  27 ld_E_rr_off_ix_d
	(  OP_BYTE_OFF_3  , "ld h,rr (ix%s)"), #  28 ld_H_rr_off_ix_d
	(  OP_BYTE_OFF_3  , "ld l,rr (ix%s)"), #  29 ld_L_rr_off_ix_d
	(  OP_BYTE_OFF_3  , "rr (ix%s)"     ), #  30 rr_off_ix_d
	(  OP_BYTE_OFF_3  , "ld a,rr (ix%s)"), #  31 ld_A_rr_off_ix_d
	(  OP_BYTE_OFF_3  , "ld b,sla (ix%s)"), #  32 ld_B_sla_off_ix_d
	(  OP_BYTE_OFF_3  , "ld c,sla (ix%s)"), #  33 ld_C_sla_off_ix_d
	(  OP_BYTE_OFF_3  , "ld d,sla (ix%s)"), #  34 ld_D_sla_off_ix_d
	(  OP_BYTE_OFF_3  , "ld e,sla (ix%s)"), #  35 ld_E_sla_off_ix_d
	(  OP_BYTE_OFF_3  , "ld h,sla (ix%s)"), #  36 ld_H_sla_off_ix_d
	(  OP_BYTE_OFF_3  , "ld l,sla (ix%s)"), #  37 ld_L_sla_off_ix_d
	(  OP_BYTE_OFF_3  , "sla (ix%s)"   ), #  38 sla_off_ix_d
	(  OP_BYTE_OFF_3  , "ld a,sla (ix%s)"), #  39 ld_A_sla_off_ix_d
	(  OP_BYTE_OFF_3  , "ld b,sra (ix%s)"), #  40 ld_B_sra_off_ix_d
	(  OP_BYTE_OFF_3  , "ld c,sra (ix%s)"), #  41 ld_C_sra_off_ix_d
	(  OP_BYTE_OFF_3  , "ld d,sra (ix%s)"), #  42 ld_D_sra_off_ix_d
	(  OP_BYTE_OFF_3  , "ld e,sra (ix%s)"), #  43 ld_E_sra_off_ix_d
	(  OP_BYTE_OFF_3  , "ld h,sra (ix%s)"), #  44 ld_H_sra_off_ix_d
	(  OP_BYTE_OFF_3  , "ld l,sra (ix%s)"), #  45 ld_L_sra_off_ix_d
	(  OP_BYTE_OFF_3  , "sra (ix%s)"   ), #  46 sra_off_ix_d
	(  OP_BYTE_OFF_3  , "ld a,sra (ix%s)"), #  47 ld_A_sra_off_ix_d
	(  OP_BYTE_OFF_3  , "ld b,sll (ix%s)"), #  48 ld_B_sll_off_ix_d
	(  OP_BYTE_OFF_3  , "ld c,sll (ix%s)"), #  49 ld_C_sll_off_ix_d
	(  OP_BYTE_OFF_3  , "ld d,sll (ix%s)"), #  50 ld_D_sll_off_ix_d
	(  OP_BYTE_OFF_3  , "ld e,sll (ix%s)"), #  51 ld_E_sll_off_ix_d
	(  OP_BYTE_OFF_3  , "ld h,sll (ix%s)"), #  52 ld_H_sll_off_ix_d
	(  OP_BYTE_OFF_3  , "ld l,sll (ix%s)"), #  53 ld_L_sll_off_ix_d
	(  OP_BYTE_OFF_3  , "sll (ix%s)"   ), #  54 sll_off_ix_d
	(  OP_BYTE_OFF_3  , "ld a,sll (ix%s)"), #  55 ld_A_sll_off_ix_d
	(  OP_BYTE_OFF_3  , "ld b,srl (ix%s)"), #  56 ld_B_srl_off_ix_d
	(  OP_BYTE_OFF_3  , "ld c,srl (ix%s)"), #  57 ld_C_srl_off_ix_d
	(  OP_BYTE_OFF_3  , "ld d,srl (ix%s)"), #  58 ld_D_srl_off_ix_d
	(  OP_BYTE_OFF_3  , "ld e,srl (ix%s)"), #  59 ld_E_srl_off_ix_d
	(  OP_BYTE_OFF_3  , "ld h,srl (ix%s)"), #  60 ld_H_srl_off_ix_d
	(  OP_BYTE_OFF_3  , "ld l,srl (ix%s)"), #  61 ld_L_srl_off_ix_d
	(  OP_BYTE_OFF_3  , "srl (ix%s)"   ), #  62 srl_off_ix_d
	(  OP_BYTE_OFF_3  , "ld a,srl (ix%s)"), #  63 ld_A_srl_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 0,(ix%s)" ), #  64 bit_0_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 0,(ix%s)" ), #  65 bit_0_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 0,(ix%s)" ), #  66 bit_0_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 0,(ix%s)" ), #  67 bit_0_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 0,(ix%s)" ), #  68 bit_0_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 0,(ix%s)" ), #  69 bit_0_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 0,(ix%s)" ), #  70 bit_0_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 0,(ix%s)" ), #  71 bit_0_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 1,(ix%s)" ), #  72 bit_1_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 1,(ix%s)" ), #  73 bit_1_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 1,(ix%s)" ), #  74 bit_1_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 1,(ix%s)" ), #  75 bit_1_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 1,(ix%s)" ), #  76 bit_1_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 1,(ix%s)" ), #  77 bit_1_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 1,(ix%s)" ), #  78 bit_1_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 1,(ix%s)" ), #  79 bit_1_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 2,(ix%s)" ), #  80 bit_2_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 2,(ix%s)" ), #  81 bit_2_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 2,(ix%s)" ), #  82 bit_2_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 2,(ix%s)" ), #  83 bit_2_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 2,(ix%s)" ), #  84 bit_2_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 2,(ix%s)" ), #  85 bit_2_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 2,(ix%s)" ), #  86 bit_2_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 2,(ix%s)" ), #  87 bit_2_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 3,(ix%s)" ), #  88 bit_3_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 3,(ix%s)" ), #  89 bit_3_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 3,(ix%s)" ), #  90 bit_3_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 3,(ix%s)" ), #  91 bit_3_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 3,(ix%s)" ), #  92 bit_3_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 3,(ix%s)" ), #  93 bit_3_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 3,(ix%s)" ), #  94 bit_3_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 3,(ix%s)" ), #  95 bit_3_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 4,(ix%s)" ), #  96 bit_4_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 4,(ix%s)" ), #  97 bit_4_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 4,(ix%s)" ), #  98 bit_4_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 4,(ix%s)" ), #  99 bit_4_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 4,(ix%s)" ), # 100 bit_4_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 4,(ix%s)" ), # 101 bit_4_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 4,(ix%s)" ), # 102 bit_4_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 4,(ix%s)" ), # 103 bit_4_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 5,(ix%s)" ), # 104 bit_5_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 5,(ix%s)" ), # 105 bit_5_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 5,(ix%s)" ), # 106 bit_5_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 5,(ix%s)" ), # 107 bit_5_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 5,(ix%s)" ), # 108 bit_5_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 5,(ix%s)" ), # 109 bit_5_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 5,(ix%s)" ), # 110 bit_5_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 5,(ix%s)" ), # 111 bit_5_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 6,(ix%s)" ), # 112 bit_6_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 6,(ix%s)" ), # 113 bit_6_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 6,(ix%s)" ), # 114 bit_6_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 6,(ix%s)" ), # 115 bit_6_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 6,(ix%s)" ), # 116 bit_6_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 6,(ix%s)" ), # 117 bit_6_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 6,(ix%s)" ), # 118 bit_6_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 6,(ix%s)" ), # 119 bit_6_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 7,(ix%s)" ), # 120 bit_7_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 7,(ix%s)" ), # 121 bit_7_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 7,(ix%s)" ), # 122 bit_7_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 7,(ix%s)" ), # 123 bit_7_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 7,(ix%s)" ), # 124 bit_7_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 7,(ix%s)" ), # 125 bit_7_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 7,(ix%s)" ), # 126 bit_7_off_ix_d
	(  OP_BYTE_OFF_3  , "bit 7,(ix%s)" ), # 127 bit_7_off_ix_d
	(  OP_BYTE_OFF_3  , "ld b,res 0,(ix%s)"), # 128 ld_B_res_0_off_ix_d
	(  OP_BYTE_OFF_3  , "ld c,res 0,(ix%s)"), # 129 ld_C_res_0_off_ix_d
	(  OP_BYTE_OFF_3  , "ld d,res 0,(ix%s)"), # 130 ld_D_res_0_off_ix_d
	(  OP_BYTE_OFF_3  , "ld e,res 0,(ix%s)"), # 131 ld_E_res_0_off_ix_d
	(  OP_BYTE_OFF_3  , "ld h,res 0,(ix%s)"), # 132 ld_H_res_0_off_ix_d
	(  OP_BYTE_OFF_3  , "ld l,res 0,(ix%s)"), # 133 ld_L_res_0_off_ix_d
	(  OP_BYTE_OFF_3  , "res 0,(ix%s)" ), # 134 res_0_off_ix_d
	(  OP_BYTE_OFF_3  , "ld a,res 0,(ix%s)"), # 135 ld_A_res_0_off_ix_d
	(  OP_BYTE_OFF_3  , "ld b,res 1,(ix%s)"), # 136 ld_B_res_1_off_ix_d
	(  OP_BYTE_OFF_3  , "ld c,res 1,(ix%s)"), # 137 ld_C_res_1_off_ix_d
	(  OP_BYTE_OFF_3  , "ld d,res 1,(ix%s)"), # 138 ld_D_res_1_off_ix_d
	(  OP_BYTE_OFF_3  , "ld e,res 1,(ix%s)"), # 139 ld_E_res_1_off_ix_d
	(  OP_BYTE_OFF_3  , "ld h,res 1,(ix%s)"), # 140 ld_H_res_1_off_ix_d
	(  OP_BYTE_OFF_3  , "ld l,res 1,(ix%s)"), # 141 ld_L_res_1_off_ix_d
	(  OP_BYTE_OFF_3  , "res 1,(ix%s)" ), # 142 res_1_off_ix_d
	(  OP_BYTE_OFF_3  , "ld a,res 1,(ix%s)"), # 143 ld_A_res_1_off_ix_d
	(  OP_BYTE_OFF_3  , "ld b,res 2,(ix%s)"), # 144 ld_B_res_2_off_ix_d
	(  OP_BYTE_OFF_3  , "ld c,res 2,(ix%s)"), # 145 ld_C_res_2_off_ix_d
	(  OP_BYTE_OFF_3  , "ld d,res 2,(ix%s)"), # 146 ld_D_res_2_off_ix_d
	(  OP_BYTE_OFF_3  , "ld e,res 2,(ix%s)"), # 147 ld_E_res_2_off_ix_d
	(  OP_BYTE_OFF_3  , "ld h,res 2,(ix%s)"), # 148 ld_H_res_2_off_ix_d
	(  OP_BYTE_OFF_3  , "ld l,res 2,(ix%s)"), # 149 ld_L_res_2_off_ix_d
	(  OP_BYTE_OFF_3  , "res 2,(ix%s)" ), # 150 res_2_off_ix_d
	(  OP_BYTE_OFF_3  , "ld a,res 2,(ix%s)"), # 151 ld_A_res_2_off_ix_d
	(  OP_BYTE_OFF_3  , "ld b,res 3,(ix%s)"), # 152 ld_B_res_3_off_ix_d
	(  OP_BYTE_OFF_3  , "ld c,res 3,(ix%s)"), # 153 ld_C_res_3_off_ix_d
	(  OP_BYTE_OFF_3  , "ld d,res 3,(ix%s)"), # 154 ld_D_res_3_off_ix_d
	(  OP_BYTE_OFF_3  , "ld e,res 3,(ix%s)"), # 155 ld_E_res_3_off_ix_d
	(  OP_BYTE_OFF_3  , "ld h,res 3,(ix%s)"), # 156 ld_H_res_3_off_ix_d
	(  OP_BYTE_OFF_3  , "ld l,res 3,(ix%s)"), # 157 ld_L_res_3_off_ix_d
	(  OP_BYTE_OFF_3  , "res 3,(ix%s)" ), # 158 res_3_off_ix_d
	(  OP_BYTE_OFF_3  , "ld a,res 3,(ix%s)"), # 159 ld_A_res_3_off_ix_d
	(  OP_BYTE_OFF_3  , "ld b,res 4,(ix%s)"), # 160 ld_B_res_4_off_ix_d
	(  OP_BYTE_OFF_3  , "ld c,res 4,(ix%s)"), # 161 ld_C_res_4_off_ix_d
	(  OP_BYTE_OFF_3  , "ld d,res 4,(ix%s)"), # 162 ld_D_res_4_off_ix_d
	(  OP_BYTE_OFF_3  , "ld e,res 4,(ix%s)"), # 163 ld_E_res_4_off_ix_d
	(  OP_BYTE_OFF_3  , "ld h,res 4,(ix%s)"), # 164 ld_H_res_4_off_ix_d
	(  OP_BYTE_OFF_3  , "ld l,res 4,(ix%s)"), # 165 ld_L_res_4_off_ix_d
	(  OP_BYTE_OFF_3  , "res 4,(ix%s)" ), # 166 res_4_off_ix_d
	(  OP_BYTE_OFF_3  , "ld a,res 4,(ix%s)"), # 167 ld_A_res_4_off_ix_d
	(  OP_BYTE_OFF_3  , "ld b,res 5,(ix%s)"), # 168 ld_B_res_5_off_ix_d
	(  OP_BYTE_OFF_3  , "ld c,res 5,(ix%s)"), # 169 ld_C_res_5_off_ix_d
	(  OP_BYTE_OFF_3  , "ld d,res 5,(ix%s)"), # 170 ld_D_res_5_off_ix_d
	(  OP_BYTE_OFF_3  , "ld e,res 5,(ix%s)"), # 171 ld_E_res_5_off_ix_d
	(  OP_BYTE_OFF_3  , "ld h,res 5,(ix%s)"), # 172 ld_H_res_5_off_ix_d
	(  OP_BYTE_OFF_3  , "ld l,res 5,(ix%s)"), # 173 ld_L_res_5_off_ix_d
	(  OP_BYTE_OFF_3  , "res 5,(ix%s)" ), # 174 res_5_off_ix_d
	(  OP_BYTE_OFF_3  , "ld a,res 5,(ix%s)"), # 175 ld_A_res_5_off_ix_d
	(  OP_BYTE_OFF_3  , "ld b,res 6,(ix%s)"), # 176 ld_B_res_6_off_ix_d
	(  OP_BYTE_OFF_3  , "ld c,res 6,(ix%s)"), # 177 ld_C_res_6_off_ix_d
	(  OP_BYTE_OFF_3  , "ld d,res 6,(ix%s)"), # 178 ld_D_res_6_off_ix_d
	(  OP_BYTE_OFF_3  , "ld e,res 6,(ix%s)"), # 179 ld_E_res_6_off_ix_d
	(  OP_BYTE_OFF_3  , "ld h,res 6,(ix%s)"), # 180 ld_H_res_6_off_ix_d
	(  OP_BYTE_OFF_3  , "ld l,res 6,(ix%s)"), # 181 ld_L_res_6_off_ix_d
	(  OP_BYTE_OFF_3  , "res 6,(ix%s)" ), # 182 res_6_off_ix_d
	(  OP_BYTE_OFF_3  , "ld a,res 6,(ix%s)"), # 183 ld_A_res_6_off_ix_d
	(  OP_BYTE_OFF_3  , "ld b,res 7,(ix%s)"), # 184 ld_B_res_7_off_ix_d
	(  OP_BYTE_OFF_3  , "ld c,res 7,(ix%s)"), # 185 ld_C_res_7_off_ix_d
	(  OP_BYTE_OFF_3  , "ld d,res 7,(ix%s)"), # 186 ld_D_res_7_off_ix_d
	(  OP_BYTE_OFF_3  , "ld e,res 7,(ix%s)"), # 187 ld_E_res_7_off_ix_d
	(  OP_BYTE_OFF_3  , "ld h,res 7,(ix%s)"), # 188 ld_H_res_7_off_ix_d
	(  OP_BYTE_OFF_3  , "ld l,res 7,(ix%s)"), # 189 ld_L_res_7_off_ix_d
	(  OP_BYTE_OFF_3  , "res 7,(ix%s)" ), # 190 res_7_off_ix_d
	(  OP_BYTE_OFF_3  , "ld a,res 7,(ix%s)"), # 191 ld_A_res_7_off_ix_d
	(  OP_BYTE_OFF_3  , "ld b,set 0,(ix%s)"), # 192 ld_B_SET_0_off_ix_d
	(  OP_BYTE_OFF_3  , "ld c,set 0,(ix%s)"), # 193 ld_C_SET_0_off_ix_d
	(  OP_BYTE_OFF_3  , "ld d,set 0,(ix%s)"), # 194 ld_D_SET_0_off_ix_d
	(  OP_BYTE_OFF_3  , "ld e,set 0,(ix%s)"), # 195 ld_E_SET_0_off_ix_d
	(  OP_BYTE_OFF_3  , "ld h,set 0,(ix%s)"), # 196 ld_H_SET_0_off_ix_d
	(  OP_BYTE_OFF_3  , "ld l,set 0,(ix%s)"), # 197 ld_L_SET_0_off_ix_d
	(  OP_BYTE_OFF_3  , "set 0,(ix%s)" ), # 198 SET_0_off_ix_d
	(  OP_BYTE_OFF_3  , "ld a,set 0,(ix%s)"), # 199 ld_A_SET_0_off_ix_d
	(  OP_BYTE_OFF_3  , "ld b,set 1,(ix%s)"), # 200 ld_B_SET_1_off_ix_d
	(  OP_BYTE_OFF_3  , "ld c,set 1,(ix%s)"), # 201 ld_C_SET_1_off_ix_d
	(  OP_BYTE_OFF_3  , "ld d,set 1,(ix%s)"), # 202 ld_D_SET_1_off_ix_d
	(  OP_BYTE_OFF_3  , "ld e,set 1,(ix%s)"), # 203 ld_E_SET_1_off_ix_d
	(  OP_BYTE_OFF_3  , "ld h,set 1,(ix%s)"), # 204 ld_H_SET_1_off_ix_d
	(  OP_BYTE_OFF_3  , "ld l,set 1,(ix%s)"), # 205 ld_L_SET_1_off_ix_d
	(  OP_BYTE_OFF_3  , "set 1,(ix%s)" ), # 206 SET_1_off_ix_d
	(  OP_BYTE_OFF_3  , "ld a,set 1,(ix%s)"), # 207 ld_A_SET_1_off_ix_d
	(  OP_BYTE_OFF_3  , "ld b,set 2,(ix%s)"), # 208 ld_B_SET_2_off_ix_d
	(  OP_BYTE_OFF_3  , "ld c,set 2,(ix%s)"), # 209 ld_C_SET_2_off_ix_d
	(  OP_BYTE_OFF_3  , "ld d,set 2,(ix%s)"), # 210 ld_D_SET_2_off_ix_d
	(  OP_BYTE_OFF_3  , "ld e,set 2,(ix%s)"), # 211 ld_E_SET_2_off_ix_d
	(  OP_BYTE_OFF_3  , "ld h,set 2,(ix%s)"), # 212 ld_H_SET_2_off_ix_d
	(  OP_BYTE_OFF_3  , "ld l,set 2,(ix%s)"), # 213 ld_L_SET_2_off_ix_d
	(  OP_BYTE_OFF_3  , "set 2,(ix%s)" ), # 214 SET_2_off_ix_d
	(  OP_BYTE_OFF_3  , "ld a,set 2,(ix%s)"), # 215 ld_A_SET_2_off_ix_d
	(  OP_BYTE_OFF_3  , "ld b,set 3,(ix%s)"), # 216 ld_B_SET_3_off_ix_d
	(  OP_BYTE_OFF_3  , "ld c,set 3,(ix%s)"), # 217 ld_C_SET_3_off_ix_d
	(  OP_BYTE_OFF_3  , "ld d,set 3,(ix%s)"), # 218 ld_D_SET_3_off_ix_d
	(  OP_BYTE_OFF_3  , "ld e,set 3,(ix%s)"), # 219 ld_E_SET_3_off_ix_d
	(  OP_BYTE_OFF_3  , "ld h,set 3,(ix%s)"), # 220 ld_H_SET_3_off_ix_d
	(  OP_BYTE_OFF_3  , "ld l,set 3,(ix%s)"), # 221 ld_L_SET_3_off_ix_d
	(  OP_BYTE_OFF_3  , "set 3,(ix%s)" ), # 222 SET_3_off_ix_d
	(  OP_BYTE_OFF_3  , "ld a,set 3,(ix%s)"), # 223 ld_A_SET_3_off_ix_d
	(  OP_BYTE_OFF_3  , "ld b,set 4,(ix%s)"), # 224 ld_B_SET_4_off_ix_d
	(  OP_BYTE_OFF_3  , "ld c,set 4,(ix%s)"), # 225 ld_C_SET_4_off_ix_d
	(  OP_BYTE_OFF_3  , "ld d,set 4,(ix%s)"), # 226 ld_D_SET_4_off_ix_d
	(  OP_BYTE_OFF_3  , "ld e,set 4,(ix%s)"), # 227 ld_E_SET_4_off_ix_d
	(  OP_BYTE_OFF_3  , "ld h,set 4,(ix%s)"), # 228 ld_H_SET_4_off_ix_d
	(  OP_BYTE_OFF_3  , "ld l,set 4,(ix%s)"), # 229 ld_L_SET_4_off_ix_d
	(  OP_BYTE_OFF_3  , "set 4,(ix%s)" ), # 230 SET_4_off_ix_d
	(  OP_BYTE_OFF_3  , "ld a,set 4,(ix%s)"), # 231 ld_A_SET_4_off_ix_d
	(  OP_BYTE_OFF_3  , "ld b,set 5,(ix%s)"), # 232 ld_B_SET_5_off_ix_d
	(  OP_BYTE_OFF_3  , "ld c,set 5,(ix%s)"), # 233 ld_C_SET_5_off_ix_d
	(  OP_BYTE_OFF_3  , "ld d,set 5,(ix%s)"), # 234 ld_D_SET_5_off_ix_d
	(  OP_BYTE_OFF_3  , "ld e,set 5,(ix%s)"), # 235 ld_E_SET_5_off_ix_d
	(  OP_BYTE_OFF_3  , "ld h,set 5,(ix%s)"), # 236 ld_H_SET_5_off_ix_d
	(  OP_BYTE_OFF_3  , "ld l,set 5,(ix%s)"), # 237 ld_L_SET_5_off_ix_d
	(  OP_BYTE_OFF_3  , "set 5,(ix%s)" ), # 238 SET_5_off_ix_d
	(  OP_BYTE_OFF_3  , "ld a,set 5,(ix%s)"), # 239 ld_A_SET_5_off_ix_d
	(  OP_BYTE_OFF_3  , "ld b,set 6,(ix%s)"), # 240 ld_B_SET_6_off_ix_d
	(  OP_BYTE_OFF_3  , "ld c,set 6,(ix%s)"), # 241 ld_C_SET_6_off_ix_d
	(  OP_BYTE_OFF_3  , "ld d,set 6,(ix%s)"), # 242 ld_D_SET_6_off_ix_d
	(  OP_BYTE_OFF_3  , "ld e,set 6,(ix%s)"), # 243 ld_E_SET_6_off_ix_d
	(  OP_BYTE_OFF_3  , "ld h,set 6,(ix%s)"), # 244 ld_H_SET_6_off_ix_d
	(  OP_BYTE_OFF_3  , "ld l,set 6,(ix%s)"), # 245 ld_L_SET_6_off_ix_d
	(  OP_BYTE_OFF_3  , "set 6,(ix%s)" ), # 246 SET_6_off_ix_d
	(  OP_BYTE_OFF_3  , "ld a,set 6,(ix%s)"), # 247 ld_A_SET_6_off_ix_d
	(  OP_BYTE_OFF_3  , "ld b,set 7,(ix%s)"), # 248 ld_B_SET_7_off_ix_d
	(  OP_BYTE_OFF_3  , "ld c,set 7,(ix%s)"), # 249 ld_C_SET_7_off_ix_d
	(  OP_BYTE_OFF_3  , "ld d,set 7,(ix%s)"), # 250 ld_D_SET_7_off_ix_d
	(  OP_BYTE_OFF_3  , "ld e,set 7,(ix%s)"), # 251 ld_E_SET_7_off_ix_d
	(  OP_BYTE_OFF_3  , "ld h,set 7,(ix%s)"), # 252 ld_H_SET_7_off_ix_d
	(  OP_BYTE_OFF_3  , "ld l,set 7,(ix%s)"), # 253 ld_L_SET_7_off_ix_d
	(  OP_BYTE_OFF_3  , "set 7,(ix%s)" ), # 254 SET_7_off_ix_d
	(  OP_BYTE_OFF_3  , "ld a,set 7,(ix%s)") # 255 ld_A_SET_7_off_ix_d
)

opcodes_ED = (
	(  OP_NONE  , NULL         ), #   0 NULL
	(  OP_NONE  , NULL         ), #   1 NULL
	(  OP_NONE  , NULL         ), #   2 NULL
	(  OP_NONE  , NULL         ), #   3 NULL
	(  OP_NONE  , NULL         ), #   4 NULL
	(  OP_NONE  , NULL         ), #   5 NULL
	(  OP_NONE  , NULL         ), #   6 NULL
	(  OP_NONE  , NULL         ), #   7 NULL
	(  OP_NONE  , NULL         ), #   8 NULL
	(  OP_NONE  , NULL         ), #   9 NULL
	(  OP_NONE  , NULL         ), #  10 NULL
	(  OP_NONE  , NULL         ), #  11 NULL
	(  OP_NONE  , NULL         ), #  12 NULL
	(  OP_NONE  , NULL         ), #  13 NULL
	(  OP_NONE  , NULL         ), #  14 NULL
	(  OP_NONE  , NULL         ), #  15 NULL
	(  OP_NONE  , NULL         ), #  16 NULL
	(  OP_NONE  , NULL         ), #  17 NULL
	(  OP_NONE  , NULL         ), #  18 NULL
	(  OP_NONE  , NULL         ), #  19 NULL
	(  OP_NONE  , NULL         ), #  20 NULL
	(  OP_NONE  , NULL         ), #  21 NULL
	(  OP_NONE  , NULL         ), #  22 NULL
	(  OP_NONE  , NULL         ), #  23 NULL
	(  OP_NONE  , NULL         ), #  24 NULL
	(  OP_NONE  , NULL         ), #  25 NULL
	(  OP_NONE  , NULL         ), #  26 NULL
	(  OP_NONE  , NULL         ), #  27 NULL
	(  OP_NONE  , NULL         ), #  28 NULL
	(  OP_NONE  , NULL         ), #  29 NULL
	(  OP_NONE  , NULL         ), #  30 NULL
	(  OP_NONE  , NULL         ), #  31 NULL
	(  OP_NONE  , NULL         ), #  32 NULL
	(  OP_NONE  , NULL         ), #  33 NULL
	(  OP_NONE  , NULL         ), #  34 NULL
	(  OP_NONE  , NULL         ), #  35 NULL
	(  OP_NONE  , NULL         ), #  36 NULL
	(  OP_NONE  , NULL         ), #  37 NULL
	(  OP_NONE  , NULL         ), #  38 NULL
	(  OP_NONE  , NULL         ), #  39 NULL
	(  OP_NONE  , NULL         ), #  40 NULL
	(  OP_NONE  , NULL         ), #  41 NULL
	(  OP_NONE  , NULL         ), #  42 NULL
	(  OP_NONE  , NULL         ), #  43 NULL
	(  OP_NONE  , NULL         ), #  44 NULL
	(  OP_NONE  , NULL         ), #  45 NULL
	(  OP_NONE  , NULL         ), #  46 NULL
	(  OP_NONE  , NULL         ), #  47 NULL
	(  OP_NONE  , NULL         ), #  48 NULL
	(  OP_NONE  , NULL         ), #  49 NULL
	(  OP_NONE  , NULL         ), #  50 NULL
	(  OP_NONE  , NULL         ), #  51 NULL
	(  OP_NONE  , NULL         ), #  52 NULL
	(  OP_NONE  , NULL         ), #  53 NULL
	(  OP_NONE  , NULL         ), #  54 NULL
	(  OP_NONE  , NULL         ), #  55 NULL
	(  OP_NONE  , NULL         ), #  56 NULL
	(  OP_NONE  , NULL         ), #  57 NULL
	(  OP_NONE  , NULL         ), #  58 NULL
	(  OP_NONE  , NULL         ), #  59 NULL
	(  OP_NONE  , NULL         ), #  60 NULL
	(  OP_NONE  , NULL         ), #  61 NULL
	(  OP_NONE  , NULL         ), #  62 NULL
	(  OP_NONE  , NULL         ), #  63 NULL
	(  OP_NONE  , "in b,(c)"   ), #  64 in_B_off_C
	(  OP_NONE  , "out (c),b"  ), #  65 out_off_C_B
	(  OP_NONE  , "sbc hl,bc"  ), #  66 sbc_hl_bc
	(  OP_WORD  , "ld (%s),bc"    ), #  67 ld_off_nn_bc
	(  OP_NONE  , "neg"        ), #  68 NEG
	(  OP_NONE  , "retn"       ), #  69 retN
	(  OP_NONE  , "im 0"       ), #  70 IM_0
	(  OP_NONE  , "ld i,a"     ), #  71 ld_I_A
	(  OP_NONE  , "in c,(c)"   ), #  72 in_C_off_C
	(  OP_NONE  , "out (c),c"  ), #  73 out_off_C_C
	(  OP_NONE  , "adc hl,bc"  ), #  74 adc_hl_bc
	(  OP_WORD  , "ld bc,(%s)"    ), #  75 ld_bc_off_nn
	(  OP_NONE  , "neg"        ), #  76 NEG
	(  OP_NONE  , "reti"       ), #  77 retI
	(  OP_NONE  , "im 0"       ), #  78 IM_0
	(  OP_NONE  , "ld r,a"     ), #  79 ld_R_A
	(  OP_NONE  , "in d,(c)"   ), #  80 in_D_off_C
	(  OP_NONE  , "out (c),d"  ), #  81 out_off_C_D
	(  OP_NONE  , "sbc hl,de"  ), #  82 sbc_hl_de
	(  OP_WORD  , "ld (%s),de"    ), #  83 ld_off_nn_de
	(  OP_NONE  , "neg"        ), #  84 NEG
	(  OP_NONE  , "retn"       ), #  85 retN
	(  OP_NONE  , "im 1"       ), #  86 IM_1
	(  OP_NONE  , "ld a,i"     ), #  87 ld_A_I
	(  OP_NONE  , "in e,(c)"   ), #  88 in_E_off_C
	(  OP_NONE  , "out (c),e"  ), #  89 out_off_C_E
	(  OP_NONE  , "adc hl,de"  ), #  90 adc_hl_de
	(  OP_WORD  , "ld de,(%s)"    ), #  91 ld_de_off_nn
	(  OP_NONE  , "neg"        ), #  92 NEG
	(  OP_NONE  , "retn"       ), #  93 retN
	(  OP_NONE  , "im 2"       ), #  94 IM_2
	(  OP_NONE  , "ld a,r"     ), #  95 ld_A_R
	(  OP_NONE  , "in h,(c)"   ), #  96 in_H_off_C
	(  OP_NONE  , "out (c),h"  ), #  97 out_off_C_H
	(  OP_NONE  , "sbc hl,hl"  ), #  98 sbc_hl_hl
	(  OP_WORD  , "ld (%s),hl"    ), #  99 ld_off_nn_hl
	(  OP_NONE  , "neg"        ), # 100 NEG
	(  OP_NONE  , "retn"       ), # 101 retN
	(  OP_NONE  , "im 0"       ), # 102 IM_0
	(  OP_NONE  , "rrd"        ), # 103 RRD
	(  OP_NONE  , "in l,(c)"   ), # 104 in_L_off_C
	(  OP_NONE  , "out (c),l"  ), # 105 out_off_C_L
	(  OP_NONE  , "adc hl,hl"  ), # 106 adc_hl_hl
	(  OP_WORD  , "ld hl,(%s)"    ), # 107 ld_hl_off_nn
	(  OP_NONE  , "neg"        ), # 108 NEG
	(  OP_NONE  , "retn"       ), # 109 retN
	(  OP_NONE  , "im 0"       ), # 110 IM_0
	(  OP_NONE  , "rld"        ), # 111 Rld
	(  OP_NONE  , "in f,(c)"   ), # 112 in_F_off_C
	(  OP_NONE  , "out (c),0"  ), # 113 out_off_C_0
	(  OP_NONE  , "sbc hl,sp"  ), # 114 sbc_hl_sp
	(  OP_WORD  , "ld (%s),sp"    ), # 115 ld_off_nn_sp
	(  OP_NONE  , "neg"        ), # 116 NEG
	(  OP_NONE  , "retn"       ), # 117 retN
	(  OP_NONE  , "im 1"       ), # 118 IM_1
	(  OP_NONE  , NULL         ), # 119 NULL
	(  OP_NONE  , "in a,(c)"   ), # 120 in_A_off_C
	(  OP_NONE  , "out (c),a"  ), # 121 out_off_C_A
	(  OP_NONE  , "adc hl,sp"  ), # 122 adc_hl_sp
	(  OP_WORD  , "ld sp,(%s)"    ), # 123 ld_sp_off_nn
	(  OP_NONE  , "neg"        ), # 124 NEG
	(  OP_NONE  , "retn"       ), # 125 retN
	(  OP_NONE  , "im 2"       ), # 126 IM_2
	(  OP_NONE  , NULL         ), # 127 NULL
	(  OP_NONE  , NULL         ), # 128 NULL
	(  OP_NONE  , NULL         ), # 129 NULL
	(  OP_NONE  , NULL         ), # 130 NULL
	(  OP_NONE  , NULL         ), # 131 NULL
	(  OP_NONE  , NULL         ), # 132 NULL
	(  OP_NONE  , NULL         ), # 133 NULL
	(  OP_NONE  , NULL         ), # 134 NULL
	(  OP_NONE  , NULL         ), # 135 NULL
	(  OP_NONE  , NULL         ), # 136 NULL
	(  OP_NONE  , NULL         ), # 137 NULL
	(  OP_NONE  , NULL         ), # 138 NULL
	(  OP_NONE  , NULL         ), # 139 NULL
	(  OP_NONE  , NULL         ), # 140 NULL
	(  OP_NONE  , NULL         ), # 141 NULL
	(  OP_NONE  , NULL         ), # 142 NULL
	(  OP_NONE  , NULL         ), # 143 NULL
	(  OP_NONE  , NULL         ), # 144 NULL
	(  OP_NONE  , NULL         ), # 145 NULL
	(  OP_NONE  , NULL         ), # 146 NULL
	(  OP_NONE  , NULL         ), # 147 NULL
	(  OP_NONE  , NULL         ), # 148 NULL
	(  OP_NONE  , NULL         ), # 149 NULL
	(  OP_NONE  , NULL         ), # 150 NULL
	(  OP_NONE  , NULL         ), # 151 NULL
	(  OP_NONE  , NULL         ), # 152 NULL
	(  OP_NONE  , NULL         ), # 153 NULL
	(  OP_NONE  , NULL         ), # 154 NULL
	(  OP_NONE  , NULL         ), # 155 NULL
	(  OP_NONE  , NULL         ), # 156 NULL
	(  OP_NONE  , NULL         ), # 157 NULL
	(  OP_NONE  , NULL         ), # 158 NULL
	(  OP_NONE  , NULL         ), # 159 NULL
	(  OP_NONE  , "ldi"        ), # 160 ldI
	(  OP_NONE  , "cpi"        ), # 161 cPI
	(  OP_NONE  , "ini"        ), # 162 ini
	(  OP_NONE  , "outi"       ), # 163 outi
	(  OP_NONE  , NULL         ), # 164 NULL
	(  OP_NONE  , NULL         ), # 165 NULL
	(  OP_NONE  , NULL         ), # 166 NULL
	(  OP_NONE  , NULL         ), # 167 NULL
	(  OP_NONE  , "ldd"        ), # 168 ldD
	(  OP_NONE  , "cpd"        ), # 169 cPD
	(  OP_NONE  , "ind"        ), # 170 ind
	(  OP_NONE  , "outd"       ), # 171 outd
	(  OP_NONE  , NULL         ), # 172 NULL
	(  OP_NONE  , NULL         ), # 173 NULL
	(  OP_NONE  , NULL         ), # 174 NULL
	(  OP_NONE  , NULL         ), # 175 NULL
	(  OP_NONE  , "ldir"       ), # 176 ldir
	(  OP_NONE  , "cpir"       ), # 177 cPIR
	(  OP_NONE  , "inir"       ), # 178 inir
	(  OP_NONE  , "otir"       ), # 179 OTIR
	(  OP_NONE  , NULL         ), # 180 NULL
	(  OP_NONE  , NULL         ), # 181 NULL
	(  OP_NONE  , NULL         ), # 182 NULL
	(  OP_NONE  , NULL         ), # 183 NULL
	(  OP_NONE  , "lddr"       ), # 184 lddr
	(  OP_NONE  , "cpdr"       ), # 185 cPDR
	(  OP_NONE  , "indr"       ), # 186 indr
	(  OP_NONE  , "otdr"       ), # 187 OTDR
	(  OP_NONE  , NULL         ), # 188 NULL
	(  OP_NONE  , NULL         ), # 189 NULL
	(  OP_NONE  , NULL         ), # 190 NULL
	(  OP_NONE  , NULL         ), # 191 NULL
	(  OP_NONE  , NULL         ), # 192 NULL
	(  OP_NONE  , NULL         ), # 193 NULL
	(  OP_NONE  , NULL         ), # 194 NULL
	(  OP_NONE  , NULL         ), # 195 NULL
	(  OP_NONE  , NULL         ), # 196 NULL
	(  OP_NONE  , NULL         ), # 197 NULL
	(  OP_NONE  , NULL         ), # 198 NULL
	(  OP_NONE  , NULL         ), # 199 NULL
	(  OP_NONE  , NULL         ), # 200 NULL
	(  OP_NONE  , NULL         ), # 201 NULL
	(  OP_NONE  , NULL         ), # 202 NULL
	(  OP_NONE  , NULL         ), # 203 NULL
	(  OP_NONE  , NULL         ), # 204 NULL
	(  OP_NONE  , NULL         ), # 205 NULL
	(  OP_NONE  , NULL         ), # 206 NULL
	(  OP_NONE  , NULL         ), # 207 NULL
	(  OP_NONE  , NULL         ), # 208 NULL
	(  OP_NONE  , NULL         ), # 209 NULL
	(  OP_NONE  , NULL         ), # 210 NULL
	(  OP_NONE  , NULL         ), # 211 NULL
	(  OP_NONE  , NULL         ), # 212 NULL
	(  OP_NONE  , NULL         ), # 213 NULL
	(  OP_NONE  , NULL         ), # 214 NULL
	(  OP_NONE  , NULL         ), # 215 NULL
	(  OP_NONE  , NULL         ), # 216 NULL
	(  OP_NONE  , NULL         ), # 217 NULL
	(  OP_NONE  , NULL         ), # 218 NULL
	(  OP_NONE  , NULL         ), # 219 NULL
	(  OP_NONE  , NULL         ), # 220 NULL
	(  OP_NONE  , NULL         ), # 221 NULL
	(  OP_NONE  , NULL         ), # 222 NULL
	(  OP_NONE  , NULL         ), # 223 NULL
	(  OP_NONE  , NULL         ), # 224 NULL
	(  OP_NONE  , NULL         ), # 225 NULL
	(  OP_NONE  , NULL         ), # 226 NULL
	(  OP_NONE  , NULL         ), # 227 NULL
	(  OP_NONE  , NULL         ), # 228 NULL
	(  OP_NONE  , NULL         ), # 229 NULL
	(  OP_NONE  , NULL         ), # 230 NULL
	(  OP_NONE  , NULL         ), # 231 NULL
	(  OP_NONE  , NULL         ), # 232 NULL
	(  OP_NONE  , NULL         ), # 233 NULL
	(  OP_NONE  , NULL         ), # 234 NULL
	(  OP_NONE  , NULL         ), # 235 NULL
	(  OP_NONE  , NULL         ), # 236 NULL
	(  OP_NONE  , NULL         ), # 237 NULL
	(  OP_NONE  , NULL         ), # 238 NULL
	(  OP_NONE  , NULL         ), # 239 NULL
	(  OP_NONE  , NULL         ), # 240 NULL
	(  OP_NONE  , NULL         ), # 241 NULL
	(  OP_NONE  , NULL         ), # 242 NULL
	(  OP_NONE  , NULL         ), # 243 NULL
	(  OP_NONE  , NULL         ), # 244 NULL
	(  OP_NONE  , NULL         ), # 245 NULL
	(  OP_NONE  , NULL         ), # 246 NULL
	(  OP_NONE  , NULL         ), # 247 NULL
	(  OP_NONE  , NULL         ), # 248 NULL
	(  OP_NONE  , NULL         ), # 249 NULL
	(  OP_NONE  , NULL         ), # 250 NULL
	(  OP_NONE  , NULL         ), # 251 NULL
	(  OP_NONE  , NULL         ), # 252 NULL
	(  OP_NONE  , NULL         ), # 253 NULL
	(  OP_NONE  , NULL         ), # 254 NULL
	(  OP_NONE  , NULL         ) # 255 NULL
)

opcodes_FD = (
	(  OP_NONE  , NULL         ), #   0 NULL
	(  OP_NONE  , NULL         ), #   1 NULL
	(  OP_NONE  , NULL         ), #   2 NULL
	(  OP_NONE  , NULL         ), #   3 NULL
	(  OP_NONE  , NULL         ), #   4 NULL
	(  OP_NONE  , NULL         ), #   5 NULL
	(  OP_NONE  , NULL         ), #   6 NULL
	(  OP_NONE  , NULL         ), #   7 NULL
	(  OP_NONE  , NULL         ), #   8 NULL
	(  OP_NONE  , "add iy,bc"  ), #   9 add_iy_bc
	(  OP_NONE  , NULL         ), #  10 NULL
	(  OP_NONE  , NULL         ), #  11 NULL
	(  OP_NONE  , NULL         ), #  12 NULL
	(  OP_NONE  , NULL         ), #  13 NULL
	(  OP_NONE  , NULL         ), #  14 NULL
	(  OP_NONE  , NULL         ), #  15 NULL
	(  OP_NONE  , NULL         ), #  16 NULL
	(  OP_NONE  , NULL         ), #  17 NULL
	(  OP_NONE  , NULL         ), #  18 NULL
	(  OP_NONE  , NULL         ), #  19 NULL
	(  OP_NONE  , NULL         ), #  20 NULL
	(  OP_NONE  , NULL         ), #  21 NULL
	(  OP_NONE  , NULL         ), #  22 NULL
	(  OP_NONE  , NULL         ), #  23 NULL
	(  OP_NONE  , NULL         ), #  24 NULL
	(  OP_NONE  , "add iy,de"  ), #  25 add_iy_de
	(  OP_NONE  , NULL         ), #  26 NULL
	(  OP_NONE  , NULL         ), #  27 NULL
	(  OP_NONE  , NULL         ), #  28 NULL
	(  OP_NONE  , NULL         ), #  29 NULL
	(  OP_NONE  , NULL         ), #  30 NULL
	(  OP_NONE  , NULL         ), #  31 NULL
	(  OP_NONE  , NULL         ), #  32 NULL
	(  OP_WORD  , "ld iy,%s"      ), #  33 ld_iy_nn
	(  OP_WORD  , "ld (%s),iy"    ), #  34 ld_off_nn_iy
	(  OP_NONE  , "inc iy"     ), #  35 inc_iy
	(  OP_NONE  , "inc iyh"    ), #  36 inc_iyh
	(  OP_NONE  , "dec iyh"    ), #  37 dec_iyh
	(  OP_BYTE  , "ld iyh,%s"     ), #  38 ld_iyh_n
	(  OP_NONE  , NULL         ), #  39 NULL
	(  OP_NONE  , NULL         ), #  40 NULL
	(  OP_NONE  , "add iy,iy"  ), #  41 add_iy_iy
	(  OP_WORD  , "ld iy,(%s)"    ), #  42 ld_iy_off_nn
	(  OP_NONE  , "dec iy"     ), #  43 dec_iy
	(  OP_NONE  , "inc iyl"    ), #  44 inc_iyl
	(  OP_NONE  , "dec iyl"    ), #  45 dec_iyl
	(  OP_BYTE  , "ld iyl,%s"     ), #  46 ld_iyl_n
	(  OP_NONE  , NULL         ), #  47 NULL
	(  OP_NONE  , NULL         ), #  48 NULL
	(  OP_NONE  , NULL         ), #  49 NULL
	(  OP_NONE  , NULL         ), #  50 NULL
	(  OP_NONE  , NULL         ), #  51 NULL
	(  OP_BYTE_OFF, "inc (iy%s)"   ), #  52 inc_off_iy_d
	(  OP_BYTE_OFF, "dec (iy%s)"   ), #  53 dec_off_iy_d
	(  OP_BYTE_OFF_2, "ld (iy%s),%s"), #  54 ld_off_iy_d_n
	(  OP_NONE  , NULL         ), #  55 NULL
	(  OP_NONE  , NULL         ), #  56 NULL
	(  OP_NONE  , "add iy,sp"  ), #  57 add_iy_sp
	(  OP_NONE  , NULL         ), #  58 NULL
	(  OP_NONE  , NULL         ), #  59 NULL
	(  OP_NONE  , NULL         ), #  60 NULL
	(  OP_NONE  , NULL         ), #  61 NULL
	(  OP_NONE  , NULL         ), #  62 NULL
	(  OP_NONE  , NULL         ), #  63 NULL
	(  OP_NONE  , NULL         ), #  64 NULL
	(  OP_NONE  , NULL         ), #  65 NULL
	(  OP_NONE  , NULL         ), #  66 NULL
	(  OP_NONE  , NULL         ), #  67 NULL
	(  OP_NONE  , "ld b,iyh"   ), #  68 ld_B_iyh
	(  OP_NONE  , "ld b,iyl"   ), #  69 ld_B_iyl
	(  OP_BYTE_OFF  , "ld b,(iy%s)"  ), #  70 ld_B_off_iy_d
	(  OP_NONE  , NULL         ), #  71 NULL
	(  OP_NONE  , NULL         ), #  72 NULL
	(  OP_NONE  , NULL         ), #  73 NULL
	(  OP_NONE  , NULL         ), #  74 NULL
	(  OP_NONE  , NULL         ), #  75 NULL
	(  OP_NONE  , "ld c,iyh"   ), #  76 ld_C_iyh
	(  OP_NONE  , "ld c,iyl"   ), #  77 ld_C_iyl
	(  OP_BYTE_OFF  , "ld c,(iy%s)"  ), #  78 ld_C_off_iy_d
	(  OP_NONE  , NULL         ), #  79 NULL
	(  OP_NONE  , NULL         ), #  80 NULL
	(  OP_NONE  , NULL         ), #  81 NULL
	(  OP_NONE  , NULL         ), #  82 NULL
	(  OP_NONE  , NULL         ), #  83 NULL
	(  OP_NONE  , "ld d,iyh"   ), #  84 ld_D_iyh
	(  OP_NONE  , "ld d,iyl"   ), #  85 ld_D_iyl
	(  OP_BYTE_OFF  , "ld d,(iy%s)"  ), #  86 ld_D_off_iy_d
	(  OP_NONE  , NULL         ), #  87 NULL
	(  OP_NONE  , NULL         ), #  88 NULL
	(  OP_NONE  , NULL         ), #  89 NULL
	(  OP_NONE  , NULL         ), #  90 NULL
	(  OP_NONE  , NULL         ), #  91 NULL
	(  OP_NONE  , "ld e,iyh"   ), #  92 ld_E_iyh
	(  OP_NONE  , "ld e,iyl"   ), #  93 ld_E_iyl
	(  OP_BYTE_OFF  , "ld e,(iy%s)"  ), #  94 ld_E_off_iy_d
	(  OP_NONE  , NULL         ), #  95 NULL
	(  OP_NONE  , "ld iyh,b"   ), #  96 ld_iyh_B
	(  OP_NONE  , "ld iyh,c"   ), #  97 ld_iyh_C
	(  OP_NONE  , "ld iyh,d"   ), #  98 ld_iyh_D
	(  OP_NONE  , "ld iyh,e"   ), #  99 ld_iyh_E
	(  OP_NONE  , "ld iyh,iyh" ), # 100 ld_iyh_iyh
	(  OP_NONE  , "ld iyh,iyl" ), # 101 ld_iyh_iyl
	(  OP_BYTE_OFF  , "ld h,(iy%s)"  ), # 102 ld_H_off_iy_d
	(  OP_NONE  , "ld iyh,a"   ), # 103 ld_iyh_A
	(  OP_NONE  , "ld iyl,b"   ), # 104 ld_iyl_B
	(  OP_NONE  , "ld iyl,c"   ), # 105 ld_iyl_C
	(  OP_NONE  , "ld iyl,d"   ), # 106 ld_iyl_D
	(  OP_NONE  , "ld iyl,e"   ), # 107 ld_iyl_E
	(  OP_NONE  , "ld iyl,iyh" ), # 108 ld_iyl_iyh
	(  OP_NONE  , "ld iyl,iyl" ), # 109 ld_iyl_iyl
	(  OP_BYTE_OFF  , "ld l,(iy%s)"  ), # 110 ld_L_off_iy_d
	(  OP_NONE  , "ld iyl,a"   ), # 111 ld_iyl_A
	(  OP_BYTE_OFF  , "ld (iy%s),b"  ), # 112 ld_off_iy_d_B
	(  OP_BYTE_OFF  , "ld (iy%s),c"  ), # 113 ld_off_iy_d_C
	(  OP_BYTE_OFF  , "ld (iy%s),d"  ), # 114 ld_off_iy_d_D
	(  OP_BYTE_OFF  , "ld (iy%s),e"  ), # 115 ld_off_iy_d_E
	(  OP_BYTE_OFF  , "ld (iy%s),h"  ), # 116 ld_off_iy_d_H
	(  OP_BYTE_OFF  , "ld (iy%s),l"  ), # 117 ld_off_iy_d_L
	(  OP_NONE  , NULL         ), # 118 NULL
	(  OP_BYTE_OFF  , "ld (iy%s),a"  ), # 119 ld_off_iy_d_A
	(  OP_NONE  , NULL         ), # 120 NULL
	(  OP_NONE  , NULL         ), # 121 NULL
	(  OP_NONE  , NULL         ), # 122 NULL
	(  OP_NONE  , NULL         ), # 123 NULL
	(  OP_NONE  , "ld a,iyh"   ), # 124 ld_A_iyh
	(  OP_NONE  , "ld a,iyl"   ), # 125 ld_A_iyl
	(  OP_BYTE_OFF  , "ld a,(iy%s)"  ), # 126 ld_A_off_iy_d
	(  OP_NONE  , NULL         ), # 127 NULL
	(  OP_NONE  , NULL         ), # 128 NULL
	(  OP_NONE  , NULL         ), # 129 NULL
	(  OP_NONE  , NULL         ), # 130 NULL
	(  OP_NONE  , NULL         ), # 131 NULL
	(  OP_NONE  , "add a,iyh"  ), # 132 add_A_iyh
	(  OP_NONE  , "add a,iyl"  ), # 133 add_A_iyl
	(  OP_BYTE_OFF  , "add a,(iy%s)" ), # 134 add_A_off_iy_d
	(  OP_NONE  , NULL         ), # 135 NULL
	(  OP_NONE  , NULL         ), # 136 NULL
	(  OP_NONE  , NULL         ), # 137 NULL
	(  OP_NONE  , NULL         ), # 138 NULL
	(  OP_NONE  , NULL         ), # 139 NULL
	(  OP_NONE  , "adc a,iyh"  ), # 140 adc_A_iyh
	(  OP_NONE  , "adc a,iyl"  ), # 141 adc_A_iyl
	(  OP_BYTE_OFF  , "adc a,(iy%s)" ), # 142 adc_A_off_iy_d
	(  OP_NONE  , NULL         ), # 143 NULL
	(  OP_NONE  , NULL         ), # 144 NULL
	(  OP_NONE  , NULL         ), # 145 NULL
	(  OP_NONE  , NULL         ), # 146 NULL
	(  OP_NONE  , NULL         ), # 147 NULL
	(  OP_NONE  , "sub a,iyh"  ), # 148 sub_A_iyh
	(  OP_NONE  , "sub a,iyl"  ), # 149 sub_A_iyl
	(  OP_BYTE_OFF  , "sub a,(iy%s)" ), # 150 sub_A_off_iy_d
	(  OP_NONE  , NULL         ), # 151 NULL
	(  OP_NONE  , NULL         ), # 152 NULL
	(  OP_NONE  , NULL         ), # 153 NULL
	(  OP_NONE  , NULL         ), # 154 NULL
	(  OP_NONE  , NULL         ), # 155 NULL
	(  OP_NONE  , "sbc a,iyh"  ), # 156 sbc_A_iyh
	(  OP_NONE  , "sbc a,iyl"  ), # 157 sbc_A_iyl
	(  OP_BYTE_OFF  , "sbc a,(iy%s)" ), # 158 sbc_A_off_iy_d
	(  OP_NONE  , NULL         ), # 159 NULL
	(  OP_NONE  , NULL         ), # 160 NULL
	(  OP_NONE  , NULL         ), # 161 NULL
	(  OP_NONE  , NULL         ), # 162 NULL
	(  OP_NONE  , NULL         ), # 163 NULL
	(  OP_NONE  , "and iyh"    ), # 164 and_iyh
	(  OP_NONE  , "and iyl"    ), # 165 and_iyl
	(  OP_BYTE_OFF  , "and (iy%s)"   ), # 166 and_off_iy_d
	(  OP_NONE  , NULL         ), # 167 NULL
	(  OP_NONE  , NULL         ), # 168 NULL
	(  OP_NONE  , NULL         ), # 169 NULL
	(  OP_NONE  , NULL         ), # 170 NULL
	(  OP_NONE  , NULL         ), # 171 NULL
	(  OP_NONE  , "xor iyh"    ), # 172 xor_iyh
	(  OP_NONE  , "xor iyl"    ), # 173 xor_iyl
	(  OP_BYTE_OFF  , "xor (iy%s)"   ), # 174 xor_off_iy_d
	(  OP_NONE  , NULL         ), # 175 NULL
	(  OP_NONE  , NULL         ), # 176 NULL
	(  OP_NONE  , NULL         ), # 177 NULL
	(  OP_NONE  , NULL         ), # 178 NULL
	(  OP_NONE  , NULL         ), # 179 NULL
	(  OP_NONE  , "or iyh"     ), # 180 OR_iyh
	(  OP_NONE  , "or iyl"     ), # 181 OR_iyl
	(  OP_BYTE_OFF  , "or (iy%s)"    ), # 182 OR_off_iy_d
	(  OP_NONE  , NULL         ), # 183 NULL
	(  OP_NONE  , NULL         ), # 184 NULL
	(  OP_NONE  , NULL         ), # 185 NULL
	(  OP_NONE  , NULL         ), # 186 NULL
	(  OP_NONE  , NULL         ), # 187 NULL
	(  OP_NONE  , "cp iyh"     ), # 188 cP_iyh
	(  OP_NONE  , "cp iyl"     ), # 189 cP_iyl
	(  OP_BYTE_OFF  , "cp (iy%s)"    ), # 190 cP_off_iy_d
	(  OP_NONE  , NULL         ), # 191 NULL
	(  OP_NONE  , NULL         ), # 192 NULL
	(  OP_NONE  , NULL         ), # 193 NULL
	(  OP_NONE  , NULL         ), # 194 NULL
	(  OP_NONE  , NULL         ), # 195 NULL
	(  OP_NONE  , NULL         ), # 196 NULL
	(  OP_NONE  , NULL         ), # 197 NULL
	(  OP_NONE  , NULL         ), # 198 NULL
	(  OP_NONE  , NULL         ), # 199 NULL
	(  OP_NONE  , NULL         ), # 200 NULL
	(  OP_NONE  , NULL         ), # 201 NULL
	(  OP_NONE  , NULL         ), # 202 NULL
	(  OP_FDCB  , NULL         ), # 203 NULL
	(  OP_NONE  , NULL         ), # 204 NULL
	(  OP_NONE  , NULL         ), # 205 NULL
	(  OP_NONE  , NULL         ), # 206 NULL
	(  OP_NONE  , NULL         ), # 207 NULL
	(  OP_NONE  , NULL         ), # 208 NULL
	(  OP_NONE  , NULL         ), # 209 NULL
	(  OP_NONE  , NULL         ), # 210 NULL
	(  OP_NONE  , NULL         ), # 211 NULL
	(  OP_NONE  , NULL         ), # 212 NULL
	(  OP_NONE  , NULL         ), # 213 NULL
	(  OP_NONE  , NULL         ), # 214 NULL
	(  OP_NONE  , NULL         ), # 215 NULL
	(  OP_NONE  , NULL         ), # 216 NULL
	(  OP_NONE  , NULL         ), # 217 NULL
	(  OP_NONE  , NULL         ), # 218 NULL
	(  OP_NONE  , NULL         ), # 219 NULL
	(  OP_NONE  , NULL         ), # 220 NULL
	(  OP_NONE  , NULL         ), # 221 NULL
	(  OP_NONE  , NULL         ), # 222 NULL
	(  OP_NONE  , NULL         ), # 223 NULL
	(  OP_NONE  , NULL         ), # 224 NULL
	(  OP_NONE  , "pop iy"     ), # 225 pop_iy
	(  OP_NONE  , NULL         ), # 226 NULL
	(  OP_NONE  , "ex (sp),iy" ), # 227 EX_off_sp_iy
	(  OP_NONE  , NULL         ), # 228 NULL
	(  OP_NONE  , "push iy"    ), # 229 push_iy
	(  OP_NONE  , NULL         ), # 230 NULL
	(  OP_NONE  , NULL         ), # 231 NULL
	(  OP_NONE  , NULL         ), # 232 NULL
	(  OP_NONE  , "jp (iy)"    ), # 233 jp_off_iy
	(  OP_NONE  , NULL         ), # 234 NULL
	(  OP_NONE  , NULL         ), # 235 NULL
	(  OP_NONE  , NULL         ), # 236 NULL
	(  OP_NONE  , NULL         ), # 237 NULL
	(  OP_NONE  , NULL         ), # 238 NULL
	(  OP_NONE  , NULL         ), # 239 NULL
	(  OP_NONE  , NULL         ), # 240 NULL
	(  OP_NONE  , NULL         ), # 241 NULL
	(  OP_NONE  , NULL         ), # 242 NULL
	(  OP_NONE  , NULL         ), # 243 NULL
	(  OP_NONE  , NULL         ), # 244 NULL
	(  OP_NONE  , NULL         ), # 245 NULL
	(  OP_NONE  , NULL         ), # 246 NULL
	(  OP_NONE  , NULL         ), # 247 NULL
	(  OP_NONE  , NULL         ), # 248 NULL
	(  OP_NONE  , "ld sp,iy"   ), # 249 ld_sp_iy
	(  OP_NONE  , NULL         ), # 250 NULL
	(  OP_NONE  , NULL         ), # 251 NULL
	(  OP_NONE  , NULL         ), # 252 NULL
	(  OP_FD    , NULL         ), # 253 NULL
	(  OP_NONE  , NULL         ), # 254 NULL
	(  OP_NONE  , NULL         ) # 255 NULL
)

opcodes_FDCB = (
	(  OP_BYTE_OFF_3  , "ld b,rlc (iy%s)"), #   0 ld_B_rlc_off_iy_d
	(  OP_BYTE_OFF_3  , "ld c,rlc (iy%s)"), #   1 ld_C_rlc_off_iy_d
	(  OP_BYTE_OFF_3  , "ld d,rlc (iy%s)"), #   2 ld_D_rlc_off_iy_d
	(  OP_BYTE_OFF_3  , "ld e,rlc (iy%s)"), #   3 ld_E_rlc_off_iy_d
	(  OP_BYTE_OFF_3  , "ld h,rlc (iy%s)"), #   4 ld_H_rlc_off_iy_d
	(  OP_BYTE_OFF_3  , "ld l,rlc (iy%s)"), #   5 ld_L_rlc_off_iy_d
	(  OP_BYTE_OFF_3  , "rlc (iy%s)"   ), #   6 rlc_off_iy_d
	(  OP_BYTE_OFF_3  , "ld a,rlc (iy%s)"), #   7 ld_A_rlc_off_iy_d
	(  OP_BYTE_OFF_3  , "ld b,rrc (iy%s)"), #   8 ld_B_rrc_off_iy_d
	(  OP_BYTE_OFF_3  , "ld c,rrc (iy%s)"), #   9 ld_C_rrc_off_iy_d
	(  OP_BYTE_OFF_3  , "ld d,rrc (iy%s)"), #  10 ld_D_rrc_off_iy_d
	(  OP_BYTE_OFF_3  , "ld e,rrc (iy%s)"), #  11 ld_E_rrc_off_iy_d
	(  OP_BYTE_OFF_3  , "ld h,rrc (iy%s)"), #  12 ld_H_rrc_off_iy_d
	(  OP_BYTE_OFF_3  , "ld l,rrc (iy%s)"), #  13 ld_L_rrc_off_iy_d
	(  OP_BYTE_OFF_3  , "rrc (iy%s)"   ), #  14 rrc_off_iy_d
	(  OP_BYTE_OFF_3  , "ld a,rrc (iy%s)"), #  15 ld_A_rrc_off_iy_d
	(  OP_BYTE_OFF_3  , "ld b,rl (iy%s)"), #  16 ld_B_rl_off_iy_d
	(  OP_BYTE_OFF_3  , "ld c,rl (iy%s)"), #  17 ld_C_rl_off_iy_d
	(  OP_BYTE_OFF_3  , "ld d,rl (iy%s)"), #  18 ld_D_rl_off_iy_d
	(  OP_BYTE_OFF_3  , "ld e,rl (iy%s)"), #  19 ld_E_rl_off_iy_d
	(  OP_BYTE_OFF_3  , "ld h,rl (iy%s)"), #  20 ld_H_rl_off_iy_d
	(  OP_BYTE_OFF_3  , "ld l,rl (iy%s)"), #  21 ld_L_rl_off_iy_d
	(  OP_BYTE_OFF_3  , "rl (iy%s)"    ), #  22 rl_off_iy_d
	(  OP_BYTE_OFF_3  , "ld a,rl (iy%s)"), #  23 ld_A_rl_off_iy_d
	(  OP_BYTE_OFF_3  , "ld b,rr (iy%s)"), #  24 ld_B_rr_off_iy_d
	(  OP_BYTE_OFF_3  , "ld c,rr (iy%s)"), #  25 ld_C_rr_off_iy_d
	(  OP_BYTE_OFF_3  , "ld d,rr (iy%s)"), #  26 ld_D_rr_off_iy_d
	(  OP_BYTE_OFF_3  , "ld e,rr (iy%s)"), #  27 ld_E_rr_off_iy_d
	(  OP_BYTE_OFF_3  , "ld h,rr (iy%s)"), #  28 ld_H_rr_off_iy_d
	(  OP_BYTE_OFF_3  , "ld l,rr (iy%s)"), #  29 ld_L_rr_off_iy_d
	(  OP_BYTE_OFF_3  , "rr (iy%s)"    ), #  30 rr_off_iy_d
	(  OP_BYTE_OFF_3  , "ld a,rr (iy%s)"), #  31 ld_A_rr_off_iy_d
	(  OP_BYTE_OFF_3  , "ld b,sla (iy%s)"), #  32 ld_B_sla_off_iy_d
	(  OP_BYTE_OFF_3  , "ld c,sla (iy%s)"), #  33 ld_C_sla_off_iy_d
	(  OP_BYTE_OFF_3  , "ld d,sla (iy%s)"), #  34 ld_D_sla_off_iy_d
	(  OP_BYTE_OFF_3  , "ld e,sla (iy%s)"), #  35 ld_E_sla_off_iy_d
	(  OP_BYTE_OFF_3  , "ld h,sla (iy%s)"), #  36 ld_H_sla_off_iy_d
	(  OP_BYTE_OFF_3  , "ld l,sla (iy%s)"), #  37 ld_L_sla_off_iy_d
	(  OP_BYTE_OFF_3  , "sla (iy%s)"   ), #  38 sla_off_iy_d
	(  OP_BYTE_OFF_3  , "ld a,sla (iy%s)"), #  39 ld_A_sla_off_iy_d
	(  OP_BYTE_OFF_3  , "ld b,sra (iy%s)"), #  40 ld_B_sra_off_iy_d
	(  OP_BYTE_OFF_3  , "ld c,sra (iy%s)"), #  41 ld_C_sra_off_iy_d
	(  OP_BYTE_OFF_3  , "ld d,sra (iy%s)"), #  42 ld_D_sra_off_iy_d
	(  OP_BYTE_OFF_3  , "ld e,sra (iy%s)"), #  43 ld_E_sra_off_iy_d
	(  OP_BYTE_OFF_3  , "ld h,sra (iy%s)"), #  44 ld_H_sra_off_iy_d
	(  OP_BYTE_OFF_3  , "ld l,sra (iy%s)"), #  45 ld_L_sra_off_iy_d
	(  OP_BYTE_OFF_3  , "sra (iy%s)"   ), #  46 sra_off_iy_d
	(  OP_BYTE_OFF_3  , "ld a,sra (iy%s)"), #  47 ld_A_sra_off_iy_d
	(  OP_BYTE_OFF_3  , "ld b,sll (iy%s)"), #  48 ld_B_sll_off_iy_d
	(  OP_BYTE_OFF_3  , "ld c,sll (iy%s)"), #  49 ld_C_sll_off_iy_d
	(  OP_BYTE_OFF_3  , "ld d,sll (iy%s)"), #  50 ld_D_sll_off_iy_d
	(  OP_BYTE_OFF_3  , "ld e,sll (iy%s)"), #  51 ld_E_sll_off_iy_d
	(  OP_BYTE_OFF_3  , "ld h,sll (iy%s)"), #  52 ld_H_sll_off_iy_d
	(  OP_BYTE_OFF_3  , "ld l,sll (iy%s)"), #  53 ld_L_sll_off_iy_d
	(  OP_BYTE_OFF_3  , "sll (iy%s)"   ), #  54 sll_off_iy_d
	(  OP_BYTE_OFF_3  , "ld a,sll (iy%s)"), #  55 ld_A_sll_off_iy_d
	(  OP_BYTE_OFF_3  , "ld b,srl (iy%s)"), #  56 ld_B_srl_off_iy_d
	(  OP_BYTE_OFF_3  , "ld c,srl (iy%s)"), #  57 ld_C_srl_off_iy_d
	(  OP_BYTE_OFF_3  , "ld d,srl (iy%s)"), #  58 ld_D_srl_off_iy_d
	(  OP_BYTE_OFF_3  , "ld e,srl (iy%s)"), #  59 ld_E_srl_off_iy_d
	(  OP_BYTE_OFF_3  , "ld h,srl (iy%s)"), #  60 ld_H_srl_off_iy_d
	(  OP_BYTE_OFF_3  , "ld l,srl (iy%s)"), #  61 ld_L_srl_off_iy_d
	(  OP_BYTE_OFF_3  , "srl (iy%s)"   ), #  62 srl_off_iy_d
	(  OP_BYTE_OFF_3  , "ld a,srl (iy%s)"), #  63 ld_A_srl_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 0,(iy%s)" ), #  64 bit_0_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 0,(iy%s)" ), #  65 bit_0_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 0,(iy%s)" ), #  66 bit_0_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 0,(iy%s)" ), #  67 bit_0_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 0,(iy%s)" ), #  68 bit_0_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 0,(iy%s)" ), #  69 bit_0_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 0,(iy%s)" ), #  70 bit_0_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 0,(iy%s)" ), #  71 bit_0_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 1,(iy%s)" ), #  72 bit_1_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 1,(iy%s)" ), #  73 bit_1_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 1,(iy%s)" ), #  74 bit_1_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 1,(iy%s)" ), #  75 bit_1_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 1,(iy%s)" ), #  76 bit_1_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 1,(iy%s)" ), #  77 bit_1_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 1,(iy%s)" ), #  78 bit_1_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 1,(iy%s)" ), #  79 bit_1_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 2,(iy%s)" ), #  80 bit_2_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 2,(iy%s)" ), #  81 bit_2_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 2,(iy%s)" ), #  82 bit_2_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 2,(iy%s)" ), #  83 bit_2_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 2,(iy%s)" ), #  84 bit_2_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 2,(iy%s)" ), #  85 bit_2_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 2,(iy%s)" ), #  86 bit_2_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 2,(iy%s)" ), #  87 bit_2_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 3,(iy%s)" ), #  88 bit_3_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 3,(iy%s)" ), #  89 bit_3_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 3,(iy%s)" ), #  90 bit_3_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 3,(iy%s)" ), #  91 bit_3_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 3,(iy%s)" ), #  92 bit_3_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 3,(iy%s)" ), #  93 bit_3_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 3,(iy%s)" ), #  94 bit_3_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 3,(iy%s)" ), #  95 bit_3_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 4,(iy%s)" ), #  96 bit_4_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 4,(iy%s)" ), #  97 bit_4_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 4,(iy%s)" ), #  98 bit_4_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 4,(iy%s)" ), #  99 bit_4_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 4,(iy%s)" ), # 100 bit_4_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 4,(iy%s)" ), # 101 bit_4_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 4,(iy%s)" ), # 102 bit_4_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 4,(iy%s)" ), # 103 bit_4_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 5,(iy%s)" ), # 104 bit_5_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 5,(iy%s)" ), # 105 bit_5_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 5,(iy%s)" ), # 106 bit_5_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 5,(iy%s)" ), # 107 bit_5_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 5,(iy%s)" ), # 108 bit_5_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 5,(iy%s)" ), # 109 bit_5_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 5,(iy%s)" ), # 110 bit_5_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 5,(iy%s)" ), # 111 bit_5_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 6,(iy%s)" ), # 112 bit_6_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 6,(iy%s)" ), # 113 bit_6_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 6,(iy%s)" ), # 114 bit_6_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 6,(iy%s)" ), # 115 bit_6_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 6,(iy%s)" ), # 116 bit_6_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 6,(iy%s)" ), # 117 bit_6_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 6,(iy%s)" ), # 118 bit_6_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 6,(iy%s)" ), # 119 bit_6_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 7,(iy%s)" ), # 120 bit_7_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 7,(iy%s)" ), # 121 bit_7_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 7,(iy%s)" ), # 122 bit_7_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 7,(iy%s)" ), # 123 bit_7_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 7,(iy%s)" ), # 124 bit_7_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 7,(iy%s)" ), # 125 bit_7_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 7,(iy%s)" ), # 126 bit_7_off_iy_d
	(  OP_BYTE_OFF_3  , "bit 7,(iy%s)" ), # 127 bit_7_off_iy_d
	(  OP_BYTE_OFF_3  , "ld b,res 0,(iy%s)"), # 128 ld_B_res_0_off_iy_d
	(  OP_BYTE_OFF_3  , "ld c,res 0,(iy%s)"), # 129 ld_C_res_0_off_iy_d
	(  OP_BYTE_OFF_3  , "ld d,res 0,(iy%s)"), # 130 ld_D_res_0_off_iy_d
	(  OP_BYTE_OFF_3  , "ld e,res 0,(iy%s)"), # 131 ld_E_res_0_off_iy_d
	(  OP_BYTE_OFF_3  , "ld h,res 0,(iy%s)"), # 132 ld_H_res_0_off_iy_d
	(  OP_BYTE_OFF_3  , "ld l,res 0,(iy%s)"), # 133 ld_L_res_0_off_iy_d
	(  OP_BYTE_OFF_3  , "res 0,(iy%s)" ), # 134 res_0_off_iy_d
	(  OP_BYTE_OFF_3  , "ld a,res 0,(iy%s)"), # 135 ld_A_res_0_off_iy_d
	(  OP_BYTE_OFF_3  , "ld b,res 1,(iy%s)"), # 136 ld_B_res_1_off_iy_d
	(  OP_BYTE_OFF_3  , "ld c,res 1,(iy%s)"), # 137 ld_C_res_1_off_iy_d
	(  OP_BYTE_OFF_3  , "ld d,res 1,(iy%s)"), # 138 ld_D_res_1_off_iy_d
	(  OP_BYTE_OFF_3  , "ld e,res 1,(iy%s)"), # 139 ld_E_res_1_off_iy_d
	(  OP_BYTE_OFF_3  , "ld h,res 1,(iy%s)"), # 140 ld_H_res_1_off_iy_d
	(  OP_BYTE_OFF_3  , "ld l,res 1,(iy%s)"), # 141 ld_L_res_1_off_iy_d
	(  OP_BYTE_OFF_3  , "res 1,(iy%s)" ), # 142 res_1_off_iy_d
	(  OP_BYTE_OFF_3  , "ld a,res 1,(iy%s)"), # 143 ld_A_res_1_off_iy_d
	(  OP_BYTE_OFF_3  , "ld b,res 2,(iy%s)"), # 144 ld_B_res_2_off_iy_d
	(  OP_BYTE_OFF_3  , "ld c,res 2,(iy%s)"), # 145 ld_C_res_2_off_iy_d
	(  OP_BYTE_OFF_3  , "ld d,res 2,(iy%s)"), # 146 ld_D_res_2_off_iy_d
	(  OP_BYTE_OFF_3  , "ld e,res 2,(iy%s)"), # 147 ld_E_res_2_off_iy_d
	(  OP_BYTE_OFF_3  , "ld h,res 2,(iy%s)"), # 148 ld_H_res_2_off_iy_d
	(  OP_BYTE_OFF_3  , "ld l,res 2,(iy%s)"), # 149 ld_L_res_2_off_iy_d
	(  OP_BYTE_OFF_3  , "res 2,(iy%s)" ), # 150 res_2_off_iy_d
	(  OP_BYTE_OFF_3  , "ld a,res 2,(iy%s)"), # 151 ld_A_res_2_off_iy_d
	(  OP_BYTE_OFF_3  , "ld b,res 3,(iy%s)"), # 152 ld_B_res_3_off_iy_d
	(  OP_BYTE_OFF_3  , "ld c,res 3,(iy%s)"), # 153 ld_C_res_3_off_iy_d
	(  OP_BYTE_OFF_3  , "ld d,res 3,(iy%s)"), # 154 ld_D_res_3_off_iy_d
	(  OP_BYTE_OFF_3  , "ld e,res 3,(iy%s)"), # 155 ld_E_res_3_off_iy_d
	(  OP_BYTE_OFF_3  , "ld h,res 3,(iy%s)"), # 156 ld_H_res_3_off_iy_d
	(  OP_BYTE_OFF_3  , "ld l,res 3,(iy%s)"), # 157 ld_L_res_3_off_iy_d
	(  OP_BYTE_OFF_3  , "res 3,(iy%s)" ), # 158 res_3_off_iy_d
	(  OP_BYTE_OFF_3  , "ld a,res 3,(iy%s)"), # 159 ld_A_res_3_off_iy_d
	(  OP_BYTE_OFF_3  , "ld b,res 4,(iy%s)"), # 160 ld_B_res_4_off_iy_d
	(  OP_BYTE_OFF_3  , "ld c,res 4,(iy%s)"), # 161 ld_C_res_4_off_iy_d
	(  OP_BYTE_OFF_3  , "ld d,res 4,(iy%s)"), # 162 ld_D_res_4_off_iy_d
	(  OP_BYTE_OFF_3  , "ld e,res 4,(iy%s)"), # 163 ld_E_res_4_off_iy_d
	(  OP_BYTE_OFF_3  , "ld h,res 4,(iy%s)"), # 164 ld_H_res_4_off_iy_d
	(  OP_BYTE_OFF_3  , "ld l,res 4,(iy%s)"), # 165 ld_L_res_4_off_iy_d
	(  OP_BYTE_OFF_3  , "res 4,(iy%s)" ), # 166 res_4_off_iy_d
	(  OP_BYTE_OFF_3  , "ld a,res 4,(iy%s)"), # 167 ld_A_res_4_off_iy_d
	(  OP_BYTE_OFF_3  , "ld b,res 5,(iy%s)"), # 168 ld_B_res_5_off_iy_d
	(  OP_BYTE_OFF_3  , "ld c,res 5,(iy%s)"), # 169 ld_C_res_5_off_iy_d
	(  OP_BYTE_OFF_3  , "ld d,res 5,(iy%s)"), # 170 ld_D_res_5_off_iy_d
	(  OP_BYTE_OFF_3  , "ld e,res 5,(iy%s)"), # 171 ld_E_res_5_off_iy_d
	(  OP_BYTE_OFF_3  , "ld h,res 5,(iy%s)"), # 172 ld_H_res_5_off_iy_d
	(  OP_BYTE_OFF_3  , "ld l,res 5,(iy%s)"), # 173 ld_L_res_5_off_iy_d
	(  OP_BYTE_OFF_3  , "res 5,(iy%s)" ), # 174 res_5_off_iy_d
	(  OP_BYTE_OFF_3  , "ld a,res 5,(iy%s)"), # 175 ld_A_res_5_off_iy_d
	(  OP_BYTE_OFF_3  , "ld b,res 6,(iy%s)"), # 176 ld_B_res_6_off_iy_d
	(  OP_BYTE_OFF_3  , "ld c,res 6,(iy%s)"), # 177 ld_C_res_6_off_iy_d
	(  OP_BYTE_OFF_3  , "ld d,res 6,(iy%s)"), # 178 ld_D_res_6_off_iy_d
	(  OP_BYTE_OFF_3  , "ld e,res 6,(iy%s)"), # 179 ld_E_res_6_off_iy_d
	(  OP_BYTE_OFF_3  , "ld h,res 6,(iy%s)"), # 180 ld_H_res_6_off_iy_d
	(  OP_BYTE_OFF_3  , "ld l,res 6,(iy%s)"), # 181 ld_L_res_6_off_iy_d
	(  OP_BYTE_OFF_3  , "res 6,(iy%s)" ), # 182 res_6_off_iy_d
	(  OP_BYTE_OFF_3  , "ld a,res 6,(iy%s)"), # 183 ld_A_res_6_off_iy_d
	(  OP_BYTE_OFF_3  , "ld b,res 7,(iy%s)"), # 184 ld_B_res_7_off_iy_d
	(  OP_BYTE_OFF_3  , "ld c,res 7,(iy%s)"), # 185 ld_C_res_7_off_iy_d
	(  OP_BYTE_OFF_3  , "ld d,res 7,(iy%s)"), # 186 ld_D_res_7_off_iy_d
	(  OP_BYTE_OFF_3  , "ld e,res 7,(iy%s)"), # 187 ld_E_res_7_off_iy_d
	(  OP_BYTE_OFF_3  , "ld h,res 7,(iy%s)"), # 188 ld_H_res_7_off_iy_d
	(  OP_BYTE_OFF_3  , "ld l,res 7,(iy%s)"), # 189 ld_L_res_7_off_iy_d
	(  OP_BYTE_OFF_3  , "res 7,(iy%s)" ), # 190 res_7_off_iy_d
	(  OP_BYTE_OFF_3  , "ld a,res 7,(iy%s)"), # 191 ld_A_res_7_off_iy_d
	(  OP_BYTE_OFF_3  , "ld b,set 0,(iy%s)"), # 192 ld_B_SET_0_off_iy_d
	(  OP_BYTE_OFF_3  , "ld c,set 0,(iy%s)"), # 193 ld_C_SET_0_off_iy_d
	(  OP_BYTE_OFF_3  , "ld d,set 0,(iy%s)"), # 194 ld_D_SET_0_off_iy_d
	(  OP_BYTE_OFF_3  , "ld e,set 0,(iy%s)"), # 195 ld_E_SET_0_off_iy_d
	(  OP_BYTE_OFF_3  , "ld h,set 0,(iy%s)"), # 196 ld_H_SET_0_off_iy_d
	(  OP_BYTE_OFF_3  , "ld l,set 0,(iy%s)"), # 197 ld_L_SET_0_off_iy_d
	(  OP_BYTE_OFF_3  , "set 0,(iy%s)" ), # 198 SET_0_off_iy_d
	(  OP_BYTE_OFF_3  , "ld a,set 0,(iy%s)"), # 199 ld_A_SET_0_off_iy_d
	(  OP_BYTE_OFF_3  , "ld b,set 1,(iy%s)"), # 200 ld_B_SET_1_off_iy_d
	(  OP_BYTE_OFF_3  , "ld c,set 1,(iy%s)"), # 201 ld_C_SET_1_off_iy_d
	(  OP_BYTE_OFF_3  , "ld d,set 1,(iy%s)"), # 202 ld_D_SET_1_off_iy_d
	(  OP_BYTE_OFF_3  , "ld e,set 1,(iy%s)"), # 203 ld_E_SET_1_off_iy_d
	(  OP_BYTE_OFF_3  , "ld h,set 1,(iy%s)"), # 204 ld_H_SET_1_off_iy_d
	(  OP_BYTE_OFF_3  , "ld l,set 1,(iy%s)"), # 205 ld_L_SET_1_off_iy_d
	(  OP_BYTE_OFF_3  , "set 1,(iy%s)" ), # 206 SET_1_off_iy_d
	(  OP_BYTE_OFF_3  , "ld a,set 1,(iy%s)"), # 207 ld_A_SET_1_off_iy_d
	(  OP_BYTE_OFF_3  , "ld b,set 2,(iy%s)"), # 208 ld_B_SET_2_off_iy_d
	(  OP_BYTE_OFF_3  , "ld c,set 2,(iy%s)"), # 209 ld_C_SET_2_off_iy_d
	(  OP_BYTE_OFF_3  , "ld d,set 2,(iy%s)"), # 210 ld_D_SET_2_off_iy_d
	(  OP_BYTE_OFF_3  , "ld e,set 2,(iy%s)"), # 211 ld_E_SET_2_off_iy_d
	(  OP_BYTE_OFF_3  , "ld h,set 2,(iy%s)"), # 212 ld_H_SET_2_off_iy_d
	(  OP_BYTE_OFF_3  , "ld l,set 2,(iy%s)"), # 213 ld_L_SET_2_off_iy_d
	(  OP_BYTE_OFF_3  , "set 2,(iy%s)" ), # 214 SET_2_off_iy_d
	(  OP_BYTE_OFF_3  , "ld a,set 2,(iy%s)"), # 215 ld_A_SET_2_off_iy_d
	(  OP_BYTE_OFF_3  , "ld b,set 3,(iy%s)"), # 216 ld_B_SET_3_off_iy_d
	(  OP_BYTE_OFF_3  , "ld c,set 3,(iy%s)"), # 217 ld_C_SET_3_off_iy_d
	(  OP_BYTE_OFF_3  , "ld d,set 3,(iy%s)"), # 218 ld_D_SET_3_off_iy_d
	(  OP_BYTE_OFF_3  , "ld e,set 3,(iy%s)"), # 219 ld_E_SET_3_off_iy_d
	(  OP_BYTE_OFF_3  , "ld h,set 3,(iy%s)"), # 220 ld_H_SET_3_off_iy_d
	(  OP_BYTE_OFF_3  , "ld l,set 3,(iy%s)"), # 221 ld_L_SET_3_off_iy_d
	(  OP_BYTE_OFF_3  , "set 3,(iy%s)" ), # 222 SET_3_off_iy_d
	(  OP_BYTE_OFF_3  , "ld a,set 3,(iy%s)"), # 223 ld_A_SET_3_off_iy_d
	(  OP_BYTE_OFF_3  , "ld b,set 4,(iy%s)"), # 224 ld_B_SET_4_off_iy_d
	(  OP_BYTE_OFF_3  , "ld c,set 4,(iy%s)"), # 225 ld_C_SET_4_off_iy_d
	(  OP_BYTE_OFF_3  , "ld d,set 4,(iy%s)"), # 226 ld_D_SET_4_off_iy_d
	(  OP_BYTE_OFF_3  , "ld e,set 4,(iy%s)"), # 227 ld_E_SET_4_off_iy_d
	(  OP_BYTE_OFF_3  , "ld h,set 4,(iy%s)"), # 228 ld_H_SET_4_off_iy_d
	(  OP_BYTE_OFF_3  , "ld l,set 4,(iy%s)"), # 229 ld_L_SET_4_off_iy_d
	(  OP_BYTE_OFF_3  , "set 4,(iy%s)" ), # 230 SET_4_off_iy_d
	(  OP_BYTE_OFF_3  , "ld a,set 4,(iy%s)"), # 231 ld_A_SET_4_off_iy_d
	(  OP_BYTE_OFF_3  , "ld b,set 5,(iy%s)"), # 232 ld_B_SET_5_off_iy_d
	(  OP_BYTE_OFF_3  , "ld c,set 5,(iy%s)"), # 233 ld_C_SET_5_off_iy_d
	(  OP_BYTE_OFF_3  , "ld d,set 5,(iy%s)"), # 234 ld_D_SET_5_off_iy_d
	(  OP_BYTE_OFF_3  , "ld e,set 5,(iy%s)"), # 235 ld_E_SET_5_off_iy_d
	(  OP_BYTE_OFF_3  , "ld h,set 5,(iy%s)"), # 236 ld_H_SET_5_off_iy_d
	(  OP_BYTE_OFF_3  , "ld l,set 5,(iy%s)"), # 237 ld_L_SET_5_off_iy_d
	(  OP_BYTE_OFF_3  , "set 5,(iy%s)" ), # 238 SET_5_off_iy_d
	(  OP_BYTE_OFF_3  , "ld a,set 5,(iy%s)"), # 239 ld_A_SET_5_off_iy_d
	(  OP_BYTE_OFF_3  , "ld b,set 6,(iy%s)"), # 240 ld_B_SET_6_off_iy_d
	(  OP_BYTE_OFF_3  , "ld c,set 6,(iy%s)"), # 241 ld_C_SET_6_off_iy_d
	(  OP_BYTE_OFF_3  , "ld d,set 6,(iy%s)"), # 242 ld_D_SET_6_off_iy_d
	(  OP_BYTE_OFF_3  , "ld e,set 6,(iy%s)"), # 243 ld_E_SET_6_off_iy_d
	(  OP_BYTE_OFF_3  , "ld h,set 6,(iy%s)"), # 244 ld_H_SET_6_off_iy_d
	(  OP_BYTE_OFF_3  , "ld l,set 6,(iy%s)"), # 245 ld_L_SET_6_off_iy_d
	(  OP_BYTE_OFF_3  , "set 6,(iy%s)" ), # 246 SET_6_off_iy_d
	(  OP_BYTE_OFF_3  , "ld a,set 6,(iy%s)"), # 247 ld_A_SET_6_off_iy_d
	(  OP_BYTE_OFF_3  , "ld b,set 7,(iy%s)"), # 248 ld_B_SET_7_off_iy_d
	(  OP_BYTE_OFF_3  , "ld c,set 7,(iy%s)"), # 249 ld_C_SET_7_off_iy_d
	(  OP_BYTE_OFF_3  , "ld d,set 7,(iy%s)"), # 250 ld_D_SET_7_off_iy_d
	(  OP_BYTE_OFF_3  , "ld e,set 7,(iy%s)"), # 251 ld_E_SET_7_off_iy_d
	(  OP_BYTE_OFF_3  , "ld h,set 7,(iy%s)"), # 252 ld_H_SET_7_off_iy_d
	(  OP_BYTE_OFF_3  , "ld l,set 7,(iy%s)"), # 253 ld_L_SET_7_off_iy_d
	(  OP_BYTE_OFF_3  , "set 7,(iy%s)" ), # 254 SET_7_off_iy_d
	(  OP_BYTE_OFF_3  , "ld a,set 7,(iy%s)") # 255 ld_A_SET_7_off_iy_d
)

code = array.array('B')

label = [False] * 65536
defb = [False] * 65536

def read_data(begin, f):
    if begin < 0 or begin > 65535:
        raise ValueError("Start address must be between 0 and 65535")
    
    # Create array of correct size
    code = bytearray(65536)
    
    # Read the data
    try:
        if hasattr(f, 'seekable') and f.seekable():
            f.seek(0)
            data = f.read()
        else:
            # For non-seekable streams like stdin
            data = f.read()
            
        # Convert to bytes if it's not already
        if isinstance(data, str):
            data = data.encode('latin1')
            
        # Copy data starting at begin
        data_len = len(data)
        code[begin:begin+data_len] = data
        return begin + data_len - 1
        
    except IOError as e:
        print(f"Error reading input: {e}", file=sys.stderr)
        return begin
	
def process(begin, end, which):
	global current_opcode_table, second, label, defb

	current_opcode_table = opcodes_main
	second = which
	PC = begin
	while PC <= end:
		if second:
			if label[PC]:
				print_label(PC)
		if defb[PC]:
			increment, text = print_defb(PC)
			print_text(PC, text)
			PC += increment
			continue
		increment, text = print_code(PC)
		print_text(PC, text)
		PC += increment

def print_defb(PC):
	global second

	if not second:
		return 1, ''
	b = get_byte(PC)
	return 1, "defb %s" % hex_or_decimal(b)

def print_text(PC, text):
	global second, outfile, show_address

	if not second or not text:
		return
	if show_address:
		spaces = " " * (24 - len(text))
		a = "%s; %s" % (spaces, hex_or_decimal(PC))
	else:
		a = ''
	outfile.write("\t%s%s\n" % (text, a))

def first_pass(begin, end):
	process(begin, end, False)

def second_pass(begin, end):
	global outfile

	outfile.write("\torg %s\n" % hex_or_decimal(begin))
	process(begin, end, True)

def print_label(address):
	global outfile

	outfile.write(".Lab%s\n" % hex_or_decimal(address))

def op_none(PC, c, t):
	global current_opcode_table, second

	st = ''
	if second:
		if t[1] == NULL:
			st = "NOP"
		else:
			st = "%s" % t[1]
	current_opcode_table = opcodes_main
	return 1, st

def op_byte(PC, c, t):
	global current_opcode_table, second

	st = ''
	if second:
		b = get_byte(PC + 1)
		st = t[1] % hex_or_decimal(b)
	current_opcode_table = opcodes_main
	return 2, st

def op_byte_off(PC, c, t):
	global current_opcode_table, second

	st = ''
	if second:
		b = get_byte(PC + 1)
		if b > 127:
			b -= 256
			sign = ""
		else:
			sign = "+"
		st = t[1] % (sign + hex_or_decimal(b))
	current_opcode_table = opcodes_main
	return 2, st

def op_byte_off_3(PC, c, t):
	global current_opcode_table, second, dis

	st = ''
	if second:
		if dis > 127:
			dis -= 256
			sign = ""
		else:
			sign = "+"
		st = t[1] % (sign + hex_or_decimal(dis))
	current_opcode_table = opcodes_main
	return 1, st

def op_byte_off_2(PC, c, t):
	global current_opcode_table, second

	st = ''
	if second:
		b = get_byte(PC + 1)
		if b > 127:
			b -= 256
			sign = ""
		else:
			sign = "+"
		n = get_byte(PC + 2)
		st = t[1] % (sign + hex_or_decimal(b), hex_or_decimal(n))
	current_opcode_table = opcodes_main
	return 3, st

def op_word(PC, c, t):
	global current_opcode_table, second, label

	st = ''
	w = get_word(PC + 1)
	if second:
		st = t[1] % hex_or_decimal(w)
	else:
		label[w] = True
	current_opcode_table = opcodes_main
	return 3, st

def op_offset(PC, c, t):
	global current_opcode_table, second, label

	st = ''
	address = get_short(PC + 1)
	if second:
		st = t[1] % make_lab(address)
	else:
		label[address] = True
	current_opcode_table = opcodes_main
	return 2, st

def make_lab(address):
	return "Lab%s" % hex_or_decimal(address)

def op_jump(PC, c, t):
	global current_opcode_table, second, label

	st = ''
	w = get_word(PC + 1)
	if second:
		st = t[1] % make_lab(w)
	else:
		label[w] = True
	current_opcode_table = opcodes_main
	return 3, st

def op_cb(PC, c, t):
	global current_opcode_table

	current_opcode_table = opcodes_CB
	return 1, ''

def op_dd(PC, c, t):
	global current_opcode_table

	current_opcode_table = opcodes_DD
	return 1, ''

def op_ed(PC, c, t):
	global current_opcode_table

	current_opcode_table = opcodes_ED
	return 1, ''

def op_fd(PC, c, t):
	global current_opcode_table

	current_opcode_table = opcodes_FD
	return 1, ''

def op_ddcb(PC, c, t):
	global current_opcode_table, dis

	current_opcode_table = opcodes_DDCB
	dis = get_byte(PC + 1)
	return 2, ''

def op_fdcb(PC, c, t):
	global current_opcode_table, dis

	current_opcode_table = opcodes_FDCB
	dis = get_byte(PC + 1)
	return 2, ''

def print_code(PC):
	global code, current_opcode_table

	c = code[PC]
	t = current_opcode_table[c]
	f = func[t[0]]
	return f(PC, c, t)

def hex_or_decimal(v):
	global hexadecimal

	if hexadecimal:
		return str("%xh" % v)
	return str("%d" % v)

def get_short(a):
	global code

	a = a & 65535
	d = code[a]
	if d > 127:
		d -= 256
	address = ((a + 1) + d) & 65535
	return address

def get_byte(a):
	global code

	a = a & 65535
	return code[a]

def get_word(a):
	global code

	al = a & 65535
	ah = (al + 1) & 65535
	return 256 * code[ah] + code[al]

func = (
	op_none,
	op_byte,
	op_word,
	op_offset,
	op_jump,
	op_cb,
	op_dd,
	op_ed,
	op_fd,
	op_byte_off,
	op_byte_off_2,
	op_ddcb,
	op_fdcb,
	op_byte_off_3,
)

current_opcode_table = opcodes_main
dis = 0

def get_defb(text):
	global defb

	#print text
	for pairs in text.split(','):
		#print pairs
		start, end = pairs.split('-')
		start = int(start)
		end = int(end)
		if start < 0:
			start = 0
		if start > 65535:
			start = 65535
		if end < 0:
			end = 0
		if end > 65535:
			end = 65535
		for i in xrange(start, end+1):
			defb[i] = True

def main(config):
	global outfile, show_address

	begin = int(config["start"])
	if config["input"] == "sys.stdin":
		inp = sys.stdin
	else:
		inp = open(config["input"], "rb")
	end = read_data(begin, inp)
	inp.close()

	if config["output"] == "sys.stdout":
		outfile = sys.stdout
	else:
		outfile = open(config["output"], "rw")
	if config["binary"]:
		get_defb(config["binary"])

	if config["comments"]:
		show_address = True
	else:
		show_address = False

	first_pass(begin, end)
	second_pass(begin, end)
	outfile.close()

def config(a):
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Disassemble Z80 code")
    parser.add_argument("-c", '--comments', 
                       help="Show addresses of instructions after semicolon",
                       required=False, action="store_true")
    parser.add_argument("-b", '--binary', 
                       help="Addresses of binary data. Ranges separated by comma. For example 1000-2000,3000-4000",
                       required=False, default="", action="store")
    parser.add_argument("-i", '--input', 
                       help="Input filename. Default stdin", 
                       required=False, default="-", action="store")
    parser.add_argument("-o", '--output', 
                       help="Output filename. Default stdout", 
                       required=False, default="-", action="store")
    parser.add_argument("-s", '--start', 
                       help="Start address. Default 32768", 
                       required=False, default="32768", action="store")
    
    args = parser.parse_args(a)
    config = vars(args)

    # Handle input file
    if config['input'] == '-':
        config['input'] = sys.stdin.buffer  # Use buffer for binary reading
    else:
        try:
            config['input'] = open(config['input'], 'rb')
        except IOError as e:
            print(f"Error opening input file: {e}", file=sys.stderr)
            sys.exit(1)

    # Handle output file
    if config['output'] == '-':
        config['output'] = sys.stdout
    else:
        try:
            config['output'] = open(config['output'], 'w')
        except IOError as e:
            print(f"Error opening output file: {e}", file=sys.stderr)
            if config['input'] != sys.stdin.buffer:
                config['input'].close()
            sys.exit(1)

    try:
        main(config)
    finally:
        # Clean up file handles
        if config['input'] != sys.stdin.buffer:
            config['input'].close()
        if config['output'] != sys.stdout:
            config['output'].close()

if __name__ == "__main__":
    import sys
    config(sys.argv[1:])