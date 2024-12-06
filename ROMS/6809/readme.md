Instructions to build the 6809 basic interpreter

- must run in dosbox
as9 basic.asm -now l s19              

srec_cat basic.s19 -fill 0xFF -within basic.s19 -range-pad 32 -o basic.hex -intel -data-only -address-length=2

python hex_addr_remap.py E000 basic.hex >basic_remap.hex

remove the 1st 2 lines from basic_remap.hex
