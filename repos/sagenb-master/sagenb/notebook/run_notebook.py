# -*- coding: utf-8 -*
"""nodoctest
Serve the Sage Notebook.
"""
from __future__ import absolute_import

#############################################################################
#       Copyright (C) 2009 William Stein <wstein@gmail.com>
#  Distributed under the terms of the GNU General Public License (GPL)
#  The full text of the GPL is available at:
#                  http://www.gnu.org/licenses/
#############################################################################

# System libraries
import getpass
import os
import shutil
import socket
import sys
import hashlib

from twisted.python.runtime import platformType

from six import iteritems

try:
    basestring
except NameError:
    basestring = (str, bytes)

from sagenb.misc.misc import (DOT_SAGENB, find_next_available_port,
                              print_open_msg)

from . import notebook

conf_path     = os.path.join(DOT_SAGENB, 'notebook')

private_pem   = os.path.join(conf_path, 'private.pem')
public_pem    = os.path.join(conf_path, 'public.pem')
template_file = os.path.join(conf_path, 'cert.cfg')


class NotebookRun(object):
    config_stub="""
####################################################################
# WARNING -- Do not edit this file!   It is autogenerated each time
# the notebook(...) command is executed.
####################################################################
import sagenb.notebook.misc
sagenb.notebook.misc.DIR = %(cwd)r #We should really get rid of this!

#########
# Flask #
#########
import os, sys, random
import sagenb.flask_version.base as flask_base
opts={}
startup_token = '{0:x}'.format(random.randint(0, 2**128))
if %(automatic_login)s:
    opts['startup_token'] = startup_token
flask_app = flask_base.create_app(%(notebook_opts)s, **opts)

def save_notebook(notebook):
    print("Quitting all running worksheets...")
    notebook.quit()
    print("Saving notebook...")
    notebook.save()
    print("Notebook cleanly saved.")

"""
    def prepare_kwds(self, kw):
        import os
        kw['absdirectory']=os.path.abspath(kw['directory'])
        kw['notebook_opts'] = '"%(absdirectory)s",interface="%(interface)s",port=%(port)s,secure=%(secure)s'%kw
        kw['hostname'] = kw['interface'] if kw['interface'] else 'localhost'

        if kw['automatic_login']:
            kw['start_path'] = "'/?startup_token=%s' % startup_token"
            kw['open_page'] = "from sagenb.misc.misc import open_page; open_page('%(hostname)s', %(port)s, %(secure)s, %(start_path)s)" % kw

            if kw['upload']:
                import urllib
                # If we have to login and upload a file, then we do them
                # in that order and hope that the login is fast enough.
                kw['start_path'] = "'/upload_worksheet?url=file://%s'" % (urllib.quote(kw['upload']))
                kw['open_page'] = kw['open_page']+ "; open_page('%(hostname)s', %(port)s, %(secure)s, %(start_path)s)" % kw

        elif kw['upload']:
            import urllib
            kw['start_path'] = "'/upload_worksheet?url=file://%s'" % (urllib.quote(kw['upload']))
            kw['open_page'] = "from sagenb.misc.misc import open_page; open_page('%(hostname)s', %(port)s, %(secure)s, %(start_path)s)" % kw

        else:
            kw['open_page'] = ''


    def profile_file(self, profile):
        import random
        _id=random.random()
        if isinstance(profile, basestring):
            profilefile = profile+'%s.stats'%_id
        else:
            profilefile = 'sagenb-%s-profile-%s.stats'%(self.name,_id)
        return profilefile

    def run_command(self, kw):
        raise NotImplementedError

class NotebookRunTornado(NotebookRun):
    name="tornado"
    TORNADO_NOTEBOOK_CONFIG = """
from tornado import web
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

%(open_page)s
wsgi_app = WSGIContainer(flask_app)
http_server = HTTPServer(wsgi_app)
http_server.listen(%(port)s)
IOLoop.instance().start()
"""
    def run_command(self, kw):
        """Run a tornado webserver."""
        self.prepare_kwds(kw)
        run_file = os.path.join(kw['directory'], 'run_tornado')

        with open(run_file, 'w') as script:
            script.write((self.config_stub+self.TORNADO_NOTEBOOK_CONFIG)%kw)

        cmd = 'python %s' % (run_file)
        return cmd

