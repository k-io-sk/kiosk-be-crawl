from datetime import datetime
from app.db import get_conn 

# ------------------------------
# 문자열 날짜 -> 날짜 파싱 함수
# ------------------------------
def parse_date(d):
            try:
                return datetime.strptime(d, "%Y-%m-%d").date() if d else None
            except ValueError:
                return None

# ------------------------------
# 문자열 -> float 변환 함수
# ------------------------------
def parse_float(v):
            try:
                return float(v) if v else None
            except ValueError:
                return None

# ------------------------------
# event DB 삽입 함수
# ------------------------------
def insert_event(events):
    conn = get_conn()
    cursor = conn.cursor()

    sql = """
    INSERT INTO event
        (cult_code, title, location, start_date, end_date, event_time, event_category,
        recruit_target, price, inquiry, detail_url, main_image, address, latitude, longitude, status, created_at, modified_at)
    VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        title = VALUES(title),
        location = VALUES(location),
        start_date = VALUES(start_date),
        end_date = VALUES(end_date),
        event_time = VALUES(event_time),
        event_category = VALUES(event_category),
        recruit_target = VALUES(recruit_target),
        price = VALUES(price),
        inquiry = VALUES(inquiry),
        detail_url = VALUES(detail_url),
        main_image = VALUES(main_image),
        address = VALUES(address),
        latitude = VALUES(latitude),
        longitude = VALUES(longitude),
        status = VALUES(status),
        modified_at = VALUES(modified_at)
    """

    inserted = 0
    updated = 0
    unchanged = 0

    for e in events:
        start_date = parse_date(e.get("start_date"))
        end_date = parse_date(e.get("end_date"))
        latitude = parse_float(e.get("latitude"))
        longitude = parse_float(e.get("longitude"))
        created_at = datetime.now()
        modified_at = None

        cursor.execute(sql, (
            e.get("cult_code"),
            e.get("title"),
            e.get("location"),
            start_date,
            end_date,
            e.get("event_time"),
            e.get("event_category"),
            e.get("recruit_target"),
            e.get("price"),
            e.get("inquiry"),
            e.get("detail_url"),
            e.get("main_image"),
            e.get("address"),
            latitude,
            longitude,
            e.get("status"),
            created_at,
            modified_at
        ))

        if cursor.rowcount == 1:
            inserted += 1
        elif cursor.rowcount == 2:
            updated += 1
        elif cursor.rowcount == 0:
            unchanged += 1

    conn.commit()
    cursor.close()
    conn.close()

    print(f"SK_KIOSK: DB 작업 결과 [Inserted: {inserted}, Updated: {updated}, Unchanged: {unchanged}]")

# ------------------------------
# 해당 이벤트 존재 여부 반환 함수
# ------------------------------
def is_exist_event(cultcode):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT EXISTS (SELECT 1 FROM event WHERE cult_code = %s)", (cultcode, ))
    is_exist = cursor.fetchone()[0]
    
    if is_exist==1:
        cursor.execute("SELECT main_image FROM event WHERE cult_code = %s", (cultcode, ))
        main_image_url = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return main_image_url
    
    cursor.close()
    conn.close()

    return False

# ------------------------------
# event DB soft delete 함수
# ------------------------------
def softDelete_event():
    conn = get_conn()
    cursor = conn.cursor()

    print("SK_KIOSK: 만료된 이벤트 SOFT DELETE 작업 수행")

    cursor.execute("UPDATE event SET status='ENDED' WHERE end_date < CURDATE()")
    
    print(f"SK_KIOSK: DB 작업 결과 [Soft_Deleted: {cursor.rowcount}]")

    conn.commit()
    cursor.close()
    conn.close()