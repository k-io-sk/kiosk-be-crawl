from crawlling import main_crawlling
from db import soft_delete_event
from datetime import date

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

def main():
    start, end = get_today_and_next_month()

    # 메뉴 번호 : 200008(공연), 200009(전시), 200010(축제), 200011(교육체험)
    # 지역코드 : 11110(종로구)
    # 카테고리 : SHOW, EXHIBITION, FESTIVAL, EDUEXP
    main_crawlling(200008, 11110, 11110, 'SHOW', 'SHOW', start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    main_crawlling(200009, 11110, 11110, 'EXHIBITION', 'EXHIBITION', start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    main_crawlling(200010, 11110, 11110, 'FESTIVAL', 'FESTIVAL', start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    main_crawlling(200011, 11110, 11110, 'EDUEXP', 'EDUEXP', start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    soft_delete_event()


if __name__ == "__main__":
    main()