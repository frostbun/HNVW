from inspect import getfullargspec

from discord import Interaction


class InteractionCallback:

    def __init__(self, func, default_arg_name: str | None = None, default_arg_type = None, **kwargs):
        # check args
        argspec = getfullargspec(func)

        # pass default arg to func
        if isinstance(default_arg_name, str):
            kwargs[default_arg_name] = None

        # pass interaction to func
        if "interaction" in argspec.args:
            kwargs["interaction"] = None

        # missing args
        required_args = argspec.args[:-len(argspec.defaults)] if argspec.defaults is not None else argspec.args
        for arg in required_args:
            if arg != "self" and arg not in kwargs.keys():
                raise ValueError(f"Missing callback {arg = }")

        # func does not have **kwargs but pass in too many kwargs
        if argspec.varkw is None:
            for arg in kwargs.keys():
                if arg not in argspec.args:
                    raise ValueError(f"Redundant callback {arg = }")

        self.func = func
        self.kwargs = kwargs
        self.default_arg_name = default_arg_name
        self.default_arg_type = default_arg_type

    async def __call__(self, interaction: Interaction, default_arg_value = None):
        if self.default_arg_name in self.kwargs:
            self.kwargs[self.default_arg_name] = self.default_arg_type(default_arg_value)
        if "interaction" in self.kwargs:
            self.kwargs["interaction"] = interaction
        if "context" in self.kwargs:
            self.kwargs["context"].author = interaction.user
        return await self.func(**self.kwargs)
