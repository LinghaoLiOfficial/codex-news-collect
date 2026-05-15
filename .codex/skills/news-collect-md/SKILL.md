---
name: news-collect-md
description: Collect recent news articles from one target media site with Google Chrome-only navigation, extract paragraph-ordered article text, save Markdown under output/, and produce a consistently styled DOCX by using the global Documents skill render-and-verify workflow.
---

# News Collect Md

## Overview

Use this skill to build a reproducible Markdown digest from one media site search.
Collect up to `最大数量` items with verifiable metadata and content evidence.
Within a site run, enforce strict item-serial extraction: finish current article extraction and validation before opening the next candidate article.

## Inputs

Keep these configurable for each run:
- `目标媒体网站` - the site to search
- `主题` - the article theme or query phrase
- `时间范围` - the publication window to apply
- `最大数量` - the maximum number of articles to collect

## Query Fallback Chain (Mandatory)

For every site, use this ordered query chain until collected count reaches `最大数量`:
1. Q1: translate user `主题` into the target media site's language, then search with the translated query
2. Q2: `Trump China visit` translated into the target media site's language
3. Q3: `Trump Xi summit` translated into the target media site's language (or equivalent in that language)

Execution requirements:
- Before each query round, ensure the query text is in the target media site's language.
- If the input `主题` is already in the target site language, use it directly without back-translation.
- Prefer searching from the website's visible search input box and press `Enter`.
- If no visible search input exists on the target site, treat the target site's homepage as the post-search result page and continue candidate collection there first.
- If search input is unavailable, use the site's search URL pattern as fallback.
- Do not stop after one query if collected count is below `最大数量`.

Homepage shortcut:
- Before starting the Query Fallback Chain, inspect the homepage for direct-news candidate cards.
- If the homepage already shows more than `最大数量` clearly relevant high-news items, skip the search/query step entirely and proceed directly to homepage candidate collection, dedup, open_extract, validate, and count.
- "Clearly relevant" still requires direct relevance to `主题` in title or lead text and a usable publication date.

## Mandatory Browser Constraint

Enforce the following constraint for the entire workflow:
- Use `@chrome` (Google Chrome) only.
- Do not use any other browser.
- Do not open a new tab.
- Always operate on the current active tab.
- Do not switch to web search tools, direct HTTP fetch tools, or non-Chrome page-reading fallbacks for article retrieval.
- If `@chrome` (Google Chrome) is unavailable or blocked, stop and report that the task cannot proceed under the Chrome-only requirement.

## Reference

For stricter collection decisions and extraction consistency, use:
- `references/collection-checklist.md`

## Workflow

1. Open `@chrome` (Google Chrome) and visit `目标媒体网站` exactly as provided in the current active tab.
2. Do not rewrite `目标媒体网站` into `site:` search syntax or otherwise shorten the URL.
3. Run a state loop until completion or exhaustion:
   - `search -> collect_candidates -> dedup -> open_extract -> validate -> count`
4. Search with the Query Fallback Chain.
   - First check whether the homepage already exposes more than `最大数量` clearly relevant high-news items.
   - If yes, skip search and collect from the homepage directly.
5. For each query round:
   - collect candidate links from result page 1, then page 2+ if needed
   - deduplicate by canonical URL (remove tracking params)
   - open candidate article pages in Chrome by reusing the current active tab only (no new tab)
6. Filter or verify each candidate against `时间范围`.
7. Validate article against `references/collection-checklist.md` `Completion Definition`.
8. Continue query/page rounds until:
   - counted items >= `最大数量`, or
   - all query rounds + page rounds exhausted.
   - Never start another target site from this worker before this site reaches a final status.
9. Write a new local `.md` file under `output/` that includes:
   - source site and run parameters
   - per-item metadata and content type
   - article title, publication date, and link
   - paragraph-by-paragraph excerpts for each fulltext article
   - `未收录原因` summary when counted items < `最大数量`
10. Convert Markdown to `.docx` by invoking global `$Documents` skill workflow (create/edit + render-and-verify loop) instead of ad-hoc conversion.
11. Keep output focused on selected articles only.

