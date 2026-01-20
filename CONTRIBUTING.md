# Contributing to Ontology2Graph

We would love for you to contribute to **Ontology2Graph** and help make it even better than it is today!

Please contribute to this repository if any of the following is true:
- You have expertise in *knowledge graphs*, *synthetic datasets*, or *graph generation*,
- You want to *challenge AI pipelines* with domain-related knowledge graphs and domain-specific graph patterns.

## How to Contribute

We welcome community contributions, whether they are documentations, refactoring, tests, or new features.

You can contribute to Ontology2Graph in the following ways:

### to be modified  ### to be modified  ### to be modified  ### to be modified ### to be modified ### to be modified
- File a [bug report](https://github.com/nicolas-hbt/pygraft/issues/new?assignees=&labels=&template=bug_report.md&title=)
- File a [feature request](https://github.com/nicolas-hbt/pygraft/issues/new?assignees=&labels=&projects=&template=feature_request.md&title=)
- Help other users by commenting on [pending issues](https://github.com/nicolas-hbt/pygraft/issues)
- Help implementing unit tests
- Help refactoring code and ensuring best practices are respected
- Generate clean docstrings for the existing code base
- Implement a new feature (see [Desirable Features](#desirable-features))


## Desirable Features <a name="desirable-features"></a>

Additional features will be provided in the next versions of PyGraft. You want to contribute but do not know how? Here are a few desirable features to implement to get you up and running:

**High Priority**

**Medium Priority**

**Low Priority**

## Styleguides

### Commit Convention

Commits are formatted as follows &xrarr; `<emoji> <type>(<scope>): <subject>` where :

- emoji is optional

Example :

```text
# ------------------------------------------- TEMPLATE ------------------------------------------- #
<emoji> <type>(<scope>): <short imperative summary>
        ^----^  ^----^   ^------------------------^
        |       |        |
        |       |        +-> Subject: Summary in present tense (WHAT & WHY, not HOW)
        |       +----------> Scope: optional, specific module or area changed
        +------------------> Type: feat, fix, docs, style, refactor, perf, test, chore, etc.

Signed-off-by: git.user.name <git.user.email>


# -------------------------------------------- EXAMPLE ------------------------------------------- #

:sparkles: feat(core): add configuration file support

Implement support for reading settings from a config file.
- Enables environment-specific configuration
- Simplifies deployment and local setup

Signed-off-by: Mad Max <mad.max@example.com>
```

**Core Commit Types:**

| Type     | Emoji              | Code                 | Description                                    |
|:---------|:-------------------|:---------------------|:-----------------------------------------------|
| feat     | :sparkles:         | `:sparkles:`         | Add a new feature for the user                 |
| fix      | :bug:              | `:bug:`              | Fix a bug affecting the user                   |
| docs     | :memo:             | `:memo:`             | Documentation updates only                     |
| style    | :art:              | `:art:`              | Formatting or linting; no logic change         |
| refactor | :recycle:          | `:recycle:`          | Code restructuring without behavior change     |
| perf     | :zap:              | `:zap:`              | Performance improvement                        |
| test     | :white_check_mark: | `:white_check_mark:` | Add or update tests; no production code change |
| chore    | :wrench:           | `:wrench:`           | Maintenance, tooling, or config updates        |

**Optional Project-Specific Types:**

| Type      | Emoji      | Code         | Description                           |
|:----------|:-----------|:-------------|:--------------------------------------|
| build     | :package:  | `:package:`  | Build system or dependency changes    |
| ci        | :gear:     | `:gear:`     | CI/CD pipeline configuration          |
| revert    | :back:     | `:back:`     | Revert a previous commit              |
| logging   | :scroll:   | `:scroll:`   | Logging or observability code changes |
| notebooks | :notebook: | `:notebook:` | Development or analysis notebooks     |

References:

- https://www.conventionalcommits.org/
- https://seesparkbox.com/foundry/semantic_commit_messages
- http://karma-runner.github.io/1.0/dev/git-commit-msg.html

### Python Styleguide

Our python style is defined by:

- [ruff](https://github.com/astral-sh/ruff) &xrarr; handles formatting and linting, keeping code clean, consistent, and auto-formatted.
- [pyright](https://github.com/microsoft/pyright) &xrarr; enforces strict typing and static analysis, ensuring type safety and predictable behavior.
- [Google-style docstrings](https://github.com/google/styleguide/blob/gh-pages/pyguide.md) &xrarr; provide clear, structured documentation for all public classes and functions.

```python
def top_k(items: list[str], k: int) -> list[str]:
    """Return the first k items.
  
    Args:
        items: Input list.
        k: Number of items to return. Must be >= 0.
  
    Returns:
        The first k items, or all if len(items) < k.
  
    Raises:
        ValueError: If k is negative.
    """
    if k < 0:
        raise ValueError("k must be >= 0")
    return items[:k]
```

## Communication

GitHub issues are the primary way for communicating about specific proposed changes to this project.
Do not open issues for general support questions as we want to keep GitHub issues for bug reports and feature requests.

You may also contact the maintainers by e-mail for more specific purposes and questions.

In both contexts, please be kind and courteous.
Language issues are often contentious and we'd like to keep discussion brief, civil and focused on what we're actually doing, not wandering off into too much imaginary stuff.
Likewise any spamming, trolling, flaming, baiting or other attention-stealing behaviour is not welcome.
