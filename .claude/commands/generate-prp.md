---
description: Generate PRP from PLANNING.md or proposal file
---

# Generate PRP

## Feature file: $ARGUMENTS

**First, read `.ai/AGENTS.md` for planning workflow directives.**

Generate a complete PRP for general feature implementation with thorough research. Ensure context is passed to the AI agent to enable self-validation and iterative refinement. Read the feature file first to understand what needs to be created, how the examples provided help, and any other considerations.

The AI agent only gets the context you are appending to the PRP and training data. Assume the AI agent has access to the codebase and the same knowledge cutoff as you, so it's important that your research findings are included or referenced in the PRP. The Agent has Websearch capabilities, so pass urls to documentation and examples.

## Work Package Numbering Mode

**IMPORTANT: Before proceeding, prompt the user to select numbering mode:**

```
Work Package numbering mode:

1) Linear Mode
   Files: WP-1_feature.md, WP-2_feature.md, WP-3_feature.md...
   Use for: Single branch, sequential work

2) Parallel Mode
   Files: WP-10_feature.md, WP-20_feature.md, WP-30_feature.md...
   Use for: Git worktrees, parallel development streams
   Each worktree/stream gets its own ID block (10-19, 20-29, 30-39...)

Select mode (1/2):
```

Wait for user response. Use this selection to determine WP-ID assignment strategy throughout the command execution.

- **Linear Mode (1)**: Assign sequential IDs starting from WP-1, WP-2, WP-3, etc.
- **Parallel Mode (2)**: Use block-based IDs (WP-10, WP-20, WP-30) and reference the multi-engineer guidance below

## Two Modes

### Mode 1: PLANNING.md (Initial Build Only)
When invoked with `PLANNING.md`, process all Work Table rows:

**CRITICAL**: After Mode 1 completes, the initial Work Table rows (typically WP-1 through WP-N for MVP) become FROZEN. Never modify or delete these rows. New features are added via Mode 2 below the frozen section.

For each row in the Work Table:
1. **Skip** if PRP instance exists: `.ai/planning/prp/instances/<ID>_*.md` (PRP already generated)
2. **Generate standalone PRP** if proposal exists: `.ai/planning/prp/proposals/<ID>_*.md`
   - Use `.ai/planning/prp/templates/prp_standalone.md` template
   - Extract What/Why/How from proposal
   - Save to `.ai/planning/prp/instances/<ID>_<kebab-title>.md`
3. **Generate bulk PRP** if no proposal exists
   - Use `.ai/planning/prp/templates/prp_bulk.md` template
   - Infer details from Work Table row and PLANNING.md context
   - Save to `.ai/planning/prp/instances/<ID>_<kebab-title>.md`

### Mode 2: Proposal File (Post-MVP Standalone Work)
When invoked with a proposal file path (e.g., `.ai/planning/prp/proposals/WP-10_feature.md`):

1. **Read proposal** - extract ID, Title, What/Why/How
2. **Check Work Table in PLANNING.md** - skip adding row if ID already exists
3. **Auto-add row to PLANNING.md Work Table** with ID and Title from proposal (if not exists)
   - **CRITICAL**: Append new row AFTER the frozen initial build rows
   - Maintain ID sequence (WP-10, WP-11, WP-12, etc.)
   - Format: `| WP-ID | Title | Outcome |`
4. **Generate standalone PRP** using `.ai/planning/prp/templates/prp_standalone.md`
5. **Save** to `.ai/planning/prp/instances/<ID>_<kebab-title>.md`

**Work Table Growth Pattern**:
- Initial build rows (WP-1 to WP-N): FROZEN, never edit
- Post-MVP rows (WP-10+): Growing section, auto-added by Mode 2
- Each new proposal adds exactly one new row to the growing section

### ID Assignment for Parallel Mode
**Only applicable when user selects Parallel Mode (2):**

When working with parallel development streams (e.g., git worktrees), assign ID blocks to avoid conflicts:
- Stream/Worktree A: WP-10 to WP-19
- Stream/Worktree B: WP-20 to WP-29
- Stream/Worktree C: WP-30 to WP-39

Check existing proposals and Work Table to determine next available ID in your assigned block.

**For Linear Mode (1):** Simply use sequential numbering WP-1, WP-2, WP-3, etc.


## Research Process

1. **Codebase Analysis**
   - Search for similar features/patterns in the codebase
   - Identify files to reference in PRP
   - Note existing conventions to follow
   - Check test patterns for validation approach

2. **External Research**
   - Search for similar features/patterns online
   - Library documentation (include specific URLs)
   - Implementation examples (GitHub/StackOverflow/blogs)
   - Best practices and common pitfalls

3. **User Clarification** (if needed)
   - Specific patterns to mirror and where to find them?
   - Integration requirements and where to find them?

## PRP Generation

Using `.ai/planning/prp/templates/prp_bulk.md` for bulk generation or `.ai/planning/prp/templates/prp_standalone.md` for individual items:

### Critical Context to Include and pass to the AI agent as part of the PRP
- **Documentation**: URLs with specific sections
- **Code Examples**: Real snippets from codebase
- **Gotchas**: Library quirks, version issues
- **Patterns**: Existing approaches to follow

### Implementation Blueprint
- Start with pseudocode showing approach
- Reference real files for patterns
- Include error handling strategy
- List tasks to be completed to fulfill the PRP in the order they should be completed

### Validation Gates (Must be Executable)
Replace with project-specific commands. Examples:

**Python:**
```bash
# Syntax/Style
ruff check --fix && mypy .

# Unit Tests
uv run pytest tests/ -v
```

**JavaScript/TypeScript:**
```bash
# Syntax/Style
npm run lint

# Unit Tests
npm test
```

*** CRITICAL AFTER YOU ARE DONE RESEARCHING AND EXPLORING THE CODEBASE BEFORE YOU START WRITING THE PRP ***

*** ULTRATHINK ABOUT THE PRP AND PLAN YOUR APPROACH THEN START WRITING THE PRP ***

## Output
Save as: `.ai/planning/prp/instances/<ID>_<kebab-title>.md`

## Quality Checklist
- [ ] All necessary context included
- [ ] Validation gates are executable by AI
- [ ] References existing patterns
- [ ] Clear implementation path
- [ ] Error handling documented

Score the PRP on a scale of 1-10 (confidence level to succeed in one-pass implementation using claude code)

Remember: The goal is one-pass implementation success through comprehensive context.
