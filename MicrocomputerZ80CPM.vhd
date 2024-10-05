-- This file is copyright by Grant Searle 2014
-- You are free to use this file in your own projects but must never charge for it nor use it without
-- acknowledgement.
-- Please ask permission from Grant Searle before republishing elsewhere.
-- If you use this file or any part of it, please add an acknowledgement to myself and
-- a link back to my main web site http://searle.hostei.com/grant/    
-- and to the "multicomp" page at http://searle.hostei.com/grant/Multicomp/index.html
--
-- Please check on the above web pages to see if there are any updates before using this file.
-- If for some reason the page is no longer available, please search for "Grant Searle"
-- on the internet to see if I have moved to another web hosting service.
--
-- Grant Searle
-- eMail address available on my main web page link above.

library ieee;
use ieee.std_logic_1164.all;
use  IEEE.STD_LOGIC_ARITH.all;
use  IEEE.STD_LOGIC_UNSIGNED.all;

entity MicrocomputerZ80CPM is
	port(
		N_RESET	   		: in std_logic;
		clk				: in std_logic;

		sramData		: inout std_logic_vector(7 downto 0);
		sramAddress		: out std_logic_vector(15 downto 0);
		n_sRamWE		: out std_logic;
		n_sRamCS		: out std_logic;
		n_sRamOE		: out std_logic;
		n_sRamLB		: out std_logic;
		n_sRamUB		: out std_logic;
		
		rxd1			: in std_logic;
		txd1			: out std_logic;
		rts1			: out std_logic;
		cts1                    : in  std_logic;

		rxd2			: in std_logic;
		txd2			: out std_logic;
		rts2			: out std_logic;
		
		videoSync		: out std_logic;
		video			: out std_logic;

		R       		: out std_logic_vector(1 downto 0);
		G       		: out std_logic_vector(1 downto 0);
		B       		: out std_logic_vector(1 downto 0);
		HS		  		: out std_logic;
		VS 				: out std_logic;
		hBlank			: out std_logic;
		vBlank			: out std_logic;
		cepix  			: out std_logic;

		ps2Clk			: in std_logic;
		ps2Data			: in std_logic;

		sdCS			: out std_logic;
		sdMOSI			: out std_logic;
		sdMISO			: in std_logic;
		sdSCLK			: out std_logic;
		driveLED		: out std_logic :='1';

		usbCS			: out std_logic;
		usbMOSI			: out std_logic;
		usbMISO			: in std_logic;
		usbSCLK			: out std_logic
	);
end MicrocomputerZ80CPM;

architecture struct of MicrocomputerZ80CPM is

	signal n_WR						: std_logic;
	signal n_RD						: std_logic;
	signal cpuAddress				: std_logic_vector(15 downto 0);
	signal cpuDataOut				: std_logic_vector(7 downto 0);
	signal cpuDataIn				: std_logic_vector(7 downto 0);

	signal basRomData				: std_logic_vector(7 downto 0);
	signal internalRam1DataOut		: std_logic_vector(7 downto 0);
	signal internalRam2DataOut		: std_logic_vector(7 downto 0);
	signal interface1DataOut		: std_logic_vector(7 downto 0);
	signal interface2DataOut		: std_logic_vector(7 downto 0);
	signal ch376sDataOut			: std_logic_vector(7 downto 0);
	signal sdCardDataOut			: std_logic_vector(7 downto 0);

	signal n_memWR					: std_logic :='1';
	signal n_memRD 					: std_logic :='1';

	signal n_ioWR					: std_logic :='1';
	signal n_ioRD 					: std_logic :='1';
	
	signal n_MREQ					: std_logic :='1';
	signal n_IORQ					: std_logic :='1';	

	signal n_int1					: std_logic :='1';	
	signal n_int2					: std_logic :='1';	
	
	signal n_externalRamCS			: std_logic :='1';
	signal n_internalRam1CS			: std_logic :='1';
	signal n_internalRam2CS			: std_logic :='1';
	signal n_basRomCS				: std_logic :='1';
	signal n_interface1CS			: std_logic :='1';
	signal n_interface2CS			: std_logic :='1';
	signal n_ch376sCS				: std_logic :='1';
	signal n_sdCardCS				: std_logic :='1';

	signal serialClkCount			: std_logic_vector(15 downto 0);
	signal cpuClkCount				: std_logic_vector(5 downto 0); 
	signal sdClkCount				: std_logic_vector(5 downto 0); 	
	signal cpuClock					: std_logic;
	signal serialClock				: std_logic;
	signal sdClock					: std_logic;

	--CPM
	signal n_RomActive 				: std_logic := '0';

	component ch376s_module is
		port (
			-- interface
			clk : 	in std_logic;
			rd : 	in std_logic;
			wr : 	in std_logic;
			reset : in std_logic;
			a0 : 	in std_logic;
			
			-- SPI wires
			sck : 	out std_logic;
			sdcs : 	out std_logic;
			sdo : 	out std_logic; -- reg
			sdi : 	in std_logic;
			
			-- data
			din : 	in std_logic_vector (7 downto 0);
			dout : 	out std_logic_vector (7 downto 0) -- reg
		);
	end component;
	
	
