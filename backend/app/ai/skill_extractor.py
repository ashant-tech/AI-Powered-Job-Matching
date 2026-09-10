import re

SKILL_TAXONOMY: dict[str, list[str]] = {
    "python": ["python"],
    "javascript": ["javascript", "js"],
    "typescript": ["typescript", "ts"],
    "java": ["java"],
    "c#": ["c#", "csharp", ".net"],
    "c++": ["c++", "cpp"],
    "go": ["golang", "go"],
    "rust": ["rust"],
    "php": ["php", "laravel"],
    "ruby": ["ruby", "rails"],
    "kotlin": ["kotlin"],
    "swift": ["swift"],
    "dart": ["dart", "flutter"],
    "sql": ["sql", "postgresql", "postgres", "mysql", "sqlite", "mssql"],
    "nosql": ["mongodb", "nosql", "dynamodb", "cassandra"],
    "redis": ["redis"],
    "react": ["react", "reactjs", "react.js"],
    "next.js": ["next.js", "nextjs"],
    "vue": ["vue", "vuejs", "nuxt"],
    "angular": ["angular"],
    "node.js": ["node.js", "nodejs", "node", "express"],
    "django": ["django"],
    "flask": ["flask"],
    "fastapi": ["fastapi"],
    "spring": ["spring", "spring boot"],
    "html": ["html", "html5"],
    "css": ["css", "css3", "tailwind", "sass", "bootstrap"],
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "aws": ["aws", "amazon web services"],
    "azure": ["azure"],
    "gcp": ["gcp", "google cloud"],
    "linux": ["linux", "ubuntu"],
    "git": ["git", "github", "gitlab"],
    "ci/cd": ["ci/cd", "jenkins", "github actions"],
    "terraform": ["terraform"],
    "machine learning": ["machine learning", "ml", "scikit-learn", "sklearn"],
    "deep learning": ["deep learning", "tensorflow", "pytorch", "keras"],
    "nlp": ["nlp", "natural language processing", "transformers", "bert"],
    "data analysis": ["data analysis", "pandas", "numpy", "excel"],
    "data visualization": ["tableau", "power bi", "matplotlib"],
    "rest api": ["rest", "restful", "rest api"],
    "graphql": ["graphql"],
    "microservices": ["microservices"],
    "agile": ["agile", "scrum", "kanban"],
    "project management": ["project management", "pmp", "jira"],
    "communication": ["communication"],
    "leadership": ["leadership", "team lead"],
    "problem solving": ["problem solving", "problem-solving"],
    "accounting": ["accounting", "bookkeeping", "quickbooks"],
    "marketing": ["marketing", "seo", "digital marketing"],
    "sales": ["sales", "business development"],
    "customer service": ["customer service", "customer support"],
    "ui/ux": ["ui/ux", "figma", "user experience", "ux"],
}

_ALIAS_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (skill, re.compile(r"(?<![\w+#.])" + re.escape(alias) + r"(?![\w+#])", re.IGNORECASE))
    for skill, aliases in SKILL_TAXONOMY.items()
    for alias in sorted(aliases, key=len, reverse=True)
]


def extract_skills(text: str) -> list[str]:
    found: set[str] = set()
    for skill, pattern in _ALIAS_PATTERNS:
        if pattern.search(text):
            found.add(skill)
    return sorted(found)
