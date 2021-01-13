// part of NeoGS project (c) 2007-2008 NedoPC
//

// SPI mode 0 8-bit master module
//
// short diagram for speed=0 (Fclk/Fspi=2, no rdy shown)
//
// clk:     ^  ^  ^  ^  ^  ^  ^  ^  ^  ^  ^  ^  ^  ^  ^  ^  ^  ^  ^  ^  ^  ^  ^  ^ (positive edges)
// counter: 00|00|00|10|11|12|13|14|15|16|17|18|19|1A|1B|1C|1D|1E|1F|00|00|00 // internal!
// sck:     ___________/``\__/``\__/``\__/``\__/``\__/``\__/``\__/``\_______
// sdo:     --------< do7 | do6 | do5 | do4 | do3 | do2 | do1 | do0 >-------
// sdi:     --------< di7 | di6 | di5 | di4 | di3 | di2 | di1 | di0 >-------
// bsync:   ________/`````\_________________________________________________
// start:   _____/``\_______________________________________________________
// din:     -----<IN>-------------------------------------------------------
// dout:     old old old old old old old old old old old old old | new new new
//
// data on sdo must be latched by slave on rising sck edge. data on sdo changes on falling edge of sck
//
// data from sdi is latched by master on positive edge of sck, while slave changes it on falling edge.
//  WARNING: slave must emit valid di7 bit BEFORE first pulse on sck!
//
// start is synchronous pulse, which starts all transfer and also latches din data on the same clk edge
//  as it is registered high. start can be given anytime (only when speed=0),
//  so it is functioning then as synchronous reset. when speed!=0, there is global enable for majority of
//  flipflops in the module, so start can't be accepted at any time
//
//  dout updates with freshly received data at the clk edge in which sck goes high for the last time, thus
//  latching last bit on sdi.
//
// sdo emits last bit shifted out after the transfer end

module spi
(
  	// interface
	input           clk,	// system clock
  	input           rd,
	input			wr,
  	input			reset,
	
	// SPI wires
	output 			sck,	// SCK
	output 			sdcs,	// SCS
	output reg  	sdo,	// MOSI
	input           sdi,	// MISO

  	// data
	input      [7:0] din,
  	output reg [7:0] dout,
  
	// output
	output           ready 	// start strobe, 1 clock length
);

	reg  [4:0] counter;

	assign sck 	= counter[0];
	assign sdcs = 1'b0; 		// slave always selected
	assign ready = counter[4];  // 0 - transmission in progress
	
	always @(posedge clk) begin
		reg [7:0] shift;

		if (reset) begin
		counter[4] <= 5'b0;
		end
		else if (wr) begin
			counter <= 5'b0;
			sdo <= din[7];
			shift[7:1] <= din[6:0];
		end
		else if (!ready) begin
			counter <= counter + 5'd1;

			// shift in (rising edge of SCK)
			if (!sck) begin
				shift[0] <= sdi;
				if (&counter[3:1]) dout <= {shift[7:1], sdi};
			end

			// shift out (falling edge of sck)
			if (sck) begin
				sdo <= shift[7];
				shift[7:1] <= shift[6:0]; // last bit remains after end of exchange
			end
		end
	end

endmodule