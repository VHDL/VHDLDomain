.. _NEWS:

News
####

See :gh:`VHDLDomain Release Pages <VHDL/VHDLDomain/releases>` for detail release notes on every release.


Version 0.2.0 (2026)
********************

.. topic:: :gh:`v0.2.0 - 30.10.2026 <VHDL/VHDLDomain/releases/v0.2.0>`

   .. rubric:: Changes

   * The domain ``vhdl`` is rebuilt on pyVHDLModel: objects, references by qualified name or a part of it, the
     directives ``vhdl:design`` and ``vhdl:library``, and design-unit directives for entities, packages, contexts and
     configurations.
   * Indices of the described entities, packages, subprograms and types.
   * Generated pages: a page per library and design unit of a design.
   * pyTooling 10.1, pyTooling.Sphinx 1.0 and pyVHDLModel 0.40 are required; Python 3.12 to 3.15 are supported.

   .. rubric:: Documentation

   * The documentation is built with the ReadTheDocs theme and pyTooling.Sphinx.


Version 0.x (2023)
******************

.. topic:: Initial Implementation of a VHDL Domain (Jan. 2023)

   * Connecting pyGHDL.dom, pyVHDLModel and Sphinx with this extension.
