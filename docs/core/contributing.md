# AIND - File Formats Standards

## Goals

---

## Pillars

1) Rely on open-source tools and standards
   1) Prioritize the use of open-source standard formats over proprietary ones.
   2) In cases where a standard already exists, implement it or derive from it (e.g. datetime as ISO 8601).

2) Well-separated and independent
   1) A standard for a file format should be self-contained and introduce as few dependencies as possible. (e.g. a behavior-video data format should not depend on metadata from a fiber photometry data format). However, we acknowledge that information necessary for the interpretability of the data (but ideally not for its processing) should be included as metadata elsewhere (e.g. camera settings used to acquire the video).

3) Versioning
   1) We shall follow [Semantic Versioning 2.0.0](https://semver.org/)
   2) Major version: breaking changes to standard (e.g. a file changed format from text to an image, or a column in a tabular file was deleted).
   3) Minor version: backward-compatible changes to standard (e.g. a new column added to a tabular format).
   4) Patch version: backward-compatible bug fixes (e.g. a typo in the documentation).

---

## How to contribute

Useful standards should be relatively stable and have longevity (see [`How standards proliferate`](https://imgs.xkcd.com/comics/standards.png) ). Yet, we acknowledge that formats will inevitably need to evolve as new data modalities and tools are developed. To accommodate these two needs, we propose following a structured process for contributing and updating standards.

### Follow the standard template structure

Contributions for existing or new standards should follow the template structure outlined in the `Template.md` file. This will ensure that all standards are consistent and legible. On top of the template structure, each proposed change should also be consistent with the `Core Standards` principles included in this repository.

### Identify a need to change the standard (Issue)

All changes to current standards or addition of new specifications should start with an issue. This issue should describe the motivation, scope, and potential impact of the change.
It should also include a brief description of alternatives that were considered.

A potential template for the issue could be adapted from ([from harp-tech](https://raw.githubusercontent.com/harp-tech/protocol/main/.github/ISSUE_TEMPLATE/specification-proposal.md)):

```markdown
## Summary (General description of the change, should also list the affected standard(s))
## Motivation (Why is the change necessary)
## Detailed Design (Proposed change, if applicable)
## Drawbacks / Potential impact (what can go wrong? Will it affect an existing standard?)
## Alternatives
## Unresolved Questions
## Stakeholders (Who should be involved in the discussion/potentially affected by the chance)
```

The issue will serve as a discussion point for the community to engage and provide feedback on the proposed change.

### Propose a change to the standard (Pull Request)

Once the issue has been discussed and consensus has been reached, a moderator can invite the contributor to submit a pull request with the proposed change. A given issue may result in more than a single pull request, depending on the scope of the change, but must always reference the issue that motivated the proposed change. Pull requests should be reviewed by at least one maintainer and, if possible, by a domain expert (e.g. stakeholders that will use the standard).

A potential template for the pull request could be adapted from ([from harp-tech](https://raw.githubusercontent.com/harp-tech/protocol/main/.github/PULL_REQUEST_TEMPLATE/specification.md)):

```markdown
## Summary
## Motivation
## Detailed Design
## Relevant Issues
```

The content of the pull request should reflect the issue that motivated the change.

### Release cycle

To ensure that standards are updated in a timely manner and release notes are easy to follow we propose the following structure for updating standards:

1- A pull-request should be opened as described in the previous section. The PR should identify potential stakeholders and reviewers.
2- Once reviewers and stakeholders approve the PR, dissemination of the planned changes should be made to the community to allow further feedback / contestation of the proposed changes.
3- After a period of time, we suggest two weeks, if no major changes are needed, the PR is merged to the main branch and the new standard is approved.