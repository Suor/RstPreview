"""
RstPreview renders reStructuredText files as HTML and shows them in your
default browser.
"""

import sys
import os

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from webbrowser import open as open_in_browser

import sublime
from sublime_plugin import TextCommand
from sublime import Region

SETTINGS_FILE = 'RstPreview.sublime-settings'


def rst_to_html(rst_text):
    try:
        from docutils.core import publish_string
        css_path = os.path.join(sublime.packages_path(), 'RstPreview/css/')
        args = {
            'stylesheet_path': ','.join(
                css_path + css for css in ('bootstrap.min.css', 'base.css', 'pygments-default.css')
            )
        }
        return publish_string(rst_text, writer_name='html', settings_overrides=args)
    except ImportError:
        error_msg = """RstPreview requires docutils to be installed for the python interpreter that Sublime uses.
    run: `sudo easy_install-2.6 docutils` and restart Sublime (if on Mac OS X or Linux). For Windows check the docs at
    https://github.com/d0ugal/RstPreview"""

        sublime.error_message(error_msg)
        raise


def render_in_browser(html):
    """
    Starts a simple HTTP server, directs the browser to it and handles that
    request before closing down. This avoids the need to create many temp
    files. However, it does mean the page can't be reloaded after which is
    a little odd.
    """

    class RequestHandler(BaseHTTPRequestHandler):

        def do_GET(self):
            """
            Write the HTML to the request file
            """
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html)

    # Start the server on a given random port
    server = HTTPServer(('127.0.0.1', 0), RequestHandler)
    # point the browser to that IP and port.
    open_in_browser('http://127.0.0.1:%s' % server.server_port)
    # handle the single request and then end.
    server.handle_request()


class RstpreviewCommand(TextCommand):

    def run(self, edit):

        settings = sublime.load_settings(SETTINGS_FILE)
        site_packages_path = settings.get('site_packages_path')
        if site_packages_path and site_packages_path not in sys.path:
            sys.path.append(site_packages_path)

        # Select all the text in the current document
        text = self.view.substr(Region(0, self.view.size()))

        # Write that RST text as HTML
        html = rst_to_html(text)

        render_in_browser(html)
