//============================================================================
//  Grant’s multi computer
// 
//  Port to MiSTer.
//
//  Based on Grant’s multi computer
//  http://searle.hostei.com/grant/
//  http://searle.hostei.com/grant/Multicomp/index.html
//	 and WiSo's collector blog (MiST port)
//	 https://ws0.org/building-your-own-custom-computer-with-the-mist-fpga-board-part-1/
//	 https://ws0.org/building-your-own-custom-computer-with-the-mist-fpga-board-part-2/
//
//  This program is free software; you can redistribute it and/or modify it
//  under the terms of the GNU General Public License as published by the Free
//  Software Foundation; either version 2 of the License, or (at your option)
//  any later version.
//
//  This program is distributed in the hope that it will be useful, but WITHOUT
//  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
//  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
//  more details.
//
//  You should have received a copy of the GNU General Public License along
//  with this program; if not, write to the Free Software Foundation, Inc.,
//  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
//============================================================================


module emu
(
	//Master input clock
	input         CLK_50M,

	//Async reset from top-level module.
	//Can be used as initial reset.
	input         RESET,

	//Must be passed to hps_io module
	inout  [45:0] HPS_BUS,

	//Base video clock. Usually equals to CLK_SYS.
	output        CLK_VIDEO,

	//Multiple resolutions are supported using different CE_PIXEL rates.
	//Must be based on CLK_VIDEO
	output        CE_PIXEL,

	//Video aspect ratio for HDMI. Most retro systems have ratio 4:3.
	output  [7:0] VIDEO_ARX,
	output  [7:0] VIDEO_ARY,

	output  [7:0] VGA_R,
	output  [7:0] VGA_G,
	output  [7:0] VGA_B,
	output        VGA_HS,
	output        VGA_VS,
	output        VGA_DE,    // = ~(VBlank | HBlank)
	output        VGA_F1,
	output [1:0]  VGA_SL,

	/*
	// Use framebuffer from DDRAM (USE_FB=1 in qsf)
	// FB_FORMAT:
	//    [2:0] : 011=8bpp(palette) 100=16bpp 101=24bpp 110=32bpp
	//    [3]   : 0=16bits 565 1=16bits 1555
	//    [4]   : 0=RGB  1=BGR (for 16/24/32 modes)
	//
	// FB_STRIDE either 0 (rounded to 256 bytes) or multiple of 16 bytes.
	output        FB_EN,
	output  [4:0] FB_FORMAT,
	output [11:0] FB_WIDTH,
	output [11:0] FB_HEIGHT,
	output [31:0] FB_BASE,
	output [13:0] FB_STRIDE,
	input         FB_VBL,
	input         FB_LL,
	output        FB_FORCE_BLANK,

	// Palette control for 8bit modes.
	// Ignored for other video modes.
	output        FB_PAL_CLK,
	output  [7:0] FB_PAL_ADDR,
	output [23:0] FB_PAL_DOUT,
	input  [23:0] FB_PAL_DIN,
	output        FB_PAL_WR,
	*/

	output        LED_USER,  // 1 - ON, 0 - OFF.

	// b[1]: 0 - LED status is system status OR'd with b[0]
	//       1 - LED status is controled solely by b[0]
	// hint: supply 2'b00 to let the system control the LED.
	output  [1:0] LED_POWER,
	output  [1:0] LED_DISK,

	// I/O board button press simulation (active high)
	// b[1]: user button
	// b[0]: osd button
	output  [1:0] BUTTONS,

	input         CLK_AUDIO, // 24.576 MHz
	output [15:0] AUDIO_L,
	output [15:0] AUDIO_R,
	output        AUDIO_S,   // 1 - signed audio samples, 0 - unsigned
	output  [1:0] AUDIO_MIX, // 0 - no mix, 1 - 25%, 2 - 50%, 3 - 100% (mono)

	//ADC
	inout   [3:0] ADC_BUS,

	//SD-SPI SECONDARY SDCARD
	output        SD_SCK,
	output        SD_MOSI,
	input         SD_MISO,
	output        SD_CS,
	input         SD_CD,

	//High latency DDR3 RAM interface
	//Use for non-critical time purposes
	output        DDRAM_CLK,
	input         DDRAM_BUSY,
	output  [7:0] DDRAM_BURSTCNT,
	output [28:0] DDRAM_ADDR,
	input  [63:0] DDRAM_DOUT,
	input         DDRAM_DOUT_READY,
	output        DDRAM_RD,
	output [63:0] DDRAM_DIN,
	output  [7:0] DDRAM_BE,
	output        DDRAM_WE,

	//SDRAM interface with lower latency
	output        SDRAM_CLK,
	output        SDRAM_CKE,
	output [12:0] SDRAM_A,
	output  [1:0] SDRAM_BA,
	inout  [15:0] SDRAM_DQ,
	output        SDRAM_DQML,
	output        SDRAM_DQMH,
	output        SDRAM_nCS,
	output        SDRAM_nCAS,
	output        SDRAM_nRAS,
	output        SDRAM_nWE,

	input         UART_CTS,
	output        UART_RTS,
	input         UART_RXD,
	output        UART_TXD,
	output        UART_DTR,
	input         UART_DSR,

	// Open-drain User port.
	// 0 - D+/RX
	// 1 - D-/TX
	// 2..6 - USR2..USR6
	// Set USER_OUT to 1 to read from USER_IN.
	input   [6:0] USER_IN,
	output  [6:0] USER_OUT,

	input         OSD_STATUS
);

