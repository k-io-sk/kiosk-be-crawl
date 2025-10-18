from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
from urllib.parse import urlencode
import json
from io import BytesIO
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.crawlling.repository.crawlling_repository import insert_event, is_exist_event
from app.s3.service.s3_service import upload_s3, convert_path, create_keyName

# ------------------------------
# 3. 이미지 변환 함수
# ------------------------------
def convert_image(main_image_url):
    url = main_image_url
    with urllib.request.urlopen(url) as response:
        img_data = response.read()

    img = Image.open(BytesIO(img_data))
    output_buffer = BytesIO()
    img.save(output_buffer, format="WEBP", quality=85)
    output_buffer.seek(0)

    return output_buffer


# ------------------------------
# 3. 상세 페이지 크롤링 함수
# ------------------------------
def webCrawlling(menuNo, searchDist, searchField, sdate, edate, pageIndex, cultCode):
    base = "https://culture.seoul.go.kr/culture/culture/cultureEvent/view.do"
    params = {
        "cultcode": cultCode,
        "menuNo": menuNo,
        "searchDist": searchDist,
        "searchCost": "",
        "searchField": searchField,
        "searchAge": "",
        "sdate": sdate,
        "edate": edate,
        "searchStr": "",
        "pageIndex": pageIndex
    }

    url = f"{base}?{urlencode(params)}"
    html = urllib.request.urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')

    s3_main_image_url = is_exist_event(cultCode)
    if s3_main_image_url==False:
        main_image = soup.select_one('div.img-box img')
        if main_image:
            main_image_url = main_image.get('src')
            if main_image_url.startswith('/'):
                main_image_url = f"https://culture.seoul.go.kr{main_image_url}"
                output = convert_image(main_image_url)
                s3_main_image_url = upload_s3(output, create_keyName(convert_path("m")), "image/webp")

    tds = soup.select('div.type-box li div.type-td span')
    values = [td.get_text(strip=True) for td in tds]

    detail = soup.select_one('div.detail-btn a')
    detail_url = ""
    if detail:
        detail_url = detail.get('href')
    
    result = {
        "main_image": s3_main_image_url,
        "location": values[0] if len(values) > 0 else "",
        "event_time": values[2] if len(values) > 2 else "",
        "recruit_target": values[3] if len(values) > 3 else "",
        "price": values[4] if len(values) > 4 else "",
        "inquiry": values[5] if len(values) > 5 else "",
        "detail_url": detail_url
    }

    return result

# ------------------------------
# 2. 각 이벤트를 처리하는 작업 단위
# ------------------------------
def process_event(event, menuNo, searchDist, searchField, sdate, edate, pageIndex):
    item = {
        "cult_code": event.get('cultcode', ''),
        "title": event.get('title', ''),
        "start_date": event.get('strtdate', ''),
        "end_date": event.get('endDate', ''),
        "event_category": searchField,
        "latitude": event.get('xCoord', ''),
        "longitude": event.get('yCoord', ''),
        "address": event.get('addr', ''),
        "status": "ONGOING"
    }
    wcInfo = webCrawlling(menuNo, searchDist, searchField, sdate, edate, pageIndex, event['cultcode'])
    if isinstance(wcInfo, dict):
        item.update(wcInfo)
    return item

# ------------------------------
# 1. 메인 크롤링 함수
# ------------------------------
def mainCrawlling(menuNo, searchDist, dist, searchField, field, sdate, edate):
    event_result = []
    url = 'https://culture.seoul.go.kr/culture/culture/cultureEvent/jsonList.json'
    pageIndex = 1

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": f"https://culture.seoul.go.kr/culture/culture/cultureEvent/list.do?searchCate={searchField}&menuNo={menuNo}",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    while True:
        payload = {
            "pageIndex": pageIndex,
            "menuNo": menuNo,
            "isSearched": "",
            "searchDist": searchDist,
            "searchCost": "",
            "searchField": searchField,
            "searchAge": "",
            "sdate": sdate,
            "edate": edate,
            "searchStr": "",
            "field": field,
            "dist": dist
        }

        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        with urllib.request.urlopen(req) as response:
            resp_text = response.read().decode("utf-8")
            result = json.loads(resp_text)

        if not result or not result.get("resultList"):
            break

        events = result.get("resultList", [])
        print(f"SK_KIOSK: {searchField} {pageIndex} 페이지에서 {len(events)}개 이벤트 수집 중...")

        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = [
                executor.submit(process_event, e, menuNo, searchDist, searchField, sdate, edate, pageIndex)
                for e in events
            ]
            for future in as_completed(futures):
                event_result.append(future.result())

        pageIndex += 1

    print(f"SK_KIOSK: {searchField} 에서 총 {len(event_result)}개 이벤트 수집 완료")

    insert_event(event_result)