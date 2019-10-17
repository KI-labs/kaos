import click


class CustomHelpOrder(click.Group):
    """
    This class overrides the click.Group.command() method which is used to override the list_commands functionality.
    It shows the commands with the same order in which they are added in the main group.
    """

    def __init__(self, *args, **kwargs):
        super(CustomHelpOrder, self).__init__(*args, **kwargs)

    def list_commands(self, ctx):
        """reorder the list of commands when listing the help"""
        return self.commands


class NotRequiredIf(click.Option):
    """
    This class is used when two "competing" options are required but mutually exclusive.
    It also handles when both options are given and collide.
    """

    def __init__(self, *args, **kwargs):
        self.not_required_if = kwargs.pop('not_required_if')
        assert self.not_required_if, "'not_required_if' parameter required"
        kwargs['help'] = (kwargs.get('help', '') + ' [NOTE: Mutually exclusive with {}]'.format(self.not_required_if))
        super(NotRequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        we_are_present = self.name in opts
        other_present = self.not_required_if in opts

        if other_present:
            if we_are_present:
                raise click.UsageError(
                    "Illegal usage: {} is mutually exclusive with {}".format(click.style(self.name, bold=True),
                                                                             click.style(self.not_required_if,
                                                                                         bold=True)))
            else:
                self.prompt = None

        return super(NotRequiredIf, self).handle_parse_result(
            ctx, opts, args)


class MutuallyExclusiveWith(click.Option):
    def __init__(self, *args, **kwargs):
        self.mutually_exclusive = set(kwargs.pop('mutually_exclusive', []))
        help_desc = kwargs.get('help', '')
        if self.mutually_exclusive:
            ex_str = ', '.join(self.mutually_exclusive)
            kwargs['help'] = f"{help_desc} NOTE: This argument is mutually exclusive with arguments: [ {ex_str} ]."
        super(MutuallyExclusiveWith, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        if self.mutually_exclusive.intersection(opts) and self.name in opts:
            raise click.UsageError(
                "Illegal usage: `{}` is mutually exclusive with "
                "arguments `{}`.".format(
                    self.name,
                    ', '.join(self.mutually_exclusive)
                )
            )

        return super(MutuallyExclusiveWith, self).handle_parse_result(
            ctx,
            opts,
            args
        )
