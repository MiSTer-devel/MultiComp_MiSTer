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

entity Microcomputer6502Basic is
	port(
		N_RESET	   : in std_logic;
		clk			: in std_logic;
		baud_increment	: in std_logic_vector(15 downto 0);

		sramData		: inout std_logic_vector(7 downto 0);
		sramAddress	: out std_logic_vector(15 downto 0);
		n_sRamWE		: out std_logic;
		n_sRamCS		: out std_logic;
		n_sRamOE		: out std_logic;
		n_sRamLB		: out std_logic;
		n_sRamUB		: out std_logic;
		
		rxd1			: in std_logic;
		txd1			: out std_logic;
		rts1			: out std_logic;
		cts1			: in std_logic;  -- Added CTS input

		rxd2			: in std_logic;
		txd2			: out std_logic;
		rts2			: out std_logic;
		
		videoSync	: out std_logic;
		video			: out std_logic;

		R       		: out std_logic_vector(1 downto 0);
		G       		: out std_logic_vector(1 downto 0);
		B       		: out std_logic_vector(1 downto 0);
		HS		  		: out std_logic;
		VS 			: out std_logic;
		hBlank		: out std_logic;
		vBlank		: out std_logic;
		cepix  		: out std_logic;

		ps2Clk		: in std_logic;
		ps2Data		: in std_logic;

		sdCS			: out std_logic;
		sdMOSI		: out std_logic;
		sdMISO		: in std_logic;
		sdSCLK		: out std_logic;
		sd_ctrl_sel : in std_logic;
		driveLED		: out std_logic :='1'	
	);
end Microcomputer6502Basic;

architecture struct of Microcomputer6502Basic is

    signal reset_counter : unsigned(15 downto 0) := (others => '0');
    signal reset_n_internal : std_logic := '0';  -- Active low internal reset

	signal n_WR							: std_logic;
	signal n_RD							: std_logic;
	signal cpuAddress					: std_logic_vector(15 downto 0);
	signal cpuDataOut					: std_logic_vector(7 downto 0);
	signal cpuDataIn					: std_logic_vector(7 downto 0);

	signal basRomData					: std_logic_vector(7 downto 0);
	signal internalRam1DataOut		: std_logic_vector(7 downto 0);
	signal internalRam2DataOut		: std_logic_vector(7 downto 0);
	signal interface1DataOut		: std_logic_vector(7 downto 0);
	signal interface2DataOut		: std_logic_vector(7 downto 0);
	signal sdCardDataOut				: std_logic_vector(7 downto 0);

	signal n_memWR						: std_logic :='1';
	signal n_memRD 					: std_logic :='1';

	signal n_ioWR						: std_logic :='1';
	signal n_ioRD 						: std_logic :='1';
	
	signal n_MREQ						: std_logic :='1';
	signal n_IORQ						: std_logic :='1';	

	signal n_int1						: std_logic :='1';	
	signal n_int2						: std_logic :='1';	
	
	signal n_externalRamCS			: std_logic :='1';
	signal n_internalRam1CS			: std_logic :='1';
	signal n_internalRam2CS			: std_logic :='1';
	signal n_basRomCS					: std_logic :='1';
	signal n_interface1CS			: std_logic :='1';
	signal n_interface2CS			: std_logic :='1';
	signal n_sdCardCS					: std_logic :='1';

    signal sdCardDataOut_sd  : std_logic_vector(7 downto 0);
    signal sdCardDataOut_img : std_logic_vector(7 downto 0);
    signal driveLED_sd, driveLED_img : std_logic;
    signal sdMISO_int : std_logic;  -- Add this signal declaration

   signal serialClkCount         : unsigned(15 downto 0);
	signal cpuClkCount				: std_logic_vector(5 downto 0); 
	signal sdClkCount					: std_logic_vector(5 downto 0); 	
	signal cpuClock					: std_logic;
	signal serialClock				: std_logic;
	signal sdClock						: std_logic;

begin

process(clk)
begin
	if rising_edge(clk) then
		if N_RESET = '0' then
			reset_counter <= (others => '0');
			reset_n_internal <= '0';
		else
			if reset_counter /= unsigned'(X"FFFF") then
				reset_counter <= reset_counter + 1;
				reset_n_internal <= '0';
			else
				reset_n_internal <= '1';
			end if;
		end if;
	end if;
end process;

-- ____________________________________________________________________________________
-- CPU CHOICE GOES HERE

cpu1 : entity work.T65
port map(
	Enable => '1',
	Mode => "00",
	Res_n => reset_n_internal,
	Clk => cpuClock,
	Rdy => '1',
	Abort_n => '1',
	IRQ_n => '1',
	NMI_n => '1',
	SO_n => '1',
	R_W_n => n_WR,
	A(15 downto 0) => cpuAddress,
	DI => cpuDataIn,
	DO => cpuDataOut
);

-- ____________________________________________________________________________________
-- ROM GOES HERE	

