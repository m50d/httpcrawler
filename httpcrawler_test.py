#!/usr/bin/env python
import unittest
from httpcrawler import PageResult

class PageResultTest(unittest.TestCase):

    def setUp(self):
        self.pr = PageResult("dummyUrl",
"""
<!DOCTYPE html>
  <head>
    <meta charset="utf-8">
    <title>Dummy Title</title>
    <link href="/dummyStylesheet.css" media="screen" rel="stylesheet" type="text/css" />
  </head>
  <body>Dummy Body</body>
""")

    def test_findsCss(self):
        #check we pulled some css out of the page
        self.assertTrue(self.pr.css)

if __name__ == '__main__':
    unittest.main()
