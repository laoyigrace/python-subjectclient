The :program:`subject` shell utility
=================================

.. program:: subject
.. highlight:: bash

The :program:`subject` shell utility interacts with OpenStack Subject API
from the command line. It supports the entirety of the OpenStack Subject API.

First, you'll need an OpenStack Subject account and an API key. You get this
by using the `subject-manage` command in OpenStack Subject.

You'll need to provide :program:`subject` with your OpenStack username and
API key. You can do this with the :option:`--os-username`, :option:`--os-password`
and :option:`--os-tenant-id` options, but it's easier to just set them as
environment variables by setting two environment variables:

.. envvar:: OS_USERNAME

    Your OpenStack Subject username.

.. envvar:: OS_PASSWORD

    Your password.

.. envvar:: OS_TENANT_NAME

    Project for work.

.. envvar:: OS_AUTH_URL

    The OpenStack API server URL.

.. envvar:: OS_COMPUTE_API_VERSION

    The OpenStack API version.

For example, in Bash you'd use::

    export OS_USERNAME=yourname
    export OS_PASSWORD=yadayadayada
    export OS_TENANT_NAME=myproject
    export OS_AUTH_URL=http://...
    export OS_COMPUTE_API_VERSION=2
    
From there, all shell commands take the form::
    
    subject <command> [arguments...]

Run :program:`subject help` to get a full list of all possible commands,
and run :program:`subject help <command>` to get detailed help for that
command.
