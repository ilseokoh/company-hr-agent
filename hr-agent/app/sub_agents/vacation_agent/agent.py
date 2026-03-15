from google.adk.agents import Agent

def get_vacation_balance() -> dict:
    """
    특정 날짜와 사용자 ID를 기준으로 사용자의 남은 휴가 정보를 반환합니다.

    Returns:
        휴가 잔여 정보가 담긴 사전.
    """
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


vacation_agent = Agent(
    name="vacation_agent",
    model="gemini-2.5-flash",
    description="내 휴가에 대한 정보를 가져오는 에이전트로 남은 휴가에 대해서 답변합니다.",
    instruction="""
    당신은 임직원들의 휴가를 관리하는 매니저 입니다. 
    남은 휴가에 대해서 물어보면 get_vacation_balance 툴을 사용하여 답변합니다. 
    """,
    tools=[get_vacation_balance]
)