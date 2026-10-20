.. |PackageName| replace:: VHDLDomain

.. _INSTALL:

Installation/Updates
####################

.. _INSTALL/pip:

Using PIP to Install from PyPI
******************************

The following instruction are using PIP (Package Installer for Python) as a package manager and PyPI (Python Package
Index) as a source of Python packages.


.. _INSTALL/pip/install:

Installing a Wheel Package from PyPI using PIP
==============================================

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: Linux

      .. code-block:: bash

         # Basic VHDLDomain package
         pip3 install VHDLDomain

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         # Basic VHDLDomain package
         pip install VHDLDomain

Developers can install further dependencies for documentation generation (``doc``) or running unit tests (``test``) or
just all (``all``) dependencies.

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: Linux

      .. tab-set::

         .. tab-item:: With Documentation Dependencies
            :sync: Doc

            .. code-block:: bash

               # Install with dependencies to generate documentation
               pip3 install VHDLDomain[doc]

         .. tab-item:: With Unit Testing Dependencies
            :sync: Unit

            .. code-block:: bash

               # Install with dependencies to run unit tests
               pip3 install VHDLDomain[test]

         .. tab-item:: All Developer Dependencies
            :sync: All

            .. code-block:: bash

               # Install with all developer dependencies
               pip3 install VHDLDomain[all]

   .. tab-item:: Windows
      :sync: Windows

      .. tab-set::

         .. tab-item:: With Documentation Dependencies
            :sync: Doc

            .. code-block:: powershell

               # Install with dependencies to generate documentation
               pip install VHDLDomain[doc]

         .. tab-item:: With Unit Testing Dependencies
            :sync: Unit

            .. code-block:: powershell

               # Install with dependencies to run unit tests
               pip install VHDLDomain[test]

         .. tab-item:: All Developer Dependencies
            :sync: All

            .. code-block:: powershell

               # Install with all developer dependencies
               pip install VHDLDomain[all]

.. _INSTALL/pip/update:

Updating from PyPI using PIP
============================

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: Linux

      .. code-block:: bash

         pip3 install -U VHDLDomain

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         pip install -U VHDLDomain


.. _INSTALL/pip/uninstall:

Uninstallation using PIP
========================

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: Linux

      .. code-block:: bash

         pip3 uninstall VHDLDomain

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         pip uninstall VHDLDomain


.. _INSTALL/setup:

Using ``setup.py`` (legacy)
***************************

See sections above on how to use PIP.

Installation using ``setup.py``
===============================

.. code-block:: bash

   setup.py install


.. _INSTALL/building:

Local Packaging and Installation via PIP
****************************************

For development and bug fixing it might be handy to create a local wheel package and also install it locally on the
development machine. The following instructions will create a local wheel package (``*.whl``) and then use PIP to
install it. As a user might have a VHDLDomain installation from PyPI, it's recommended to uninstall any previous
VHDLDomain packages. (This step is also needed if installing an updated local wheel file with same version number.
PIP will not detect a new version and thus not overwrite/reinstall the updated package contents.)

Ensure the packaging requirements ``build``, ``setuptools`` and ``pyTooling`` are installed.

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: Linux

      .. code-block:: bash

         cd <VHDLDomain>

         # Package the code in a wheel (*.whl)
         python3 -m build --wheel

         # Uninstall the old package
         python3 -m pip uninstall -y VHDLDomain

         # Install from wheel
         python3 -m pip install ./dist/vhdldomain-0.1.0-py3-none-any.whl

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         cd <VHDLDomain>

         # Package the code in a wheel (*.whl)
         py -m build --wheel

         # Uninstall the old package
         py -m pip uninstall -y VHDLDomain

         # Install from wheel
         py -m pip install .\dist\vhdldomain-0.1.0-py3-none-any.whl
