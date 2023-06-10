
import sys
sys.path.append(r'C:\Users\ashwi\Documents\Playstorecrawler')
from lxml import html
from urllib3 import PoolManager
from urllib.parse import parse_qs, urlparse
from utils.webdriver import FirefoxDriver
from utils.console import Console
import unicodedata

class PlayApps:
    __PLAY_URL = 'https://play.google.com'

    def get_app_urls(self, page_url, mode='slow'):
        """
        Given an app page url, get the list of all app urls returned by Google
        Play as being similar to the app.

        Parameters:
            page_url (str) - the app page url
            mode (str) - the mode of reading ('slow' will read entire pages)

        Returns:
            set of similar app page urls
        """

        urls = set()

        for url in self.read_page_urls(self.read_page_content(page_url, mode)):
            # in case of a cluster page, we need to make another request to
            # get the list of apps within the cluster. typically, a single
            # cluster will contain all the similar apps. 
            if self.is_cluster_page(url):
                for url2 in self.read_page_urls(self.read_page_content(url, mode)):
                    if self.is_app_page(url2):
                        urls.add(url2)

            if self.is_app_page(url):
                urls.add(url)

        return urls

    def read_page_content(self, page_url, mode='slow'):
        """
        Given a page url, read the contents of page from the Google Play Store.

        Parameters:
            page_url (str) - the page url
            mode (str) - the mode of reading ('slow' will read entire pages)

        Returns:
            the contents of the page
        """

        try:
            if self.is_cluster_page(page_url) and mode == 'slow':
                # the cluster pages have dynamic loading in which more apps are
                # loaded when scrolled to bottom. we need to use a browser to 
                # emulate the scrolling behavior. note that this option takes
                # time as sleep is used to wait for the page to load up after
                # scrolling is simulated.
                driver = FirefoxDriver()
                content = driver.get_page(page_url)
                driver.close()
            else:
                http = PoolManager()
                content = http.request('GET', page_url).data

            return content
        except Exception as err:
            print(f'Error reading page: {page_url}. Error: {err}')
            return b''

    def read_page_urls(self, content):
        """
        Given a page's contents, get the set of all the app and cluster urls
        within the page.

        Parameters:
            content (str) - the page contents

        Returns:
            the set of all the app and cluster urls
        """

        urls = set()

        tree = html.fromstring(content)
        all_urls = [str(link) for link in tree.xpath('//a/@href')]

        for url in set(all_urls):
            if url.startswith('/'):
                url = self.__PLAY_URL + url

            if self.is_app_page(url):
                urls.add(self.get_app_url(url))
            if self.is_cluster_page(url):
                urls.add(url)
        
        return urls

    def is_app_page(self, page_url):
        """
        Given a page url, check if the url contains details of an Android app.

        Parameters:
            page_url (str) - the page url

        Returns:
            true if url contains app details, false otherwise
        """

        return page_url.startswith(
                f'{self.__PLAY_URL}/store/apps/details?id='
            )

    def is_cluster_page(self, page_url):
        """
        Given a page url, check if the url contains details of an app cluster.

        Parameters:
            page_url (str) - the page url

        Returns:
            true if url is an app cluster, false otherwise
        """

        return page_url.startswith(
                f'{self.__PLAY_URL}/store/apps/collection/cluster?clp='
            )

    def read_app_desc(self, app_id: str, app_data: bytes) -> bytes:
        """
        Read the app icon from the Google Play Store given the app id
        and contents.

        Parameters:
            app_id (str) - the app id
            app_data (bytes) - the contents of the app page

        Returns:
            contents of the icon as bytes; b'' in case of an error
        """

        try:
            tree = html.fromstring(app_data)
            #done
            desc_tag = tree.xpath('//*[@id="fcxH9b"]/div[4]/c-wiz/div/div[2]/div/div/main/c-wiz[1]/c-wiz[4]/div/div[1]/div[2]/div[1]/span/div/text()')           
            #done
            app_title = tree.xpath("//h1[contains(@class, 'AHFaub')]/span/text()")
            #done
            #hrTbp R8zArc
            appName_Pub_cat = tree.xpath("//a[contains(@class, 'hrTbp R8zArc')]/text()")
            #done
            #publisher_tag = tree.xpath('//*[@id="fcxH9b"]/div[4]/c-wiz[5]/div/div[2]/div/div/main/c-wiz[3]/div[1]/div[2]/div/div[9]/span/div/span/text()')
            #done   
            content_class = tree.xpath("//div[contains(@class, 'KmO8jd')]/text()")                       
            #BHMmbe
            agg_rating = tree.xpath("//div[contains(@class, 'BHMmbe')]/text()")
            
            ratings = tree.xpath("//span[contains(@class, 'EymY4b')]/span/text()")           
            #done
            installs = tree.xpath("//span[contains(@class, 'htlgb')]/div/span/text()")           
           
            #contains_adds = tree.xpath('//*[@id="fcxH9b"]/div[4]/c-wiz/div/div[2]/div/div/main/c-wiz[1]/c-wiz[4]/div/div[1]/div[2]/div[1]/span/div/text()')
            
            
            fin = ""
            for txt in desc_tag:
                fin+=txt
            print(type(fin))      
            fin = fin.encode('latin-1').decode("ascii", "ignore")
            
            if(len(agg_rating) == 0):
                agg_rating = "0.0"
            if(len(installs) == 0):
                installs = "0"
            
            if(len(installs) == 0):
                installs = ["0","0","0"]
                
            if(len(appName_Pub_cat) == 0):
                appName_Pub_cat[1] = "No category"
                  
            print(type(appName_Pub_cat[0]),type(appName_Pub_cat[1]),type(content_class),type(ratings),type(installs[2]))
            return fin, str(app_title), str(appName_Pub_cat[0]),str(appName_Pub_cat[1]),str(content_class),str(ratings),str(agg_rating),str(installs[2])
        except Exception as err:
            Console.log_error(f'Error reading icon: {app_id}, Error: {err}')
            return b''


    def read_app_title(self, app_id: str, app_data: bytes) -> bytes:
        """
        Read the app icon from the Google Play Store given the app id
        and contents.

        Parameters:
            app_id (str) - the app id
            app_data (bytes) - the contents of the app page

        Returns:
            contents of the icon as bytes; b'' in case of an error
        """

        try:
            tree = html.fromstring(app_data)

            app_title = tree.xpath("//h1[contains(@class, 'AHFaub')]/span/text()")
            #done
            fin = ""
            for txt in app_title:
                fin+=txt
            print(type(fin))
            
            fin = fin.encode('latin-1').decode('utf-8', errors="replace")
            return str(app_title)
        except Exception as err:
            Console.log_error(f'Error reading icon: {app_id}, Error: {err}')
            return b''


    def get_app_id(self, page_url):
        """
        Given an app page url, get the package id of the app.

        Parameters:
            page_url (str) - the app page url

        Returns:
            the package id of the app
        """

        return parse_qs(urlparse(page_url).query)['id'][0]

    def get_app_url(self, page_url):
        """
        Given an app page url, get a shortened url that can be used to read the
        app details.

        Parameters:
            page_url (str) - the app page url

        Returns:
            the package id of the app
        """

        app_id = self.get_app_id(page_url)
        return f'{self.__PLAY_URL}/store/apps/details?id={app_id}'

def remove_accented_chars(text):
    new_text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')
    return new_text


if __name__ == '__main__':
    root_app = 'com.whatsapp'
    root_url = f'https://play.google.com/store/apps/details?id={root_app}'

    obj = PlayApps()
    urls = obj.get_app_urls(root_url)
    
    print(f'Found {len(urls)} URLs')
    for url in urls:
        app = obj.get_app_id(url)
        print(f'{url} ({app})')
