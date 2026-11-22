-- Author:  Patrick Lehmann
-- License: MIT
--
-- A context to simplify the usage of packages.
--

-- A context for the users of ``lib_Utilities``.
--
-- It references the IEEE packages ``std_logic_1164`` and ``numeric_std``, and :vhdl:pack:`Utilities_pkg`.
context Utilities_ctx is
	library IEEE;
	use     IEEE.std_logic_1164.all,
	        IEEE.numeric_std.all;

	library lib_Utilities;
	use     lib_Utilities.Utilities_pkg.all;
end context;
