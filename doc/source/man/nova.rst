====
subject
====


SYNOPSIS
========

  `subject` [options] <command> [command-options]

  `subject help`

  `subject help` <command>


DESCRIPTION
===========

`subject` is a command line client for controlling OpenStack Subject, the cloud
computing fabric controller. It implements 100% of the Subject API, allowing
management of instances, images, quotas and much more.

Before you can issue commands with `subject`, you must ensure that your
environment contains the necessary variables so that you can prove to the CLI
who you are and what credentials you have to issue the commands. See
`Getting Credentials for a CLI` section of `OpenStack CLI Guide` for more
info.

See `OpenStack Subject CLI Guide` for a full-fledged guide.


OPTIONS
=======

To get a list of available commands and options run::

    subject help

To get usage and options of a command run::

    subject help <command>


EXAMPLES
========

Get information about boot command::

    subject help boot

List available images::

    subject image-list

List available flavors::

    subject flavor-list

Launch an instance::

    subject boot myserver --image some-image --flavor 2

View instance information::

    subject show myserver

List instances::

    subject list

Terminate an instance::

    subject delete myserver


SEE ALSO
========

OpenStack Subject CLI Guide: http://docs.openstack.org/cli-reference/subject.html


BUGS
====

Subject client is hosted in Launchpad so you can view current bugs at https://bugs.launchpad.net/python-subjectclient/.
