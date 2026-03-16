from google.adk.agents import Agent
from datetime import date
from datetime import datetime

def get_vacation_balance() -> dict:
    """
    특정 날짜와 사용자 ID를 기준으로 사용자의 남은 휴가 정보를 반환합니다.

    Returns:
        휴가 잔여 정보가 담긴 사전.
    """
    # TODO: Vacation API 호출 
    return {
        "absence_plan": "KR - Vacation Plan",
        "unit_of_time": "Hours",
        "beginning_year_balance": 32,
        "carryover_balance": 8,
        "accrued_year_to_date": 168,
        "absence_paid_year_to_date": 24,
        "beginning_period_balance": 176,
        "accrued_in_period": 0,
        "absence_paid_in_period": 0,
        "carryover_forfeited_in_period": 0,
        "balance_as_of_date": 176,
        "balance_as_of_date_includes_events_awaiting_approval": 176,
        "as_of_period": "01/03/2026 - 31/03/2026 (Monthly)"
    }

def submit_leave_request(start_date: str, end_date: str, reason: str = None): 
    """
    휴가 신청을 제출하고, 신청된 휴가 정보를 반환합니다.

    Args:
        start_date (str): 휴가 시작일 (YYYY-MM-DD 형식)
        end_date (str): 휴가 종료일 (YYYY-MM-DD 형식)
        reason (str, optional): 휴가 사유. Defaults to None.

    Returns:
        dict: 휴가 신청 정보 (시작일, 종료일, 총 일수, 총 시간, 사유)
    """
    # YYYY-MM-DD 형식의 문자열을 date 객체로 변환합니다.
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

    # 종료일과 시작일의 차이를 계산하여 휴가 일수를 구합니다. (시작일 포함을 위해 +1)
    total_days = (end_date_obj - start_date_obj).days + 1
    
    # 총 휴가 시간을 계산합니다. (일수 * 8시간)
    total_hours = total_days * 8

    # TODO: Vacation API 호출 
    return { 
        "start_date": start_date, 
        "end_date": end_date,
        "total_days": total_days, 
        "total_hours": total_hours, 
        "reason": reason
    }


vacation_agent = Agent(
    name="vacation_agent",
    model="gemini-2.5-flash",
    description="내 휴가에 대한 정보를 가져오고, 휴가를 신청해주는 에이전트",
    instruction=f"""
    당신은 임직원들의 휴가를 관리하는 매니저 입니다. 
    오늘은 {date.today().strftime("%Y-%m-%d")} 입니다. 

    **지시사항**
    남은 휴가에 대해서 물어보면 get_vacation_balance 툴을 사용하여 답변합니다. 
    남은 휴가를 시간과 일로 모두 답변합니다. 
    * balance_as_of_date: 남은 휴가 시간
    * accrued_year_to_date: 올해 시작할 때 휴가 시간
    * carryover_balance: 작년에 이월된 휴가 시간
    * absence_paid_in_period: 사용한 휴가 시간

    남은 휴가 질문에 답변 예시
    당신의 남은 휴가는 22일(176시간) 입니다. 
    * 작년에 이월된 휴가 1일(8시간)
    * 올해 지급된 휴가 21일(168시간)
    * 올해 사용한 휴가 0일(0시간) 

    휴가 신청을 요청하면 submit_leave_request 툴을 사용하여 답변합니다. 
    * 사용자로 부터 반드시 시작일(start_date), 종료일(end_date), 사유(reason)을 받아야 합니다. 
    * 신청 결과를 요약해서 사용자에게 리턴합니다. 
    
    휴가신청 답변 예시: 2026년 3월 3일 부터 2026년 3월 4일까지 총 2일(16시간)의 휴가를 ""사유로 신청했습니다. 
    """,
    tools=[get_vacation_balance, submit_leave_request]
)