begin
	--CPM
	-- Disable ROM if out 38. Re-enable when (asynchronous) reset pressed
	process (n_ioWR, N_RESET) begin
		if (N_RESET = '0') then
			n_RomActive <= '0';
		elsif (rising_edge(n_ioWR)) then
			if cpuAddress(7 downto 0) = "00111000" then -- $38
				n_RomActive <= '1';
			end if;
		end if;
	end process;
-- ____________________________________________________________________________________
-- CPU CHOICE GOES HERE

cpu1 : entity work.t80s
generic map(mode => 1, t2write => 1, iowait => 0)
port map(
	reset_n => N_RESET,
	clk_n => cpuClock,
	wait_n => '1',
	int_n => '1',
	nmi_n => '1',
	busrq_n => '1',
	mreq_n => n_MREQ,
	iorq_n => n_IORQ,
	rd_n => n_RD,
	wr_n => n_WR,
	a => cpuAddress,
	di => cpuDataIn,
	do => cpuDataOut
);
-- ____________________________________________________________________________________
-- ROM GOES HERE	

rom1 : entity work.Z80_CPM_BASIC_ROM
port map(
	address => cpuAddress(12 downto 0),
	clock => clk,
	q => basRomData
);

-- ____________________________________________________________________________________
-- RAM GOES HERE

ram1: entity work.InternalRam64K
port map
(
	address => cpuAddress(15 downto 0),
	clock => clk,
	data => cpuDataOut,
	wren => not(n_memWR or n_internalRam1CS),
	q => internalRam1DataOut
);

-- ____________________________________________________________________________________
-- INPUT/OUTPUT DEVICES GO HERE	


io1 : entity work.SBCTextDisplayRGB
port map (
	n_reset => N_RESET,
	clk => clk,

	-- RGB video signals
	hSync => HS,
	vSync => VS,
   	videoR0 => R(1),
   	videoR1 => R(0),
   	videoG0 => G(1),
   	videoG1 => G(0),
   	videoB0 => B(1),
   	videoB1 => B(0),
	hBlank => hBlank,
	vBlank => vBlank,
	cepix => cepix,

	-- Monochrome video signals (when using TV timings only)
	sync => videoSync,
	video => video,

	n_wr => n_interface1CS or n_ioWR,
	n_rd => n_interface1CS or n_ioRD,
	n_int => n_int1,
	regSel => cpuAddress(0),
	dataIn => cpuDataOut,
	dataOut => interface1DataOut,
	ps2Clk => ps2Clk,
	ps2Data => ps2Data
);

io2 : entity work.bufferedUART
port map(
	clk => clk,
	n_wr => n_interface2CS or n_ioWR,
	n_rd => n_interface2CS or n_ioRD,
	n_int => n_int2,
	regSel => cpuAddress(0),
	dataIn => cpuDataOut,
	dataOut => interface2DataOut,
	rxClock => serialClock,
	txClock => serialClock,
	rxd => rxd1,
	txd => txd1,
	n_cts => cts1,
	n_dcd => '0',
	n_rts => rts1
);

sd1 : entity work.sd_controller
port map(
	sdCS 	=> 	sdCS,
	sdMOSI 	=> 	sdMOSI,
	sdMISO 	=> 	sdMISO,
	sdSCLK 	=> 	sdSCLK,
	n_wr 	=> 	n_sdCardCS or n_ioWR,
	n_rd 	=> 	n_sdCardCS or n_ioRD,
	n_reset => 	N_RESET,
	dataIn 	=> 	cpuDataOut,
	dataOut => 	sdCardDataOut,
	regAddr => 	cpuAddress(2 downto 0),
	driveLED=> 	driveLED,
	clk 	=> 	clk -- 50 MHz clock = 25 MHz SPI clock
);