class NotebookRunuWSGI(NotebookRun):
    name="uWSGI"
    uWSGI_NOTEBOOK_CONFIG  = """
import atexit
from functools import partial
atexit.register(partial(save_notebook,flask_base.notebook))
%(open_page)s
"""
    def run_command(self, kw):
        """Run a uWSGI webserver."""
        # TODO: Check to see if server is running already (PID file?)
        self.prepare_kwds(kw)
        run_file = os.path.join(kw['directory'], 'run_uwsgi')

        with open(run_file, 'w') as script:
            script.write((self.config_stub+self.uWSGI_NOTEBOOK_CONFIG)%kw)

        port=kw['port']
        pidfile=kw['pidfile']
        cmd = 'uwsgi --single-interpreter --socket-timeout 30 --http-timeout 30 --listen 300 --http-socket :%s --file %s --callable flask_app --pidfile %s' % (port, run_file, pidfile)
        # Comment out the line below to turn on request logging
        cmd += ' --disable-logging'
        cmd += ' --threads 4 --enable-threads'
        return cmd

class NotebookRunFlask(NotebookRun):
    name="flask"
    FLASK_NOTEBOOK_CONFIG = """
import os
with open(%(pidfile)r, 'w') as pidfile:
    pidfile.write(str(os.getpid()))

if %(secure)s:
    try:
        from OpenSSL import SSL
        ssl_context = SSL.Context(SSL.SSLv23_METHOD)
        ssl_context.use_privatekey_file(%(private_pem)r)
        ssl_context.use_certificate_file(%(public_pem)r)
    except ImportError:
        raise RuntimeError("HTTPS cannot be used without pyOpenSSL"
                " installed. See the Sage README for more information.")
else:
    ssl_context = None

import logging
logger=logging.getLogger('werkzeug')
logger.setLevel(logging.WARNING)
#logger.setLevel(logging.INFO) # to see page requests
#logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

if %(secure)s:
    # Monkey-patch werkzeug so that it works with pyOpenSSL and Python 2.7
    # otherwise, we constantly get TypeError: shutdown() takes exactly 0 arguments (1 given)

    # Monkey patching idiom: http://mail.python.org/pipermail/python-dev/2008-January/076194.html
    def monkeypatch_method(cls):
        def decorator(func):
            setattr(cls, func.__name__, func)
            return func
        return decorator
    from werkzeug import serving

    @monkeypatch_method(serving.BaseWSGIServer)
    def shutdown_request(self, request):
        request.shutdown()

%(open_page)s
try:
    flask_app.run(host=%(interface)r, port=%(port)s, threaded=True,
                  ssl_context=ssl_context, debug=False)
finally:
    save_notebook(flask_base.notebook)
    os.unlink(%(pidfile)r)
"""

    def run_command(self, kw):
        """Run a flask (werkzeug) webserver."""
        # TODO: Check to see if server is running already (PID file?)
        self.prepare_kwds(kw)
        run_file = os.path.join(kw['directory'], 'run_flask')

        with open(run_file, 'w') as script:
            script.write((self.config_stub+self.FLASK_NOTEBOOK_CONFIG)%kw)

        if kw['profile']:
            profilecmd = '-m cProfile -o %s'%self.profile_file(kw['profile'])
        else:
            profilecmd=''
        cmd = 'python %s %s' % (profilecmd, run_file)
        return cmd

