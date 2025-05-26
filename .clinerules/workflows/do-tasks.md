When working in *Act* mode:

1. Read the following files in the `experiments/<experiment>/memory-bank/` directory: **projectArchitecture.md**, **techContext.md**, **progress.md**.
3. Find the **first unchecked item** in **progress.md** (a line that starts with `- [ ]`).
4. Create a plan (including tests as needed) to complete that item, then implement it.
5. When the work is finished, mark the item `- [x]` in progress.md. Stage and commit the changes.
6. **If unchecked items remain**, automatically begin a **new task** that repeats steps 1-4
   (use the `new_task` tool so the context window stays small).
7. If you hit the same error twice in a row *or* there are no open items, stop and ask the user what to do next.
