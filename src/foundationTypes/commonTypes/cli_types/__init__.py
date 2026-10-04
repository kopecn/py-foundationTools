"""CLI-tool command models.

One self-contained package per command (schema-generated model + hand-written
``wire_config.py`` binding its ``wire_invoke`` argv and ``wire_decode`` parser +
``__init__`` that activates the binding on import). Import a command's package to
get its model with wiring active, e.g.::

    from foundationTypes.commonTypes.cli_types.uname_report import UnameReport

``disk_usage`` (``df -h``) is the original exemplar of this shape and lives here too.
"""