class NotebookRunTwisted(NotebookRun):
    name="twistd"
    TWISTD_NOTEBOOK_CONFIG = """
########################################################################
# See http://twistedmatrix.com/documents/current/web/howto/using-twistedweb.html
#  (Serving WSGI Applications) for the basic ideas of the below code
####################################################################

##### START EPOLL
# Take this out when Twisted 12.1 is released, since epoll will then
# be the default reactor when needed.  See http://twistedmatrix.com/trac/ticket/5478
import sys, platform
if (platform.system()=='Linux'
    and (platform.release().startswith('2.6')
         or platform.release().startswith('3'))):
    try:
        from twisted.internet import epollreactor
        epollreactor.install()
    except:
        pass
#### END EPOLL


def save_notebook2(notebook):
    from twisted.internet.error import ReactorNotRunning
    save_notebook(notebook)

import signal
from twisted.internet import reactor
def my_sigint(x, n):
    try:
        reactor.stop()
    except ReactorNotRunning:
        pass
    signal.signal(signal.SIGINT, signal.SIG_DFL)

signal.signal(signal.SIGINT, my_sigint)

from twisted.web import server
from twisted.web.wsgi import WSGIResource
resource = WSGIResource(reactor, reactor.getThreadPool(), flask_app)

class QuietSite(server.Site):
    def log(*args, **kwargs):
        "Override the logging so that requests are not logged"
        pass

# Log only errors, not every page hit
site = QuietSite(resource)

# To log every single page hit, uncomment the following line
#site = server.Site(resource)

from twisted.application import service, strports
application = service.Application("Sage Notebook")
s = strports.service(%(strport)r, site)
%(open_page)s
s.setServiceParent(application)

#This has to be done after flask_base.create_app is run
from functools import partial
reactor.addSystemEventTrigger('before', 'shutdown', partial(save_notebook2, flask_base.notebook))
"""

    def run_command(self, kw):
        """Run a twistd webserver."""
        # Is a server already running? Check if a Twistd PID exists in
        # the given directory.

        self.prepare_kwds(kw)
        conf = os.path.join(kw['directory'], 'twistedconf.tac')
        if platformType != 'win32':
            from twisted.scripts._twistd_unix import checkPID
            try:
                checkPID(kw['pidfile'])
            except SystemExit as e:
                pid = int(open(kw['pidfile']).read())

                if str(e).startswith('Another twistd server is running,'):
                    print('Another Sage Notebook server is running, PID %d.' % pid)

                    old_interface, old_port, old_secure = self.get_old_settings(conf)
                    if (kw['automatic_login'] or kw['upload']) and old_port:
                        old_interface = old_interface or 'localhost'
                        if kw['upload']:
                            import urllib
                            startpath = '/upload_worksheet?url=file://%s' % (urllib.quote(kw['upload']))
                        else:
                            startpath = '/'

                        print('Opening web browser at http%s://%s:%s%s ...' % (
                            's' if old_secure else '', old_interface, old_port, startpath))

                        from sagenb.misc.misc import open_page as browse_to
                        browse_to(old_interface, old_port, old_secure, startpath)
                        return None
                    print('\nPlease either stop the old server or run the new server in a different directory.')
                    return None

        ## Create the config file
        if kw['secure']:
            kw['strport'] = 'ssl:%(port)s:interface=%(interface)s:privateKey=%(private_pem)s:certKey=%(public_pem)s'%kw
        else:
            kw['strport'] = 'tcp:%(port)s:interface=%(interface)s'%kw


        with open(conf, 'w') as config:
            config.write((self.config_stub+self.TWISTD_NOTEBOOK_CONFIG)%kw)

        if kw['profile']:
            profilecmd = '--profile=%s --profiler=cprofile --savestats'%self.profile_file(kw['profile'])
        else:
            profilecmd=''
        cmd = 'twistd %s --pidfile="%s" -ny "%s"' % (profilecmd, kw['pidfile'], conf)
        return cmd

    def get_old_settings(self, conf):
        """
        Returns three settings from the Twisted configuration file conf:
        the interface, port number, and whether the server is secure.  If
        there are any errors, this returns (None, None, None).
        """
        import re
        # This should match the format written to twistedconf.tac below.
        p = re.compile(r'interface="(.*)",port=(\d*),secure=(True|False)')
        try:
            interface, port, secure = p.search(open(conf, 'r').read()).groups()
            if secure == 'True':
                secure = True
            else:
                secure = False
            return interface, port, secure
        except (IOError, AttributeError):
            return None, None, None


def cmd_exists(cmd):
    """
    Return True if the given cmd exists.
    """
    return os.system('which %s 2>/dev/null >/dev/null' % cmd) == 0


