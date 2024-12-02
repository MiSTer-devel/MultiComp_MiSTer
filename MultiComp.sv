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
	// 2..6 - RTS,CTS,DTR,DSR,IO6
	// Set USER_OUT to 1 to read from USER_IN.
	input   [6:0] USER_IN,
	output  [6:0] USER_OUT,

	input         OSD_STATUS
);


// User Port - extra USB 3.1A style connector on MiSTer
//
// USB	P7	Name PIN	Mister	emu wire
// 1	+5V	+5V			
// 2	2	TX	SDA		AH9		USER_IO[1]
// 3	1	RX	SCL		AG11	USER_IO[0]
// 4	GND	GND			
// 5	8	DSR	IO10	AF15	USER_IO[5]
// 6	7	DTR	IO11	AG16	USER_IO[4]
// 7	6	CTS	IO12	AH11	USER_IO[3]
// 8	5	RTS	IO13	AH12	USER_IO[2]
// 9	10	IO6	IO8		AF17	USER_IO[6]

// FT232 USB to serial cable
//          sig     usb io connector
// Red	 	5V
// Black 	GND		GND
// White	RXD		2
// Green	TXD		3
// Yellow	RTS		7
// Blue		CTS     8

// Define meaningful names for USER_IO signals
// Input pins (USER_IN)
wire user_rx      = USER_IN[0];    // Serial RX from USER_IO port
wire user_cts     = USER_IN[3];    // CTS from USER_IO port 
// USER_IN[1] unused
// USER_IN[2] unused
// USER_IN[4:6] unused

// Output pins (USER_OUT) 
// Active high enables for input pins
wire user_rx_en   = USER_OUT[0];    // Enable RX input
wire user_tx      = USER_OUT[1];    // Serial TX to USER_IO port
wire user_rts     = USER_OUT[2];    // RTS to USER_IO port
wire user_cts_en  = USER_OUT[3];    // Enable CTS input
// USER_OUT[4:6] unused

assign ADC_BUS  = 'Z;
//assign {SD_SCK, SD_MOSI, SD_CS} = 'Z;
assign {SDRAM_DQ, SDRAM_A, SDRAM_BA, SDRAM_CLK, SDRAM_CKE, SDRAM_DQML, SDRAM_DQMH, SDRAM_nWE, SDRAM_nCAS, SDRAM_nRAS, SDRAM_nCS} = 'Z;
assign {DDRAM_CLK, DDRAM_BURSTCNT, DDRAM_ADDR, DDRAM_DIN, DDRAM_BE, DDRAM_RD, DDRAM_WE} = 0;

//assign UART_RTS = UART_CTS;
assign UART_DTR = UART_DSR;

assign LED_POWER = 0;
assign BUTTONS = 0;

assign VIDEO_ARX = 4;
assign VIDEO_ARY = 3;
assign VGA_SL = 0;
assign VGA_F1 = 0;
assign VGA_SCALER = 1;

assign AUDIO_S = 0;
assign AUDIO_L = 0;
assign AUDIO_R = 0;
assign AUDIO_MIX = 0;

