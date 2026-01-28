# IT Access Domain + VerifyingAccessAgent - Demo Guide

## 1. What I Built

### Overview

Simple extension of the tau2-bench framework (AI agent evaluation platform) with a new domain and custom agent to demonstrate end-to-end AI agent development skills.

| Component | Description |
|-----------|-------------|
| **IT Access Domain** | A simulated IT helpdesk environment for testing AI agents on access/permissions management |
| **VerifyingAccessAgent** | A custom agent (bare bones) that automatically verifies its actions worked before responding to users |
| **Evaluation Tasks** | 2 structured tasks with success criteria to measure agent performance |

### Deliverables

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        WHAT I BUILT                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. NEW DOMAIN: it_access (for prod - broaden to "it")                  │
│     ├── Simple Data model (Users, Resources, Permissions)               │
│     ├── 5 API tools for IT operations                                   │
│     ├── Policy document defining agent behavior                         │
│     ├── Mock database                                                   │
│     └── 2 evaluation tasks with success criteria                        │
│                                                                         │
│  2. CUSTOM AGENT: VerifyingAccessAgent                                  │
│     └── Extends baseline LLMAgent with verification loop                │
│         (confirms write operations succeeded before responding)         │
│                                                                         │
│  3. FRAMEWORK INTEGRATION                                               │
│     └── Registry updates to make domain + agent available               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              TAU2-BENCH FRAMEWORK                                       │
│                                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                              SIMULATION ENGINE                                  │    │
│  │                                                                                 │    │
│  │    ┌──────────────┐         ┌──────────────┐         ┌──────────────┐           │    │
│  │    │    USER      │ ──────► │    AGENT     │ ──────► │  ENVIRONMENT │           │    │
│  │    │  SIMULATOR   │ ◄────── │              │ ◄────── │              │           │    │
│  │    └──────────────┘         └──────────────┘         └──────────────┘           │    │
│  │                                    │                        │                   │    │
│  │                                    ▼                        ▼                   │    │
│  │                             ┌──────────────┐         ┌──────────────┐           │    │
│  │                             │     LLM      │         │   TOOLKIT    │           │    │
│  │                             │   (GPT-4)    │         │   (Tools)    │           │    │
│  │                             └──────────────┘         └──────────────┘           │    │
│  │                                                                                 │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                               REGISTRY                                          │    │
│  │                                                                                 │    │
│  │   DOMAINS              AGENTS                    USERS                          │    │
│  │   ├── airline          ├── llm_agent            ├── user_simulator              │    │
│  │   ├── retail           ├── llm_agent_gt         └── dummy_user                  │    │
│  │   ├── telecom          ├── llm_agent_solo                                       │    │
│  │   │                    │                                                        │    │
│  │   │  ╔═══════════════╗ │  ╔════════════════════════╗                            │    │
│  │   └──║  it_access ◄──║─┴──║ verifying_access_agent ║  ◄──   ADDED THESE         │    │
│  │      ╚═══════════════╝    ╚════════════════════════╝                            │    │
│  │                                                                                 │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘


┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                        │
│    ╔═══════════════════════════════════════════════════════════════════════════════╗   │
│    ║                                MY ADDITIONS                                   ║   │
│    ╚═══════════════════════════════════════════════════════════════════════════════╝   │
│                                                                                        │
│    src/tau2/domains/it_access/           data/tau2/domains/it_access/                  │
│    ┌─────────────────────────┐           ┌─────────────────────────┐                   │
│    │ __init__.py             │           │ db.json                 │                   │
│    │ utils.py (paths)        │           │ ├── 3 users             │                   │
│    │ data_model.py           │           │ ├── 3 resources         │                   │
│    │ ├── User                │           │ ├── 2 permissions       │                   │
│    │ ├── Resource            │           │ └── 2 tickets           │                   │
│    │ ├── Permission          │           │                         │                   │
│    │ └── ItAccessDB          │           │ policy.md               │                   │
│    │                         │           │ └── Agent behavior rules│                   │
│    │ tools.py                │           │                         │                   │
│    │ ├── get_user_info       │           │ tasks.json              │                   │
│    │ ├── get_user_permissions│           │ ├── access_grant_task   │                   │
│    │ ├── grant_access        │           │ └── access_revoke_task  │                   │
│    │ ├── revoke_access       │           └─────────────────────────┘                   │
│    │ └── transfer_to_human   │                                                         │
│    │                         │           src/tau2/agent/                               │
│    │ environment.py          │           ┌─────────────────────────┐                   │
│    │ └── get_environment()   │           │ verifying_access_agent. │                   │
│    └─────────────────────────┘           │ py                      │                   │
│                                          │                         │                   │
│                                          │ Extends LLMAgent with:  │                   │
│                                          │ ├── WRITE_TOOLS set     │                   │
│                                          │ ├── _needs_verification │                   │
│                                          │ └── Auto-verify after   │                   │
│                                          │     grant/revoke        │                   │
│                                          └─────────────────────────┘                   │
│                                                                                        │
│    src/tau2/registry.py (MODIFIED)                                                     │                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Agent Behavior Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                    BASELINE LLMAgent vs VerifyingAccessAgent                            │
└─────────────────────────────────────────────────────────────────────────────────────────┘

