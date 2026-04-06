---
source_id: web_mcp_microsoft_agent_factory
source_type: web
url: https://azure.microsoft.com/en-us/blog/agent-factory-designing-the-open-agentic-web-stack/
title: Agent Factory: Designing the open agentic web stack | Microsoft Azure Blog
extracted_at: 2026-04-06 10:26:19
---

# Agent Factory: Designing the open agentic web stack | Microsoft Azure Blog

This blog is a wrap-up post in a blog series called Agent Factory which shares best practices, design patterns, and tools to help guide you through adopting and building agentic AI.
The rise of AI agents—autonomous software entities acting on behalf of users and organizations—marks a transformative moment for enterprise technology. But as we’ve explored throughout this blog series, building effective agents is about more than just code. It requires a repeatable blueprint, spanning use case design, developer tooling, observability, integrations, and governance.
Throughout this series, we’ve walked through the journey of building enterprise-grade agents: from early use cases and design patterns to the tools and developer workflows needed to move from prototype to production, to the importance of observability, interoperability, and open standards, and finally the governance and security principles required to deploy agents responsibly.
Now, as we conclude the series, we zoom out to the bigger picture: the agentic web stack. Much like HTTP and TCP/IP standardized the internet, this stack provides the common services and protocols needed to make multi-agent ecosystems secure, scalable, and interoperable across organizational boundaries.
Blueprint: 8 essential components and services
A robust agentic web stack is not one technology but a composition of services that together provide the foundation for open, secure, and enterprise-grade multi-agent systems. Here’s what it takes—and how Azure AI Foundry is making it real.
1. Communication protocol service
Agents need a shared “language” to exchange messages, requests, and structured data. Without it, collaboration breaks down into isolated silos. Standards like Model Context Protocol (MCP) and Agent-to-Agent (A2A) provide this foundation, ensuring agents can negotiate, coordinate, and cooperate—regardless of who built them or where they’re hosted. In Azure AI Foundry, A2A support enables not only intra-organization workflows but also cross-boundary collaboration, where supply chain partners or business ecosystems can securely exchange actions through a common protocol.
2. Discovery registry service
Just as the web needed directories and search engines, agents need a way to be found and reused. The Catalog serves as the listing of assets—a curated collection of agents, tools, and applications that can be discovered and composed into new solutions. The Registry, by contrast, tracks the deployed instances of those assets—the live agentic app instances running across providers, with their endpoints, health, and status. Together, the Catalog and Registry bridge the gap between what’s available and what’s active, enabling developers to publish once, discover broadly, and reliably orchestrate workflows against running systems.
3. Identity and trust management service
Trust is the lifeblood of the agentic web. Every agent must carry a verifiable identity, enforced through standards like OIDC (OpenID Connect) and JWT (JSON Web Token), and tied into enterprise systems like Microsoft Entra ID. In Azure AI Foundry, identity is not an afterthought—it’s the control plane. This enables fine-grained role-based access, ensures that only authorized actors participate in workflows, and provides auditable accountability for every action an agent takes. Combined with encrypted channels, this identity-first model enforces a zero-trust security posture across the agentic stack.
4. Tool invocation and integration service
No agent can succeed in isolation; value comes when agents can connect with data, APIs, and enterprise systems. The Model Context Protocol (MCP) provides a vendor-neutral standard for exposing tools in a way that any compliant agent can invoke. In Azure AI Foundry, MCP integration is deeply embedded, so developers can register enterprise APIs once and instantly make them available to multiple agents—whether they’re built on Microsoft’s agent frameworks like Semantic Kernel and AutoGen, LangGraph, or third-party SDKs. This eliminates bespoke integrations and allows enterprises to compose workflows from best-in-class components.
5. Orchestration service
Single agents can handle discrete tasks, but the real breakthroughs come from multi-agent orchestration: teams of agents collaborating across multi-step, distributed processes. Azure AI Foundry delivers this through a unified framework that brings together Semantic Kernel and AutoGen—and extends it with multi-agent workflow orchestration inside Azure AI Foundry Agent Service. These workflows manage dependencies, allocate resources, and resolve conflicts, enabling enterprise-scale use cases such as financial transaction processing or IT incident response.
6. Telemetry and observability service
As we covered in Part 3, observability is non-negotiable for reliable agents. Azure AI Foundry extends OpenTelemetry with agent-aware instrumentation—tracing conversations, capturing performance data, and surfacing anomalies in real time. This makes agent behavior explainable and debuggable, while also serving governance needs: every decision and action is logged, auditable, and tied back to identity. For enterprises, this is the bedrock of trust, compliance, and continuous improvement.
7. Memory service
Agents without memory are limited to stateless interactions; agents with memory become adaptive, contextual, and human-like in their continuity. Azure AI Foundry supports both short-term session memory and long-term enterprise knowledge integration. Imagine a customer support agent that recalls prior interactions across channels, or a supply chain agent that tracks historical disruptions to improve future decisions. With memory, agents evolve from transactional helpers into strategic partners that learn and adapt over time.
8. Evaluation and governance service
Finally, no stack is complete without governance. This includes continuous evaluation, policy enforcement, ethical safeguards, and regulatory compliance. In Azure AI Foundry, governance hooks are built into orchestration, observability, and identity services—enabling enterprises to block unsafe actions, enforce approvals for sensitive workflows, and generate compliance-ready audit trails. This ensures organizations don’t just innovate fast, but innovate responsibly.
Strategic use cases and business value
The agentic web stack is not theoretical; it unlocks concrete enterprise value.
- End-to-end business process automation: Imagine a procure-to-pay workflow where one agent negotiates with suppliers, another verifies compliance, a third triggers payment, and a fourth updates ERP records. With Azure AI Foundry’s orchestration and discovery registry, these agents collaborate seamlessly, cutting manual intervention and cycle times from weeks to hours.
- Cross-organization supply chain synchronization: In global supply chains, delays often come from mismatched systems and data. With A2A and discovery services, a logistics agent from one company can securely interoperate with a customs agent from another—both governed by identity and observability. The result: faster border clearance, lower costs, and higher resilience.
- Knowledge worker augmentation: Agents built with Azure AI Foundry can take on repetitive but high-value tasks—scheduling, research, first-draft writing—while humans focus on creativity and judgment. The memory integration ensures continuity: a legal research agent remembers prior cases analyzed, while a marketing agent recalls brand guidelines across campaigns.
- Complex IT operations: When outages occur, every second counts. Multi-agent workflows in Azure AI Foundry can detect anomalies, route alerts, execute diagnostics, and propose mitigations across distributed environments. Observability ensures root causes are transparent, while governance enforces that corrective actions comply with policy.
- Memory-driven customer journeys: A customer support agent that recalls a prior complaint, a personalization agent that adapts recommendations, a compliance agent that enforces rules—working together, these create adaptive, context-rich interactions. The outcome is not just efficiency but stronger relationships and trust.
Preparing for the agentic era
For organizations, the path forward is as much about strategy and culture as it is about technology:
- Start with open standards: Adopt MCP and A2A from the outset, even in pilots, to avoid future rework and ensure interoperability.
- Invest in foundations: Identity, observability, and memory are not optional; they are the pillars that differentiate ad hoc automations from enterprise-grade systems.
- Operationalize governance: Define policies now and embed them into workflows through Azure AI Foundry’s governance services, so oversight scales with adoption.
- Engage the ecosystem: Participate in open-source and standards communities, influence their direction, and ensure your organization’s voice is heard.
- Prepare your workforce: Train employees not just to use agents, but to collaborate with them, supervise them, and improve them over time.
Leaders who act on these imperatives will not only adopt agentic AI but shape its trajectory in their industries.
Shaping the future together at Ignite 2025
The Agent Factory series has laid out the foundations: design patterns, developer tools, observability practices, interoperability standards, and governance principles. The agentic web stack brings these threads together into a cohesive vision: an open, secure, and interoperable ecosystem where agents can scale across organizational boundaries.
Azure AI Foundry is your platform to make this vision real—unifying frameworks, standards, and enterprise capabilities so organizations can accelerate value while staying in control.
At Ignite 2025, we’ll showcase the next wave of innovations—from multi-agent orchestration to deeper integrations with enterprise apps, data, and security systems. Join us to see how Azure AI Foundry is not only enabling enterprises to adopt agentic AI but also shaping the agent-driven future of business.
Did you miss these posts in the series?
- The new era of agentic AI—common use cases and design patterns
- Building your first AI agent with the tools to deliver real-world outcomes
- Top 5 agent observability best practices for reliable AI
- From prototype to production—developer tools and rapid agent development
- Connecting agents, apps, and data with new open standards like MCP and A2A
- Creating a blueprint for safe and secure AI agents
