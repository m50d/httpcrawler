# httpcrawler

Very basic HTTP crawler, written in python.
Crawls a single domain and outputs an SVG graph showing links between pages and resources (images, css, javascript)

Usage:

    $ python httpcrawler.py http://m50d.github.com

Graph will be in the file "out.svg". Nodes and links are coloured according to type - black for pages, red for javascript, green for images and yellow for css.

Dependencies:
* Twisted (async HTTP client)
* BeautifulSoup (HTML parsing)
* Pygraphviz (graph drawing)

Known issues:
* Hangs if passed an invalid URL
* Will not follow links to query pages, but will happily follow an infinitely generated chain of "plain" links (if you have e.g. /page/1 linking to /page/2 linking to ...)
* Redirects may or may not show up as blue nodes in the graph - untested

Potential improvements:
* Separate crawling and graphing parts of the program
* More control over which links to follow (currently follows any links on the same host)
* More control over graphviz output (e.g. filename, format, ...)