def notebook_setup(self=None):
    if not os.path.exists(conf_path):
        os.makedirs(conf_path)

    if not cmd_exists('certtool'):
        raise RuntimeError("You must install certtool to use the secure notebook server.")

    dn = raw_input("Domain name [localhost]: ").strip()
    if dn == '':
        print("Using default localhost")
        dn = 'localhost'

    import random
    template_dict = {'organization': 'SAGE (at %s)' % (dn),
                'unit': '389',
                'locality': None,
                'state': 'Washington',
                'country': 'US',
                'cn': dn,
                'uid': 'sage_user',
                'dn_oid': None,
                'serial': str(random.randint(1, 2 ** 31)),
                'dns_name': None,
                'crl_dist_points': None,
                'ip_address': None,
                'expiration_days': 8999,
                'email': 'sage@sagemath.org',
                'ca': None,
                'tls_www_client': None,
                'tls_www_server': True,
                'signing_key': True,
                'encryption_key': True,
                }

    s = ""
    for key, val in iteritems(template_dict):
        if val is None:
            continue
        if val is True:
            w = ''
        elif isinstance(val, list):
            w = ' '.join(['"%s"' % x for x in val])
        else:
            w = '"%s"' % val
        s += '%s = %s \n' % (key, w)

    with open(template_file, 'w') as f:
        f.write(s)

    import subprocess

    if cmd_exists('openssl'):
        # We use openssl by default if it exists, since it is open
        # *vastly* faster on Linux, for some weird reason.
        cmd = ['openssl genrsa 1024 > %s' % private_pem]
        print("Using openssl to generate key")
        print(cmd[0])
        subprocess.call(cmd, shell=True)
    else:
        # We checked above that certtool is available.
        cmd = ['certtool --generate-privkey --outfile %s' % private_pem]
        print("Using certtool to generate key")
        print(cmd[0])
        subprocess.call(cmd, shell=True)

    cmd = ['certtool --generate-self-signed --template %s --load-privkey %s '
           '--outfile %s' % (template_file, private_pem, public_pem)]
    print(cmd[0])
    subprocess.call(cmd, shell=True)

    # Set permissions on private cert
    os.chmod(private_pem, 0o600)

    print("Successfully configured notebook.")

