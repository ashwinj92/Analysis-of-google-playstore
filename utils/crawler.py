import sys
sys.path.append(r'C:\Users\ashwi\Documents\Playstorecrawler')

from utils.apps import PlayApps
from collections import deque
from threading import Thread
from time import sleep

class Crawler:
    __PENDING = None
    __VISITED = None

    def __init__(self, start_url, depth, mode='slow'):
        """
        Parameters:
            start_url (str) - the url to begin crawling
            depth (int) - the depth at which to stop
        """

        self.__start_url = start_url
        self.__depth = depth
        self.__mode = mode
        self.__apps = PlayApps()
        self.__active_threads = 0

        Crawler.__PENDING = deque()
        Crawler.__VISITED = set()

    def start(self, num_threads=24):
        """
        Start the crawler on a specified number of threads.

        Parameters:
            num_threads (int) - the number of threads

        Returns:
            a list of all app urls that were crawled
        """

        results = []

        # crawl the start url in the main thread itself. that ways, the queue
        # contains diverse urls that each individual thread can pick up.
        for url in self.__apps.get_app_urls(self.__start_url, self.__mode):
            Crawler.__PENDING.append((url, 1)) # track depth for early stopping
            Crawler.__VISITED.add(url)

            results.append((self.__start_url, url, 1)) # (src, dst, depth)

        # now that we should have enough items in queue, start up the crawler
        # on multiple threads to process the queue faster.
        for _ in range(num_threads):
            Thread(target=self.__thread, args=(results,)).start()

        # now we just need to wait till all threads have finished before we
        # return the results to the calling function.
        while self.__active_threads > 0:
            sleep(5) 

        return results

    def __thread(self, results):
        self.__active_threads += 1

        while Crawler.__PENDING:
            page_url, depth = Crawler.__PENDING.popleft()
            print(f'Pending URLs -> {len(Crawler.__PENDING)}')

            for url in self.__apps.get_app_urls(page_url, self.__mode):
                # we should add a new url to queue only if this url is not
                # already visited and satisfies the depth requirement.
                if url not in Crawler.__VISITED and depth < self.__depth-1:
                    Crawler.__PENDING.append((url, depth+1))
                    Crawler.__VISITED.add(url)

                results.append((page_url, url, depth+1))

        self.__active_threads -= 1


if __name__ == '__main__':
    root_app = 'com.ratelekom.findnow'
    root_url = f'https://play.google.com/store/apps/details?id={root_app}'

    # Crawler depth-method is fast
    crawler = Crawler(start_url=root_url, depth=2, mode='fast')
    results = crawler.start()
    uniqueNodes = set()

    #print all edges 
    print(f'Found {len(results)} URLs')
    f1 = open('EdgePairs.txt', 'w')  
    
    # Generate all unique nodes
    for src_app, dst_app, depth in results:
         uniqueNodes.add(src_app)
         uniqueNodes.add(dst_app)
         f1.write("%s,%s,%d\n" % (src_app, dst_app,depth))
         print(src_app, dst_app, depth)
    f1.close()
    nodeid = 0; 
    myfile = open('uniqueNodes.txt', 'w')  

    # To Create dictionary of unqiye node IDs and their crawl URLs
    for unique in uniqueNodes:
         myfile.write("%s,%s\n" % (nodeid, unique))
         nodeid = nodeid+1
    myfile.close()
    
    
    
    