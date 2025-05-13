# PROJECT INTERCONNECTIONS PROMPT

## Overview
This prompt enhances your understanding of the complex interconnections between different projects in the ecosystem. Use this knowledge to make informed decisions about code changes, task management, and resource allocation.

## Core Project Relationships

### Omnispindle ↔ Swarmonomicon
- **Data Flow:** Task status updates, workflow events, user assignments
- **Integration Points:** 
  - Shared MongoDB collections for tasks
  - MQTT message bus for event notifications
  - Status transition webhooks
- **Dependencies:** 
  - Status changes in Omnispindle trigger worker actions in Swarmonomicon
  - Swarmonomicon processes tasks and updates their status in shared database
  - Both rely on consistent status taxonomy (reviewed, rejected, processed, pending-complete, pending-cluster)

### Madness Interactive ↔ Docker Implementation
- **Data Flow:** Container configurations, build artifacts, deployment manifests
- **Integration Points:**
  - Shared compose files
  - Container orchestration manifests
  - Build pipeline configurations
- **Dependencies:**
  - Docker Implementation provides containerization for Madness Interactive components
  - Cross-container networking configuration shared between projects
  - Deployment procedures documented in both repositories

### Hammerspoon ↔ EventGhost
- **Data Flow:** Remote control commands, UI interaction events
- **Integration Points:**
  - Shared event bus for cross-platform operations
  - Compatible UI component structure
  - Synchronized navigation commands
- **Dependencies:**
  - EventGhost (Windows) and Hammerspoon (Mac) implement platform-specific versions of same functionality
  - Shared configuration format for UI component definitions
  - Common protocol for remote device interaction

### MCP Integration ↔ Jira/Todo System
- **Data Flow:** Task metadata, status updates, project assignments
- **Integration Points:**
  - Bidirectional sync between Todo system and Jira
  - Shared field mappings
  - Webhook event handlers
  - **Jira ticket references (ABD-###)** in Todo items
- **Dependencies:**
  - Status changes propagate between systems
  - Project assignments must be consistent across platforms
  - Potential circular update conflicts require resolution strategy
  - **Todo items reference Jira tickets with ABD-### format**
  - **Clicking Todo items can deep-link to corresponding Jira tickets**

## Cross-Cutting Concerns

### Authentication & Authorization
- Common authentication model shared across:
  - Omnispindle dashboard
  - Swarmonomicon admin interface
  - MCP Integration endpoints
  - Docker management interface

### Deployment Pipeline
- Shared CI/CD infrastructure touches all projects:
  - Build server configurations
  - Testing environments
  - Staging deployment procedures
  - Production release protocols

### Monitoring & Telemetry
- Unified monitoring approach impacts:
  - Application performance metrics
  - Cross-service transaction tracing
  - Error aggregation and alerting
  - Usage analytics

## Conflict Resolution Guidelines

When making changes that affect multiple interconnected projects:

1. **Identify all affected systems** by tracing the relationship graph outlined above
2. **Plan synchronized deployments** when changes break compatibility
3. **Update integration tests** that verify cross-project functionality
4. **Document dependency changes** in all affected projects
5. **Consider feature flags** to enable gradual rollout of cross-project features

## Development Best Practices

1. **Coordinate API changes** with maintainers of dependent projects
2. **Version integration points** explicitly in documentation and code
3. **Test cross-project workflows** end-to-end before deployment
4. **Maintain compatibility layers** when breaking changes are necessary
5. **Document interconnection details** in project READMEs and central knowledge base

## Knowledge Gaps & Improvement Areas

Current known gaps in interconnection understanding:

1. Exact database schema overlap between Omnispindle and Swarmonomicon
2. EventGhost/Hammerspoon messaging protocol specifics
3. Complete mapping of Docker dependencies for all Madness Interactive components
4. ~~Detailed field mapping between Todo system and Jira~~ ✓ Implemented Jira ticket references (ABD-###) in Todo schema

---

*This is a living document. When you identify new interconnections or clarify existing ones, update this prompt accordingly.* 