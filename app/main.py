from app.crawlling.service.crawlling_service import mainCrawlling
from app.crawlling.repository.crawlling_repository import softDelete_event
from datetime import date

# ------------------------------
# 오늘 날짜, 다음 달 날짜 반환 함수
# ------------------------------
def get_today_and_next_month():
    today = date.today()
    year = today.year
    month = today.month
    day = today.day

    if month == 12:
        next_year = year + 1
        next_month = 1
    else:
        next_year = year
        next_month = month + 1

    import calendar
    last_day_of_next_month = calendar.monthrange(next_year, next_month)[1]

    next_day = min(day, last_day_of_next_month)

    next_month_date = date(next_year, next_month, next_day)

    return today, next_month_date

# ------------------------------
# 크롤링 메인 함수
# ------------------------------
def main():
    start, end = get_today_and_next_month()

    # 메뉴 번호 : 200008(공연), 200009(전시), 200010(축제), 200011(교육체험)
    # 지역코드 : 11110(종로구)
    # 카테고리 : SHOW, EXHIBITION, FESTIVAL, EDUEXP
    print(f"SK_KIOSK: [ {start} 자동화 작업 시작 ]")
    mainCrawlling(200008, 11110, 11110, 'SHOW', 'SHOW', start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    mainCrawlling(200009, 11110, 11110, 'EXHIBITION', 'EXHIBITION', start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    mainCrawlling(200010, 11110, 11110, 'FESTIVAL', 'FESTIVAL', start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    mainCrawlling(200011, 11110, 11110, 'EDUEXP', 'EDUEXP', start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))

    # 기간 지난 event soft delete
    softDelete_event()
    print(f"SK_KIOSK: [ {start} 자동화 작업 종료 ]")


if __name__ == "__main__":
    main()