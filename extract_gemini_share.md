Think step by step.

You have access to browser, bash and file tools.

Target URL:
https://share.gemini.google/bdpo1CWmSqzG

Task:
Extract the complete Gemini shared conversation.

Requirements:

1. Open the URL using a real browser session.
2. Wait for JavaScript rendering to finish.
3. Inspect:
   - DOM
   - embedded JSON
   - script tags
   - XHR requests
   - fetch requests
   - GraphQL requests
   - browser state

4. If the page is only an application shell,
   identify the API endpoint that contains the
   conversation payload.

5. Recover:
   - conversation title
   - all user messages
   - all model messages
   - code blocks
   - links

6. Export:

conversation.md
conversation.json
conversation_debug.txt

conversation.json schema:

{
  "url": "",
  "title": "",
  "messages": []
}

7. Verify:
   - message count
   - chronological order
   - exact code block preservation

8. If extraction fails,
   generate a forensic report containing:
   - rendered DOM snapshot
   - detected API endpoints
   - detected JSON blobs
   - detected script variables
   - reason for failure

Do not summarize.
Extract raw conversation data.
