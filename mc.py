import threading
import urllib.request
from html.parser import HTMLParser
import sys
from urllib.parse import urljoin

class LinkHTMLParser(HTMLParser):
    A_TAG = "a"
    HREF_ATTRIBUTE = "href"

    def __init__(self):
        self.links = []
        super().__init__()

    def handle_starttag(self, tag, attrs):
        """Add all 'href' links within 'a' tags to self.links"""
        if tag == self.A_TAG:
            for (key, value) in attrs:
                if key == self.HREF_ATTRIBUTE:
                    self.links.append(value)

    def handle_endtag(self, tag):
        pass

class CrawlerThread(threading.Thread):
    def __init__(self, binarySemaphore, url, crawlDepth):
        self.binarySemaphore = binarySemaphore
        self.url = url
        self.crawlDepth = crawlDepth
        self.threadId = hash(self)
        super().__init__()

    def run(self):
        """Print out all of the links on the given URL associated with this particular thread. Grab the passed-in
        binary semaphore when attempting to write to STDOUT so that there is no overlap between threads' output."""
        with urllib.request.urlopen(self.url) as socket:
            urlMarkup = socket.read().decode('utf-8')
            linkHTMLParser = LinkHTMLParser()
            linkHTMLParser.feed(urlMarkup)
            self.binarySemaphore.acquire()  # wait if another thread has acquired and not yet released binary semaphore
            print("Thread #%d: Reading from %s" % (self.threadId, self.url))
            print("Thread #%d: Crawl Depth = %d" % (self.threadId, self.crawlDepth))
            print("Thread #%d: Retrieved the following links..." % (self.threadId))
            urls = []
            for link in linkHTMLParser.links:
                link = urljoin(self.url, link)
                urls.append(link)
                print("\t" + link)
            print("")
            self.binarySemaphore.release()
            for url in urls:
                # Keep crawling to different URLs until the crawl depth is less than 1
                if self.crawlDepth > 1:
                    CrawlerThread(self.binarySemaphore, url, self.crawlDepth - 1).start()

if __name__ == "__main__":
    binarySemaphore = threading.Semaphore(1)
    urls = [("http://www.google.com", 1), ("http://www.twitter.com", 2), ("http://www.facebook.com", 1),
            ("http://www.cnn.com", 1), ("http://www.nyt.com", 1), ("http://www.schwab.com", 1),
            ("http://www.bankofamerica.com", 1)]
    for (url, crawlDepth) in urls:
        CrawlerThread(binarySemaphore, url, crawlDepth).start()
