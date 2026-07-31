import re
from typing import Any, Dict, List

PERFORMANCE_RULES: List[Dict[str, Any]] = [
    # 1. Nested Loops
    {
        "id": "PERF-LOOP-001",
        "category": "Nested Loops",
        "title": "Nested Loop Complexity O(N^2) Bottleneck",
        "description": "Nested iteration loops detected. Performing O(N^2) or O(N^3) operations in a loop leads to severe CPU degradation as collection sizes grow.",
        "impact_level": "HIGH",
        "complexity_delta": "O(N^2) -> O(N)",
        "suggestion_type": "Caching",
        "pattern": re.compile(
            r"(?:for\s+.*in\s+.*:[\s\S]{1,200}?for\s+.*in\s+.*:|for\s*\([^)]*\)\s*\{[\s\S]{1,200}?for\s*\([^)]*\)\s*\{|while\s+.*:[\s\S]{1,200}?for\s+.*in\s+.*:|forEach\s*\(.*=>\s*\{[\s\S]{1,200}?forEach\s*\()",
            re.MULTILINE
        ),
        "optimization_suggestion": "Convert inner lookup into a Hash Map (Dictionary / Set) lookup or memoize pre-computed indexed values.",
        "structured_recommendation": (
            "Refactor nested loop to lookup dictionary:\n"
            "```python\n"
            "# Before: O(N^2)\n"
            "# for item in items:\n"
            "#     for target in targets: if item.id == target.id: ...\n"
            "# After: O(N)\n"
            "target_map = {t.id: t for t in targets}\n"
            "for item in items:\n"
            "    match = target_map.get(item.id)\n"
            "```"
        )
    },
    
    # 2. Repeated Database Queries (N+1 Problem)
    {
        "id": "PERF-NPLUS1-001",
        "category": "Repeated Database Queries",
        "title": "N+1 Database Query Execution Inside Loop",
        "description": "Database query invocation detected inside a loop body. Executing N database roundtrips introduces catastrophic network latency and DB connection exhaustion.",
        "impact_level": "HIGH",
        "complexity_delta": "N Queries -> 1 Query",
        "suggestion_type": "Indexes",
        "pattern": re.compile(
            r"(?:for\s+.*in\s+.*:|while\s+.*:|forEach\s*\().*?(?:db\.execute|session\.query|select\(|objects\.get|objects\.filter|repository\.find|findAll|createQuery|executeQuery|cursor\.execute)",
            re.DOTALL | re.IGNORECASE
        ),
        "optimization_suggestion": "Eager load related entities using JOIN / joinedload / selectinload, or fetch all IDs in a single 'IN (...)' batch query.",
        "structured_recommendation": (
            "Replace loop queries with batch fetching or eager loading:\n"
            "```python\n"
            "# Before: N+1 queries\n"
            "# for user in users:\n"
            "#     orders = db.execute(select(Order).where(Order.user_id == user.id))\n"
            "# After: 1 batch query with IN clause or joinedload\n"
            "user_ids = [u.id for u in users]\n"
            "orders_by_user = db.execute(select(Order).where(Order.user_id.in_(user_ids)))\n"
            "```"
        )
    },

    # 3. Blocking Operations in Async Routines
    {
        "id": "PERF-BLOCK-001",
        "category": "Blocking Operations",
        "title": "Synchronous Blocking I/O Operation in Execution Path",
        "description": "Synchronous blocking function call (e.g. time.sleep, fs.readFileSync, requests.get, Thread.sleep) detected. Synchronous blocking halts the main event loop / worker thread.",
        "impact_level": "HIGH",
        "complexity_delta": "Blocking (Sync) -> Async Non-blocking",
        "suggestion_type": "Async",
        "pattern": re.compile(
            r"(?:async\s+def\s+.*|async\s+function\s+.*)[\s\S]{1,300}?(?:time\.sleep\(|requests\.get\(|requests\.post\(|fs\.readFileSync\(|fs\.writeFileSync\(|urllib\.request|Thread\.sleep\()",
            re.MULTILINE | re.IGNORECASE
        ),
        "optimization_suggestion": "Replace synchronous calls with non-blocking async primitives (asyncio.sleep, httpx.AsyncClient, fs.promises.readFile).",
        "structured_recommendation": (
            "Convert synchronous call to non-blocking async:\n"
            "```python\n"
            "# Before: Blocking event loop\n"
            "# response = requests.get(url)\n"
            "# After: Async non-blocking HTTP client\n"
            "async with httpx.AsyncClient() as client:\n"
            "    response = await client.get(url)\n"
            "```"
        )
    },

    # 4. Large Memory Allocations
    {
        "id": "PERF-MEM-001",
        "category": "Large Memory Allocations",
        "title": "Unbuffered Whole-File Read into Memory",
        "description": "Reading an entire file or dataset into memory at once without chunking or streaming risks Out-Of-Memory (OOM) crashes on large files.",
        "impact_level": "MEDIUM",
        "complexity_delta": "O(N) Memory -> O(1) Streaming Memory",
        "suggestion_type": "Lazy Loading",
        "pattern": re.compile(
            r"(?:\.read\(\)|readFileSync\(|json\.loads\(open\(|\[0\]\s*\*\s*\d{5,}|new\s+Array\(\d{5,}\)|list\(range\(\d{6,}\)\))",
            re.IGNORECASE
        ),
        "optimization_suggestion": "Stream file line-by-line using generators, chunked reads, or cursor iterators to keep RAM memory overhead flat at O(1).",
        "structured_recommendation": (
            "Use line-by-line generator streaming or chunking:\n"
            "```python\n"
            "# Before: Loads entire file into RAM\n"
            "# data = open('huge.log').read()\n"
            "# After: O(1) Memory streaming generator\n"
            "with open('huge.log', 'r') as f:\n"
            "    for line in f:\n"
            "        process(line)\n"
            "```"
        )
    },

    # 5. Repeated API Calls
    {
        "id": "PERF-API-001",
        "category": "Repeated API Calls",
        "title": "Un-memoized Repeated HTTP API Call in Loop",
        "description": "HTTP request endpoint call inside a loop body. Making un-memoized repeated remote API network requests leads to severe rate limiting, high latency, and redundant network bandwidth usage.",
        "impact_level": "HIGH",
        "complexity_delta": "N API Requests -> 1 Cached Request",
        "suggestion_type": "Caching",
        "pattern": re.compile(
            r"(?:for\s+.*in\s+.*:|while\s+.*:|forEach\s*\().*?(?:fetch\(|axios\.get\(|axios\.post\(|requests\.get\(|requests\.post\(|httpx\.get\()",
            re.DOTALL | re.IGNORECASE
        ),
        "optimization_suggestion": "Cache API response using in-memory LRU cache or Redis, or batch requests using Promise.all / asyncio.gather.",
        "structured_recommendation": (
            "Cache API results using LRU memoization or Redis:\n"
            "```python\n"
            "from functools import lru_cache\n"
            "\n"
            "@lru_cache(maxsize=128)\n"
            "def fetch_user_profile(user_id: int):\n"
            "    return requests.get(f'https://api.example.com/users/{user_id}').json()\n"
            "```"
        )
    },

    # 6. Expensive Regex Patterns
    {
        "id": "PERF-REGEX-001",
        "category": "Expensive Regex",
        "title": "Potentially Catastrophic Backtracking Regex Pattern",
        "description": "Regex pattern containing nested quantifiers (e.g. (a+)+, (.*)+, ([a-zA-Z]+)*) or re.compile initialized inside a loop body.",
        "impact_level": "MEDIUM",
        "complexity_delta": "Exponential O(2^N) -> Linear O(N)",
        "suggestion_type": "Caching",
        "pattern": re.compile(
            r"(?:re\.compile\(.*(?:\(a\+\)\+|\(\.\*\)\+|\([a-zA-Z0-9_\-]+\)\+|\(\.\+\)\*)|new\s+RegExp\(.*(?:\(a\+\)\+|\(\.\*\)\+|\([a-zA-Z0-9_\-]+\)\+)|(?:for|while)[\s\S]{1,150}?re\.compile\()",
            re.IGNORECASE
        ),
        "optimization_suggestion": "Pre-compile regex outside loop scopes and eliminate nested wildcard quantifiers to avoid exponential Catastrophic Backtracking.",
        "structured_recommendation": (
            "Compile regex once at module level and avoid nested quantifiers:\n"
            "```python\n"
            "# Before: Compiled on every iteration\n"
            "# for line in lines: match = re.compile(r'(a+)+').search(line)\n"
            "# After: Pre-compiled static regex pattern\n"
            "PATTERN = re.compile(r'a+')\n"
            "for line in lines:\n"
            "    match = PATTERN.search(line)\n"
            "```"
        )
    },
]
