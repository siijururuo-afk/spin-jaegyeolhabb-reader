# Maintaining the Spin archive

- Read `sources.json` and `UPDATE_GUIDE.md` before refreshing content. These files persist the original profile URLs requested by the user.
- Keep the existing repository and multi-account selector. Preserve all existing accounts and bookmark namespaces.
- Fetch only public answered questions. Validate captured unique IDs against the public reply counter and probe the empty next page. Page is an index, not an offset.
- Compare IDs and original text against each account archive. Translate new or changed content; preserve reviewed translations otherwise.
- Never equate currently accessible public answers with deleted/private lifetime history.
- Keep question/answer pairing, original Korean, timestamps, source links and media. Preserve ambiguous CP names rather than inventing expansions.
- Regenerate the selected account's JSON/Markdown, `accounts.js`, source registry and capture report. Do not publish untranslated placeholders.
- Test account switching, account URL parameters, isolated bookmarks, search, sorting, pagination, original-language view and mobile layout before publishing.
