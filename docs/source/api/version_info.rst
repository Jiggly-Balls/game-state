.. currentmodule:: game_state

Version Info
============

There are two main ways to query version information about the library.

.. data:: version_info

  A named tuple that is similar to :obj:`sys.version_info`.

  Just like :obj:`sys.version_info` the valid values for ``releaselevel`` are
  'alpha', 'beta', 'candidate' and 'final'.

.. data:: __version__

  A string representation of the version. e.g. ``'1.0.0'``. This is based
  off of :pep:`440`.
