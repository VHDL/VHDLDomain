-- Author:  Patrick Lehmann
-- License: MIT
--
-- A context summarizing other contexts and a stopwatch package.
--

-- A context for the units of ``lib_StopWatch``.
--
-- .. seealso::
--
--    :vhdl:ctx:`Utilities_ctx`
--       |rarr| The context it references.
--    :vhdl:pack:`StopWatch_pkg`
--       |rarr| The package it uses.
context StopWatch_ctx is
	library lib_Utilities;
	context lib_Utilities.Utilities_ctx;

	library lib_StopWatch;
	use     lib_StopWatch.StopWatch_pkg.all;
end context;
