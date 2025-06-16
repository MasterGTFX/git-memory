# Project Memory Aggregation Prompt

You are analyzing the complete commit history of a Git repository to extract high-level insights about the project's evolution, architecture, and current state. Your goal is to synthesize individual commit memories into strategic project understanding.

## Analysis Framework

### Major Features
Identify the **key features and capabilities** that define this project:
- What are the **primary functionalities** the project provides?
- Which features represent **significant milestones** in development?
- What **user-facing capabilities** have been built?
- What **technical capabilities** or infrastructure has been established?

### Architecture Evolution  
Track how the **project structure and design** has evolved:
- What **architectural patterns** or frameworks were adopted?
- How has the **codebase organization** changed over time?
- What **technical debt** was addressed or accumulated?
- What **refactoring efforts** shaped the current structure?
- What **design decisions** had lasting impact?

### Key Technical Decisions
Highlight **important technical choices** made during development:
- **Technology stack** decisions (languages, frameworks, libraries)
- **Architecture patterns** chosen (MVC, microservices, etc.)
- **Data storage** and persistence approaches
- **API design** and integration patterns
- **Testing strategies** and quality assurance approaches
- **Deployment and infrastructure** decisions

### Current State Assessment
Provide a **realistic assessment** of where the project stands:
- What is the project's **current maturity level**?
- What are its **core strengths** and capabilities?
- What **technical debt** or limitations exist?
- How **maintainable and extensible** is the current codebase?
- What is the **quality** of documentation and testing?

### Strategic Next Steps
Based on the commit history patterns, suggest **logical next development steps**:
- What **missing features** would add significant value?
- What **technical improvements** would enhance the project?
- What **refactoring** or **architectural changes** might be beneficial?
- What **quality improvements** (testing, docs, performance) are needed?
- What **expansion opportunities** align with the project's direction?

## Analysis Guidelines

### Pattern Recognition
Look for **patterns and trends** across commits:
- **Recurring themes** in development focus
- **Phases of development** (initial setup, feature building, stabilization)
- **Problem areas** that required multiple fixes or refactoring
- **Growth areas** where significant development effort was invested

### Impact Assessment
Evaluate the **significance of changes**:
- Focus on commits with **major** or **moderate** impact ratings
- Identify **turning points** in the project's development
- Recognize **foundational changes** that enabled future development
- Distinguish between **feature work** and **maintenance work**

### Synthesis Guidelines
Create **coherent narratives** from individual changes:
- **Connect related commits** that build toward a common goal
- **Explain the reasoning** behind technical decisions when possible
- **Identify dependencies** between different features or changes
- **Highlight innovations** or clever solutions

## Quality Standards

### Be Strategic
- Focus on **high-level insights** rather than implementation details
- Think like a **technical lead** assessing project health and direction
- Consider **business value** and **user impact** of features
- Evaluate **technical sustainability** and maintainability

### Be Specific
- Use **concrete examples** from the commit history
- Reference **specific technologies, patterns, or approaches** used
- Quantify where possible (number of features, size of refactoring, etc.)
- Avoid vague generalizations

### Be Forward-Looking
- **Anticipate future needs** based on current trajectory
- **Identify opportunities** for improvement or expansion
- **Consider scalability** and long-term maintenance needs
- **Suggest practical next steps** that build on existing work

## Context Considerations

- **Project type** (web app, library, CLI tool, etc.) affects priorities
- **Development phase** (prototype, MVP, mature product) influences needs
- **Team size** and **development velocity** from commit patterns
- **Code quality trends** from the types of fixes and refactoring
- **External dependencies** and integration complexity

Remember: This analysis will help developers understand their project's journey and make informed decisions about future development priorities.