rom1 : entity work.M6502_BASIC_ROM -- 8KB BASIC
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

	n_wr => n_interface1CS or cpuClock or n_WR,
	n_rd => n_interface1CS or cpuClock or (not n_WR),
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
	n_wr => n_interface2CS or cpuClock or n_WR,
	n_rd => n_interface2CS or cpuClock or (not n_WR),
	n_int => n_int2,
	regSel => cpuAddress(0),
	dataIn => cpuDataOut,
	dataOut => interface2DataOut,
	rxClock => serialClock,
	txClock => serialClock,
	rxd => rxd1,
	txd => txd1,
	n_cts => cts1,  -- Connect CTS signal
	n_dcd => '0',
	n_rts => rts1
);

sd1 : entity work.sd_controller
port map(
	sdCS => sdCS,
	sdMOSI => sdMOSI,
	sdMISO => sdMISO_int,
	sdSCLK => sdSCLK,
	n_wr => n_sdCardCS or cpuClock or n_WR,
	n_rd => n_sdCardCS or cpuClock or (not n_WR),
	n_reset => N_RESET,
	dataIn => cpuDataOut,
	dataOut => sdCardDataOut_sd,
	regAddr => cpuAddress(2 downto 0),
	driveLED => driveLED_sd,
	clk => sdClock -- twice the spi clk
);

    -- Add signal assignment outside port map:
    sdMISO_int <= sdMISO when sd_ctrl_sel = '0' else '1';

    -- New image controller
    img1 : entity work.image_controller
    port map(
        clk => clk,
        n_reset => N_RESET,
        n_rd => n_sdCardCS or n_ioRD,
        n_wr => n_sdCardCS or n_ioWR,
        dataIn => cpuDataOut,
        dataOut => sdCardDataOut_img,
        regAddr => cpuAddress(2 downto 0),
        driveLED => driveLED_img
    );

-- ____________________________________________________________________________________
-- MEMORY READ/WRITE LOGIC GOES HERE

n_memRD <= not(cpuClock) nand n_WR;
n_memWR <= not(cpuClock) nand (not n_WR);

-- ____________________________________________________________________________________
-- CHIP SELECTS GO HERE

n_basRomCS <= '0' when cpuAddress(15 downto 13) = "111" else '1'; --8K at top of memory
n_interface1CS <= '0' when cpuAddress(15 downto 1) = "111111111101000" else '1'; -- 2 bytes FFD0-FFD1
n_interface2CS <= '0' when cpuAddress(15 downto 1) = "111111111101001" else '1'; -- 2 bytes FFD2-FFD3
n_sdCardCS <= '0' when cpuAddress(15 downto 3) = "1111111111011" else '1'; -- 8 bytes FFD8-FFDF
n_internalRam1CS <= not n_basRomCS; -- Full Internal RAM - 64 K

-- ____________________________________________________________________________________
-- BUS ISOLATION GOES HERE
    -- Mux controller outputs based on selection
    sdCardDataOut <= sdCardDataOut_img when sd_ctrl_sel = '1' else 
                     sdCardDataOut_sd;
                     
    driveLED <= driveLED_img when sd_ctrl_sel = '1' else 
                driveLED_sd;


cpuDataIn <=
interface1DataOut when n_interface1CS = '0' else
interface2DataOut when n_interface2CS = '0' else
sdCardDataOut when n_sdCardCS = '0' else
basRomData when n_basRomCS = '0' else
internalRam1DataOut when n_internalRam1CS= '0' else
sramData when n_externalRamCS= '0' else
x"FF";

-- ____________________________________________________________________________________
-- SYSTEM CLOCKS GO HERE

-- SUB-CIRCUIT CLOCK SIGNALS

serialClock <= serialClkCount(15);
process (clk)
begin
	if rising_edge(clk) then

		if cpuClkCount < 4 then -- 4 = 10MHz, 3 = 12.5MHz, 2=16.6MHz, 1=25MHz
			cpuClkCount <= cpuClkCount + 1;
		else
			cpuClkCount <= (others=>'0');
		end if;
		if cpuClkCount < 2 then -- 2 when 10MHz, 2 when 12.5MHz, 2 when 16.6MHz, 1 when 25MHz
			cpuClock <= '0';
		else
			cpuClock <= '1';
		end if; 

		if sdClkCount < 49 then -- 1MHz
			sdClkCount <= sdClkCount + 1;
		else
			sdClkCount <= (others=>'0');
		end if;

		if sdClkCount < 25 then
			sdClock <= '0';
		else
			sdClock <= '1';
		end if;

		-- Serial clock DDS
		-- 50MHz master input clock:
		-- Baud Increment
		-- 115200 2416
		-- 38400 805
		-- 19200 403
		-- 9600 201
		-- 4800 101
		-- 2400 50
		serialClkCount <= serialClkCount + unsigned(baud_increment);
	end if;
end process;

end;