command={'flask': NotebookRunFlask, 'twistd': NotebookRunTwisted, 'uwsgi': NotebookRunuWSGI, 'tornado': NotebookRunTornado}
def notebook_run(self,
             directory     = None,
             port          = 8080,
             interface     = 'localhost',
             port_tries    = 50,
             secure        = False,
             reset         = False,
             accounts      = None,
             openid        = None,

             server_pool   = None,
             ulimit        = '',

             timeout       = None,   # timeout for normal worksheets. This is the
                                  # same as idle_timeout in server_conf.py
             doc_timeout   = None, # timeout for documentation worksheets

             upload        = None,
             automatic_login = True,

             start_path    = "",
             fork          = False,
             quiet         = False,

             server = "twistd",
             profile = False,

             subnets = None,
             require_login = None,
             open_viewer = None,
             address = None,
             ):

    # Check whether pyOpenSSL is installed or not (see Sage trac #13385)
    if secure:
        try:
            import OpenSSL
        except ImportError:
            raise RuntimeError("HTTPS cannot be used without pyOpenSSL"
                    " installed. See the Sage README for more information.")

    # Turn it into a full path for later conversion to a file URL
    if upload:
        upload_abs = os.path.abspath(upload)
        if os.path.exists(upload_abs):
            upload = upload_abs
        else:
            # They might have expected ~ to be expanded to their user directory
            upload = os.path.expanduser(upload)
            if not os.path.exists(upload):
                raise ValueError("Unable to find the file %s to upload" % upload)


    if subnets is not None:
        raise ValueError("""The subnets parameter is no longer supported. Please use a firewall to block subnets, or even better, volunteer to write the code to implement subnets again.""")
    if require_login is not None or open_viewer is not None:
        raise ValueError("The require_login and open_viewer parameters are no longer supported.  "
                         "Please use automatic_login=True to automatically log in as admin, "
                         "or use automatic_login=False to not automatically log in.")
    if address is not None:
        raise ValueError("Use 'interface' instead of 'address' when calling notebook(...).")

    cwd = os.getcwd()

    if directory is None:
        directory = '%s/sage_notebook.sagenb' % DOT_SAGENB
    else:
        directory = directory.rstrip('/')
        if not directory.endswith('.sagenb'):
            directory += '.sagenb'

    # First change to the directory that contains the notebook directory
    wd = os.path.split(directory)
    if wd[0]:
        os.chdir(wd[0])
    directory = wd[1]
    pidfile = os.path.join(directory, 'sagenb.pid')

    port = int(port)

    if not secure and interface != 'localhost':
        print('*' * 70)
        print("WARNING: Running the notebook insecurely not on localhost is dangerous")
        print("because its possible for people to sniff passwords and gain access to")
        print("your account. Make sure you know what you are doing.")
        print('*' * 70)

    # first use provided values, if none, use loaded values,
    # if none use defaults

    nb = notebook.load_notebook(directory)

    directory = nb._dir

    if not quiet:
        print("The notebook files are stored in:", nb._dir)

    if timeout is not None:
        nb.conf()['idle_timeout'] = int(timeout)
    if doc_timeout is not None:
        nb.conf()['doc_timeout'] = int(doc_timeout)

    if openid is not None:
        nb.conf()['openid'] = openid
    elif not nb.conf()['openid']:
        # What is the purpose behind this elif?  It seems rather pointless.
        # all it appears to do is set the config to False if bool(config) is False
        nb.conf()['openid'] = False

    if accounts is not None:
        nb.user_manager().set_accounts(accounts)
    else:
        nb.user_manager().set_accounts(nb.conf()['accounts'])

    if nb.user_manager().user_exists('root') and not nb.user_manager().user_exists('admin'):
        # This is here only for backward compatibility with one
        # version of the notebook.
        s = nb.create_user_with_same_password('admin', 'root')
        # It would be a security risk to leave an escalated account around.

    if not nb.user_manager().user_exists('admin'):
        reset = True

    if reset:
        passwd = get_admin_passwd()
        if nb.user_manager().user_exists('admin'):
            admin = nb.user_manager().user('admin')
            admin.set_password(passwd)
            print("Password changed for user 'admin'.")
        else:
            nb.user_manager().create_default_users(passwd)
            print("User admin created with the password you specified.")
            print("\n\n")
            print("*" * 70)
            print("\n")
            if secure:
                print("Login to the Sage notebook as admin with the password you specified above.")
        #nb.del_user('root')

    # For old notebooks, make sure that default users are always created.
    # This fixes issue #175 (https://github.com/sagemath/sagenb/issues/175)
    um = nb.user_manager()
    for user in ('_sage_', 'pub'):
        if not um.user_exists(user):
            um.add_user(user, '', '', account_type='user', force=True)
    if not um.user_exists('guest'):
        um.add_user('guest', '', '', account_type='guest', force=True)

    nb.set_server_pool(server_pool)
    nb.set_ulimit(ulimit)

    if os.path.exists('%s/nb-older-backup.sobj' % directory):
        nb._migrate_worksheets()
        os.unlink('%s/nb-older-backup.sobj' % directory)
        print("Updating to new format complete.")


    nb.upgrade_model()
    nb.save()
    del nb

    if interface != 'localhost' and not secure:
            print("*" * 70)
            print("WARNING: Insecure notebook server listening on external interface.")
            print("Unless you are running this via ssh port forwarding, you are")
            print("**crazy**!  You should run the notebook with the option secure=True.")
            print("*" * 70)

    port = find_next_available_port(interface, port, port_tries)
    if automatic_login:
        "Automatic login isn't fully implemented.  You have to manually open your web browser to the above URL."
    if secure:
        if (not os.path.exists(private_pem) or
            not os.path.exists(public_pem)):
            print("In order to use an SECURE encrypted notebook, you must first run notebook.setup().")
            print("Now running notebook.setup()")
            notebook_setup()
        if (not os.path.exists(private_pem) or
            not os.path.exists(public_pem)):
            print("Failed to setup notebook.  Please try notebook.setup() again manually.")

    kw = dict(port=port, automatic_login=automatic_login, secure=secure, private_pem=private_pem, public_pem=public_pem,
              interface=interface, directory=directory, pidfile=pidfile, cwd=cwd, profile=profile, upload = upload )
    cmd = command[server]().run_command(kw)
    if cmd is None:
        return

    if not quiet:
        print_open_msg('localhost' if not interface else interface,
        port, secure=secure)
    if secure and not quiet:
        print("There is an admin account.  If you do not remember the password,")
        print("quit the notebook and type notebook(reset=True).")
    print("Executing {}".format(cmd))
    if fork:
        import pexpect
        return pexpect.spawn(cmd)
    else:
        e = os.system(cmd)

    os.chdir(cwd)
    if e == 256:
        raise socket.error

def get_admin_passwd():
    print("\n" * 2)
    print("Please choose a new password for the Sage Notebook 'admin' user.")
    print("Do _not_ choose a stupid password, since anybody who could guess your password")
    print("and connect to your machine could access or delete your files.")
    print("NOTE: Only the hash of the password you type is stored by Sage.")
    print("You can change your password by typing notebook(reset=True).")
    print("\n" * 2)
    while True:
        passwd = getpass.getpass("Enter new password: ")
        from sagenb.misc.misc import min_password_length
        if len(passwd) < min_password_length:
            print("That password is way too short. Enter a password with at least %d characters."%min_password_length)
            continue
        passwd2 = getpass.getpass("Retype new password: ")
        if passwd != passwd2:
            print("Sorry, passwords do not match.")
        else:
            break

    print("Please login to the notebook with the username 'admin' and the above password.")
    return passwd