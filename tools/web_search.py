"""
tools/web_search.py
Looks up current information on the open web. Uses the `duckduckgo-search`
package when available (no API key needed); falls back to SerpAPI if the
user supplied SERPAPI_API_KEY; degrades to a clear error message if
neither path is reachable (e.g. offline sandbox) rather than crashing
the run.
"""

from config import SERPAPI_API_KEY


def _search_duckduckgo(query: str, max_results: int = 5):
    try:
        from ddgs import DDGS  # current package name
    except ImportError:
        from duckduckgo_search import DDGS  # legacy package name, still widely installed
    with DDGS() as ddgs:
        return list(ddgs.text(query, max_results=max_results))


def _search_serpapi(query: str, max_results: int = 5):
    import requests
    resp = requests.get(
        "https://serpapi.com/search",
        params={"q": query, "api_key": SERPAPI_API_KEY, "num": max_results},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    results = []
    for item in data.get("organic_results", [])[:max_results]:
        results.append({
            "title": item.get("title", ""),
            "href": item.get("link", ""),
            "body": item.get("snippet", ""),
        })
    return results


def run(query: str) -> dict:
    query = query.strip()
    if not query:
        return {"ok": False, "output": "No search query provided.", "meta": {"error_type": "EmptyQuery"}}

    errors = []

    if SERPAPI_API_KEY:
        try:
            results = _search_serpapi(query)
            if results:
                return _format(results, query, source="SerpAPI")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"SerpAPI: {exc}")

    try:
        results = _search_duckduckgo(query)
        if results:
            return _format(results, query, source="DuckDuckGo")
        errors.append("DuckDuckGo returned no results")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"DuckDuckGo: {exc}")

    return {
        "ok": False,
        "output": f"Web search failed for '{query}'. " + " | ".join(errors),
        "meta": {"error_type": "SearchUnavailable", "query": query},
    }


def _format(results, query, source):
    lines = []
    for r in results[:5]:
        title = r.get("title", "Untitled")
        href = r.get("href", "")
        body = (r.get("body", "") or "")[:180]
        lines.append(f"• {title}\n  {href}\n  {body}")
    return {
        "ok": True,
        "output": "\n\n".join(lines),
        "meta": {"query": query, "source": source, "result_count": len(results)},
    }
