from selenium.webdriver import Firefox, FirefoxOptions, FirefoxProfile
from time import sleep


class FirefoxDriver:

    def __init__(self):
        profile = FirefoxProfile()
        profile.set_preference("marionette.actors.enabled", False)

        options = FirefoxOptions()
        options.profile = profile
        options.headless = True
        options.set_capability("marionette", True)
        options.add_argument("-devtools")

        self.__driver = Firefox(options=options)

    def get_page(self, page_url: str) -> str:
        self.__driver.get(page_url)

        # keep scrolling till end of page to address
        # pages that have dynamic loading
        curr_height = self.get_max_height()
        while True:
            self.scroll_to_end()
            sleep(1)

            new_height = self.get_max_height()
            if new_height == curr_height:
                break
            curr_height = new_height

        return self.__driver.page_source

    def get_max_height(self) -> int:
        return self.__driver.execute_script(
                'return document.body.scrollHeight'
            )

    def scroll_to_end(self) -> None:
        self.__driver.execute_script(
                'window.scrollTo(0, document.body.scrollHeight)'
            )

    def close(self):
        self.__driver.close()
