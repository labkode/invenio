# -*- coding: utf-8 -*-
##
## $Id$
##
## This file is part of CDS Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007, 2008 CERN.
##
## CDS Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## CDS Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with CDS Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Unit tests for htmlutils library."""

__revision__ = "$Id$"

import unittest

from invenio import dbquery
from invenio.htmlutils import HTMLWasher, nmtoken_from_string
from invenio.testutils import make_test_suite, run_test_suite

class XSSEscapingTest(unittest.TestCase):
    """Test functions related to the prevention of XSS attacks."""

    def __init__(self, methodName='test'):
        self.washer = HTMLWasher()
        unittest.TestCase.__init__(self, methodName)

    def test_forbidden_formatting_tags(self):
        """htmlutils - washing of tags altering formatting of a page (e.g. </html>)"""
        test_str = """</html></body></div></pre>"""
        self.assertEqual(self.washer.wash(html_buffer=test_str),
                         '')
        self.assertEqual(self.washer.wash(html_buffer=test_str,
                                          render_unallowed_tags=True),
                         '&lt;/html&gt;&lt;/body&gt;&lt;/div&gt;&lt;/pre&gt;')

    def test_forbidden_script_tags(self):
        """htmlutils - washing of tags defining scripts (e.g. <script>)"""
        test_str = """<script>malicious_function();</script>"""
        self.assertEqual(self.washer.wash(html_buffer=test_str),
                         'malicious_function();')
        self.assertEqual(self.washer.wash(html_buffer=test_str,
                                          render_unallowed_tags=True),
                         '&lt;script&gt;malicious_function();&lt;/script&gt;')

    def test_forbidden_attributes(self):
        """htmlutils - washing of forbidden attributes in allowed tags (e.g. onLoad)"""
        # onload
        test_str = """<p onload="javascript:malicious_functtion();">"""
        self.assertEqual(self.washer.wash(html_buffer=test_str), '<p>')
        # tricky: css calling a javascript
        test_str = """<p style="background: url('http://malicious_site.com/malicious_script.js');">"""
        self.assertEqual(self.washer.wash(html_buffer=test_str), '<p>')

    def test_fake_url(self):
        """htmlutils - washing of fake URLs which execute scripts"""
        test_str = """<a href="javascript:malicious_function();">link</a>"""
        self.assertEqual(self.washer.wash(html_buffer=test_str),
                         '<a href="">link</a>')
        # Pirates could encode ascii values, or use uppercase letters...
        test_str = """<a href="&#106;a&#118;asCRi&#112;t:malicious_function();">link</a>"""
        self.assertEqual(self.washer.wash(html_buffer=test_str),
                         '<a href="">link</a>')
        # MSIE treats 'java\ns\ncript:' the same way as 'javascript:'
        # Here we test with:
        # j
        #     avas
        #   crIPt :
        test_str = """<a href="&#106;\n    a&#118;as\n  crI&#80;t :malicious_function();">link</a>"""
        self.assertEqual(self.washer.wash(html_buffer=test_str),
                         '<a href="">link</a>')

class CharactersEscapingTest(unittest.TestCase):
    """Test functions related to escaping reserved or forbidden characters """

    def test_convert_string_to_nmtoken(self):
        """htmlutils - converting string to Nmtoken"""

        # TODO: possibly extend this test to include 'extenders' and
        # 'combining characters' as defined in
        # http://www.w3.org/TR/2000/REC-xml-20001006#NT-Nmtoken

        ascii_str = "".join([chr(i) for i in range(0, 256)])
        nmtoken = nmtoken_from_string(ascii_str)
        for char in nmtoken:
            self.assert_(char in ['.', '-', '_', ':'] or char.isalnum())

TEST_SUITE = make_test_suite(XSSEscapingTest,
                             CharactersEscapingTest,)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)

