-- Author:  Patrick Lehmann
-- License: MIT
--
-- A package for stopwatch specific types and helper functions.
--
library IEEE;
use     IEEE.std_logic_1164.all;
use     IEEE.numeric_std.all;

-- Package with stop watch specific types.
package StopWatch_pkg is
	-- A BCD digit: 0 to 9 in four bits.
	subtype T_BCD is unsigned(3 downto 0);

	-- A vector of BCD digits, e.g. the digits of a display.
	type T_BCD_Vector is array(natural range <>) of T_BCD;

	-- The configuration of one digit of a stop watch.
	type T_DIGIT_CONFIGURATION is record
		Modulo : positive;   -- The digit counts from 0 to ``Modulo - 1``.
		Dot    : std_logic;  -- The dot after the digit is lit.
	end record;

	-- The configuration of a stop watch: an element per digit, the least significant digit first.
	type T_STOPWATCH_CONFIGURATION is array(natural range <>) of T_DIGIT_CONFIGURATION;

	-- Encoder that translates from 4-bit binary (BCD) to 7-segment code.
	--
	-- In addition, an optional dot input is supported.
	component seg7_Encoder is
		port (
			BCDValue  : in  T_BCD;
			Dot       : in  std_logic  := '0';

			Seg7Code  : out std_logic_vector(7 downto 0)
		);
	end component;

	-- A driver of a multiplexed 7-segment display with ``DIGITS`` digits.
	component seg7_Display is
		generic (
			CLOCK_PERIOD  : time := 10 ns;
			REFRESH_RATE  : time := 200 us;
			DIGITS        : positive
		);
		port (
			Clock         : in  std_logic;

			DigitValues   : in  T_BCD_Vector(DIGITS - 1 downto 0);
			DotValues     : in  std_logic_vector(DIGITS - 1 downto 0) := (others => '0');

			Seg7_Segments : out std_logic_vector(7 downto 0);
			Seg7_Selects  : out std_logic_vector(DIGITS - 1 downto 0)
		);
	end component;
end package;
