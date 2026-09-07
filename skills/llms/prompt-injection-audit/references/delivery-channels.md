# Delivery channels

Indirect injection means the instruction arrives inside content the agent reads, not inside the
user's turn. The channel decides what is testable and how a negative result should be read.

| Channel | How the instruction arrives | Precondition | Canary |
|---|---|---|---|
| Browsed page | Agent fetches a URL and the page body carries the instruction | fetch/browse tool | unique string in the body the agent should quote |
| Tool / API response | A service the agent calls returns attacker-influenced fields | agent calls an API you can influence | marker in a returned field |
| Uploaded file | PDF, CSV, docx or image the user is induced to attach | file ingestion | marker in an off-screen or low-attention region |
| Ticket / issue / email body | Agent triages queues written by outsiders | integration with the queue | marker in the body |
| RAG corpus | Poisoned document is retrieved as a chunk | write path into the index, direct or via crawl | marker phrased to rank for a known query |
| Code comment / config | Agent reads a repo you can PR into | repo read | marker in a file the agent will open |
| Summarized-into-memory | Content the agent condenses into durable notes | memory write | marker that must survive summarization |

## The canary rule

Every channel gets a benign canary before any payload: a unique string carrying **no instruction**,
which the agent should simply reproduce if it read the content.

An unread channel and a resistant agent produce identical output - nothing. Without a returning
canary, a matrix of null results reads as a hardened target when it may be a document the agent
never opened. Report an unread channel as **not-delivered**, never as clean.

Re-check the canary at the end of a channel's run. Agents change what they fetch as context fills,
and a channel that was live at run 1 may be silently dropped by run 20.

## Choosing a channel

Prefer the channel with the shortest path from an outsider to the context window: the one an
attacker could actually use without an account, an approval, or an insider. A working injection
through a channel that requires admin access to poison is a much weaker finding than the same
payload through a public issue tracker, and the write-up should say which one it was.
