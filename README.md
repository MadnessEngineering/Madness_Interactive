# Madness Interactive

> *"Confidence isn't a measure of truth — it's a measure of how much damage we're willing to risk."*

Welcome to the **Mad Tinker's Workshop** — a living, interconnected ecosystem of AI-powered tools, agents, and interfaces built to harness the beautiful chaos of a mind with too many ideas.

This is not a collection of isolated side projects. Every piece connects. Cartogomancy scans your code and feeds a 3D city. Omnispindle gives AI agents the tools to think out loud. Inventorium renders it all into something you can walk through. MadnessVR puts on the headset.

---

## The Philosophy

ADHD is being awake to too many possibilities at once. The right tools don't suppress that — they *capture it*. Throw every idea into the machine. Keep your focus where it belongs. Let the agents do the rest.

We write careful code and push ambitious boundaries. Nothing is oversold, but nothing is undersold either.

---

## Ecosystem Map

```
                        ┌─────────────────────────────────────┐
                        │       MADNESS INTERACTIVE           │
                        │     madnessinteractive.cc           │
                        └──────────────┬──────────────────────┘
                                       │
          ┌────────────────────────────┼──────────────────────────┐
          │                            │                           │
   ┌──────▼──────┐             ┌──────▼──────┐            ┌──────▼──────┐
   │ Inventorium │             │  SwarmDesk  │            │  Cogwyrm2   │
   │  React Web  │◄────────────│  3D WebGL   │            │   Mobile    │
   │  Dashboard  │             │  Workspace  │            │  React Nat. │
   └──────┬──────┘             └──────┬──────┘            └──────┬──────┘
          │                           │                           │
          └───────────────────────────┼───────────────────────────┘
                                      │ Auth0
                               ┌──────▼──────┐
                               │ Omnispindle │
                               │  MCP Server │  ← AI agents talk here
                               │  33 tools   │
                               └──────┬──────┘
                                      │ JSON-RPC
                        ┌─────────────┼─────────────┐
                        │             │              │
                 ┌──────▼──────┐  ┌───▼────┐  ┌─────▼──────┐
                 │  REST API   │  │ MongoDB│  │    MQTT    │
                 │ (Express)   │  │  DB    │  │  Realtime  │
                 └─────────────┘  └────────┘  └────────────┘

  CODE ANALYSIS                          NATIVE RUNTIME
  ─────────────                          ──────────────
  ┌─────────────┐                        ┌─────────────┐
  │ Cartogomancy│──► UML JSON ──►────────│  MadnessVR  │
  │  CLI tool   │         │              │ Unity 6 LTS │
  │  5 analyzers│         └──────────────│ Desktop+VR  │
  └─────────────┘                        └─────────────┘
                                               ▲
                              SwarmDesk behavioral reference

  AGENT ORCHESTRATION         AUTOMATION BACKBONE
  ───────────────────         ───────────────────
  ┌──────────────┐            ┌──────────────────┐
  │ Swarmonomicon│            │ EventGhost-Rust  │
  │ Rust agents  │            │ EventGhost (Py)  │
  │ Hive coord.  │            │ Tinker (testing) │
  └──────────────┘            └──────────────────┘

  CONFIG FORGE                GAME INTEGRATIONS
  ────────────                ─────────────────
  ┌─────────────┐             ┌──────────────────┐
  │ Anathesmelt │             │ DevCrystal-      │
  │ Claude hooks│             │ TaskForge        │
  │ & AI config │             │ (Terraria mod)   │
  └─────────────┘             └──────────────────┘
```

---

## Core Projects

### 📊 [Inventorium](projects/common/Inventorium/README.md)
*"Where chaos becomes visible."*

