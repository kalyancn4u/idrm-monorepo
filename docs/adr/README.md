# Architecture Decision Records

Short documents recording why a decision was made.

## What an ADR is

An ADR captures one decision, its context, and its consequences, in under
one page. The format was popularised by Michael Nygard in 2011 and is used
by AWS, Google, and most large engineering organisations.

## Format

Every ADR follows this structure:

- Title (numbered: 0001, 0002, ...)
- Status (Proposed, Accepted, Superseded by NNNN)
- Date
- Context (what problem, what constraints)
- Decision (what we decided)
- Consequences (what changes as a result)

## What is inside this folder

    docs/adr/
      README.md          this file
      template.md        the template every new ADR follows
      0001-...md         the first decision
      0002-...md         and so on

## How to add an ADR

1. Copy template.md to NNNN-your-title.md (zero-padded to four digits).
2. Fill in the six sections.
3. Open a pull request. ADRs are reviewed like code.
4. Once merged, the ADR is permanent. If the decision later changes, do not
   edit the old ADR. Write a new one that supersedes it.

## Reading order

Read them in numerical order. Each builds on the ones before it.

## Next steps

- The decisions currently recorded are in the numbered files beside this one.
- The reasoning behind them: ../../docs/architecture/
