.. _DEP:

Dependencies
############

.. _DEP/package:

VHDLDomain Package (Mandatory)
******************************

.. rubric:: Manually Installing Package Requirements

Use the :file:`requirements.txt` file to install all dependencies via ``pip3`` or install the package directly from
PyPI (see :ref:`INSTALL`).

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: Linux

      .. code-block:: bash

         pip3 install -U -r requirements.txt

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         pip install -U -r requirements.txt

.. rubric:: Dependency List

.. dependency-table:: package
   :caption: Mandatory dependencies of the VHDLDomain package.


.. _DEP/testing:

Unit Testing / Coverage (Optional)
**********************************

Additional Python packages needed for testing and code coverage collection. These packages are only needed for
developers or on a CI server.

.. rubric:: Manually Installing Test Requirements

Use the :file:`tests/unit/requirements.txt` file to install all dependencies via ``pip3``. The file will recursively
install the mandatory dependencies too.

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: Linux

      .. code-block:: bash

         pip3 install -U -r tests/unit/requirements.txt

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         pip install -U -r tests\unit\requirements.txt

.. rubric:: Dependency List

.. dependency-table:: unittest
   :caption: Dependencies for unit testing and code coverage.


.. _DEP/typing:

Static Type Checking (Optional)
*******************************

Additional Python packages needed for static type checking. These packages are only needed for developers or on a CI
server.

.. rubric:: Manually Installing Static Type Checking Requirements

Use the :file:`tests/typing/requirements.txt` file to install all dependencies via ``pip3``. The file will recursively
install the mandatory dependencies too.

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: Linux

      .. code-block:: bash

         pip3 install -U -r tests/typing/requirements.txt

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         pip install -U -r tests\typing\requirements.txt

.. rubric:: Dependency List

.. dependency-table:: typing
   :caption: Dependencies for static type checking.


.. _DEP/documentation:

Sphinx Documentation (Optional)
*******************************

Additional Python packages needed for building the documentation. These packages are only needed for developers or on
a CI server.

.. rubric:: Manually Installing Documentation Requirements

Use the :file:`doc/requirements.txt` file to install all dependencies via ``pip3``. The file will recursively install
the mandatory dependencies too.

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: Linux

      .. code-block:: bash

         pip3 install -U -r doc/requirements.txt

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         pip install -U -r doc\requirements.txt

.. rubric:: Dependency List

.. dependency-table:: documentation
   :caption: Dependencies for building the documentation.