`include "build_id.v"
localparam CONF_STR = {
	"MultiComp;;",
	"S,IMG;",
	"OF,Reset after Mount,No,Yes;", 
	"-;",
	"O78,CPU-ROM,Z80-CP/M,Z80-BASIC,6502-Basic,6809-Basic;",
	"-;",
	"O9B,Baud Rate tty,115200,38400,19200,9600,4800,2400;",
	"OC,Serial Port,Console Port,User IO Port;",
	"OE,Flow Control,None,RTS/CTS;",  // New flow control option
	"OD,Storage Controller,SD Controller,Image Controller;",
	"-;",
	"RE,Reset;",
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

wire reset = RESET | status[0] | buttons[1] | (status[15] && img_mounted);

/////////////////  SDCARD  ////////////////////////

// SD card interface signal declarations
// _sd suffix for SD controller signals
// _img suffix for image controller signals 
// _mux suffix for multiplexed signals 
wire sdclk_sd, sdmosi_sd, sdcs_sd;        // SD controller outputs
wire sdclk_img, sdmosi_img, sdcs_img;     // Image controller outputs
wire driveLED_sd, driveLED_img;           // Drive activity indicators

// Multiplexed signals that route to physical SD interface
wire sdclk_mux, sdmosi_mux, sdcs_mux;     // Multiplexed control signals
wire sdmiso_mux;                          // Multiplexed data input
wire driveLED_mux;                        // Multiplexed activity indicator

// Controller selection - determines which controller drives SD interface
wire storage_ctrl_select = status[13];     // 0=SD controller, 1=image controller 

// Multiplex between SD and image controller outputs
assign sdclk_mux = storage_ctrl_select ? sdclk_img : sdclk_sd;    // Clock output
assign sdmosi_mux = storage_ctrl_select ? sdmosi_img : sdmosi_sd; // Data output to SD
assign sdcs_mux = storage_ctrl_select ? sdcs_img : sdcs_sd;       // Chip select
assign driveLED_mux = storage_ctrl_select ? driveLED_img : driveLED_sd; // Activity LED

// MISO input routing - selects between SD card and virtual SD based on vsd_sel
assign sdmiso_mux = vsd_sel ? vsdmiso : SD_MISO;

// Virtual SD interface enable
reg vsd_sel = 0;
always @(posedge clk_sys) if(img_mounted) vsd_sel <= |img_size;

// Map multiplexed signals to physical SD interface
// Keep physical SD enabled when using SD controller
assign SD_SCK = (vsd_sel || !storage_ctrl_select) ? sdclk_mux : 1'bZ;   
assign SD_MOSI = (vsd_sel || !storage_ctrl_select) ? sdmosi_mux : 1'bZ;  
assign SD_CS = (vsd_sel || !storage_ctrl_select) ? sdcs_mux : 1'bZ;

// Serial port selection
wire serial_port_select = status[12];    // 0 = Console Port (UART), 1 = User IO Port

// Flow control enable
wire flow_control_enable = status[14];    // 0 = No flow control, 1 = RTS/CTS enabled

// Serial interface routing 
wire serial_rx = serial_port_select ? user_rx : UART_RXD;
wire serial_tx;

localparam INIT_TIMEOUT = 24'd50000; // 1ms at 50MHz clock
reg [23:0] init_counter = 0;
reg init_complete = 0;

always @(posedge clk_sys) begin
    if (reset) begin
        init_complete <= 0;
        init_counter <= 0;
    end
    else if (!init_complete) begin
        if (init_counter == INIT_TIMEOUT) begin
            init_complete <= 1;
        end
        else begin
            init_counter <= init_counter + 1;
        end
    end
end

// CTS handling - active low when flow control enabled
wire serial_cts = flow_control_enable ? 
                (init_complete ? (serial_port_select ? user_cts : UART_CTS) : 1'b0) :
                1'b0;

// Serial interface output routing
wire serial_rts;  // RTS signal from CPUs

// Serial port output routing
assign UART_TXD = serial_port_select ? 1'b1 : serial_tx;
assign UART_RTS = (serial_port_select || !flow_control_enable) ? 1'b1 : serial_rts;


// USER_IO port control - single assignment for all outputs
assign USER_OUT = {
    3'b0,          // [6:4] unused
    serial_port_select && flow_control_enable,    // [3] CTS input enable
    (serial_port_select && flow_control_enable) ? serial_rts : 1'b1,    // [2] RTS output
    serial_port_select ? serial_tx : 1'b1,    // [1] TX output
    serial_port_select     // [0] RX input enable
};

// Connect the read-only signals to the USER_OUT bits for monitoring
assign user_rx_en 	= USER_OUT[0];
assign user_tx 		= USER_OUT[1];
assign user_rts 	= USER_OUT[2];
assign user_cts_en 	= USER_OUT[3];

// Virtual SD card implementation
sd_card sd_card
(
    .*,
    .clk_spi(clk_sys),
    .sdhc(1),
    .sck(sdclk_mux),
    .ss(sdcs_mux | ~vsd_sel),
    .mosi(sdmosi_mux),
    .miso(vsdmiso)
);

// Drive activity detection
reg sd_act;
always @(posedge clk_sys) begin
    reg old_mosi, old_miso;
    integer timeout = 0;

    old_mosi <= sdmosi_mux;
    old_miso <= sdmiso_mux;

    sd_act <= 0;
    if(timeout < 1000000) begin
        timeout <= timeout + 1;
        sd_act <= 1;
    end

    if((old_mosi ^ sdmosi_mux) || (old_miso ^ sdmiso_mux)) timeout <= 0;
end

// Map drive LED to system LED output
assign LED_USER = vsd_sel & sd_act;
assign LED_DISK = {2{~driveLED_mux}};

///////////////////////////////////////////////////

assign CLK_VIDEO = clk_sys;

typedef enum {cpuZ80CPM='b00, cpuZ80Basic='b01, cpu6502Basic='b10, cpu6809Basic='b11} cpu_type_enum;
wire [1:0] cpu_type = status[8:7];

typedef enum {baud115200='b000, baud38400='b001, baud19200='b010, baud9600='b011, baud4800='b100, baud2400='b101} baud_rate_enum;
wire [2:0] baud_rate = status[11:9];

wire hblank, vblank;
wire hs, vs;
wire [1:0] r,g,b;

wire [3:0] _hblank, _vblank;
wire [3:0] _hs, _vs;
wire [1:0] _r[3:0], _g[3:0], _b[3:0];
wire [3:0] _CE_PIXEL;
wire [3:0] _txd;
wire [3:0] _rts;  // RTS signals from CPUs

// Define signal arrays for each microcomputer's SD interface
wire [3:0] sdcs_ctrl;    // SD chip select signals from controllers
wire [3:0] sdmosi_ctrl;  // SD MOSI signals from controllers
wire [3:0] sdclk_ctrl;   // SD clock signals from controllers
wire [3:0] driveLED_ctrl; // Drive LED signals from controllers

// Add baud rate selection logic
reg [15:0] baud_increment;
always @(*) begin
    case(baud_rate)
        baud115200: baud_increment = 16'd2416;  // 115200
        baud38400:  baud_increment = 16'd805;   // 38400
        baud19200:  baud_increment = 16'd403;   // 19200
        baud9600:   baud_increment = 16'd201;   // 9600
        baud4800:   baud_increment = 16'd101;   // 4800
        baud2400:   baud_increment = 16'd50;    // 2400
        default:    baud_increment = 16'd2416;  // Default to 115200
    endcase
end

always_comb 
begin
    hblank      <= _hblank[cpu_type];
    vblank      <= _vblank[cpu_type];
    hs          <= _hs[cpu_type];
    vs          <= _vs[cpu_type];
    r           <= _r[cpu_type][1:0];
    g           <= _g[cpu_type][1:0];
    b           <= _b[cpu_type][1:0];
    CE_PIXEL    <= _CE_PIXEL[cpu_type];
    serial_tx   <= _txd[cpu_type];
    serial_rts  <= _rts[cpu_type];

    // Override based on selected CPU
    case(cpu_type)
        cpuZ80CPM: begin
            sdcs_sd = sdcs_ctrl[cpuZ80CPM];
            sdmosi_sd = sdmosi_ctrl[cpuZ80CPM];
            sdclk_sd = sdclk_ctrl[cpuZ80CPM];
            driveLED_sd = driveLED_ctrl[cpuZ80CPM];
        end
        cpuZ80Basic: begin
            sdcs_sd = sdcs_ctrl[cpuZ80Basic];
            sdmosi_sd = sdmosi_ctrl[cpuZ80Basic];
            sdclk_sd = sdclk_ctrl[cpuZ80Basic];
            driveLED_sd = driveLED_ctrl[cpuZ80Basic];
        end
        cpu6502Basic: begin
            sdcs_sd = sdcs_ctrl[cpu6502Basic];
            sdmosi_sd = sdmosi_ctrl[cpu6502Basic];
            sdclk_sd = sdclk_ctrl[cpu6502Basic];
            driveLED_sd = driveLED_ctrl[cpu6502Basic];
        end
        cpu6809Basic: begin
            sdcs_sd = sdcs_ctrl[cpu6809Basic];
            sdmosi_sd = sdmosi_ctrl[cpu6809Basic];
            sdclk_sd = sdclk_ctrl[cpu6809Basic];
            driveLED_sd = driveLED_ctrl[cpu6809Basic];
        end
    endcase
end

MicrocomputerZ80CPM MicrocomputerZ80CPM
(
    .N_RESET(~reset & cpu_type == cpuZ80CPM),
    .clk(cpu_type == cpuZ80CPM ? clk_sys : 0),
    .baud_increment(baud_increment),
    .R(_r[cpuZ80CPM][1:0]),
    .G(_g[cpuZ80CPM][1:0]), 
    .B(_b[cpuZ80CPM][1:0]),
    .HS(_hs[cpuZ80CPM]),
    .VS(_vs[cpuZ80CPM]),
    .hBlank(_hblank[cpuZ80CPM]),
    .vBlank(_vblank[cpuZ80CPM]),
    .cepix(_CE_PIXEL[cpuZ80CPM]),
    .ps2Clk(PS2_CLK),
    .ps2Data(PS2_DAT),
    .sdCS(sdcs_ctrl[cpuZ80CPM]),
    .sdMOSI(sdmosi_ctrl[cpuZ80CPM]),
    .sdMISO(sdmiso_mux),
    .sdSCLK(sdclk_ctrl[cpuZ80CPM]),
    .driveLED(driveLED_ctrl[cpuZ80CPM]),
    .sd_ctrl_sel(storage_ctrl_select),
    .rxd1(serial_rx),
    .txd1(_txd[cpuZ80CPM]),
    .rts1(_rts[cpuZ80CPM]),
    .cts1(serial_cts)
);

MicrocomputerZ80Basic MicrocomputerZ80Basic
(
    .N_RESET(~reset & cpu_type == cpuZ80Basic),
    .clk(cpu_type == cpuZ80Basic ? clk_sys : 0),
    .baud_increment(baud_increment),
    .R(_r[cpuZ80Basic][1:0]),
    .G(_g[cpuZ80Basic][1:0]),
    .B(_b[cpuZ80Basic][1:0]),
    .HS(_hs[cpuZ80Basic]),
    .VS(_vs[cpuZ80Basic]),
    .hBlank(_hblank[cpuZ80Basic]),
    .vBlank(_vblank[cpuZ80Basic]),
    .cepix(_CE_PIXEL[cpuZ80Basic]),
    .ps2Clk(PS2_CLK),
    .ps2Data(PS2_DAT),
    .sdCS(sdcs_ctrl[cpuZ80Basic]),
    .sdMOSI(sdmosi_ctrl[cpuZ80Basic]), 
    .sdMISO(sdmiso_mux),
    .sdSCLK(sdclk_ctrl[cpuZ80Basic]),
    .driveLED(driveLED_ctrl[cpuZ80Basic]),
    .sd_ctrl_sel(storage_ctrl_select),
    .rxd1(serial_rx),
    .txd1(_txd[cpuZ80Basic]),
    .rts1(_rts[cpuZ80Basic]),
    .cts1(serial_cts)
);

Microcomputer6502Basic Microcomputer6502Basic
(
    .N_RESET(~reset & cpu_type == cpu6502Basic),
    .clk(cpu_type == cpu6502Basic ? clk_sys : 0),
    .baud_increment(baud_increment),
    .R(_r[cpu6502Basic][1:0]),
    .G(_g[cpu6502Basic][1:0]),
    .B(_b[cpu6502Basic][1:0]),
    .HS(_hs[cpu6502Basic]),
    .VS(_vs[cpu6502Basic]),
    .hBlank(_hblank[cpu6502Basic]),
    .vBlank(_vblank[cpu6502Basic]),
    .cepix(_CE_PIXEL[cpu6502Basic]),
    .ps2Clk(PS2_CLK),
    .ps2Data(PS2_DAT),
    .sdCS(sdcs_ctrl[cpu6502Basic]),
    .sdMOSI(sdmosi_ctrl[cpu6502Basic]),
    .sdMISO(sdmiso_mux),
    .sdSCLK(sdclk_ctrl[cpu6502Basic]),
    .driveLED(driveLED_ctrl[cpu6502Basic]),
    .sd_ctrl_sel(storage_ctrl_select),
    .rxd1(serial_rx),
    .txd1(_txd[cpu6502Basic]),
    .rts1(_rts[cpu6502Basic]),
    .cts1(serial_cts)
);

//Reset is not working (even on the original Grant's 6809)
Microcomputer6809Basic Microcomputer6809Basic
(
    .N_RESET(~reset & cpu_type == cpu6809Basic),
    .clk(cpu_type == cpu6809Basic ? clk_sys : 0),
    .baud_increment(baud_increment),
    .R(_r[cpu6809Basic][1:0]),
    .G(_g[cpu6809Basic][1:0]),
    .B(_b[cpu6809Basic][1:0]),
    .HS(_hs[cpu6809Basic]),
    .VS(_vs[cpu6809Basic]),
    .hBlank(_hblank[cpu6809Basic]),
    .vBlank(_vblank[cpu6809Basic]),
    .cepix(_CE_PIXEL[cpu6809Basic]),
    .ps2Clk(PS2_CLK),
    .ps2Data(PS2_DAT),
    .sdCS(sdcs_ctrl[cpu6809Basic]),
    .sdMOSI(sdmosi_ctrl[cpu6809Basic]),
    .sdMISO(sdmiso_mux),
    .sdSCLK(sdclk_ctrl[cpu6809Basic]),
    .driveLED(driveLED_ctrl[cpu6809Basic]),
    .sd_ctrl_sel(storage_ctrl_select),
    .rxd1(serial_rx),
    .txd1(_txd[cpu6809Basic]),
    .rts1(_rts[cpu6809Basic]),
    .cts1(serial_cts)
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
