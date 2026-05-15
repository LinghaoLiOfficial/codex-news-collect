# Collection Checklist

## Completion Definition (Count Gate)

An item is countable only if all required fields exist:
- `title`
- `publish_time_raw`
- `publish_time_norm` (`YYYY-MM-DD`)
- `url`
- `content_type`

Additional count rules by type:
- `fulltext`: paragraph count must be `>= 3`
- `video`: allowed only when page-level title/date/url are clear
- `paywall_meta`: allowed when fulltext is blocked but title/date/url are visible

Never count:
- search result cards without opening the target page
- pages with missing/ambiguous date
- duplicate canonical URLs

## Time Window Decision

1. Parse the user-provided `时间范围` into explicit date boundaries.
2. Prefer article pages that show a clear publication date.
3. Include an article only when its date is inside the requested window.
4. If date is missing or ambiguous, exclude it and record the reason.

## Relevance Decision

1. Require direct relevance to `主题` in title or lead paragraphs.
2. If multiple candidates compete near `最大数量`, prefer higher relevance first, then recency.
3. Exclude opinion or photo-only pages unless the user explicitly allows them.

## Paragraph Extraction Rules

1. Extract paragraph content in original reading order.
2. Skip navigation text, ad blocks, related-links blocks, footer boilerplate, and share widgets.
3. Preserve quotations and proper nouns exactly as shown.
4. If a paragraph contains inline link anchors, keep readable sentence text and omit tracking fragments.

## Failure Logging

For each failed URL, record:
- URL
- failure type (`paywall`, `login_required`, `load_error`, `missing_date`, `not_relevant`)
- short note

For each site, record:
- `queries_tried`
- `pages_visited`
- `candidates_found`
- `items_counted`
- `status` (`SUCCESS|PARTIAL_SUCCESS|FAILED`)

## Output Consistency

1. Keep numbering stable (`## 1)`, `## 2)` ...).
2. Keep each article section in this order:
   - title
   - publication date
   - URL
   - content_type
   - paragraph-by-paragraph excerpts
3. If collected count is lower than `最大数量`, add a short "未收录原因" section at the end.

## Backfill Loop Rules

1. Continue collection rounds while `items_counted < 最大数量`.
2. For each round:
- run next query from fallback chain
- scan next result page(s)
- open, validate, count
3. Stop only when:
- `items_counted >= 最大数量`, or
- all queries exhausted and no new candidates remain.
