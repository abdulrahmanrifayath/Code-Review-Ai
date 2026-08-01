import re
from typing import Any

SECURITY_RULES: list[dict[str, Any]] = [
    # 1. SQL Injection
    {
        "id": "SEC-SQLI-001",
        "category": "SQL Injection",
        "cwe_id": "CWE-89",
        "severity": "CRITICAL",
        "title": "Unsanitized Dynamic SQL Query Construction",
        "description": "Dynamic string formatting or concatenation used in SQL query construction allows arbitrary SQL injection.",
        "pattern": re.compile(r"(?:SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|EXEC)\s+.*(?:%s|\{\}|\+|\.format|f['\"])", re.IGNORECASE),
        "remediation": "Use parameterized queries or ORM binding interfaces (e.g. SQLAlchemy bindparams or PreparedStatements).",
    },
    # 2. Hardcoded Passwords
    {
        "id": "SEC-CRED-001",
        "category": "Hardcoded Credentials",
        "cwe_id": "CWE-259",
        "severity": "HIGH",
        "title": "Hardcoded Cleartext Password Credential",
        "description": "Hardcoded cleartext password assigned in source code.",
        "pattern": re.compile(r"(?:password|passwd|pwd|secret_key)\s*[:=]\s*['\"][^'\"]{4,}['\"]", re.IGNORECASE),
        "remediation": "Move credentials to secure environment variables or vault secrets manager.",
    },
    # 3. API Keys & Token Credentials
    {
        "id": "SEC-KEY-001",
        "category": "API Keys",
        "cwe_id": "CWE-798",
        "severity": "HIGH",
        "title": "Hardcoded API Key or Access Token",
        "description": "Hardcoded API key or private access token found in source file.",
        "pattern": re.compile(r"(?:api_key|apikey|access_token|github_token|stripe_key|aws_secret)\s*[:=]\s*['\"][a-zA-Z0-9_\-\.]{12,}['\"]", re.IGNORECASE),
        "remediation": "Store API tokens in environment variables or cloud secrets management.",
    },
    # 4. JWT Issues
    {
        "id": "SEC-JWT-001",
        "category": "JWT Issues",
        "cwe_id": "CWE-347",
        "severity": "HIGH",
        "title": "Insecure JWT Algorithm 'none' or Disabled Verification",
        "description": "JSON Web Token decode initialized with algorithm 'none' or signature verification disabled.",
        "pattern": re.compile(r"(?:jwt\.decode\(.*verify=False|algorithm\s*=\s*['\"]none['\"]|algorithms\s*=\s*\[['\"]none['\"]\])", re.IGNORECASE),
        "remediation": "Enforce strong asymmetric/symmetric signing algorithms (HS256/RS256) and mandatory signature verification.",
    },
    # 5. Command Injection
    {
        "id": "SEC-CMD-001",
        "category": "Command Injection",
        "cwe_id": "CWE-78",
        "severity": "CRITICAL",
        "title": "Unsafe OS System Command Execution",
        "description": "Unsanitized input passed directly to OS shell execution functions.",
        "pattern": re.compile(r"(?:os\.system\(|subprocess\.Popen\(.*shell\s*=\s*True|child_process\.exec\(|Runtime\.getRuntime\(\)\.exec\()", re.IGNORECASE),
        "remediation": "Avoid shell=True. Pass argument lists to subprocess.exec or use safer language APIs.",
    },
    # 6. Unsafe File Operations
    {
        "id": "SEC-FILE-001",
        "category": "Unsafe File Operations",
        "cwe_id": "CWE-377",
        "severity": "MEDIUM",
        "title": "Insecure Temporary File Creation",
        "description": "Creation of temporary file with insecure permissions or predictable filename.",
        "pattern": re.compile(r"(?:tempnam\(|mktemp\(|open\(['\"]/tmp/)", re.IGNORECASE),
        "remediation": "Use secure tempfile functions (e.g. tempfile.NamedTemporaryFile) with restricted permissions.",
    },
    # 7. XSS (Cross-Site Scripting)
    {
        "id": "SEC-XSS-001",
        "category": "XSS",
        "cwe_id": "CWE-79",
        "severity": "HIGH",
        "title": "Raw Unescaped HTML Injection (XSS)",
        "description": "Direct unescaped HTML string rendering enables Cross-Site Scripting attack vectors.",
        "pattern": re.compile(r"(?:dangerouslySetInnerHTML|v-html|innerHTML\s*=|\$\(.*\)\.html\()", re.IGNORECASE),
        "remediation": "Sanitize HTML using DOMPurify or rely on framework default auto-escaping.",
    },
    # 8. CSRF (Cross-Site Request Forgery)
    {
        "id": "SEC-CSRF-001",
        "category": "CSRF",
        "cwe_id": "CWE-352",
        "severity": "MEDIUM",
        "title": "Missing CSRF Protection Header or Token",
        "description": "State-changing POST/PUT/DELETE request missing anti-CSRF token verification.",
        "pattern": re.compile(r"(?:@csrf_exempt|CSRF_ENABLED\s*=\s*False|SameSite\s*=\s*['\"]None['\"])", re.IGNORECASE),
        "remediation": "Enable anti-CSRF tokens and set cookie SameSite policy to Lax or Strict.",
    },
    # 9. Path Traversal
    {
        "id": "SEC-PATH-001",
        "category": "Path Traversal",
        "cwe_id": "CWE-22",
        "severity": "HIGH",
        "title": "Arbitrary Path Traversal Directory Vulnerability",
        "description": "Concatenating user input into file paths allows accessing restricted directory files.",
        "pattern": re.compile(r"(?:open\(.*(?:\.\./|\+\s*filename)|send_file\(.*\+|file_get_contents\(.*\.\./)", re.IGNORECASE),
        "remediation": "Sanitize filenames using os.path.basename and validate paths against strict root directory boundaries.",
    },
]
