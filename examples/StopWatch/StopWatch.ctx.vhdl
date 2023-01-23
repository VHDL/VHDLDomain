-- Author:  Patrick Lehmann
-- License: MIT
--
-- A context summarizing other contexts and a stopwatch package.
--
context StopWatch_ctx is
	library lib_Utilities;
	context lib_Utilities.Utilities_ctx;

	use work.StopWatch_pkg.all;
end context;
