# SkillBraid Project Rules

## Scope

project

## Preferences

- Explain route after each routed answer: yes
- Confirm before rule changes: yes
- Project rules override global rules: yes

## Routes

### skill-creation-maintenance

Scenario: Create or modify a Codex skill package.

Triggers:
- The user asks to create a new skill.
- The user asks to change trigger conditions, behavior constraints, or route rules for an existing skill.

Skip:
- The user only asks a factual question about what a skill does.

Chain:
1. brainstorming - clarify boundaries, trigger conditions, storage, and confirmation rules.
2. writing-plans - turn the approved design into a task-by-task implementation plan.
3. test - verify helper scripts, package structure, and behavior.

Reason:
Skill behavior is durable and easy to overfit, so design and planning reduce bad long-term rules.

Risks:
- Skipping design can create a route that is too aggressive.
- Writing rules without confirmation can make future sessions confusing.

## Usage Notes

### 2026-05-13

Scenario: Create or modify a Codex skill package.
Route: brainstorming -> writing-plans -> test
Signal: candidate_for_project_rule
Note: This pattern is useful when skill behavior affects future work.
