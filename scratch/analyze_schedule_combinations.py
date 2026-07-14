import datetime

def get_weekday_name(dt):
    weekdays = ['월', '화', '수', '목', '금', '토', '일']
    return weekdays[dt.weekday()]

def main():
    # Constraints definitions
    # Vacation: 7/22 ~ 8/11
    vacation_start = datetime.date(2026, 7, 22)
    vacation_end = datetime.date(2026, 8, 11)
    
    # 1st semester exam 2: 6/30 ~ 7/3
    # 1st semester exam 2 prep & exam week (exam, 1 week before, 2 weeks before): 6/15 ~ 7/3
    exam1_exclude_start = datetime.date(2026, 6, 15)
    exam1_exclude_end = datetime.date(2026, 7, 3)
    
    # 2nd semester exam 1: 9/29 ~ 10/2
    # 2nd semester exam 1 prep & exam week (exam, 1 week before, 2 weeks before): 9/14 ~ 10/2
    exam2_exclude_start = datetime.date(2026, 9, 14)
    exam2_exclude_end = datetime.date(2026, 10, 2)
    
    # Holidays and school events
    school_events = {
        datetime.date(2026, 7, 13): "교육과정박람회",
        datetime.date(2026, 8, 17): "광복절 대체공휴일",
        datetime.date(2026, 9, 21): "추석 연휴",
        datetime.date(2026, 9, 22): "추석 연휴",
        datetime.date(2026, 9, 23): "추석 연휴",
    }
    
    start_date = datetime.date(2026, 6, 21)
    end_date = datetime.date(2026, 9, 30)
    
    curr = start_date
    available_mondays = []
    available_fridays = []
    
    all_mondays_in_range = []
    
    while curr <= end_date:
        # Check constraints
        is_vacation = vacation_start <= curr <= vacation_end
        is_exam1 = exam1_exclude_start <= curr <= exam1_exclude_end
        is_exam2 = exam2_exclude_start <= curr <= exam2_exclude_end
        is_event_or_holiday = curr in school_events
        
        reason = []
        if is_vacation: reason.append("여름방학")
        if is_exam1: reason.append("1학기말고사 및 대비기간(2주전~시험주)")
        if is_exam2: reason.append("2학기중간고사 및 대비기간(2주전~시험주)")
        if is_event_or_holiday: reason.append(school_events[curr])
        
        is_available = len(reason) == 0
        
        if curr.weekday() == 0:  # Monday
            all_mondays_in_range.append((curr, is_available, ", ".join(reason)))
            if is_available:
                available_mondays.append(curr)
        elif curr.weekday() == 4:  # Friday
            if is_available:
                available_fridays.append(curr)
                
        curr += datetime.timedelta(days=1)
        
    print("=== ALL MONDAYS FROM JUNE 21 TO SEPT 30 ===")
    for dt, avail, res in all_mondays_in_range:
        status = "가능" if avail else f"불가 ({res})"
        print(f"{dt} ({get_weekday_name(dt)}) : {status}")
        
    print("\n=== AVAILABLE MONDAYS ===")
    for m in available_mondays:
        print(m)
        
    print("\n=== AVAILABLE FRIDAYS ===")
    for f in available_fridays:
        print(f)

if __name__ == '__main__':
    main()
