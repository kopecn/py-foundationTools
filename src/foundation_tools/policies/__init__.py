"""
Execution Policies — Layer 3 of the process-transaction stack.

Policies (retry, backoff, success evaluation) decorate command execution and are
composable and independent of one another. A policy may invoke
:class:`foundation_tools.cli_transaction.CLITransact` multiple times; CLITransact
itself never retries. Policies may be *selected* by a transport transaction but
never *implemented* by one — see the Policy Ownership rule in the umbrella spec.

See ``.claude/specs/transport_transaction_architecture.md`` (Layer 3 — Execution
Policies) for the full contract. Status: planned — no policies implemented yet.
"""