usb : ch376s_module
port map (
	sdcs	=> 	usbCS,
	sdo 	=> 	usbMOSI,
	sdi 	=> 	usbMISO,
	sck 	=> 	usbSCLK,

	wr 		=> 	not (n_ch376sCS or n_ioWR),
	rd 		=> 	not (n_ch376sCS or n_ioRD),

	dout 	=> 	ch376sDataOut,
	din 	=> 	cpuDataOut,
	
	a0 		=> 	cpuAddress (0),
	reset 	=> 	not (N_RESET),
	clk 	=> 	sdClock -- twice the spi clk
);


-- ____________________________________________________________________________________
-- MEMORY READ/WRITE LOGIC GOES HERE

n_ioWR 	<= n_WR or n_IORQ;
n_memWR <= n_WR or n_MREQ;
n_ioRD 	<= n_RD or n_IORQ;
n_memRD <= n_RD or n_MREQ;

-- ____________________________________________________________________________________
-- CHIP SELECTS GO HERE

n_basRomCS <= '0' when cpuAddress(15 downto 13) = "000" and n_RomActive = '0' else '1'; --8K at bottom of memory
n_interface1CS <= '0' when cpuAddress(7 downto 1) = "1000000" and (n_ioWR='0' or n_ioRD = '0') else '1'; -- 2 Bytes $80-$81
n_interface2CS <= '0' when cpuAddress(7 downto 1) = "1000001" and (n_ioWR='0' or n_ioRD = '0') else '1'; -- 2 Bytes $82-$83
n_ch376sCS <= '0' when cpuAddress(7 downto 1) = "0010000" and (n_ioWR='0' or n_ioRD = '0') else '1'; -- 2 Bytes $20-$21
n_sdCardCS <= '0' when cpuAddress(7 downto 3) = "10001" and (n_ioWR='0' or n_ioRD = '0') else '1'; -- 8 Bytes $88-$8F
n_internalRam1CS <= not n_basRomCS; -- Full Internal RAM - 64 K

-- ____________________________________________________________________________________
-- BUS ISOLATION GOES HERE

cpuDataIn <=
interface1DataOut when n_interface1CS = '0' else
interface2DataOut when n_interface2CS = '0' else
ch376sDataOut when n_ch376sCS = '0' else
sdCardDataOut when n_sdCardCS = '0' else
basRomData when n_basRomCS = '0' else
internalRam1DataOut when n_internalRam1CS= '0' else
sramData when n_externalRamCS= '0' else
x"FF";

-- ____________________________________________________________________________________
-- SYSTEM CLOCKS GO HERE


-- SUB-CIRCUIT CLOCK SIGNALS 
serialClock <= serialClkCount(15);
--sdClock <= clk;

process (clk)
begin
	if rising_edge(clk) then

		if cpuClkCount < 4 then -- 4 = 10MHz, 3 = 12.5MHz, 2=16.6MHz, 1=25MHz
			cpuClkCount <= cpuClkCount + 1;
		else
			cpuClkCount <= (others=>'0');
		end if;
		
		if cpuClkCount < 4 then -- 2 when 10MHz, 2 when 12.5MHz, 2 when 16.6MHz, 1 when 25MHz
			cpuClock <= '0';
		else
			cpuClock <= '1';
		end if; 

		if sdClkCount < 16 then -- 5MHz
			sdClkCount <= sdClkCount + 1;
		else
			sdClkCount <= (others=>'0');
		end if;

		sdClock <= sdClkCount (3); -- divide by 8 = 6.25 Mhz
		--usbCS <= sdClkCount (4);
		--usbMOSI <= sdClkCount (3);
		--usbSCLK <= sdClkCount (2);

		-- Serial clock DDS
		-- 50MHz master input clock:
		-- Baud Increment
		-- 115200 2416
		-- 38400 805
		-- 19200 403
		-- 9600 201
		-- 4800 101
		-- 2400 50
		serialClkCount <= serialClkCount + 2416;
	end if;
end process;

end;
