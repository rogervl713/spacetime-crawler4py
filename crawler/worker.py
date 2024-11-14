from threading import Thread

from inspect import getsource
from lxml import html
from urllib.parse import urlparse
from utils.download import download
from utils import get_logger
import scraper
import time

from tokenizer import PartA as A

stop_words = {'t', 's', 'd', 'll', 'i', 'they', 'we', 'you', 'he', 'she', 've', 're', 'here', 'how',
              'it', 'that', 'there', 'what', 'when', 'where', 'who', 'why', 'a', 'about', 'above',
              'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'aren', 'as',
              'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but',
              'by', 'can', 'cannot', 'could', 'couldn', 'did', 'didn', 'do', 'does', 'doesn',
              'doing', 'don', 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had',
              'hadn', 'has', 'hasn', 'have', 'haven', 'having', 'her', 'hers', 'herself', 'him',
              'himself', 'his', 'if', 'in', 'into', 'is', 'isn', 'its', 'itself', 'let', 'm', 'me',
              'more', 'most', 'mustn', 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on',
              'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over',
              'own', 'same', 'shan', 'should', 'shouldn', 'so', 'some', 'such', 'than', 'the',
              'their', 'theirs', 'them', 'themselves', 'then', 'these', 'this', 'those', 'through',
              'to', 'too', 'under', 'until', 'up', 'very', 'was', 'wasn', 'were', 'weren', 'which',
              'while', 'whom', 'with', 'won', 'would', 'wouldn', 'your', 'yours', 'yourself',
              'yourselves'}

class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier

        self.unique_pages = set()
        self.subdomains = dict()
        self.longest_page = ''
        self.max_tokens = 0
        self.token_freqs = dict()

        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)

    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            try:
                resp = download(tbd_url, self.config, self.logger)
                self.logger.info(
                    f"Downloaded {tbd_url}, status <{resp.status}>, "
                    f"using cache {self.config.cache_server}.")
                
                if resp.url not in self.unique_pages:
                    self.unique_pages.add(resp.url)
                    parsed = urlparse(resp.url)
                    subdomain = parsed.netloc
                    if subdomain not in self.subdomains:
                        self.subdomains[subdomain] = set()
                    self.subdomains[subdomain].add(resp.url)

                tree = html.fromstring(resp.raw_response.content)
                content = tree.xpath('//text()[not(ancestor::script or ancestor::style)]')
                text = ' '.join(content).strip()
                tokens = A.tokenize(text)

                if len(tokens) > self.max_tokens: 
                    self.longest_page = resp.url
                    self.max_tokens = len(tokens)

                page_token_freqs = A.compute_word_frequencies(tokens)
                for token in page_token_freqs:
                    if token not in stop_words:
                        self.token_freqs[token] = self.token_freqs.get(token, 0) + page_token_freqs[token]

                scraped_urls = scraper.scraper(tbd_url, resp)
                for scraped_url in scraped_urls:
                    self.frontier.add_url(scraped_url)
                self.frontier.mark_url_complete(tbd_url)
                time.sleep(self.config.time_delay)
            except Exception as exc:
                self.logger.error(f"Error processing {tbd_url}: {exc}")
                continue