assign ADC_BUS  = 'Z;
assign {SD_SCK, SD_MOSI, SD_CS} = 'Z;
assign {SDRAM_DQ, SDRAM_A, SDRAM_BA, SDRAM_CLK, SDRAM_CKE, SDRAM_DQML, SDRAM_DQMH, SDRAM_nWE, SDRAM_nCAS, SDRAM_nRAS, SDRAM_nCS} = 'Z;
assign {DDRAM_CLK, DDRAM_BURSTCNT, DDRAM_ADDR, DDRAM_DIN, DDRAM_BE, DDRAM_RD, DDRAM_WE} = 0;

//assign UART_DTR = 1;
assign UART_DTR = UART_DSR;

assign LED_USER  = vsd_sel & sd_act;
assign LED_DISK  = ~driveLED;
assign LED_POWER = 0;
assign BUTTONS = 0;

assign VIDEO_ARX = 4;
assign VIDEO_ARY = 3;
assign VGA_SL = 0;
assign VGA_F1 = 0;

assign AUDIO_S = 0;
assign AUDIO_L = 0;
assign AUDIO_R = 0;
assign AUDIO_MIX = 0;

// enable input on USER_IO[3] for ch376s MISO
assign USER_OUT[3] = 1'b1;

`include "build_id.v"
localparam CONF_STR = {
	"MultiComp;;",
	"S,IMG;",
	"OE,Reset after Mount,No,Yes;",
	"-;",
	"O78,CPU-ROM,Z80-CP/M,Z80-BASIC,6502-Basic,6809-Basic;",
	"-;",
	"RA,Reset;",
	"V,v",`BUILD_DATE
};

//////////////////   HPS I/O   ///////////////////
wire  [1:0] buttons;
wire [31:0] status;

wire PS2_CLK;
wire PS2_DAT;

wire forced_scandoubler;

wire [31:0] sd_lba;
wire        sd_rd;
wire        sd_wr;
wire        sd_ack;
wire  [8:0] sd_buff_addr;
wire  [7:0] sd_buff_dout;
wire  [7:0] sd_buff_din;
wire        sd_buff_wr;
wire        sd_ack_conf;
wire        img_mounted;
wire        img_readonly;
wire [63:0] img_size;

hps_io #(
	.STRLEN($size(CONF_STR)>>3),
	.PS2DIV (2000)
	) hps_io
