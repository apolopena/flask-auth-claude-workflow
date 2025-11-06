# Flask Auth Claude Workflow

A complete Flask authentication system demonstrating Context Engineering workflow with Claude Code. This repository serves as both a **reference implementation** showing how to build production-ready applications using PRP-driven development, and a **ready-to-use starter template** for your own projects.

## 🎯 What This Repository Demonstrates

This is a **working example** of building a real application using:

- **Context Engineering**: PRPs (Product Requirements Prompts) that guide AI through complex implementations
- **PRP-Driven Development**: Planning → Context → Execution → Validation cycle
- **Multi-Agent Workflow**: Optional observability system to monitor AI agent behavior in real-time
- **Iterative Development**: Not one-shot - shows the reality of feedback cycles and refinement

**The Result**: A production-ready Flask authentication system (~1,700 lines of code, 46 passing tests) built from structured AI collaboration. **All of this can be done in about 30 minutes** - that's how powerful the AI workflow can be.

## 📁 Repository Structure

This repository contains **two main sections**:

### 1. Development Workspace (Root Directory)
The complete Context Engineering setup infrastructure - **use as a clean slate starter** to build from scratch or practice recreating the final result:

```
flask-auth-claude-workflow/
├── .ai/                       # Planning & Context System
│   ├── planning/
│   │   ├── prd/               # Product Requirements (empty - for reference)
│   │   ├── prp/templates/     # PRP generation templates
│   │   └── templates/         # Planning templates
│   └── scratch/               # Working files (empty with .gitkeep)
│
├── .claude/                   # Claude Code Integration
│   ├── commands/              # Slash commands (/generate-prp, /execute-prp, etc.)
│   ├── agents/                # Specialized agents (Jerry, Mark, Pedro, Atlas, Bixby)
│   ├── hooks/                 # Observability hooks (optional)
│   └── settings.json          # Claude Code configuration
│
├── .github/                   # GitHub Actions (optional - enables AI provenance on PRs/issues)
│   └── workflows/
│       └── gh-dispatch-ai.yml # Provenance workflow dispatched by Mark agent
│
├── scripts/                   # Observability control wrappers (optional)
├── CLAUDE.md                  # Project instructions for Claude Code
└── initial-plan.md            # The original seed (WP-001 to WP-003)
```

### 2. Final Result (Self-Contained Implementation)
A complete, ready-to-use Flask auth system in `final-result/` - **use as a starter to build upon** or study the complete implementation:

```
final-result/
├── app.py                     # Flask application entry point
├── config.py                  # Environment-based configuration
├── models.py                  # SQLAlchemy User model
├── routes/
│   ├── auth.py                # 8 API endpoints (register, login, password reset, etc.)
│   └── frontend.py            # 8 web pages
├── utils/                     # Token generation + email sending
├── templates/                 # 10 Jinja2 HTML templates (web UI + emails)
├── static/                    # CSS (Pico.css) + JavaScript
├── tests/                     # 4 comprehensive test suites (46 tests)
├── requirements.txt           # Python dependencies
│
├── .ai/                       # Full planning system (same as root)
├── .claude/                   # Full Claude Code setup (same as root)
├── .github/                   # GitHub Actions (optional - enables AI provenance)
├── scripts/                   # Observability wrappers (optional)
└── README.md                  # Instructions for using as starter
```

## 🚀 How to Use This Repository

### Option 1: Study the Workflow (Recommended First Step)

Explore how the system was built:

1. **Read the planning artifacts** (in `final-result/`):
   - `final-result/.ai/planning/prd/PLANNING.md` - The Work Table with all 5 work packages
   - `final-result/.ai/planning/prp/instances/WP-001_*.md` through `WP-005_*.md` - The generated PRPs

2. **See the implementation**:
   - `final-result/` - Complete working Flask app
   - `final-result/.ai/scratch/` - Ancillary documents generated during development (test plans, security notes, architecture docs)

3. **Understand the workflow**:
   - Initial seed: `initial-plan.md` (in project root - the starting point)
   - Converted to: `final-result/.ai/planning/prd/PLANNING.md` (via `/convert-planning initial-plan.md`)
   - Generated PRPs: `final-result/.ai/planning/prp/instances/` (via `/generate-prp`)
   - Post-MVP proposals: `final-result/.ai/planning/prp/proposals/` (WP-004, WP-005)
   - Execution tracking: `final-result/.ai/scratch/TASKS.md` (the complete implementation journey)

### Option 2: Use as a Starter Template

Copy the `final-result/` directory to start your own project:

