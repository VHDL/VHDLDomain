-- Author:  Patrick Lehmann
-- License: MIT
--
-- A helper package.
--
library IEEE;
use     IEEE.std_logic_1164.all;
use     IEEE.numeric_std.all;


-- Useful utility functions and types.
--
-- The package collects *generic* helpers, used by both libraries of the StopWatch example:
--
-- * the physical type ``freq`` and the error counter ``T_ERROR_COUNTER``,
-- * functions computing sizes, e.g. ``log2``, and converting values, e.g. ``bin2onehot``,
-- * the component ``Debouncer``.
--
-- .. seealso::
--
--    :vhdl:ctx:`Utilities_ctx`
--       |rarr| A context referencing this package and the IEEE packages.
--    :vhdl:ent:`Counter`
--       |rarr| A counter, sized by :vhdl:func:`log2`.
package Utilities_pkg is
	-- A frequency, from Hz to THz.
	type freq is range integer'low to integer'high units
		Hz;              -- Hertz, the primary unit.
		kHz = 1000 Hz;   -- Kilohertz.
		MHz = 1000 kHz;  -- Megahertz.
		GHz = 1000 MHz;  -- Gigahertz.
		THz = 1000 GHz;  -- Terahertz.
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
	function ite(
		condition : boolean;  -- The condition choosing the value.
		ThenValue : integer;  -- The value, if ``condition`` is true.
		ElseValue : integer   -- The value, if ``condition`` is false.
	) return integer;

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

	-- The one-hot code of the binary number ``binary``: bit ``binary`` set, every other bit cleared.
	function bin2onehot(
		binary : std_logic_vector;  -- The binary number.
		bits   : natural := 0       -- The number of bits of the code; ``0`` for all ``2**binary'length`` bits.
	) return std_logic_vector;

	-- The one-hot code of the unsigned number ``binary``: bit ``binary`` set, every other bit cleared.
	function bin2onehot(
		binary : unsigned;      -- The unsigned number.
		bits   : natural := 0   -- The number of bits of the code; ``0`` for all ``2**binary'length`` bits.
	) return std_logic_vector;

	-- The index ``value`` as a natural number, limited to ``max``.
	function to_index(
		value : unsigned;  -- The index, an unsigned number.
		max   : positive   -- The highest index.
	) return natural;

	-- The index ``value``, limited to ``max``.
	function to_index(
		value : natural;   -- The index.
		max   : positive   -- The highest index.
	) return natural;

	-- The component of entity :vhdl:ent:`Debouncer`, for a component instantiation.
	component Debouncer is
		generic (
			CLOCK_PERIOD   : time := 10 ns;  -- The period of ``Clock``.
			DEBOUNCE_TIME  : time := 3 ms;   -- The time an input must be stable to pass.

			BITS           : positive        -- The number of inputs.
		);
		port (
			Clock  : in  std_logic;  -- The clock.

			Input  : in  std_logic_vector(BITS - 1 downto 0);                     -- The bouncing inputs.
			Output : out std_logic_vector(BITS - 1 downto 0) := (others => '0')   -- The debounced inputs.
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
