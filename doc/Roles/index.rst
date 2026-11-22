.. _ROLE:

Roles
#####

A role refers to an object a directive described, by the object's qualified name or by a part of it ending with the
object's name:

* An object's qualified name starts with its design and library, e.g. ``StopWatch.lib_StopWatch.Counter``.
* ``lib_StopWatch.Counter`` and ``Counter`` name the same entity, as long as no other entity has that name.
* A name matching several objects is resolved in the design and library current where the reference is written -
  set by :rst:dir:`vhdl:design` and :rst:dir:`vhdl:library` -; otherwise it is warned about, and the reference is
  shown as text.
* A subprogram's name may end in its signature, the type marks of its parameters: ``to_index(natural, positive)``.
  Without a signature, a subprogram with overloads is ambiguous.
* VHDL identifiers are case-insensitive, so are the names.
* A leading ``~`` shows only the object's name: ``:vhdl:ent:`~lib_StopWatch.Counter``` shows ``Counter``.

.. code-block:: rst

   The entity :vhdl:ent:`Counter` counts clock cycles, see :vhdl:func:`Utilities.to_index(natural, positive)`.

.. contents:: Table of Contents
   :local:


Design and library
******************

.. rst:role:: vhdl:design

   Refer to a design.

.. rst:role:: vhdl:lib

   Refer to a library.


Design units
************

.. rst:role:: vhdl:ctx

   Refer to a context.

.. rst:role:: vhdl:ent

   Refer to an entity.

.. rst:role:: vhdl:arch

   Refer to an architecture, by the entity's name and the architecture's: ``Counter.rtl``.

.. rst:role:: vhdl:pack

   Refer to a package.

.. rst:role:: vhdl:config

   Refer to a configuration.


Declarations
************

.. rst:role:: vhdl:type

   Refer to a type or subtype, e.g. ``StopWatch_pkg.T_STATE``.

.. rst:role:: vhdl:const

   Refer to a constant.

.. rst:role:: vhdl:sig

   Refer to a signal.

.. rst:role:: vhdl:var

   Refer to a shared variable.

.. rst:role:: vhdl:comp

   Refer to a component, e.g. ``StopWatch_pkg.seg7_Encoder``.

.. rst:role:: vhdl:func

   Refer to a function, optionally with its signature. A method of a protected type is named after the type, e.g.
   ``T_ERROR_COUNTER.Errors``.

.. rst:role:: vhdl:proc

   Refer to a procedure, optionally with its signature, e.g. ``T_ERROR_COUNTER.Increment``.

.. rst:role:: vhdl:generic

   Refer to a generic, by the entity's or package's name and the generic's: ``Counter.BITS``.

.. rst:role:: vhdl:port

   Refer to a port, by the entity's name and the port's: ``Counter.Clock``.


.. _ROLE/popups:

Popups
******

In HTML, a reference to a declaration of a package - a type or subtype, a constant, signal or shared variable, a
component, a subprogram or a protected type's method - shows the declaration in a popup, while the mouse is over the
reference or the reference has the keyboard focus. This holds for a role's reference and for a type mark a directive
writes, e.g. ``T_BCD`` of a port ``BCDValue : in T_BCD``. The popup shows:

* the library and design unit declaring it - and the protected type, for a method -, e.g.
  ``lib_StopWatch.StopWatch_pkg``,
* its signature, as its description shows it, e.g. ``subtype T_BCD is unsigned(3 downto 0)``,
* the first paragraph of its documentation comment,
* a record's elements, an enumeration's literals or a physical type's units: the first 8, followed by ``...`` if there
  are more.

The examples (see :ref:`EX`) show it: hover over a type mark, e.g. ``T_BCD`` of the StopWatch example.

The popup needs no JavaScript: the domain adds the style sheet :file:`VHDLDomain.css` to every HTML page, which shows
the popup by CSS (``:hover``, ``:focus-within``). The popup is the reference's description for a screen reader
(``role="tooltip"``, ``aria-describedby``), and isn't indexed by the search. Other builders - e.g. LaTeX, text - write
the reference only. :ref:`CONFIG/reference-popups` switches the popups off; a reference's title (``title`` attribute)
is the declaration's signature then.

A popup is a ``span`` with the classes ``vhdl-popup`` and ``no-search``, after the link in a ``span`` with the class
``vhdl-popup-anchor``; its parts are spans with the classes ``vhdl-popup-location``, ``vhdl-popup-signature``,
``vhdl-popup-documentation`` and ``vhdl-popup-members`` (``vhdl-popup-label``, ``vhdl-popup-member``). Its colors and
fonts follow the variables of the themes ``furo`` and ``pydata-sphinx-theme``, where they are defined, otherwise the
look of ``sphinx_rtd_theme``; each can be set in a style sheet of the documentation:

.. code-block:: CSS

   :root {
     --vhdl-popup-background: #ffffe0;  /* also: -foreground, -border, -muted, -font, -code-font */
   }

.. attention::

   A popup opens below the reference, aligned to its left edge: it is clipped by a container which scrolls its content,
   e.g. a table wider than the page, and by the page's right edge for a reference near it. It closes when the mouse
   leaves the reference and the popup, or the reference loses the focus - not by :kbd:`Esc`.
