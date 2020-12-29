module ch376s_module
(
  	// interface
	input       clk,  // input clock
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
   input [7:0] din,
  	output[7:0] dout
  
);


   reg [2:0] mycnt;
   initial mycnt = 0;
   always @(posedge clk) begin
      mycnt <= mycnt + 1'b1;
   end
   assign sck = mycnt[0];
   assign sdo = mycnt[1];
   assign sdcs = mycnt[2];

/*
   wire _ready;
   wire [7:0] _dout;

   spi SPI_Master
   (
      // Control/Data Signals,
      .clk     (clk),         // FPGA Clock
      .reset   (reset),
      .ready   (_ready),
      
      // TX (MOSI) Signals
      .din     (din),        // Byte to transmit on MOSI
      .wr      (wr),         // Data Valid Pulse with i_TX_Byte
      
      // RX (MISO) Signals
      .dout    (_dout),     // Byte received on MISO
      .rd      (rd),

      // SPI Interface
      .sck     (sck),
      .sdi     (sdi),
      .sdo     (sdo),
      .sdcs    (sdcs)
   );

   // zero when not rd
   // when a0 is 1 show status, bit 0 signals ready state.
   // when a0 is 0 show received data
   assign dout = (rd ? (a0 ? {7'b0000000,_ready} : _dout) : 8'b00000000);
*/

endmodule