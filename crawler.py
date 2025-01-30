from urllib.request import urlopen# Urllib_ URL handling module for python. Used to fetch URLs. urllib.request for opening and reading.
import fileManipulation as files
from html.parser import HTMLParser
from urllib import parse#urllib.parse for parsing URLs

#Creating our HTMLParser. 
#when you need to read loads of websites and find specific information, HTMLParser module will make the task a cakewalk for you.
class LinkFinder(HTMLParser):
    def __init__(self, base_url, page_url):#self_ instance of class,base_url is URL entered by user,page_url is domain_name extracted from URL
        super().__init__()#super()_lets you avoid referring to base class explicitly, which can be nice like super(LinkFinder, self).__init__()
        self.base_url = base_url
        self.page_url = page_url
        self.links = set()
    
    #Defining what the methods should output when called by HTMLParser.
    def handle_starttag(self, tag, attr):
        # Only parse the 'anchor' tag.
        if tag == 'a':
            for (attribute, value) in attr:
                if attribute == 'href':
                    url = parse.urljoin(self.base_url, value)
                    self.links.add(url)

    # return the set of links
    def page_links(self):
        return self.links

    # inherited abstract method of the HTMLParser class
    def error(self, message):
        pass

class Crawler:
    # Class variables (shared among all the instances)
    project_name = ''   # will be entered by the user at run time
    base_url = ''       # base url needed to get the full url from relative ones
    domain_name = ''    # for checking whether the domain names are valid or not
    queue_file = ''     # file for storing queue items from the list
    crawled_file = ''   # file for storing crawled items from the list
    queue = set()       # set of all urls in the waiting list
    crawled = set()     # set of all urls in th crawled list

    # method for creating the initial project directory and the data files within
    @staticmethod # because we are only assigning values to class variables a method was not really necessary
    def boot():
        # create the project directory with the name as specified by the user
        files.create_project_dir(Crawler.project_name)

        # create the files within the project directory
        files.create_data_files(Crawler.project_name, Crawler.base_url)

        # create the queue set and the crawled set
        Crawler.queue = files.file_to_set(Crawler.queue_file)
        Crawler.crawled = files.file_to_set(Crawler.crawled_file)

    @staticmethod
    def add_links_to_queue(links):
        for url in links:
            # checking if the urls are not in either of the queue list or the crawler list
            if url in Crawler.queue or url in Crawler.crawled:
                continue
            if Crawler.domain_name not in url:
                continue
            Crawler.queue.add(url)

    @staticmethod
    def gather_links(page_url):
        html_string = ''
        try:
            response = urlopen(page_url)#module to open URLs (mostly HTTP)
            # just check if the page contains html and is not something else eg. a pdf or something
            if 'text/html' in response.getheader('Content-Type'):#getheader()_ Return value of header name, or default if there is no 
                # header matching name. If there is more than one header with the name name, return all of the values joined by ','.
                html_bytes = response.read() # reading the raw bytes from response to html_bytes. Reads and returns the response body.
                html_string = html_bytes.decode("utf-8") # decoding the bytes to utf-8 string format
            finder = LinkFinder(Crawler.base_url, page_url)
            finder.feed(html_string)#we are feeding data to the parser. I fed basic HTML code directly.
        except Exception as e:
            print(str(e))
            return set() # our function needs to return a set from where it is called.
            # Hence even if anything is not found at least an empty set should be returned
        # finally returning the set of urls from the LinkFinder.page_links()
        return finder.page_links()
    
    @staticmethod
    def update_files():
        files.set_to_file(Crawler.queue, Crawler.queue_file)
        files.set_to_file(Crawler.crawled, Crawler.crawled_file)

    @staticmethod
    def crawl_page(thread_name, page_url):
        # making sure we haven't already crawled this page already
        if page_url not in Crawler.crawled:
            print(thread_name, 'is crawling', page_url)
            Crawler.add_links_to_queue(Crawler.gather_links(page_url))
            # remove page_url from the queue and add it to the crawled list
            Crawler.queue.remove(page_url)
            Crawler.crawled.add(page_url)
            # update the files in the directory
            Crawler.update_files()

    def __init__(self, project_name, base_url, domain_name):#"__init__" is a reseved method in python classes.
    #It is known as a constructor in object oriented concepts.
    #This method called when an object is created from the class and it allow the class to initialize the attributes of a class.
        # assigning the same project_name, base_url and domain_name for all spider instances created
        Crawler.project_name = project_name
        Crawler.base_url = base_url
        Crawler.domain_name = domain_name
        
        # assigning the file paths for queue and crawled files
        Crawler.queue_file = project_name + '/queueList.txt'
        Crawler.crawled_file = project_name + '/crawledList.txt'
        #"self"  represents the instance of the class. It binds the attributes with the given arguments.
        #Usage of "self" in class to access the methods and attributes
        self.boot()
        self.crawl_page('First Crawler', Crawler.base_url)