-- Author:  Patrick Lehmann
-- License: MIT
--
-- A generic multi-FF synchronizer.
--
library ieee;
use     ieee.std_logic_1164.all;


-- Multi-stage FF synchronizer
entity sync_Bits is
	generic (
		BITS      : positive              := 1;  -- The number of bits.
		STAGES    : positive range 2 to 5 := 3   -- The number of flip-flops per bit.
	);
	port (
		Clock     : in  std_logic;                            -- The clock the inputs are synchronized to.

		Input     : in  std_logic_vector(BITS - 1 downto 0);  -- The asynchronous inputs.
		Output    : out std_logic_vector(BITS - 1 downto 0)   -- The synchronized inputs.
	);
end entity;


-- The implementation: a chain of ``STAGES`` flip-flops per bit.
architecture rtl of sync_Bits is

begin
	gen : for i in Input'range generate
		signal meta   : std_logic := '0';
		signal ffs    : std_logic_vector(STAGES - 1 downto 1) := (others => '0');
	begin
		meta      <= Input(i) when rising_edge(Clock);
		ffs       <= (ffs(ffs'left downto 1) & meta) when rising_edge(Clock);

		Output(i) <= ffs(ffs'left);
	end generate;
end architecture;
