#!/usr/bin/env python3
"""Tavily API 팩트체크 검색"""

import os
import sys
import json
import time
import argparse


def search(query: str, max_results: int = 3) -> dict:
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return {"success": False, "error": "TAVILY_API_KEY 환경 변수가 설정되지 않았습니다."}

    try:
        from tavily import TavilyClient
    except ImportError:
        return {"success": False, "error": "tavily-python not installed. Run: pip install tavily-python"}

    client = TavilyClient(api_key=api_key)

    for attempt in range(3):
        try:
            response = client.search(
                query=query,
                search_depth="basic",
                max_results=max_results,
                include_answer=True,
            )
            results = [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", "")[:500],
                    "score": r.get("score", 0),
                }
                for r in response.get("results", [])
            ]
            return {
                "success": True,
                "query": query,
                "answer": response.get("answer", ""),
                "results": results,
            }
        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            return {"success": False, "error": str(e), "skipped": True}

    return {"success": False, "error": "max_retries_exceeded", "skipped": True}


def main():
    parser = argparse.ArgumentParser(description="Tavily 팩트체크 검색")
    parser.add_argument("--query", required=True, help="검색어")
    parser.add_argument("--max_results", type=int, default=3, help="최대 결과 수")
    args = parser.parse_args()

    result = search(args.query, args.max_results)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
