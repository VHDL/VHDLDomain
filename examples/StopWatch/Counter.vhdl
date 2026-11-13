-- :author:  Patrick Lehmann
-- :license: MIT
--
-- A generic counter module used in the StopWatch example.
--
library IEEE;
use     IEEE.std_logic_1164.all;
use     IEEE.numeric_std.all;

use     work.Utilities_pkg.all;

-- A generic implementation of an up-counting counter.
--
-- The counter counts the cycles of ``Clock`` with ``Enable`` high, from 0 to ``MODULO - 1``; then it wraps around to 0
-- and signals it on ``WrapAround`` for one cycle. ``Reset`` restarts it at 0, with priority over ``Enable``.
--
-- .. seealso::
--
--    :vhdl:ent:`StopWatch`
--       |rarr| The stop watch, counting the time base and each digit with a counter.
entity Counter is
	generic (
		MODULO : positive;                -- Modulo value of the modulo N counter.
		BITS   : natural := log2(MODULO)  -- Number of bits used by the counter output vector. This number is derived from MODULO are can be overwritten with a greater value to achieve a wider output vector.
	);
	port (
		Clock      : in  std_logic;       -- System clock to operate the whole entity.
		Reset      : in  std_logic;       -- System reset to reset the entire entity.
		Enable     : in  std_logic;       -- Enable signal to activate the counter.

		Value      : out unsigned(BITS - 1 downto 0);  -- Current state of the counter as unsigned number.
		WrapAround : out std_logic                     -- Triggered for a single cycle, when counter wraps around.
	);
end entity;


-- The implementation for synthesis.
architecture rtl of Counter is
	signal CounterValue : unsigned(log2(MODULO) - 1 downto 0) := (others => '0');
begin
	process (Clock)
	begin
		if rising_edge(Clock) then
			if ((Reset or WrapAround) = '1') then
				CounterValue <= (others => '0');
			elsif (Enable = '1') then
				CounterValue <= CounterValue + 1;
			end if;
		end if;
	end process;

	Value      <= resize(CounterValue, BITS);
	WrapAround <= Enable when (CounterValue = MODULO - 1) else '0';
end architecture;


-- The implementation for simulation, the same as ``rtl``.
architecture sim of Counter is
	signal CounterValue : unsigned(log2(MODULO) - 1 downto 0) := (others => '0');
begin
	process (Clock)
	begin
		if rising_edge(Clock) then
			if ((Reset or WrapAround) = '1') then
				CounterValue <= (others => '0');
			elsif (Enable = '1') then
				CounterValue <= CounterValue + 1;
			end if;
		end if;
	end process;

	Value      <= resize(CounterValue, BITS);
	WrapAround <= Enable when (CounterValue = MODULO - 1) else '0';
end architecture;
