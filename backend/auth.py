from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from fastapi import Request
import time
from collections import defaultdict

# API Key 헤더
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# 데모용 API Key DB (실제 서비스에선 DB 연동)
VALID_API_KEYS = {
    "sk_demo_free_12345": {"tier": "free", "daily_limit": 50},
    "sk_demo_pro_99999": {"tier": "pro", "daily_limit": 1000},
}

# Rate Limiting (메모리 저장소)
# Key: api_key, Value: {date: "YYYY-MM-DD", count: 10}
usage_tracker = defaultdict(lambda: {"date": "", "count": 0})

async def get_api_key(api_key: str = Security(api_key_header)):
    """API Key 검증 및 Rate Limiting"""
    
    # 1. API Key 존재 여부 확인
    if not api_key:
         # 웹 UI(프론트엔드)에서의 요청은 예외 처리 (쿠키/세션 방식 등)
         # 여기서는 데모를 위해 'None'이면 웹 요청으로 간주하고 패스할 수도 있지만,
         # 엄격한 보안을 위해 거부합니다. (웹은 별도 내부 API 키 사용)
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials"
        )
        
    if api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
        
    # 2. Rate Limiting 체크
    tier_info = VALID_API_KEYS[api_key]
    limit = tier_info["daily_limit"]
    
    today = time.strftime("%Y-%m-%d")
    user_usage = usage_tracker[api_key]
    
    # 날짜가 바뀌었으면 카운트 리셋
    if user_usage["date"] != today:
        user_usage["date"] = today
        user_usage["count"] = 0
        
    # 한도 초과 확인
    if user_usage["count"] >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily limit exceeded ({limit} requests)"
        )
        
    # 사용량 증가
    user_usage["count"] += 1
    
    return api_key
