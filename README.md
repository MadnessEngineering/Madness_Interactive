# Madness Interactive

A collection of project templates and interactive development tools for various programming languages and frameworks.

## Overview

This repository serves as a template hub for creating new projects with predefined structures, best practices, and development workflows. It supports multiple programming languages and frameworks, making it easy to start new projects with consistent organization and tooling.

# Human readable .cursorrules

env = windows cmd. wsl and powershell are available You can check for the availability of the commands in the environment at will
0. Use trunk-based development with feature branches. use gh cli as needed. Be detailed, I love traciability.
1. Work on the problem as asked here. Be careful not to backtrack on progress for existing methods.
2. Run available tests (e.g. 'cargo test') and iterate (word for new stuff that doesnt have to mess up other stuff)
3. Maintain a "Lessons Learned" section in readme.md
4. Update readme.md with progress after completing features
5. Git workflow rules:
   - Always append '| cat' to commands that might trigger a pager (git diff, git log, etc.)
   - Use --no-pager flag for git commands when possible
   - Keep commit messages single-line or use multiple -m flags
   - Include ticket/issue numbers in commit messages when applicable
   - Write detailed commit messages for future debugging reference
6. Command execution rules:
   - Avoid newlines in command strings
   - Use semicolons or && for multiple commands instead of newlines
   - Escape special characters in command strings
   - Set appropriate flags to prevent interactive prompts
7. Test failure triage process:
   - Analyze the root cause without immediately modifying the test
   - Identify which components or features are impacted
   - Assess the broader architectural implications
   - Prioritize preservation of existing functionality
   - Propose minimal, targeted fixes that maintain system integrity

Evaluation Criteria:
- Does the proposed fix preserve existing features?
- Is the change minimal and focused?
- Does it address the underlying architectural concern?
- Will it introduce new complexity or potential regressions?

Recommended Actions:
- Comment out problematic code instead of deleting
- Create feature flags for experimental changes
- Document the issue in "Lessons Learned"
- Discuss potential systemic improvements



## Project Languages

[X] Python
[X] Rust
[X] Powershell
[X] Lua
[X] OS
[ ] Go
[ ] C#
[ ] JavaScript
[ ] C++
[ ] Java
[ ] Ruby
[ ] PHP
[ ] TypeScript


## Project Structure

```
madness_interactive/
├── templates/
│   ├── python/
│   │   ├── games/
│   │   │   └── snowball_snowman/
│   │   └── [other-python-templates]/
│   ├── rust/
│   │   ├── tinker_template/
│   │   └── [other-rust-templates]/
│   └── [future-languages]/
├── docs/
│   ├── python/
│   └── rust/
└── scripts/
    ├── init_python_project.sh
    └── init_rust_project.sh
```

## Features

- 📁 Organized template structure for multiple languages
- 🔧 Project initialization scripts
- 📝 Comprehensive documentation templates
- 🧪 Testing frameworks setup
- 🚀 CI/CD configurations
- 📊 Project management tools

## Getting Started

### Creating a New Project

1. Choose a language template:
   ```bash
   # For Python projects
   ./scripts/init_python_project.sh [template-name] [project-name]

   # For Rust projects
   ./scripts/init_rust_project.sh [template-name] [project-name]
   ```

2. Follow the template-specific README for additional setup steps

## Contributing

We welcome contributions! Whether it's:
- Adding new language templates
- Improving existing templates
- Fixing bugs
- Enhancing documentation

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Template Standards

Each template should include:
- README.md with clear instructions
- Documentation templates
- Testing setup
- Development environment configuration
- CI/CD setup where applicable
- .gitignore and other necessary configurations

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Lessons Learned

See [LESSONS_LEARNED.md](LESSONS_LEARNED.md) for insights and best practices gathered during development.
