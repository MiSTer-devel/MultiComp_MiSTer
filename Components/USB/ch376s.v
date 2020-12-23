module ch376s
(
  	// interface
	input       clk,  // system clock
  	input       rd,
   input       wr,
  	input       reset,
   input       a0,
	
	// SPI wires
	output      sck,  // SCK
   output      sdcs, // SCS
	output      sdo,  // MOSI
	input       sdi,  // MISO

  	// data
   input    [7:0] din,
  	output 	[7:0] dout
  
);
  
  wire _ready;
  wire [7:0] _dout;
  
  spi SPI_Master
  (
   	// Control/Data Signals,
    .clk(clk),         // FPGA Clock
    .reset (reset),
    .ready (_ready),
   
   	// TX (MOSI) Signals
    .din(din),  // Byte to transmit on MOSI
    .wr (wr),    // Data Valid Pulse with i_TX_Byte
   
   	// RX (MISO) Signals
    .dout(_dout),     // Byte received on MISO
    .rd (rd),

   	// SPI Interface
    .sck(sck),
    .sdi(sdi),
    .sdo(sdo),
    .sdcs (sdcs)
   );
  
  assign dout=rd ? (a0 ? {7'b0000000,_ready} : _dout) : 8'bXXXXXXXX;
  
endmodule