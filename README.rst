python-quilt
============

.. image:: https://travis-ci.org/bjoernricks/python-quilt.svg?branch=master
    :target: https://travis-ci.org/bjoernricks/python-quilt

.. image:: https://img.shields.io/pypi/v/python-quilt.svg
    :target: https://pypi.python.org/pypi/python-quilt

python-quilt is a python_ implementation of the well-known tool quilt_
to manage a series of patches.

It's intended to be used within a python application or framework but
also provides a console client interface called pquilt.

python-quilt requires the six_ package for python 2/3 compatibility. It
also requires patch_ and diff_ tools for creating and applying diffs.

Source code of python-quilt can be found at https://github.com/bjoernricks/python-quilt

Supported quilt commands
------------------------
Currently the following quilt commands have been implemented already
*(but might still miss some features)*.

- add
- applied
- delete
- edit
- import
- new
- next
- pop
- previous
- push
- top
- refresh
- revert
- series
- unapplied

Currently unsupported commands
------------------------------
- diff
- files
- header
- rename

Unlikely to be supported
------------------------
The following quilt commands are unlikely to be implemented either
because they they don't make much sense in a python package or nobody
has stepped up to implement its feature.

- annotate
- fold
- fork
- graph
- grep
- mail
- patches
- setup
- shell
- snapshot
- upgrade


.. _python: http://www.python.org/
.. _quilt: http://savannah.nongnu.org/projects/quilt
.. _six: https://pypi.python.org/pypi/six
.. _patch: http://savannah.gnu.org/projects/patch/
.. _diff: http://www.gnu.org/software/diffutils/