BASELINE LLMAgent:
──────────────────
User: "Grant me access to the shared drive"
    │
    ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  get_user_info  │ ──► │  grant_access   │ ──► │ "Done! I've     │
│  (user_001)     │     │  (user_001,     │     │  granted you    │
│                 │     │   res_001)      │     │  access."       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                                 NO VERIFICATION


NEW VerifyingAccessAgent:
────────────────────────
User: "Grant me access to the shared drive"
    │
    ▼
┌─────────────────┐     ┌─────────────────┐     ┌───────────────────────┐
│  get_user_info  │ ──► │  grant_access   │ ──► │ get_user_permissions  │
│  (user_001)     │     │  (user_001,     │     │ (user_001)            │
│                 │     │   res_001)      │     │                       │
└─────────────────┘     └─────────────────┘     │     AUTO-INJECTED     │
                                                │     VERIFICATION      │
                                                └───────────────────────┘
                                                        │
                                                        ▼
                                                ┌─────────────────┐
                                                │ "Done! I've     │
                                                │  granted access │
                                                │  and VERIFIED   │
                                                │  it's active."  │
                                                └─────────────────┘
                                                        │
                                                        ▼
                                                     VERIFIED 
```

---

## 4. Skills Demonstrated (Mapped to Sierra Agent PM Role)
- Built a complete domain + custom agent with production-realistic verification pattern and integrated it into eval framework.
- Analyzed IT access management as a use case: Identified entities (users, resources, permissions), actions, and success criteria .
- This doc serves as a V1 Demo Guide that shows achitecture and the reasoning behind decisions.
- This demonstrated prompt engineering, LLM-powered AI agents, tool calling, and technical analysis ability.

---

## 5. Some Demo Commands

```bash
# 1. Verify domain is registered
python -c "from tau2.domains.it_access.environment import get_environment, get_tasks; \
print('Domain:', get_environment().domain_name); \
print('Tasks:', [t.id for t in get_tasks()])"

# 2. Run baseline agent (for comparison)
tau2 run -d it_access --agent llm_agent --agent-llm gpt-4o-mini \
    --num-trials 4 --save-to baseline_demo.json

# 3. Run custom VerifyingAccessAgent
tau2 run -d it_access --agent verifying_access_agent --agent-llm gpt-4o-mini \
    --num-trials 4 --save-to custom_demo.json

# 4. View results in CLI
tau2 view --file data/simulations/baseline_demo.json
tau2 view --file data/simulations/custom_demo.json

# 5. View results in web UI
cd web/leaderboard && npm run dev
# Open http://localhost:5173 -> Visualizer tab
```

---

## 6. Actual Results

| Metric | Baseline (LLMAgent) | Custom (VerifyingAccessAgent) |
|--------|---------------------|-------------------------------|
| `get_user_permissions` calls | 16 | **22** |
| `grant_access` calls | 13 | 13 |
| `revoke_access` calls | 17 | 17 |

**Takeaway:** The custom agent makes more verification calls(22 vs 16), ensuring every write operation is verified.

Note that the policy (`data/tau2/domains/it_access/policy.md`) intentionally does not have verification instructions to demonstrate the difference between the agents. A simpler workaround could be to use the existing agent and prompt engineer the verification step. The baseline agent only verifies sometimes (based on LLM judgment); the VerifyingAccessAgent guarantees verification programmatically.

---

## 7. Why This Matters for Customers and Enterprises

1. **Customer-Facing**: IT access is a real pain point enterprises face
2. **Evaluation Mindset**: Built with measurable success criteria - can quantitatively compare agent approaches
3. **Production Thinking**: Verification pattern - what you'd want in a prod deployed agent

### How to extend this

- NOTE: This is just a demo.

Before putting this in production, I'd
- Add edge cases (manager approval workflows, bulk access requests)
- Integrate with real IAM systems (Okta, Azure AD, etc)
- Add observability (track verification success rates, failure modes)
- Test with adversarial user inputs
- A/B test different agent strategies at scale using the evals to see what really works
- Broaden the domain to be for "IT" generally, rather than just IT access

---

## 8. File Summary

| File | Type | Purpose |
|------|------|---------|
| `src/tau2/domains/it_access/__init__.py` | New | Package marker |
| `src/tau2/domains/it_access/utils.py` | New | Path constants |
| `src/tau2/domains/it_access/data_model.py` | New | Pydantic models for Users, Resources, Permissions |
| `src/tau2/domains/it_access/tools.py` | New | 5 tools with @is_tool decorators |
| `src/tau2/domains/it_access/environment.py` | New | Factory functions for environment + tasks |
| `data/tau2/domains/it_access/db.json` | New | Mock database with test data |
| `data/tau2/domains/it_access/policy.md` | New | Agent behavior policy |
| `data/tau2/domains/it_access/tasks.json` | New | 2 evaluation tasks with success criteria |
| `src/tau2/agent/verifying_access_agent.py` | New | Custom agent with verification loop |
| `src/tau2/registry.py` | Modified | Register domain + agent |
