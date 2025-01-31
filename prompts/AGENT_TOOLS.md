# Agent Problem-Solving Tools

## 1. Problem Analysis Framework (PAF)

### 1.1 Initial Assessment (5W1H)
```yaml
what: "What is the exact problem?"
why: "Why does this need to be solved?"
where: "Where does this issue occur?"
when: "When does it happen?"
who: "Who is affected?"
how: "How is it impacting the system?"
```

### 1.2 Root Cause Analysis (5 Whys)
```yaml
template:
  why1: "Why is [problem] happening?"
  why2: "Why did [answer1] occur?"
  why3: "Why did [answer2] occur?"
  why4: "Why did [answer3] occur?"
  why5: "Why did [answer4] occur?"
```

## 2. Solution Development Tools (SDT)

### 2.1 DRIVE Framework
```yaml
do: "What must the solution accomplish?"
restrictions: "What must it NOT do?"
invest: "What resources are available?"
values: "What principles must be maintained?"
essential: "What are the critical outcomes?"
```

### 2.2 Implementation Checklist
```yaml
steps:
  - validate_requirements: "Verify all requirements are clear"
  - check_dependencies: "Ensure all dependencies are available"
  - test_impact: "Assess impact on existing systems"
  - review_security: "Check security implications"
  - verify_standards: "Confirm coding standards compliance"
```

## 3. Project-Specific Tools (PST)

### 3.1 Code Structure Analyzer
```yaml
checks:
  - directory_structure: "Verify against template standards"
  - file_organization: "Check file naming and placement"
  - dependency_management: "Validate package requirements"
  - documentation_completeness: "Ensure all docs are present"
```

### 3.2 Quality Assurance Matrix
```yaml
criteria:
  functionality: "Does it work as intended?"
  compatibility: "Is it compatible with existing systems?"
  maintainability: "Can it be easily maintained?"
  scalability: "Will it scale with growth?"
  testability: "Can it be properly tested?"
```

## 4. Decision Support System (DSS)

### 4.1 Solution Evaluation Template
```yaml
metrics:
  impact: "1-5 scale of change impact"
  effort: "Required implementation effort"
  risk: "Potential risks and mitigation"
  value: "Expected value delivery"
  urgency: "Implementation priority"
```

### 4.2 Trade-off Analysis
```yaml
factors:
  speed: "Implementation speed"
  quality: "Code quality and robustness"
  cost: "Resource requirements"
  complexity: "Solution complexity"
  maintenance: "Long-term maintenance needs"
```

## 5. Implementation Workflow

1. **Problem Definition**
   - Use PAF to understand the issue
   - Apply 5 Whys for root cause
   - Document initial findings

2. **Solution Design**
   - Apply DRIVE framework
   - Use PST for structure validation
   - Create implementation plan

3. **Development Process**
   - Follow implementation checklist
   - Use code structure analyzer
   - Apply quality assurance matrix

4. **Evaluation**
   - Use solution evaluation template
   - Perform trade-off analysis
   - Document lessons learned

## 6. Feature Protection Framework (FPF)

### 6.1 Feature Inventory System
```yaml
inventory:
  feature_map:
    name: "Feature name"
    status: ["active", "deprecated", "planned"]
    dependencies: ["list of dependent features"]
    core_function: "Is this a core function? [yes/no]"
    usage_metrics: "Usage frequency/importance"
    last_modified: "Date of last modification"
```

### 6.2 Change Impact Analysis
```yaml
impact_checks:
  pre_change:
    - catalog_affected_features: "List all features touched by change"
    - dependency_chain: "Map all downstream dependencies"
    - usage_assessment: "Evaluate current feature usage"
    - backup_state: "Document current state for rollback"

  during_change:
    - feature_monitoring: "Track feature availability"
    - dependency_validation: "Verify dependencies remain intact"
    - functionality_preservation: "Ensure core functions maintained"

  post_change:
    - feature_verification: "Confirm all features still work"
    - regression_testing: "Run comprehensive tests"
    - documentation_update: "Update feature documentation"
```

### 6.3 Protection Rules
```yaml
guardrails:
  hard_stops:
    - core_feature_removal: "Prevent removal of core features"
    - breaking_changes: "Block changes that break dependencies"
    - data_loss: "Prevent operations causing data loss"

  warnings:
    - feature_modification: "Alert on significant feature changes"
    - dependency_alteration: "Warn about dependency updates"
    - usage_impact: "Flag changes to heavily-used features"

  approval_required:
    - core_function_changes: "Changes to core functionality"
    - multi_feature_updates: "Changes affecting multiple features"
    - high_risk_modifications: "Changes with broad impact"
```

### 6.4 Recovery Procedures
```yaml
recovery:
  rollback_plan:
    - state_backup: "Restore from pre-change backup"
    - feature_restore: "Reinstate affected features"
    - dependency_rebuild: "Rebuild broken dependencies"

  incident_response:
    - impact_assessment: "Evaluate extent of feature loss"
    - immediate_mitigation: "Apply temporary fixes"
    - root_cause_analysis: "Identify cause of feature loss"

  prevention_measures:
    - process_review: "Update protection mechanisms"
    - documentation_enhancement: "Improve feature documentation"
    - monitoring_upgrade: "Enhance feature monitoring"
```

## 7. Report Generation Framework (RGF)

### 7.1 Alias Command: "fill out a report"
```yaml
trigger_phrases:
  - "fill out a report"
  - "generate problem report"
  - "analyze current situation"
  - "status report"
```

