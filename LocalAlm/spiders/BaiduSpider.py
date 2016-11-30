import scrapy


class BaiduSpider(scrapy.Spider):
    name = "baidu"
    allowed_domains=["www.baidu.com"]
    start_urls = ["https://www.baidu.com"]

    def parse(self, response):
        filename = response.url.split("/")[-2]
        with open(filename, "wb") as f:
            f.write(response.body)