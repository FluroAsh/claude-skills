### [BOOK-480](https://example.atlassian.net/browse/BOOK-480)

Pull request builds re-ran every test on every push, about 18 minutes each. They now run only the tests affected by the change, using the build tool's dependency graph, which takes about 4 minutes on a typical PR. Builds on `main` still run everything.

### What changes for developers

- **PR checks finish faster** and list which projects they tested.
- **A change to shared config** (the test config, the lockfile, the CI workflow itself) still runs everything, since it can affect any project.

### How it was checked

Ran on five recent PRs of different sizes: each picked the same projects a full run had failures in. Builds on `main` are untouched.

> [!NOTE]
> **Rollback:** revert this PR. Nothing outside the workflow file changes, and no secrets or permissions are added.

<!--
Why this shape: tooling reviewers want the effect on everyone's day, how it was checked (CI changes can't be unit tested), and the way back out. No Worth a close look when the whole diff is one workflow file.
-->
