# Project Addition Guidelines

## Template Structure

When adding a new project or template, follow this structure:

```
templates/
└── [language]/
    └── [category]/
        └── [project_name]/
            ├── README.md           # Project-specific documentation
            ├── CHANGELOG.md        # Version history and changes
            ├── CONTRIBUTING.md     # Contribution guidelines
            ├── LESSONS_LEARNED.md  # Development insights
            ├── requirements.txt    # Dependencies (or equivalent)
            ├── src/               # Source code directory
            ├── tests/             # Test files
            └── docs/              # Additional documentation
```

## Prompt Format

When requesting to add a new project, include:

1. **Project Basics**
   ```yaml
   language: [python/rust/etc]
   category: [games/web/cli/etc]
   project_name: [descriptive_name]
   description: [brief_overview]
   ```

2. **Technical Requirements**
   ```yaml
   dependencies:
     - name: [package_name]
       version: [version_number]
   
   dev_dependencies:
     - name: [package_name]
       version: [version_number]
   ```

3. **Project Structure**
   ```yaml
   custom_directories:
     - path: [directory_path]
       purpose: [brief_explanation]
   
   required_files:
     - path: [file_path]
       purpose: [brief_explanation]
   ```

4. **Features and Functionality**
   ```yaml
   core_features:
     - [feature_description]
   
   optional_features:
     - [feature_description]
   ```

## Example Prompt

```yaml
# New Game Project Request
language: python
category: games
project_name: space_invaders
description: A classic space invaders clone using Pygame

dependencies:
  - name: pygame
    version: "2.5.0"
  - name: numpy
    version: "1.24.0"

custom_directories:
  - path: src/assets
    purpose: Game sprites and sounds
  - path: src/levels
    purpose: Level configuration files

core_features:
  - Player spaceship movement
  - Enemy wave generation
  - Collision detection
  - Score tracking
```

## Guidelines for AI Assistants

When processing project addition requests:

1. **Validation**
   - Ensure all required fields are present
   - Verify compatibility of dependencies
   - Check for naming conflicts

2. **Implementation**
   - Create directory structure
   - Generate boilerplate files
   - Set up testing framework
   - Initialize version control

3. **Documentation**
   - Generate comprehensive README
   - Document setup instructions
   - Include example usage
   - Add contribution guidelines

4. **Quality Checks**
   - Verify file structure completeness
   - Ensure documentation clarity
   - Test build system functionality
   - Validate dependency management

## Post-Creation Checklist

- [ ] Project builds successfully
- [ ] All tests pass
- [ ] Documentation is complete
- [ ] Dependencies are properly specified
- [ ] Example code is provided
- [ ] Git repository is properly initialized
- [ ] CI/CD configuration is present (if applicable)
- [ ] License is specified 