## Universal Hard Constraints (Apply to Any Target Site)

1. No early stop after first success:
- If counted items are below `最大数量`, continue collection rounds until query/page attempts are exhausted.

2. Result snippets are never countable:
- A candidate is countable only after opening its target page and validating completion fields.

3. Search interaction priority:
- Primary method is on-page search input + `Enter`.
- If the target site has no visible search input, homepage-first collection is mandatory (treat homepage as search result page before URL-pattern search fallback).
- URL query parameter search is fallback only when on-page input is unavailable.

4. Paywall fallback is mandatory:
- If fulltext is blocked but metadata is visible, still record `title + publication date + URL` as `content_type=paywall_meta`.

5. Content-type-aware counting:
- `fulltext` needs paragraph extraction and paragraph count gate.
- `fulltext` needs paragraph extraction and paragraph count `>= 3`.
- `video`/`brief` may be included only with explicit type label and complete metadata.

6. Dedup and backfill are mandatory:
- Deduplicate by canonical URL.
- Keep backfilling until reaching `最大数量` or exhausting all fallback attempts.

7. Item-level completion gate is mandatory:
- Do not count an item before extraction is complete for that item.
- For `fulltext`, completion requires paragraph extraction (`paragraph_count >= 1`) and stored excerpts.
- For `video|brief|paywall_meta`, completion requires complete metadata fields and explicit `content_type`.

## DOCX Style Rules

- Use `$Documents` skill as the canonical formatter.
- Keep title as Heading 1.
- Keep article sections as Heading 2.
- Keep “正文逐段摘录” as Heading 3.
- Keep paragraph excerpts as ordered lists.
- Use Chinese-readable body typography with consistent line spacing and page margins.
- Before finalizing the DOCX, force all text in the document (including headings, body, lists, and table text if any) to `宋体`.
- Render and visually verify before finalizing docx.

## Output Rules

- Use `@chrome` (Google Chrome) only for navigation and reading.
- Reuse the current active tab for all navigation; never create or switch to a newly opened tab.
- Do not rely on other browsers for page collection.
- Do not substitute non-browser extraction paths for article content.
- Preserve the original `目标媒体网站` as the access URL in logs and output; do not replace it with `site:` syntax.
- Save the result as a new local Markdown file under `output/`.
- Save the final reviewed `.docx` under `output/` with the same basename.
- If fewer than `最大数量` articles match, include only valid matches and append explicit reasons.
- If results are ambiguous, prefer the most recent articles that clearly satisfy `时间范围`.

Mandatory output fields per collected item:
- `title`
- `publish_time_raw`
- `publish_time_norm` (`YYYY-MM-DD`)
- `url`
- `query_used` (must be the actual translated query used on the target site)
- `content_type` (`fulltext|video|brief|paywall_meta`)
- `paragraph_count`
- `paywall_flag` (`true|false`)

## Failure Handling

If any required page cannot be accessed in `@chrome` (Google Chrome):
- Record the affected URL.
- Record the blocking reason (for example: paywall, login requirement, page load failure, missing_date, not_relevant).
- Continue with remaining eligible URLs when possible.
- If no URLs can be processed in `@chrome` (Google Chrome), stop and report failure.

If DOCX cannot be completed through `$Documents` workflow:
- Record the blocking reason.
- Keep the Markdown artifact.
- Mark DOCX generation as failed in the run summary.

Use site-level status labels:
- `SUCCESS`: counted items >= `最大数量`
- `PARTIAL_SUCCESS`: counted items > 0 and < `最大数量`
- `FAILED`: counted items = 0, or no Chrome evidence

Site finalization gate:
- Only emit site final status after all counted items in this site run have passed the item-level completion gate.

## Markdown Layout

Use a structure like this:

```md
# {主题} 新闻汇总

- 目标媒体网站: {目标媒体网站}
- 主题: {主题}
- 时间范围: {时间范围}
- 最大数量: {最大数量}

## 1) {标题}
- 发布时间: {日期}
- 链接: {URL}

### 正文逐段摘录
1. ...
2. ...
```
