import scrapy
import scrapy_playwright.page
from ..items import LazadaCrawlingItem
from scrapy_playwright.page import PageMethod

class LazadaSpiderSpider(scrapy.Spider):
    name = "lazada_spider"
    allowed_domains = ["www.lazada.vn"]
    start_urls = ["https://www.lazada.vn/"]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                meta=dict(
                    playwright=True,
                    playwright_include_page=True,
                    playwright_page_methods=[
                        PageMethod("wait_for_selector", ".card-categories-li-content")
                    ]
                ),
                callback=self.parse
            )

    def parse(self, response):
        # Lấy tất cả các link category
        categories_link = response.css('.card-categories-li.hp-mod-card-hover a::attr(href)').getall()
        for category_link in categories_link:
            if not category_link.startswith('http'):
                category_link = response.urljoin(category_link)  # Thêm scheme nếu thiếu
            yield scrapy.Request(
                url=category_link,
                meta=dict(
                    playwright=True,
                    playwright_include_page=True,
                    playwright_page_methods=[
                        PageMethod("wait_for_load_state", "networkidle"),  # Đợi cho tất cả các yêu cầu mạng hoàn tất
                        PageMethod("wait_for_timeout", 5000),  # Đợi thêm 5 giây để đảm bảo trang đã tải xong
                        PageMethod("wait_for_selector", ".JrAyI", timeout=10000),  # Đợi phần tử trong tối đa 10 giây
                        PageMethod("scroll", "1000")  # Cuộn xuống để tải thêm dữ liệu
                    ]
                ),
                callback=self.parse_category_name
            )

    async def parse_category_name(self, response):
        print(response.text + "namtoe03")
        category_name = response.css('.JrAyI::text').get()
        products = response.css('.MefHh')
        for product in products:
            product_tmp = LazadaCrawlingItem()
            product_tmp['product_name'] = product.css('.RfADt a::text').get()
            product_tmp['product_price'] = product.css('.ooOxS::text').get()
            product_tmp['product_category'] = category_name
            product_tmp_site_link = product.css('.RfADt a::attr(href)').get()
            yield scrapy.Request(
                url=product_tmp_site_link,
                callback=self.parse_product_desc,
                meta={
                    "playwright": True,
                    "product_tmp": product_tmp
                }
            )

    async def parse_product_desc(self, response):
        # Lấy Playwright page từ meta
        page = response.meta['playwright_page']

        # Thực hiện hành động trên trang nếu cần, như nhấn vào nút mô tả
        await page.click("..pdp-button_size_m")

        # Lấy dữ liệu mô tả sản phẩm
        product_tmp = response.meta['product_tmp']
        tmp_desc = response.css('.pdp-product-desc::text').get()
        product_tmp['product_desc'] = tmp_desc

        # Trả về kết quả cuối cùng
        yield product_tmp

        # Đóng trang để tránh chiếm tài nguyên
        await page.close()
