# Boolean and X-Ray cheat sheet
*Module 3, Lessons 2–3.*

## Operators
| Operator | Does | Note |
|---|---|---|
| `AND` | Both terms | Often implicit. Every added AND shrinks the pool sharply |
| `OR` | Either term | Where your synonyms live — the highest-value operator |
| `NOT` / `-` | Excludes | Use sparingly; it removes people you cannot see |
| `"quotes"` | Exact phrase | Essential for multi-word titles. Rarely quote skills |
| `(parentheses)` | Groups terms | Omitting these is the most common error |
| `site:` | Restricts to a domain | The basis of X-Ray search |

## The three-block structure
```
(CORE TITLES joined by OR)
AND (SKILLS joined by OR)
AND (LOCATION joined by OR)
-"hiring" -"job description" -"apply now"
```

Worked example:
```
("data engineer" OR "analytics engineer" OR "ETL developer")
AND (dbt OR airflow OR "data pipeline")
AND (Bengaluru OR Bangalore)
-"hiring" -"job description"
```

## X-Ray by platform
| Platform | Prefix | Best for |
|---|---|---|
| LinkedIn | `site:linkedin.com/in` | Widest coverage, least evidence |
| LinkedIn (country) | `site:in.linkedin.com/in` | Geographic narrowing |
| GitHub | `site:github.com` | Evidence of actual work |
| Behance | `site:behance.net` | Design portfolios |
| Stack Overflow | `site:stackoverflow.com/users` | Depth, and how they explain |

## The four mistakes
1. **Missing parentheses.** `python OR java AND senior` does not mean what you think.
2. **Too many ANDs.** Each concept multiplies. Four AND groups usually leaves a handful.
3. **Over-quoting.** Quoting a skill written five ways misses four of them.
4. **Titles alone.** Titles are not standardised. Always pair with a skill block.

## Before you scale
Run the query, open the first ten results, count how many are plausibly right.
**Below five, fix the query** rather than reading 200 results.

## Query log
| Date | Role | Query | First-10 hit rate | Changed / why |
|---|---|---|---|---|
| | | | | |