The main lab management interface — a React/Node.js web app running at [madnessinteractive.cc](https://madnessinteractive.cc/). Your command center for todos, projects, lessons learned, and AI-assisted development.

| What it does | Key tech |
|---|---|
| Interactive mindmaps of project/todo relationships | React 18, Three.js, D3 |
| War Room: RPG-style productivity map with procedural terrain | Material-UI, Framer Motion |
| 3D code city visualization (via SwarmDesk, press `0` at /dashboard) | Auth0, MongoDB, PM2 |
| Embedded Claude Code interface for AI development | Zustand, @ai-sdk/google |
| Full CRUD for todos, lessons, projects, audit logs | Node.js/Express REST API |

**Connects to:** Omnispindle (MCP tools), Cartogomancy (code city data), SwarmDesk (3D view), MadnessVR (native runtime)

---

### 🕸️ [Omnispindle](projects/common/Omnispindle/README.md)
*"Genius is the ability to put into effect what is on your mind."*

The MCP server that gives AI agents hands. Every Claude, every agent, every chat interface that needs to interact with your real work talks through Omnispindle.

| What it does | Key tech |
|---|---|
| 33 MCP tools across todos, lessons, projects, admin | Python, FastMCP |
| Three modes: API-first / hybrid (API+Mongo) / local direct | PyPI package |
| Auth0 device flow — zero-config auth for any agent | Auth0 OAuth 2.0 |
| Configurable tool loadouts (minimal=4, basic=10, full=33) | MongoDB, MQTT |
| Full audit logging — every agent action leaves a trail | JSON-RPC stdio |

**Quick install:** `pip install omnispindle`

**Connects to:** Inventorium (REST API backend), Swarmonomicon (agent coordination), every Claude/AI client via MCP

---

### 🔮 [Cartogomancy](projects/common/cartogomancy/README.md)
*"Reading the entrails of your codebase."*

A static analysis CLI that divines the hidden structure of your code and exports it as rich JSON — feeding the 3D code city in Inventorium and MadnessVR.

| What it does | Key tech |
|---|---|
| Git analyzer — commit history, churn rate, bug-fix ratio | Node.js CLI |
| Complexity analyzer — cyclomatic/cognitive threat levels | `@madnessengineering/cartogomancy` |
| Import analyzer — exports, dead code detection | npm package |
| Coverage analyzer — Jest/Istanbul test metrics | OAuth 2.0 device flow upload |
| Redundancy analyzer — duplicate class/logic detection | Supports GitHub URLs |

```bash
npx @madnessengineering/cartogomancy ./your-project
```

**Connects to:** Inventorium (uploads UML JSON via API), MadnessVR (JSON consumed by CodeCityPlanner)

---

### 🎮 [SwarmDesk](projects/common/Inventorium/SwarmDesk/README.md)
*"The 3D workspace you didn't know you needed."*

Embedded inside Inventorium as a submodule. Press `0` at `/dashboard` to enter. Three.js + CSS3D spatial command center with floating panels, chat integration, and building-based code complexity visualization.

| What it does |
|---|
| 3D code city built from Cartogomancy UML output |
| Chat panel with live MCP tool execution |
| Real-time agent management and spawning |
| MQTT-driven UI events |

**Connects to:** Inventorium (host app), Cartogomancy (data source), MadnessVR (behavioral reference)

---

### 🥽 [MadnessVR](projects/common/Inventorium/MadnessVR/README.md)
*"SwarmDesk — but you're inside it."*

Unity 6.3 LTS project nested inside Inventorium. Desktop FPS + full VR via XR Origin/OpenXR. The same 3D code city, procedural workshop environment, and todo management — as a native runtime.

| What it does | Key tech |
|---|---|
| Desktop FPS (WASD + mouselook) and full VR in one build | Unity 6000.3.11f1 |
| Code city from Cartogomancy JSON via CodeCityPlanner | C#, OpenXR |
| Procedural workshop environment | InputSystem |
| Live todo/project data via madnessinteractive.cc/api | MadnessApiClient.cs |

**Color palette:** `#00ff88` (cyan-green) · `#ff6b35` (orange) · `#ff0066` (hot pink)

**Connects to:** Cartogomancy (code city data), Inventorium REST API (live data), SwarmDesk (behavioral reference, no code imports)

---

### 🌟 [Swarmonomicon](projects/common/Swarmonomicon/README.md)
*"The central nervous system of the hive mind."*

Rust-powered multi-agent orchestration. Specialized agents (Git Assistant, Project Init, Haiku, Browser, RL Agent) processing tasks from a MongoDB queue with MQTT real-time coordination.

| What it does | Key tech |
|---|---|
| Priority-based async task processing (Critical/High/Medium/Low) | Rust, tokio |
| Per-agent task queues with semaphore concurrency limiting | MongoDB, MQTT |
| AI-powered task enhancement via GPT-4 batch processing | WebSocket |
| Health monitoring based on task success rates | LM Studio local inference |

**Connects to:** Omnispindle (task source), Inventorium (MQTT events), EventGhost-Rust (event triggers)

---

### 🔥 [Anathesmelt](Anathesmelt/README.md)
*"Where forbidden code is forged."*

The crucible for all Claude AI hook configuration. Manages `claude.md` files across the ecosystem, Makefile integration for setup, and a forge for experimental high-risk AI incantations.

```bash
make setup-claude-hooks  # wire the hooks
```

**Connects to:** Every Claude-powered project in the ecosystem

---

### 📱 [Cogwyrm2](projects/mobile/Cogwyrm2/README.md)
*"The pocket madness command center."*

React Native/Expo mobile companion. Full MCP integration with Omnispindle, session-based AI chat, MQTT agent control, and todo management — all from your phone.

| What it does | Key tech |
|---|---|
| Todo/project/lesson management on mobile | React Native, Expo |
| AI chat with live MCP tool execution | TypeScript, Auth0 |
| MQTT message summoning for agent control | Full Omnispindle integration |

**Connects to:** Omnispindle (MCP tools), Inventorium REST API, MQTT broker

---

### ⚡ [EventGhost-Rust](projects/rust/EventGhost-Rust/README.md)
*"The spirit of automation, reborn in iron."*

Modern Rust rewrite of the EventGhost automation engine. Async performance, cross-platform, Swarmonomicon neural linkage, and a plugin architecture that won't trap you in 2008.

---

### 🐍 [EventGhost (Python)](projects/python/EventGhost/README.md)
*"Ancient magic renewed."*

Python 3.x compatible fork of the classic EventGhost automation tool. Modern UI updates, enhanced plugin system, and the original automation power that started it all.

---

### 🔍 [Tinker](projects/rust/Tinker/README.md)
*"That which peers beyond the veil."*

Rust testing apparatus. Headless and UI manifestations, event capture, temporal manipulation, agent-based testing rituals, and cross-platform coverage.

---

### ⚒️ [DevCrystal-TaskForge](projects/common/DevCrystal-TaskForge/README.md)
*"Your todos as loot drops."*

A Terraria mod where your real development workflow becomes gameplay. Tasks crystallize into enchanted items (priority = rarity). AI agents manifest as NPCs. Projects become buildable sanctuaries. Urgent tasks fall from the sky as meteors.

---

### ⚗️ [madnessscale](projects/common/madnessscale/README.md)
*"The cognitive combustion meter."*

Token usage tracker for AI coding assistants. Measures consumption across Claude Code, Cursor, Gemini CLI, OpenCode, Codex, Amp — generates reports so you know exactly how much brain you're burning.

---

## Full Project Directory

```
madness_interactive/
├── Anathesmelt/                    # Claude hook forge (submodule)
├── projects/
│   ├── common/                     # Core ecosystem projects
│   │   ├── Inventorium/            # 🟢 Main dashboard (+ SwarmDesk, MadnessVR nested)
│   │   ├── Omnispindle/            # 🟢 MCP server
│   │   ├── cartogomancy/           # 🟢 Code analysis CLI
│   │   ├── Swarmonomicon/          # 🟡 Rust agent orchestration
│   │   ├── Cogwyrm/                # 🟡 Mobile app (v1)
│   │   ├── MechaFiberAtelier/      # 🔵 Experimental atelier systems
│   │   ├── DevCrystal-TaskForge/   # 🟡 Terraria mod
│   │   ├── madnessscale/           # 🟡 Token usage tracker
│   │   ├── Whispermind_Conduit/    # 🔵 Cross-system neural linkage
│   │   ├── Obnubilare/             # 🔵 Experimental
│   │   ├── mcp_cli_auth_tool/      # 🔵 MCP auth utility
│   │   └── Omnispindle-cli-bridge/ # 🔵 CLI-to-MCP bridge (Ruby)
│   ├── python/                     # Python projects (16 checked out)
│   │   ├── EventGhost/             # 🟢 Automation engine (Python 3.x)
│   │   ├── Spindlewrit/            # Documentation generation
│   │   ├── dvtTestKit/             # Dev testing utilities
│   │   ├── LegoScry/               # LEGO/code interaction CLI
│   │   ├── MqttLogger/             # MQTT message logging
│   │   ├── mqtt-ai-analyzer/       # AI-powered MQTT analysis
│   │   ├── simple-mqtt-server-agent/
│   │   ├── SeleniumPageUtilities/
│   │   ├── mcp-auth-cli/           # CLI auth utility
│   │   ├── mcp-personal-jira/      # MCP Jira integration
│   │   ├── local-ai/               # Local AI experiments
│   │   ├── verified_madness/       # Verification framework
│   │   ├── wyrmwatch/              # System monitoring
│   │   └── fastmcp-balena-cli/     # balena + FastMCP integration
│   ├── rust/
│   │   ├── EventGhost-Rust/        # 🟡 Automation engine rewrite
│   │   └── Tinker/                 # 🟡 Testing apparatus
│   ├── mobile/
│   │   ├── Cogwyrm2/               # 🟡 Mobile app (current)
│   │   └── MQTTCommander/          # 🔵 MQTT device control
│   ├── typescript/
│   │   ├── RaidShadowLegendsButItsMCP/  # Game-AI agent demo
│   │   └── agorventorium/          # Analytics/visualization
│   ├── lua/
│   │   └── LGS_script_template/    # Logitech Gaming Software
│   ├── powershell/
│   │   └── WinSystemSnapshot/      # Windows system capture
│   ├── tasker/                     # MadTaskerTinkerbox modules
│   │   ├── AnathemaHexVault/
│   │   ├── ContextOfficium/
│   │   ├── EntropyVector/
│   │   ├── Fragmentarium/
│   │   ├── InvocationTome/
│   │   ├── Ludomancery/
│   │   ├── PhilosophersAmpoule/
│   │   ├── RunedManifold/
│   │   └── Verbatex/
│   ├── OS/                         # Host/platform configs
│   │   ├── barrier-configs/
│   │   └── windows/
│   ├── archive/                    # Archived/legacy projects
│   │   ├── Saws-flow/
│   │   ├── evernance/
│   │   └── saws-flow-clean/
│   ├── opencode/
│   │   └── Whispermind_Conduit/
│   ├── personal/
│   │   └── conc/
│   └── nodeJS/                     # Reserved for future Node.js projects
├── docs/                           # Documentation & cursor chat history
├── scripts/                        # Utility + git hook scripts
├── examples/                       # Reference implementations
└── Makefile                        # Monorepo task runner

Status: 🟢 Production  🟡 Active Development  🔵 Integration/Experimental
```

---

## How the Pieces Connect

```
YOU have an idea
      │
      ▼
Captured via Omnispindle MCP tools
(Claude, Cogwyrm2, Inventorium chat)
      │
      ▼
Stored in MongoDB, visible in Inventorium dashboard
      │
      ├──► Swarmonomicon agents pick up tasks, coordinate via MQTT
      │
      ├──► Cartogomancy analyzes the affected codebase
      │         └──► UML JSON → SwarmDesk 3D city → MadnessVR
      │
      └──► DevCrystal-TaskForge: the task falls from the sky in Terraria
```

---

## Getting Started

**Clone with submodules:**
```bash
git clone --recurse-submodules https://github.com/madnessengineering/madness_interactive.git
cd madness_interactive
```

**Or init submodules after cloning:**
```bash
git submodule update --init --recursive
```

**Jump into a specific project:**
```bash
# The main web dashboard
cd projects/common/Inventorium && npm install && npm run dev

# The MCP server (for AI agent integration)
pip install omnispindle
omnispindle --help

# Code analysis CLI
npx @madnessengineering/cartogomancy ./your-project
```

**Wire up Claude hooks:**
```bash
make setup-claude-hooks
```

See each project's own README for full setup instructions.

---

## Deployment

Production runs at **[madnessinteractive.cc](https://madnessinteractive.cc/)** on AWS EC2:
- **Nginx** — reverse proxy + SSL (Let's Encrypt)
- **PM2** — Node.js process management
- **MongoDB** — per-user isolated collections via Auth0 `sub`
- **Auth0** — authentication across web, mobile, and MCP clients
- **Git hooks** — auto-deploy on push

---

## Contributing

Each project has its own guidelines. The meta-rule: read the code first, ask before "fixing" anything that touches multiple systems — connections run deeper than they look.

---

## License

Each project may carry different terms. Check the individual project directory.

---

*"The difference between madness and genius is measured only by success."* — Unknown Mad Scientist
