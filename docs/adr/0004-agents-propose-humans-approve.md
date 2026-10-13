# ADR-0004: Agents propose, humans approve; enforcement outside instruction files

- Status: accepted · Date: 2026-10-06 · Deciders: @org/platform-eng, @org/security

## Context
Instruction files are context, not controls (Anthropic docs). Prompt injection through repository content is demonstrated (Invariant Labs 2025) and has no complete model-level mitigation. SOC 2 change management needs accountable human approval.

## Decision
Agents have no authority: they cannot approve, merge, deploy, edit instruction files, CI or security configuration, or hold production credentials. Every "must" in instruction files is backed by at least one technical control (ruleset, CODEOWNERS, hook, CI check, IAM). Rule changes flow through human-approved rule proposals validated by evals.

## Consequences
Some legitimate agent tasks (e.g. updating a workflow) need a human to make or approve the change through the normal process. Review capacity becomes the throughput limit, which is intended.

## Compliance check
Org settings audit (§2.6), `playbook-guard`, quarterly kill-switch rehearsal, security checklist section E.
