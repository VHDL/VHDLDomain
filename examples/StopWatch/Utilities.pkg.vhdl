-- Author:  Patrick Lehmann
-- License: MIT
--
-- A helper package.
--
library IEEE;
use     IEEE.std_logic_1164.all;
use     IEEE.numeric_std.all;


-- Useful utility functions and types.
package Utilities_pkg is
	-- A frequency, from Hz to THz.
	type freq is range integer'low to integer'high units
		Hz;
		kHz = 1000 Hz;
		MHz = 1000 kHz;
		GHz = 1000 MHz;
		THz = 1000 GHz;
	end units;

	-- A counter of errors, e.g. of the failed checks of a testbench.
	type T_ERROR_COUNTER is protected
		-- Add errors to the counter.
		procedure Increment(
			Count : positive := 1  -- The number of errors to add.
		);

		-- Reset the counter to no errors.
		procedure Reset;

		-- The number of errors since the last reset.
		impure function Errors return natural;
	end protected;

	-- ``true`` in a simulation, ``false`` in a synthesis; the package body sets this deferred constant.
	constant IS_SIMULATION : boolean;

	-- An if-then-else expression: ``ThenValue``, if ``condition`` is true, else ``ElseValue``.
	function ite(condition : boolean; ThenValue : integer; ElseValue : integer) return integer;

	-- The number of bits needed for the values 0 to ``Value - 1``: ``ceil(log2(Value))``.
	function log2(
		Value : positive  -- The number of values.
	) return positive;

	-- The value ``Value``, limited to the range ``Low`` to ``High``.
	function clamp(
		Value : integer;  -- The value to limit.
		Low   : integer;  -- The lower bound.
		High  : integer   -- The upper bound.
	) return integer;

	-- Swap the values of two variables of any type.
	procedure swap
		generic (
			type T_VALUE  -- The type of the values.
		)
		parameter (
			variable A : inout T_VALUE;  -- The first value; ``B``'s value after the call.
			variable B : inout T_VALUE   -- The second value; ``A``'s value after the call.
		);

	function bin2onehot(binary : std_logic_vector; bits : natural := 0) return std_logic_vector;
	function bin2onehot(binary : unsigned;         bits : natural := 0) return std_logic_vector;

	function to_index(value : unsigned; max : positive) return natural;
	function to_index(value : natural;  max : positive) return natural;

	component Debouncer is
		generic (
			CLOCK_PERIOD   : time := 10 ns;
			DEBOUNCE_TIME  : time := 3 ms;

			BITS           : positive
		);
		port (
			Clock  : in  std_logic;

			Input  : in  std_logic_vector(BITS - 1 downto 0);
			Output : out std_logic_vector(BITS - 1 downto 0) := (others => '0')
		);
	end component;
end package;


package body Utilities_pkg is
	function simulation return boolean is
		variable result : boolean := FALSE;
	begin
		-- synthesis translate_off
		result := TRUE;
		-- synthesis translate_on
		return result;
	end function;

	-- deferred constant initialization
	constant IS_SIMULATION : boolean := simulation;

	type T_ERROR_COUNTER is protected body
		variable Counter : natural := 0;

		procedure Increment(Count : positive := 1) is
		begin
			Counter := Counter + Count;
		end procedure;

		procedure Reset is
		begin
			Counter := 0;
		end procedure;

		impure function Errors return natural is
		begin
			return Counter;
		end function;
	end protected body;

	function ite(condition : boolean; ThenValue : integer; ElseValue : integer) return integer is
	begin
		if condition then
			return ThenValue;
		else
			return ElseValue;
		end if;
	end function;

	function log2(Value : positive) return positive is
		variable twosPower : natural := 1;
		variable result    : natural := 0;
	begin
		while (twosPower < Value) loop
			twosPower := twosPower * 2;
			result    := result + 1;
		end loop;
		return result;
	end function;

	function clamp(Value : integer; Low : integer; High : integer) return integer is
	begin
		if (Value < Low) then
			return Low;
		elsif (Value > High) then
			return High;
		else
			return Value;
		end if;
	end function;

	procedure swap
		generic (
			type T_VALUE
		)
		parameter (
			variable A : inout T_VALUE;
			variable B : inout T_VALUE
		) is
		variable temp : T_VALUE;
	begin
		temp := A;
		A    := B;
		B    := temp;
	end procedure;

	function bin2onehot(binary : std_logic_vector; bits : natural := 0) return std_logic_vector is
	begin
		return bin2onehot(unsigned(binary), bits);
	end function;

	function bin2onehot(binary : unsigned; bits : natural := 0) return std_logic_vector is
		variable result : std_logic_vector(2**binary'length - 1 downto 0) := (others => '0');
	begin
		result(to_integer(binary)) := '1';

		if (bits = 0) then
			return result;
		else
			return result(bits - 1 downto 0);
		end if;
	end function;

	function to_index(value : unsigned; max : positive) return natural is
	begin
		return to_index(to_integer(value), max);
	end function;

	function to_index(value : natural; max : positive) return natural is
	begin
		if (value <= max) then
			return value;
		else
			return max;
		end if;
		-- return minimum(value, max);
	end function;
end package body;