### 7.2 Report Template
```yaml
report_sections:
  problem_analysis:
    using: "PAF 1.1 (5W1H)"
    format: |
      PROBLEM DEFINITION
      - What: {exact problem description}
      - Why: {problem importance}
      - Where: {problem location}
      - When: {occurrence pattern}
      - Who: {affected stakeholders}
      - How: {system impact}

  root_cause:
    using: "PAF 1.2 (5 Whys)"
    format: |
      ROOT CAUSE CHAIN
      1. {initial problem}
      2. {underlying cause 1}
      3. {underlying cause 2}
      4. {underlying cause 3}
      5. {root cause}

  solution_status:
    using: "SDT 2.1 (DRIVE)"
    format: |
      SOLUTION ASSESSMENT
      - Must Do: {required actions}
      - Restrictions: {limitations}
      - Resources: {available resources}
      - Values: {principles to maintain}
      - Essential: {critical outcomes}

  impact_analysis:
    using: "FPF 6.2"
    format: |
      FEATURE IMPACT
      - Affected Features: {list}
      - Dependencies: {chain}
      - Current Status: {state}
      - Risk Level: {assessment}

  recommendations:
    using: "DSS 4.1"
    format: |
      NEXT STEPS
      - Priority: {urgency level}
      - Suggested Actions: {list}
      - Required Approvals: {if any}
      - Timeline: {estimated}
```

### 7.3 Report Generation Rules
```yaml
rules:
  completeness:
    - all_sections_required: true
    - unknown_fields_marked: "UNKNOWN"
    - partial_data_allowed: true
    
  formatting:
    - use_markdown: true
    - include_timestamps: true
    - preserve_linebreaks: true
    
  content:
    - be_concise: true
    - include_evidence: true
    - highlight_blockers: true
    - suggest_next_steps: true
```

### 7.4 Report Categories
```yaml
categories:
  incident_report:
    focus: "Problem occurrence and impact"
    priority_sections: ["problem_analysis", "root_cause"]
    
  progress_report:
    focus: "Current status and blockers"
    priority_sections: ["solution_status", "impact_analysis"]
    
  decision_report:
    focus: "Options and recommendations"
    priority_sections: ["impact_analysis", "recommendations"]
```

## 8. Shorthand Translation Framework (STF)

### 8.1 Alias Command: "translate to shorthand"
```yaml
trigger_phrases:
  - "translate to shorthand"
  - "make this concise"
  - "optimize for ai"
  - "convert to brief format"
```

### 8.2 Translation Rules
```yaml
syntax_patterns:
  commands:
    verbose: "Please execute the following command"
    shorthand: "cmd:"
    
  conditions:
    verbose: "If the following condition is true"
    shorthand: "if:"
    
  iterations:
    verbose: "Repeat the following steps"
    shorthand: "loop:"
    
  requirements:
    verbose: "The following must be implemented"
    shorthand: "req:"

formatting:
  separators:
    - use: ";" for sequential steps
    - use: "+" for combinations
    - use: "|" for alternatives
    - use: ">" for transformations
    
  prefixes:
    - "!" for critical/priority
    - "?" for conditional
    - "#" for reference
    - "@" for dependencies
    
  suffixes:
    - "_opt" for optional
    - "_req" for required
    - "_tmp" for temporary
    - "_done" for completed
```

### 8.3 Common Patterns
```yaml
patterns:
  actions:
    check: "chk"
    verify: "vrf"
    implement: "impl"
    update: "upd"
    remove: "rm"
    create: "cr"
    
  objects:
    function: "fn"
    variable: "var"
    parameter: "param"
    directory: "dir"
    database: "db"
    
  states:
    success: "ok"
    failure: "err"
    warning: "warn"
    pending: "wait"
    
  modifiers:
    quick: "q"
    force: "f"
    recursive: "r"
    verbose: "v"
```

### 8.4 Translation Templates
```yaml
templates:
  code_task:
    verbose: "Create a new function that handles user authentication"
    shorthand: "cr_fn:auth_handler;@db+user"
    
  system_task:
    verbose: "Check all dependencies and update if necessary"
    shorthand: "chk_deps;upd_if_req"
    
  test_task:
    verbose: "Run all tests and verify no regressions"
    shorthand: "run_tests;vrf!no_reg"
    
  feature_task:
    verbose: "Implement new feature with backward compatibility"
    shorthand: "impl_feat+bkwd_compat"
```

### 8.5 Context Preservation
```yaml
preservation_rules:
  must_keep:
    - critical_values: "Exact numbers/IDs"
    - unique_identifiers: "Function/variable names"
    - version_numbers: "Semantic versions"
    - error_codes: "Specific error references"
    
  can_shorten:
    - descriptive_text: "Long descriptions"
    - repeated_patterns: "Common phrases"
    - standard_commands: "Known operations"
    - status_messages: "State indicators"
```

## Usage Guidelines

1. **Start with Understanding**
   - Always begin with Problem Analysis Framework
   - Document all findings clearly
   - Validate understanding before proceeding

2. **Design Before Implementation**
   - Use appropriate tools for design phase
   - Validate against project standards
   - Consider long-term implications

3. **Implement with Care**
   - Follow structured implementation workflow
   - Use checklist-driven approach
   - Document decisions and rationale

4. **Review and Improve**
   - Evaluate results using DSS
   - Document lessons learned
   - Update tools based on experience

5. **Feature Protection**
   - Maintain up-to-date feature inventory
   - Run impact analysis before changes
   - Respect protection rules
   - Keep recovery procedures ready
   - Document all feature modifications

6. **Report Generation**
   - Respond to "fill out a report" command
   - Use appropriate report category
   - Follow report generation rules
   - Include all required sections
   - Provide actionable recommendations

7. **Shorthand Translation**
   - Use translation triggers to convert text
   - Preserve critical information
   - Apply consistent syntax patterns
   - Maintain readability for AI
   - Include necessary context markers
