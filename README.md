Cli-Twi
=======

Cli-Twi is a dead-simple command line interface Twitter client.

Features
--------

* Display unread tweets
* Display unread mentions
* Update status
* OAuth

Installation
------------

* Create a `.clitwi` directory in your home directory
* Move all the files to that directory
* Register an application on Twitter
* Put your application details into `config.py`
* Run `python main.py setup`

Optionally, set up a bash alias:

    alias m='/home/you/.clitwi/main.py'

Then you can run:

    $ m
    $ m -m
    $ m "Your tweet"
    $ m --help

Contribution
------------

Any hacks or improvements are welcome. Send all your pull requests along. The
only humble request I have is that your code adheres to PEP8.

License
-------

Licensed under BSD.
