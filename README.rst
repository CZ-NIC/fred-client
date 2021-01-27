.. image:: https://fred.nic.cz/documentation/html/_static/fred-logo.png
   :target: https://fred.nic.cz
   :alt: FRED

================
FRED: EPP Client
================

A Python EPP client – a CLI application and an API library


This repository is a subproject of FRED, the Free Registry for ENUM and Domains,
and it contains only a fraction of the source code required for running FRED.
See the
`complete list of subprojects <https://fred.nic.cz/documentation/html/Architecture/SourceCode.html>`_
that make up FRED.

Learn more about the project and our community on the `FRED's Home Page <https://fred.nic.cz>`_.

Documentation for the whole FRED project is available on-line, visit https://fred.nic.cz/documentation.

Table of Contents
=================

* `Installation <#installation>`_
* `Configuration <#configuration>`_
* `Documentation <#documentation>`_
* `Maintainers <#maintainers>`_
* `License <#license>`_

Installation
============

To build and install the ``fred-client`` application, run the following command:

.. code-block::

     python ./setup.py install --prefix=/tmp/client --single-version-externally-managed --record=/tmp/client/dummy.log

Adapt the ``prefix`` dir path to the target directory of your choice, and the ``record`` file path
to the location for the log file.

Configuration
=============

The default location of the configuration file is:


* primary: ``~/.fred-client.conf`` (hidden file in home)
* secondary: ``/etc/fred/fred-client.conf``

See also the example configuration in `examples/fred-client.conf <examples/fred-client.conf>`_.

Documentation
=============

Read about the `EPP Client Workflow <https://fred.nic.cz/documentation/html/Concepts/EPPClientWorkflow.html>`_
in the on-line FRED Documentation.

See also further README files in the `doc </doc>`_ subfolder:

.. code-block::

   doc/
       README_EN.txt       English version
       README_CS.txt       Czech version in ASCII
       README_CS.utf8      Czech version in UTF-8
       README_CS.html      Czech HTML version
       README_CS.docbook   source of the Czech versions

Maintainers
===========


* Jiri Sadek [jiri.sadek@nic.cz](mailto:jiri.sadek@nic.cz)
* Jaromir Talir [jaromir.talir@nic.cz](mailto:jaromir.talir@nic.cz)

License
=======

See `LICENSE <LICENSE>`_.
