
Setup MAP Client for Development
================================

This is a simple script to setup a development installation of MAP Client.

To start create a virtual environment::

  python -m venv venv_map_client_dev

And activate it (macOS/Linux)::

  source venv_map_client_dev/bin/activate

or (Windows)::

  venv_map_client_dev\Scripts\Activate

To setup a basic development simply run the setup script::

  python <relative-or-absolute-path-to-this-repository>/src/setup_map_client.py common

The script accepts a *set* parameter that installs plugins, workflows, and packages listed under that set.
The available sets are: common, sparc, msk.
