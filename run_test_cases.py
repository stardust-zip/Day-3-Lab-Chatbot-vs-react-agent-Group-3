"""
Run 5 structured test cases through Chatbot, Agent v1, and Agent v2.
Scenario: Phone shop assistant (Vietnamese context).

Test Cases:
  1. Tim dien thoai theo gia          — search_by_price
  2. Mua nhieu mon + hoi khuyen mai   — check_stock + list_promotions (thieu thong tin ma KM)
  3. Hoi cac hang dien thoai           — list_brands
  4. Mua combo + ap dung ma KM cu the  — check_stock x3 + get_discount + calculator
  5. Hoi ngoai domain (laptop)         — out-of-domain, agent nen tu choi lich su
"""

import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding="utf-8")

TEST_CASES = [
    {
        "id": 1,
        "name": "Tim dien thoai theo gia",
        "description": "Khach tim dien thoai Samsung duoi 3 trieu — can dung search_by_price hoac search_by_brand",
        "query": "Tim giup toi dien thoai Samsung duoi 3 trieu",
        "expected": "Agent dung search_by_price(3000000) hoac search_by_brand(Samsung). Ket qua: Samsung Galaxy A05 (2.490.000d).",
    },
    {
        "id": 2,
        "name": "Mua nhieu mon + hoi khuyen mai chung",
        "description": "Khach mua combo nhung KHONG chi dinh ma khuyen mai — thieu thong tin",
        "query": "Mua dien thoai iPhone 17 Pro + op lung + kinh cuong luc het bao nhieu tien, co khuyen mai gi khi mua nhieu khong?",
        "expected": "Agent tra gia 3 san pham, roi dung list_promotions de liet ke KM. Chatbot se bia gia.",
    },
    {
        "id": 3,
        "name": "Hoi cac hang dien thoai",
        "description": "Cau hoi don gian — chi can goi list_brands",
        "query": "Cua hang co ban dien thoai cua nhung hang nao?",
        "expected": "Agent goi list_brands. Ket qua: Samsung, Apple, Xiaomi, OPPO.",
    },
    {
        "id": 4,
        "name": "Mua combo + ap dung ma KM cu the",
        "description": "Multi-step phuc tap: check_stock x3 + get_discount + calculator",
        "query": "Toi muon mua dien thoai iPhone 17 Pro + op lung + kinh cuong luc, neu ap dung khuyen mai HSSV2026 thi het bao nhieu tien?",
        "expected": "Agent tra gia 3 mon (32.990.000 + 350.000 + 150.000), tra ma HSSV2026 (giam 5%), tinh tong: 31.815.500d.",
    },
    {
        "id": 5,
        "name": "Out-of-domain: hoi mua laptop",
        "description": "Cau hoi ngoai pham vi — cua hang chi ban dien thoai",
        "query": "Cua hang co nhan thu mua laptop khong?",
        "expected": "Agent/Chatbot tu choi lich su. Agent v2 nen nhan biet ngay va tra loi Final Answer khong can goi tool.",
    },
]


def create_provider():
    provider_type = os.getenv("DEFAULT_PROVIDER", "local")
    if provider_type == "openai":
        from src.core.openai_provider import OpenAIProvider
        return OpenAIProvider(model_name=os.getenv("DEFAULT_MODEL", "gpt-4o"), api_key=os.getenv("OPENAI_API_KEY"))
    elif provider_type == "google":
        from src.core.gemini_provider import GeminiProvider
        return GeminiProvider(model_name=os.getenv("DEFAULT_MODEL", "gemini-1.5-flash"), api_key=os.getenv("GEMINI_API_KEY"))
    else:
        from src.core.local_provider import LocalProvider
        return LocalProvider(model_path=os.getenv("LOCAL_MODEL_PATH", "./models/Phi-3-mini-4k-instruct-q4.gguf"))


def run_all():
    from src.chatbot.chatbot import Chatbot
    from src.agent.agent import ReActAgent
    from src.agent.agent_v2 import ReActAgentV2
    from src.tools import TOOLS
    from src.telemetry.logger import logger

    print("Loading LLM provider...")
    llm = create_provider()
    print(f"Provider loaded: {llm.model_name}\n")

    chatbot = Chatbot(llm)
    agent_v1 = ReActAgent(llm, TOOLS, max_steps=5)
    agent_v2 = ReActAgentV2(llm, TOOLS, max_steps=7)

    results = []

    for tc in TEST_CASES:
        print("=" * 70)
        print(f"  TEST CASE {tc['id']}: {tc['name']}")
        print(f"  Mo ta: {tc['description']}")
        print(f"  Cau hoi: \"{tc['query']}\"")
        print(f"  Ky vong: {tc['expected']}")
        print("-" * 70)

        logger.log_event("TEST_CASE_START", {"id": tc["id"], "name": tc["name"], "query": tc["query"]})

        case = {"id": tc["id"], "name": tc["name"], "query": tc["query"]}

        # Chatbot
        print("\n  [CHATBOT]")
        try:
            ans = chatbot.chat(tc["query"])
            print(f"  >>> {ans[:500]}")
            case["chatbot"] = ans
        except Exception as e:
            print(f"  ERROR: {e}")
            case["chatbot"] = f"ERROR: {e}"

        # Agent v1
        print("\n  [AGENT v1]")
        try:
            ans = agent_v1.run(tc["query"])
            print(f"  >>> {ans[:500]}")
            case["agent_v1"] = ans
        except Exception as e:
            print(f"  ERROR: {e}")
            case["agent_v1"] = f"ERROR: {e}"

        # Agent v2
        print("\n  [AGENT v2]")
        try:
            ans = agent_v2.run(tc["query"])
            print(f"  >>> {ans[:500]}")
            case["agent_v2"] = ans
        except Exception as e:
            print(f"  ERROR: {e}")
            case["agent_v2"] = f"ERROR: {e}"

        logger.log_event("TEST_CASE_END", {"id": tc["id"], "name": tc["name"]})
        results.append(case)
        print()

    # Save results
    os.makedirs("logs", exist_ok=True)
    with open("logs/test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("=" * 70)
    print("  HOAN THANH — Tat ca 5 test cases da chay xong.")
    print("  Logs:    logs/2026-04-06.log")
    print("  Results: logs/test_results.json")
    print("  Chay 'python evaluate.py' de phan tich hieu nang.")
    print("=" * 70)


if __name__ == "__main__":
    run_all()
