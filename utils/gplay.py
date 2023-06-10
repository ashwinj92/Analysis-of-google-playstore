from gzip import open as gzipopen
from io import BytesIO
from lxml import html
from os.path import join
from PIL import Image
from shutil import copyfile
from sqlite3 import connect
from typing import Set
from threading import Lock, Thread
from urllib3 import PoolManager
from utils.console import Console


class GPlay:
    def __init__(self, db_dir: str):
        self.__db_dir = db_dir
        self.__lock = Lock()

        self.__crawler_db_file = '/crawler/files/play-apps.db'
        self.__download_db_file = join(db_dir, 'downloaded-apps.db')

        self.__create_table()

    def get_apps(self) -> Set:
        """
        Get the set of all app ids that have been crawled by the Google
        Play crawler.

        Returns:
            a set of app ids
        """
        
        # copying over the database to a new file just to avoid locking
        # and slowing down the crawler running inside another container.
        new_db_file = '/tmp/play-apps.db'
        copyfile(self.__crawler_db_file, new_db_file)

        conn = connect(new_db_file)
        with conn:
            cursor = conn.execute('SELECT DISTINCT app_id FROM app')
            return set(map(lambda x: x[0], cursor.fetchall()))

    def get_downloaded_apps(self) -> Set:
        """
        Get the set of all app ids whose details and icons have already
        been downloaded.

        Returns:
            a set of downloaded app ids
        """

        # copying over the database to a new file to avoid locking.
        new_db_file = '/tmp/downloaded-apps.db'
        copyfile(self.__download_db_file, new_db_file)

        conn = connect(new_db_file)
        with conn:
            cursor = conn.execute('SELECT DISTINCT app_id FROM app')
            return set(map(lambda x: x[0], cursor.fetchall()))

    def get_app_file(self, app_id: str) -> str:
        """
        Get the file name where contents of the app have been saved.

        Parameters:
            app_id (str) - the app id

        Returns:
            the file name where contents have been saved
        """

        return join(self.__db_dir, 'apps', app_id + '.html')

    def get_icon_file(self, app_id: str) -> str:
        """
        Get the file name where the icon of the app has been saved.

        Parameters:
            app_id (str) - the app id

        Returns:
            the file name where icon has been saved
        """

        return join(self.__db_dir, 'icons', app_id + '.png')

    def read_app_page(self, app_id: str) -> bytes:
        """
        Read the app page from the Google Play Store given the app id.

        Parameters:
            app_id (str) - the app id

        Returns:
            contents of the app page as bytes; b'' in case of an error
        """

        app_url = f'https://play.google.com/store/apps/details?id={app_id}'
        
        try:
            http = PoolManager()
            response = http.request('GET', app_url)

            if response.status == 404:
                raise Exception('Page not found')

            return response.data
        except Exception as err:
            Console.log_error(f'Error reading app: {app_id}, Error: {err}')
            return b''

    def save_app_page(self, app_id: str, content: bytes) -> bool:
        """
        Save the app page downloaded from Google Play Store to a file.

        Parameters:
            app_id (str) - the app id
            content (bytes) - the contents of the app page

        Returns:
            true if the app page was saved, false otherwise
        """

        try:
            gzipopen(self.get_app_file(app_id), 'wb').write(content)
            return True
        except:
            Console.log_error(f'Error saving app: {app_id}')
            return False

    def get_app_content(self, app_id: str) -> bytes:
        """
        Get the contents of the given app from the saved file.

        Parameters:
            app_id (str) - the app id

        Returns:
            the app contents from the saved file
        """

        try:    return gzipopen(self.get_app_file(app_id), 'rb').read()
        except: return None

    def read_app_icon(self, app_id: str, app_data: bytes) -> bytes:
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
            img_tag = tree.xpath('//img[@class="T75of sHb2Xb"]/@src')[0]

            http = PoolManager()
            response = http.request('GET', img_tag)
            return response.data
        except Exception as err:
            Console.log_error(f'Error reading icon: {app_id}, Error: {err}')
            return b''

    def save_app_icon(self, app_id: str, content: bytes) -> bool:
        """
        Save the app icon downloaded from Google Play Store to a file.

        Parameters:
            app_id (str) - the app id
            content (bytes) - the contents of the icon

        Returns:
            true if the icon was saved, false otherwise
        """

        try:
            image = Image.open(BytesIO(content)).convert('RGB')
            image.save(self.get_icon_file(app_id))
            return True
        except:
            Console.log_error(f'Error saving icon: {app_id}')
            return False

    def get_icon_content(self, app_id: str) -> bytes:
        """
        Get the contents of the given icon from the saved file.

        Parameters:
            app_id (str) - the app id

        Returns:
            the icon contents from the saved file
        """

        try:    return open(self.get_icon_file(app_id), 'rb').read()
        except: return None

    def save_apps_details(self, apps: Set) -> None:
        """
        Iterate through all the apps in the given set, download their contents
        and icons, save the contents and icons to files, and then save the app
        id to a database.

        Parameters:
            apps (Set) - the set of apps
        """

        total_apps = remaining = len(apps)

        while apps:
            app_id = apps.pop()

            remaining = len(apps)
            Console.log(f'Processing {app_id} ({remaining}/{total_apps})')

            app_data = self.read_app_page(app_id)
            if app_data == b'': continue

            icon_data = self.read_app_icon(app_id, app_data)
            if icon_data == b'': continue

            if self.save_app_page(app_id, app_data) and \
                    self.save_app_icon(app_id, icon_data):
                self.__lock.acquire()
                self.__save_app_to_table(app_id)
                self.__lock.release()

                Console.log_info(f'Saved {app_id} ({remaining}/{total_apps})')

    def save_all_apps_details(self,
            force: bool = False,
            threads: int = 24
    ) -> None:
        """
        Get the list of all apps that have not yet been downloaded, and start
        threads to save these app's contents and icons.

        Parameters:
            force (bool) - if true, all apps to be downloaded again
            threads (int) - the desired count of threads
        """

        apps = self.get_apps()

        # remove downloaded apps if force download is not requested
        if not force:
            downloaded = self.get_downloaded_apps()
            apps = apps - downloaded

        for _ in range(threads):
            Thread(target=self.save_apps_details, args=(apps,)).start()

    def __create_table(self) -> None:
        conn = connect(self.__download_db_file)
        with conn:
            conn.execute(
                    f'CREATE TABLE IF NOT EXISTS app (app_id TEXT UNIQUE);'
            )

    def __save_app_to_table(self, app_id: str) -> None:
        conn = connect(self.__download_db_file, timeout=60)
        with conn:
            conn.execute(
                    f'INSERT OR IGNORE INTO app (app_id) VALUES (?)', (app_id, )
            )