```bash
# Copy final-result as your new project
cp -r final-result ~/my-new-auth-project
cd ~/my-new-auth-project

# Initialize as new git repository
git init
git add .
git commit -m "Initial commit from Flask auth starter"

# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.sample .env  # Create this file with your settings
nano .env             # Add your SECRET_KEY, JWT_SECRET_KEY, email config

# Start MailHog (Email Testing)
```bash
docker run -d \
  -p 1025:1025 -p 8025:8025 \
  --name mailhog \
  mailhog/mailhog
```

Set these in your `.env` for local email capture:
```ini
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USE_TLS=False
MAIL_USE_SSL=False
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=test@example.com
```

MailHog UI: http://localhost:8025

# Run the application
python3 app.py
```

The Flask app will be available at `http://localhost:5000`

### Option 3: Use the Context Engineering System

Adopt just the planning and workflow tools for your own project:

```bash
# Copy the Context Engineering infrastructure
mkdir my-project
cp -r .ai my-project/
cp -r .claude my-project/
cp CLAUDE.md my-project/

# Optional: Copy observability wrappers
cp -r scripts my-project/
```

Then follow the complete workflow described in the [🎓 Learning the Workflow](#-learning-the-workflow) section below, which covers:
1. **Agent Priming** - Get your agent up to speed
2. **Initial Build** - Convert seed plan to PLANNING.md, generate PRPs, execute features
3. **Post-MVP Features** - Add new features using proposals

## 🔍 What's Implemented

### Complete Authentication System

**WP-001: User Registration** (8 tests)
- Email/password registration with validation
- Werkzeug password hashing (pbkdf2:sha256)
- Duplicate email prevention

**WP-002: User Login** (14 tests)
- JWT authentication (15-min access, 30-day refresh tokens)
- Rate limiting (5 attempts/min)
- Logout and token refresh endpoints

**WP-003: Password Reset** (15 tests)
- Email-based password reset flow
- Time-limited tokens (1-hour expiration)
- Flask-Mail email delivery
- Rate limiting (3 requests/hour)

**WP-004: Web Frontend** (8 pages)
- Full HTML/CSS/JavaScript UI using Pico.css
- Landing, register, login, dashboard, password reset, email verification
- JWT token management in localStorage
- Responsive design

**WP-005: Email Verification** (9 tests)
- Email verification required before login
- 24-hour verification tokens
- Resend verification endpoint
- Rate limiting (3 requests/hour)

### Tech Stack

- **Backend**: Flask 3.0+, SQLAlchemy, Flask-JWT-Extended
- **Frontend**: Vanilla JavaScript, Pico.css (~10KB)
- **Database**: SQLite (dev), PostgreSQL/MySQL ready
- **Email**: Flask-Mail with SMTP
- **Testing**: pytest with 46 passing tests
- **Security**: Password hashing, JWT tokens, rate limiting, itsdangerous tokens

## 🔭 Multi-Agent Observability (Optional)

This repository includes **pre-configured observability hooks** that are **disabled by default**. These hooks provide real-time monitoring of Claude Code agent behavior during development.

### Why It's Optional

The observability system:
- Requires an external server and dashboard (from the multi-agent-workflow repo)
- Is **not needed** to use the Flask auth code or Context Engineering workflow
- Adds development overhead but provides valuable insights during active AI-assisted development

### Option A: Skip Observability (Recommended for Getting Started)

The system works perfectly without observability:
1. The hooks fail gracefully if the server isn't running
2. All Context Engineering features work (PRPs, agents, commands)
3. You can build applications using the workflow without monitoring

**To completely disable**:
- Edit `.claude/settings.json`
- Remove the `"hooks"` section
- Save and restart Claude Code

### Option B: Enable Observability

To use the full real-time monitoring system:

1. **Clone the multi-agent-workflow repository**:
   ```bash
   git clone https://github.com/apolopena/multi-agent-workflow ~/multi-agent-workflow
   ```

2. **Fix hard-coded paths**:
   ```bash
   ./scripts/observability-fix-paths.sh
   ```
   This updates `.claude/.observability-config` with your actual paths.

3. **Follow setup instructions** from the [multi-agent-workflow repository](https://github.com/apolopena/multi-agent-workflow)

4. **Enable and start**:
   ```bash
   ./scripts/observability-enable.sh
   ./scripts/observability-start.sh
   ```

5. **Restart Claude Code** to load the updated configuration

The observability dashboard will be available at `http://localhost:5173` with the server running on port 4000.

**Note:** When enabled, the observability hooks will create a `logs/` directory in your project root (gitignored by default).

## 🎓 Learning the Workflow

### Understanding PRPs

**PRPs (Product Requirements Prompts)** are context-engineered prompts that give AI agents comprehensive information about:
- What to build
- How it fits into the existing codebase
- Dependencies and patterns to follow
- Validation gates and success criteria

Read the generated PRPs in `final-result/.ai/planning/prp/instances/` to see examples.

### 1. Agent Priming (Start Here)

When starting a fresh agent session (recommended after every few features), the agent needs context about the codebase and current state.

**Priming Options:**

- **`/prime-full`** - Comprehensive priming using Atlas agent to generate context and architecture files (time-consuming but thorough)
  - **Creates:** `.ai/scratch/context-primer.md` (current working state, recent changes, progress)
  - **Creates:** `.ai/scratch/arch-primer.md` (architecture overview, patterns, conventions)

- **`/prime-quick`** - Fast priming from existing context files (requires prior `/prime-full` or manual context generation)
  - **Reads:** Existing `.ai/scratch/context-primer.md` and `.ai/scratch/arch-primer.md`
  - **Provides:** Quick synthesis of current state

- **Manual Atlas dispatch** - Simply ask the agent to "dispatch Atlas" for the same comprehensive priming as `/prime-full`

- **Manual combination** - Run `/generate-arch` and `/generate-context` separately for more control

**Additional context:**
- **Manually prompt the agent to read `.ai/scratch/TASKS.md`** to understand completed work (no command does this automatically)

**When to prime:**
- Starting a new agent session
- After implementing several features
- When the agent needs updated context about recent changes

**Recommendation:** Use `/prime-full` or dispatch Atlas for initial sessions or after major changes, `/prime-quick` for quick refreshers between features. Combine any of these with reading `TASKS.md` for maximum accuracy during implementation.

---

### 2. Initial Build (Bulk PRPs)

**Step 1: Start with high-level seed plan**

This project was built from `initial-plan.md` in the project root. To use this system for other projects, copy this repository, remove git history, reinitialize, and upload to a new repo.

**Step 2: Convert to structured PLANNING.md**
```bash
/convert-planning initial-plan.md
# Creates: .ai/planning/prd/PLANNING.md with Work Table (WP-1 to WP-N)
# Choose Linear or Parallel mode when prompted
```

**Step 3: Generate bulk PRPs**
```bash
/generate-prp .ai/planning/prd/PLANNING.md
# Generates comprehensive PRPs for all rows
# Creates: .ai/planning/prp/instances/WP-01_*.md, WP-02_*.md, etc.
# Initial rows become FROZEN
# Idempotent: Skips rows with existing PRPs
```

**Step 4: Execute PRPs**
```bash
/execute-prp .ai/planning/prp/instances/WP-01_feature.md
# Implement, validate, update TASKS.md
```

---

### 3. Post-MVP Features (Standalone PRPs)

**Method 1: AI-assisted (Recommended)**

Simply ask: *"Create a proposal using the planning system for [feature description]"*

The AI will:
- Read the proposal_standalone.md template
- Create and fill out the proposal file with What/Why/How
- Either run `/generate-prp` automatically or prompt you to run it

**Method 2: Manual**
1. Copy `.ai/planning/prp/templates/proposal_standalone.md`
2. Fill out What/Why/How sections
3. Save as `.ai/planning/prp/proposals/WP-XX_feature-name.md`
4. Run `/generate-prp .ai/planning/prp/proposals/WP-XX_feature-name.md`
5. Run `/execute-prp .ai/planning/prp/instances/WP-XX_feature-name.md`

**Idempotent**: Skips adding row if ID already exists in Work Table

### Work Table Organization

**ID Block Rules**:
- **WP-1 to WP-N**: Initial build rows, FROZEN after Phase 1
- **WP-10+**: Post-MVP rows, growing dynamically via Phase 2
- **Never modify or delete** frozen rows

**Multi-Engineer Workflow**:
- Engineer A: WP-10 to WP-19
- Engineer B: WP-20 to WP-29
- Engineer C: WP-30 to WP-39

Check existing proposals and Work Table for next available ID in your block.

### Iteration Reality

This project was **not one-shot**. The PRPs provided excellent guidance, but:
- Manual testing revealed edge cases
- Feedback cycles were necessary
- Validation gates caught issues
- Refinement improved quality

The `final-result/.ai/scratch/TASKS.md` file documents the actual journey.

## 📦 Mixing and Matching Context Engineering Systems

The Context Engineering infrastructure consists of three systems that can be mixed and matched:

### 1. Planning System
Structured workflow for PRP-driven development including `.ai/planning/`, planning commands, and Atlas agent.

### 2. Observability System
Real-time monitoring with hooks, scripts, Jerry agent, and multi-agent-workflow server.

### 3. Provenance System
AI attribution via `.github/workflows/`, git-ai.sh script, and Mark agent.

**Note:** These systems are interconnected through commands, agents, and the `.ai/` directory structure. Use your judgment when adapting pieces for your workflow. The complete systems work as-is.

## 🔧 Git Helper with AI Attribution (Optional)

This repository includes `scripts/git-ai.sh` - a git wrapper that adds AI attribution and handles SSH authentication for automated git operations. This is part of the opinionated workflow for tracking AI contributions with provenance.

**Using the Git Helper:**
```bash
# Instead of: git commit -m "message"
./scripts/git-ai.sh commit -m "message"

# Instead of: git push
./scripts/git-ai.sh push
```

**SSH Key Setup Required:**

The git helper requires SSH key caching to function without password prompts. You can set this up however you prefer, or follow our guide:

📖 **[SSH Key Management Guide](docs/SSH_SETUP.md)** - Covers keychain, ssh-agent, and platform-specific setup options

**GitHub Operations with Provenance:**

For GitHub operations (PRs, issues, comments) with full provenance tracking via the Mark agent:

📖 **[GitHub Provenance Setup](https://github.com/apolopena/github-workflows)** - Complete workflow setup for AI attribution on GitHub operations

**Completely Optional:**

You can use standard git and GitHub commands directly if you prefer. The attribution and provenance system is part of the opinionated workflow but not required to use the Context Engineering system or Flask auth code.

## 🔗 Related Repositories

**[multi-agent-workflow](https://github.com/apolopena/multi-agent-workflow)** - The complete workflow system with observability server, dashboard, and Context Engineering infrastructure

> **Note**: The multi-agent-workflow repository is a fork and extension of [claude-code-hooks-multi-agent-observability](https://github.com/disler/claude-code-hooks-multi-agent-observability) by [@disler](https://github.com/disler). The original project provided the foundational observability system. The fork extends it with automated GitHub operations, AI agents (Jerry, Mark, Pedro, Atlas, Bixby), git helper tooling, Context Engineering, and enhanced summary capabilities.

This flask-auth-claude-workflow repository uses the Context Engineering system from multi-agent-workflow as a reference implementation.

## 🛠️ System Requirements

### For Running the Flask App
- Python 3.10+
- pip (Python package manager)
- SQLite (included with Python)

### For Context Engineering Workflow
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) - Anthropic's official CLI
- The `.claude/` configuration (included)

### For Observability (Optional)
- [Astral uv](https://docs.astral.sh/uv/) - Python package manager for hooks
- [Bun](https://bun.sh/) or npm - JavaScript runtime for server/dashboard
- [jq](https://jqlang.github.io/jq/) - JSON processor
- Ports 4000 and 5173 available
- multi-agent-workflow repository cloned

## 📝 Key Files to Explore

**Planning & Context**:
- `initial-plan.md` - The original seed that started it all (in root)
- `final-result/.ai/planning/prd/PLANNING.md` - The complete Work Table (created from initial-plan.md via `/convert-planning`)
- `final-result/.ai/planning/prp/instances/WP-*.md` - All 5 generated PRPs
- `final-result/.ai/scratch/TASKS.md` - Implementation journey

**Implementation**:
- `final-result/app.py` - Flask app entry point
- `final-result/routes/auth.py` - All authentication endpoints
- `final-result/tests/` - Comprehensive test suites

**Configuration**:
- `CLAUDE.md` - Instructions for Claude Code
- `.claude/settings.json` - Claude Code configuration
- `.claude/commands/` - Slash commands for workflow

## 🤝 Contributing

This is a reference implementation. Feel free to:
- Use it as a template for your projects
- Adapt the workflow to your needs
- Share improvements and feedback
- Create issues for questions or suggestions

## 📄 License

[Add your license here]

## 🙏 Credits

- Observability system foundation: [@disler](https://github.com/disler)'s [claude-code-hooks-multi-agent-observability](https://github.com/disler/claude-code-hooks-multi-agent-observability)
- Context Engineering extensions and this reference implementation: Flask Auth Claude Workflow project

---

**Ready to start building?** Copy `final-result/` and adapt it for your needs, or study the planning artifacts to learn the Context Engineering workflow!
