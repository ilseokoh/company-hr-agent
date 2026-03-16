from google.adk.agents import Agent

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

def submit_leave_request(start_date: str, end_date: str, hours_per_day: int = 8, reason: str = None): 
    # TODO: Vacation API 호출 
    return { 
        "start_date": start_date, 
        "end_date": end_date,
        "total_days": 1, 
        "total_hours": 1, 
        "reason": reason
    }


vacation_agent = Agent(
    name="vacation_agent",
    model="gemini-2.5-flash",
    description="내 휴가에 대한 정보를 가져오는 에이전트로 남은 휴가에 대해서 답변합니다.",
    instruction="""
    당신은 임직원들의 휴가를 관리하는 매니저 입니다. 

    **지시사항**
    남은 휴가에 대해서 물어보면 get_vacation_balance 툴을 사용하여 답변합니다. 
    남은 휴가를 시간과 일로 모두 답변합니다. 
    * balance_as_of_date: 남은 휴가 시간
    * accrued_year_to_date: 올해 시작할 때 휴가 시간
    * carryover_balance: 작년에 이월된 휴가 시간
    * absence_paid_in_period: 사용한 휴가 시간

    **답변 예시**
    당신의 남은 휴가는 22일(176시간) 입니다. 
    * 작년에 이월된 휴가 1일(8시간)
    * 올해 지급된 휴가 21일(168시간)
    * 올해 사용한 휴가 0일(0시간) 
    """,
    tools=[get_vacation_balance]
)