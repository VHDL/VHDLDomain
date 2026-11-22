-- Author:  Patrick Lehmann
-- License: MIT
--
-- A configuration of the 7-segment display.
--
context work.StopWatch_ctx;


-- Configures architecture ``rtl`` of :vhdl:ent:`seg7_Display`: its encoder ``enc`` is entity :vhdl:ent:`seg7_Encoder`.
configuration seg7_Display_cfg of seg7_Display is
	for rtl
		for enc : seg7_Encoder
			use entity work.seg7_Encoder(rtl);
		end for;
	end for;
end configuration;
