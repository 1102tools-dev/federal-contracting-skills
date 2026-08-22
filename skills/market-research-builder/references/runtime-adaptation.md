# Runtime adaptation

- Use the host's structured selection UI only when all choices fit. Otherwise use numbered chat choices.
- Read supplied files through available file or document capabilities. Report unreadable formats rather than guessing.
- Match MCP tools by server, semantic operation, and schema. Never depend on generated namespace strings.
- Create DOCX through the host's document workflow or Python with `python-docx`.
- Render with LibreOffice or an equivalent real document engine. A parser alone does not prove layout.
- Use workspace-relative temporary paths and return a user-accessible artifact. Never hardcode `/mnt`, `/Users`, or a client-specific output directory in the workflow.
- If a capability is absent, state what is missing, what work it blocks, and the narrower supported alternative.
