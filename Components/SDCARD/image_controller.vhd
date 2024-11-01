library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity image_controller is
port (
    -- System interface
    clk      : in  std_logic;
    n_reset  : in  std_logic;
    
    -- CPU interface
    n_rd     : in  std_logic;
    n_wr     : in  std_logic;
    dataIn   : in  std_logic_vector(7 downto 0);
    dataOut  : out std_logic_vector(7 downto 0);
    regAddr  : in  std_logic_vector(2 downto 0);
    
    -- Status output
    driveLED : out std_logic := '1'
);
end image_controller;

architecture rtl of image_controller is
    -- Status register bits
    constant STATUS_WRITE_READY : integer := 7;
    constant STATUS_READ_READY  : integer := 6;
    constant STATUS_BUSY        : integer := 5;

    -- Internal registers
    signal status      : std_logic_vector(7 downto 0);
    signal block_busy  : std_logic := '0';
    signal address     : std_logic_vector(31 downto 0) := (others => '0');
    
    -- Data buffering
    signal read_data   : std_logic_vector(7 downto 0);
    signal write_data  : std_logic_vector(7 downto 0);
    signal buffer_addr : unsigned(8 downto 0);  -- 0-511 bytes per sector
    
    -- Transfer state machine
    type transfer_state is (IDLE, READ_SECTOR, WRITE_SECTOR, WAIT_COMPLETE);
    signal state : transfer_state := IDLE;
    
    -- Activity LED timer
    signal led_counter : integer range 0 to 1000000 := 0;

begin
    -- Address register handling
    process(n_wr)
    begin
        if rising_edge(n_wr) then
            case regAddr is
                when "010" => address(7 downto 0)   <= dataIn;
                when "011" => address(15 downto 8)  <= dataIn;
                when "100" => address(23 downto 16) <= dataIn;
                when others => null;
            end case;
        end if;
    end process;

    -- Command and status handling
    process(clk, n_reset)
    begin
        if n_reset = '0' then
            state <= IDLE;
            block_busy <= '0';
            buffer_addr <= (others => '0');
            led_counter <= 0;
            status <= x"80";  -- Ready to write
            
        elsif rising_edge(clk) then
            -- Default LED timeout behavior
            if led_counter /= 0 then
                led_counter <= led_counter - 1;
            end if;
            
            -- Update status register
            if state = IDLE then
                status(STATUS_WRITE_READY) <= '1';
                status(STATUS_READ_READY) <= '0';
            elsif state = READ_SECTOR then
                status(STATUS_WRITE_READY) <= '0';
                status(STATUS_READ_READY) <= '1';
            else
                status(STATUS_WRITE_READY) <= '0';
                status(STATUS_READ_READY) <= '0';
            end if;
            status(STATUS_BUSY) <= block_busy;
            
            case state is
                when IDLE =>
                    if n_wr = '0' and regAddr = "001" then
                        case dataIn is
                            when x"00" =>  -- Read command
                                state <= READ_SECTOR;
                                block_busy <= '1';
                                buffer_addr <= (others => '0');
                                led_counter <= 1000000;  -- 1M cycles = 20ms at 50MHz
                                
                            when x"01" =>  -- Write command
                                state <= WRITE_SECTOR;
                                block_busy <= '1';
                                buffer_addr <= (others => '0');
                                led_counter <= 1000000;
                                
                            when others =>
                                null;
                        end case;
                    end if;

                when READ_SECTOR =>
                    if buffer_addr = 511 then
                        state <= IDLE;
                        block_busy <= '0';
                    elsif n_rd = '0' and regAddr = "000" then
                        buffer_addr <= buffer_addr + 1;
                    end if;

                when WRITE_SECTOR =>
                    if buffer_addr = 511 then
                        state <= IDLE;
                        block_busy <= '0';
                    elsif n_wr = '0' and regAddr = "000" then
                        write_data <= dataIn;
                        buffer_addr <= buffer_addr + 1;
                    end if;

                when others =>
                    state <= IDLE;
            end case;
        end if;
    end process;
    
    -- Data output multiplexing
    dataOut <= status when regAddr = "001" else
               read_data when regAddr = "000" else
               x"FF";
    
    -- Drive LED control
    driveLED <= '0' when led_counter /= 0 else '1';

end rtl;