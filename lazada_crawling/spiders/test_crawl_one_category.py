import scrapy
from scrapy_playwright.page import PageMethod
from ..items import LazadaCrawlingItem


class TestCrawlOneCategorySpider(scrapy.Spider):
    name = "test_crawl_one_category"
    allowed_domains = ["www.lazada.vn"]
    start_urls = [
        "https://www.lazada.vn/loa-khong-day-loa-bluetooth/?up_id=2515410890&clickTrackInfo=matchType--20___description--Gi%25E1%25BA%25A3m%2B23%2525___seedItemMatchType--c2i___bucket--0___spm_id--category.hp___seedItemScore--0.0___abId--333258___score--0.1___pvid--4457df19-38e3-42e3-9a5a-fe07d531d08a___refer--___appId--7253___seedItemId--2515410890___scm--1007.17253.333258.0___categoryId--10100399___timestamp--1727987706301&from=hp_categories&item_id=2515410890&version=v2&q=loa%2Bkh%C3%B4ng%2Bd%C3%A2y%2B%2Bloa%2Bbluetooth&params=%7B%22catIdLv1%22%3A%2210100387%22%2C%22pvid%22%3A%224457df19-38e3-42e3-9a5a-fe07d531d08a%22%2C%22src%22%3A%22ald%22%2C%22categoryName%22%3A%22Loa%2Bkh%25C3%25B4ng%2Bd%25C3%25A2y%2B%2Bloa%2BBluetooth%22%2C%22categoryId%22%3A%2210100399%22%7D&src=hp_categories&spm=a2o4n.homepage.categoriesPC.d_1_10100399"]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url,
                                 meta=dict(playwright=True,
                                           playwright_include_page=True,
                                           playwright_page_methods=[
                                               PageMethod("wait_for_load_state", "networkidle"),
                                               # Đợi cho tất cả các yêu cầu mạng hoàn tất
                                               PageMethod("wait_for_timeout", 3000),
                                               # Đợi thêm 5 giây để đảm bảo trang đã tải xong
                                               PageMethod("wait_for_selector", ".JrAyI", timeout=3000),
                                               PageMethod("wait_for_selector", ".MefHh", timeout=3000),
                                               # Đợi phần tử trong tối đa 10 giây
                                               PageMethod("evaluate", "window.scrollBy(0, 1000)")  # Cuộn xuống để
                                               # tải thêm dữ liệu
                                           ]
                                           ),
                                 callback=self.parse)

    def parse(self, response):
        category_name = response.css(".JrAyI::text").get()
        product_links = response.css(".Ms6aG.MefHh .RfADt a::attr(href)").getall()
        for link in product_links:
            if not link.startswith('http'):
                link = response.urljoin(link)  # Thêm scheme nếu thiếu
            # yield {
            #     "link": link
            # }
            yield scrapy.Request(url=link,
                                 meta=dict(playwright=True,
                                           playwright_include_page=True,
                                           playwright_page_methods=[
                                               PageMethod("wait_for_load_state", "networkidle"),
                                               PageMethod("wait_for_timeout", 3000),
                                               PageMethod("wait_for_selector", ".pdp-mod-product-badge-title",
                                                          timeout=3000),
                                               # PageMethod("wait_for_selector", ".pdp-price_size_xl", timeout=3000),
                                               # PageMethod("wait_for_selector", ".pdp-button_size_m", timeout=3000),
                                               # category_name
                                           ]),
                                 callback=self.parse_products
                                 )

    async def parse_products(self, response):
        # page = response.meta["playwright_page"]

        # button_exists = await page.query_selector(".pdp-button_size_m")
        # if button_exists:
        #     await button_exists.click()
        # product_tmp = LazadaCrawlingItem()
        product_name = response.css(".pdp-mod-product-badge-title::text").get()
        # product_tmp['product_price'] = response.css(".pdp-product-price::text").get()
        # product_tmp['product_desc'] = response.css(".pdp-product-desc::text").get()
        # product_tmp['product_category'] = response.meta["category_name"]
        yield {
            "ten": product_name
        }
