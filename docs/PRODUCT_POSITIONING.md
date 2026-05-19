# Forge Agent Product Positioning

## One-sentence positioning

Forge Agent is an AI butler for ordinary users: people describe what they want in plain language, and Forge uses connected apps, memory, confirmation, records, and recovery to get the work done without forcing users to learn every tool.

In Chinese:

```text
Forge Agent 是普通人一句话办事的 AI 管家：
用户不用学邮箱、GitHub、Notion、日历、文件管理、API 或自动化流程，
只需要说自己要做什么，Forge 负责理解、确认、执行、记录和必要时恢复。
```

## Core user problem

Most software is powerful but hard for ordinary users.

A user may want to:

- send an email,
- create a GitHub repository,
- organize invoices,
- summarize important mail,
- make a report,
- prepare slides,
- update a calendar,
- file an issue,
- move files,
- or reuse the same workflow next time.

The blocker is not always intelligence. The blocker is learning cost and time cost:

```text
Where is the button?
Which app should I open?
What is a repository?
What is a pull request?
Which permission should I approve?
How do I avoid breaking something?
How do I undo it if it goes wrong?
Why do I need to repeat the same instructions every time?
```

Forge exists to remove that burden.

## Product promise

Forge should let users say things like:

```text
Use my email to send a follow-up to John.
Create a GitHub repository for this project. I do not know how GitHub works.
Organize this folder of invoices by month.
Turn these notes into a clean report.
Check whether I have important emails today.
Remember how I like project reports formatted.
```

Forge should respond in ordinary language:

```text
I can do that.
Here is what I will do:
1. Open your connected email account.
2. Draft the message to John.
3. Show it to you before sending.

I will not send anything until you confirm.
```

Then after completion:

```text
Done.
I sent the email to John.
I saved a record of what was sent.
Next time, I can use the same style unless you change it.
```

For file or account changes:

```text
Done.
I moved 23 files and skipped 2 uncertain files.
You can restore the files to their previous locations if needed.
```

## What users should see

The front end should stay simple even if the backend eventually connects thousands of services.

The user-facing surface should be:

1. A plain-language input box.
2. A short confirmation card.
3. A progress view.
4. A clear completion result.
5. A history view.
6. A simple recovery/correction option when possible.
7. A memory/preferences view written in ordinary language.

Users should not have to understand:

- API,
- OAuth scope,
- tool registry,
- rollback manifest,
- audit log,
- prompt injection,
- embeddings,
- vector search,
- Git internals,
- or agent frameworks.

Those can exist internally, but the product must explain them as:

| Internal term | User-facing language |
|---|---|
| permission | What I can see or change |
| approval | You confirm before I do it |
| rollback | Restore / undo |
| audit log | What I did |
| memory | What I remember about you |
| tool | An app I can use for you |
| risk | What this may affect |
| skill | How I should do this next time |

## Product pillars

Forge has multiple advantages. None of them should stand alone; the product wins through their combination.

### 1. Simple use

Users describe outcomes, not software procedures.

```text
Wrong product direction:
Configure this Gmail integration, choose a tool, set scope, and run a command.

Right product direction:
Tell me who to email and what you want to say. I will draft it and ask before sending.
```

### 2. Long-term memory

Forge should remember stable user preferences, project context, recurring workflows, formatting rules, and prior decisions.

The user should be able to see and correct what Forge remembers.

### 3. Memory Palace

The Memory Palace is the internal structure for long-term context.

It should support:

- user memory,
- project memory,
- skill memory,
- operation memory,
- session memory,
- visible recall,
- sensitive memory controls,
- forgetting,
- quarantine,
- restore,
- export,
- and audit.

The user-facing version is simple:

```text
Here is what I remember about you and this project.
You can edit or forget any item.
```

### 4. Safe confirmation

Important actions should be explained before execution.

Forge should say:

```text
This will send an email.
This will move files.
This will create a repository.
This will change your calendar.
```

And ask:

```text
Do you want me to continue?
```

### 5. Recovery and correction

Where possible, Forge should preserve a recovery path.

User-facing language:

```text
Restore to before I changed it.
Undo this organization.
Show me what changed.
```

### 6. Hidden complexity, visible result

Forge may eventually connect many apps and services, but the user should not need to know how many.

The product should feel like:

```text
I ask. Forge handles the apps.
```

Not:

```text
I configure APIs and tools.
```

## Competitive framing

Forge should now benchmark against three named directions:

### OpenHuman

OpenHuman proves the demand for a personal AI entry point that can connect many apps.

Forge should not blindly race on integration count first.

Forge should match the ordinary-user ambition and exceed it on:

- clearer confirmation,
- understandable action previews,
- visible memory,
- history of what was done,
- recovery/correction path,
- and user-controlled app authority.

### OpenClaw

OpenClaw represents self-hosted agent execution and practical tool automation.

Forge should match the useful execution direction and exceed it on:

- human-readable action plans,
- lower setup burden,
- safer execution defaults,
- and ordinary-user language.

### Hermes Agent

Hermes Agent represents persistent memory and self-improving skill loops.

Forge should match long-term memory and skill improvement, then exceed it on:

- visible memory palace,
- editable/forgettable memory,
- governed skill lifecycle,
- and user-friendly explanations.

## Differentiation in one line

```text
OpenHuman connects apps.
OpenClaw executes tools.
Hermes learns over time.
Forge should let ordinary users get work done through all of that without learning the software, while keeping memory visible, actions confirmable, and mistakes recoverable.
```

## North Star metric

Forge succeeds when it turns this:

```text
The user spends 30 minutes learning an app or workflow.
```

into this:

```text
The user says one sentence, reviews one clear confirmation card, and gets the task done.
```

## Product rule

Every future feature must answer:

```text
Does this reduce the user's learning cost or time cost?
Does this make the user's work easier to understand, repeat, or recover?
Does this make memory and app usage more helpful without becoming scary?
```

If not, it should wait.