(
	.clk_sys(CLK_50M),
	.HPS_BUS(HPS_BUS),

	.conf_str(CONF_STR),

	.buttons(buttons),
	.status(status),
	.forced_scandoubler(forced_scandoubler),

	.ps2_kbd_clk_out(PS2_CLK),
	.ps2_kbd_data_out(PS2_DAT),

	.sd_lba(sd_lba),
	.sd_rd(sd_rd),
	.sd_wr(sd_wr),
	.sd_ack(sd_ack),
	.sd_ack_conf(sd_ack_conf),
	.sd_buff_addr(sd_buff_addr),
	.sd_buff_dout(sd_buff_dout),
	.sd_buff_din(sd_buff_din),
	.sd_buff_wr(sd_buff_wr),

	.img_mounted(img_mounted),
	.img_readonly(img_readonly),
	.img_size(img_size),

	.uart_mode(16'b000_11111_000_11111)
);

///////////////////////   CLOCKS   ///////////////////////////////
wire clk_sys, locked;

pll pll
(
	.refclk(CLK_50M),
	.rst(0),
	.outclk_0(clk_sys),
	.locked(locked)
);

/////////////////  RESET  /////////////////////////

wire reset = RESET | status[0] | buttons[1] | status[10] | (status[14] && img_mounted);

/////////////////  SDCARD  ////////////////////////

wire sdclk;
wire sdmosi;
wire sdmiso = vsd_sel ? vsdmiso : SD_MISO;
wire sdss;

wire vsdmiso;
reg vsd_sel = 0;

always @(posedge clk_sys) if(img_mounted) vsd_sel <= |img_size;

sd_card sd_card
(
	.*,

	.clk_spi(clk_sys),
	.sdhc(1),
	.sck(sdclk),
	.ss(sdss | ~vsd_sel),
	.mosi(sdmosi),
	.miso(vsdmiso)
);

assign SD_CS   = sdss   |  vsd_sel;
assign SD_SCK  = sdclk  & ~vsd_sel;
assign SD_MOSI = sdmosi & ~vsd_sel;

reg sd_act;

always @(posedge clk_sys) begin
	reg old_mosi, old_miso;
	integer timeout = 0;

	old_mosi <= sdmosi;
	old_miso <= sdmiso;

	sd_act <= 0;
	if(timeout < 1000000) begin
		timeout <= timeout + 1;
		sd_act <= 1;
	end

	if((old_mosi ^ sdmosi) || (old_miso ^ sdmiso)) timeout <= 0;
end

///////////////////////////////////////////////////

assign CLK_VIDEO = clk_sys;

typedef enum {cpuZ80CPM='b00, cpuZ80Basic='b01, cpu6502Basic='b10, cpu6809Basic='b11} cpu_type_enum;
wire [1:0] cpu_type = status[8:7];

wire hblank, vblank;
wire hs, vs;
wire [1:0] r,g,b;
wire driveLED;

wire [3:0] _hblank, _vblank;
wire [3:0] _hs, _vs;
wire [1:0] _r[3:0], _g[3:0], _b[3:0];
wire [3:0] _driveLED;
wire [3:0] _CE_PIXEL;
wire [3:0] _SD_CS;
wire [3:0] _SD_MOSI;
wire [3:0] _SD_SCK;
wire [3:0] _txd;
wire [3:0] _dtr;
wire [3:0] _rts;


always_comb 
begin
	hblank 		<= _hblank[cpu_type];
	vblank 		<= _vblank[cpu_type];
	hs 		 	<= _hs[cpu_type];
	vs			<= _vs[cpu_type];
	r 			<= _r[cpu_type][1:0];
	g 			<= _g[cpu_type][1:0];
	b			<= _b[cpu_type][1:0];
	CE_PIXEL	<= _CE_PIXEL[cpu_type];
	sdss		<= _SD_CS[cpu_type];
	sdmosi		<= _SD_MOSI[cpu_type];
	sdclk		<= _SD_SCK[cpu_type];
	driveLED 	<= _driveLED[cpu_type];
	UART_TXD	<= _txd[cpu_type]; 
	UART_RTS        <= _rts[cpu_type]; 
end
/*
reg [6:0] test;
reg [4:0] mycnt;
initial test = 0;
initial mycnt = 0;
always @(posedge clk_sys) begin
	if (mycnt>25) begin
		test <= test + 1'b1;
		mycnt <= 0;
	end
	else begin
		mycnt <= mycnt + 1'b1;
	end

	USER_OUT[0] <= test[0];
	USER_OUT[1] <= test[1];
	USER_OUT[2] <= test[2];
	USER_OUT[3] <= test[3];
	USER_OUT[4] <= test[4];
	USER_OUT[5] <= test[5];
	USER_OUT[6] <= test[6];
end
*/
MicrocomputerZ80CPM MicrocomputerZ80CPM
(
	.N_RESET	(~reset & cpu_type == cpuZ80CPM),
	.clk		(cpu_type == cpuZ80CPM ? clk_sys : 0),
	.R			(_r[0][1:0]),
	.G			(_g[0][1:0]),
	.B			(_b[0][1:0]),
	.HS			(_hs[0]),
	.VS			(_vs[0]),
	.hBlank		(_hblank[0]),
	.vBlank		(_vblank[0]),
	.cepix		(_CE_PIXEL[0]),
	.ps2Clk		(PS2_CLK),
	.ps2Data	(PS2_DAT),
	.sdCS		(_SD_CS[0]),
	.sdMOSI		(_SD_MOSI[0]),
	.sdMISO		(sdmiso),
	.sdSCLK		(_SD_SCK[0]),
	.driveLED	(_driveLED[0]),
	.rxd1 		(UART_RXD),
	.txd1 		(_txd[0]),
	.rts1           (_rts[0]),
	.cts1           (UART_CTS),
	// CH376s via USERIO
	.usbSCLK 	(USER_OUT[2]),
	.usbMISO 	(USER_IN[3]),
	.usbMOSI 	(USER_OUT[4]),
	.usbCS 		(USER_OUT[5])
);

MicrocomputerZ80Basic MicrocomputerZ80Basic
(
	.N_RESET(~reset & cpu_type == cpuZ80Basic),
	.clk(cpu_type == cpuZ80Basic ? clk_sys : 0),
	.R(_r[1][1:0]),
	.G(_g[1][1:0]),
	.B(_b[1][1:0]),
	.HS(_hs[1]),
	.VS(_vs[1]),
	.hBlank(_hblank[1]),
	.vBlank(_vblank[1]),
	.cepix(_CE_PIXEL[1]),
	.ps2Clk(PS2_CLK),
	.ps2Data(PS2_DAT),
	.sdCS(_SD_CS[1]),
	.sdMOSI(_SD_MOSI[1]),
	.sdMISO(sdmiso),
	.sdSCLK(_SD_SCK[1]),
	.driveLED(_driveLED[1]),
	.rxd1 (UART_RXD),
	.txd1 (_txd[1])
);

Microcomputer6502Basic Microcomputer6502Basic
(
	.N_RESET(~reset & cpu_type == cpu6502Basic),
	.clk(cpu_type == cpu6502Basic ? clk_sys : 0),
	.R(_r[2][1:0]),
	.G(_g[2][1:0]),
	.B(_b[2][1:0]),
	.HS(_hs[2]),
	.VS(_vs[2]),
	.hBlank(_hblank[2]),
	.vBlank(_vblank[2]),
	.cepix(_CE_PIXEL[2]),
	.ps2Clk(PS2_CLK),
	.ps2Data(PS2_DAT),
	.sdCS(_SD_CS[2]),
	.sdMOSI(_SD_MOSI[2]),
	.sdMISO(sdmiso),
	.sdSCLK(_SD_SCK[2]),
	.driveLED(_driveLED[2]),
	.rxd1 (UART_RXD),
	.txd1 (_txd[2])
);

//Reset is not working (even on the original Grant's 6809)
Microcomputer6809Basic Microcomputer6809Basic
(
	.N_RESET(~reset & cpu_type == cpu6809Basic),
	.clk(cpu_type == cpu6809Basic ? clk_sys : 0),
	.R(_r[3][1:0]),
	.G(_g[3][1:0]),
	.B(_b[3][1:0]),
	.HS(_hs[3]),
	.VS(_vs[3]),
	.hBlank(_hblank[3]),
	.vBlank(_vblank[3]),
	.cepix(_CE_PIXEL[3]),
	.ps2Clk(PS2_CLK),
	.ps2Data(PS2_DAT),
	.sdCS(_SD_CS[3]),
	.sdMOSI(_SD_MOSI[3]),
	.sdMISO(sdmiso),
	.sdSCLK(_SD_SCK[3]),
	.driveLED(_driveLED[3]),
	.rxd1 (UART_RXD),
	.txd1 (_txd[3])
);

video_cleaner video_cleaner
(
	.clk_vid(CLK_VIDEO),
	.ce_pix(CE_PIXEL),

	.R({4{r}}),
	.G({4{g}}),
	.B({4{b}}),
	.HSync(hs),
	.VSync(vs),
	.HBlank(hblank),
	.VBlank(vblank),

	.VGA_R(VGA_R),
	.VGA_G(VGA_G),
	.VGA_B(VGA_B),
	.VGA_VS(VGA_VS),
	.VGA_HS(VGA_HS),
	.VGA_DE(VGA_DE)
);


endmodule
