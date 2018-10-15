import click

from redmine.cli.config import Config


class AliasedGroup(click.Group):
    def group_params(self, params):
        grouped_params = []

        for i in range(0, len(params), 2):
            grouped_params.append((params[i].lstrip("-"), params[i + 1]))

        return grouped_params

    def get_command(self, ctx, cmd_name):
        # Return builtin commands as normal
        ctx.alias = False
        c = click.Group.get_command(self, ctx, cmd_name)
        if c is not None:
            return c

        cfg = ctx.ensure_object(Config)

        if cmd_name in cfg.aliases:
            actual_cmd = cfg.aliases[cmd_name].split()
            params = self.group_params(actual_cmd[1:])
            for param in params:
                ctx.alias = True
                ctx.params[param[0]] = param[1]
            return click.Group.get_command(self, ctx, actual_cmd[0])
