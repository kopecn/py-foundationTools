"""
ssh_builder — pure SSH command construction.

Builds argv-style ``ssh`` command vectors. Never executes anything; execution is
delegated by callers to :mod:`foundation_tools.cli_transaction`. See
``.claude/specs/sshTransact.md`` for the full construction contract.
"""

from collections.abc import Mapping


def build_ssh_command(
    *,
    host: str,
    user: str | None = None,
    port: int | None = None,
    identity_file: str | None = None,
    command: str | list[str] | None = None,
    options: Mapping[str, str] | None = None,
) -> list[str]:
    """Construct a deterministic ``ssh`` command vector.

    ``options`` emits one ``-o key=value`` pair per entry, in mapping order,
    before all other arguments. No SSH options are added by default.

    ``-p <port>`` is emitted only when ``port`` is supplied — never a synthesized
    default, since a command-line ``-p`` overrides any ``Port`` set for the host in
    ``~/.ssh/config``. ``-i <identity_file>`` is emitted only when supplied, with no
    validation. The target is ``user@host`` when ``user`` is given, else ``host``.

    ``command`` follows the dual-mode remote-command contract: a ``str`` becomes a
    single remote-shell argument (preserving pipes/redirects/shell operators); a
    ``list[str]`` is appended as independent argv segments.
    """
    result = ["ssh"]
    if options is not None:
        for key, value in options.items():
            result.extend(["-o", f"{key}={value}"])
    if port is not None:
        result += ["-p", str(port)]
    if identity_file is not None:
        result += ["-i", identity_file]
    result.append(f"{user}@{host}" if user is not None else host)
    if command is None:
        return result
    if isinstance(command, str):
        result.append(command)
    else:
        result.extend(command)
    return result
