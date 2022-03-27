from inspect import getfullargspec

class InteractionCallback:

    def __init__(self, func, default_arg_name = None, default_arg_type = None, **kwargs):
        argspec = getfullargspec(func)
        # pass interaction to func
        if "interaction" in argspec.args: kwargs["interaction"] = None
        # missing args
        if any(
            arg not in kwargs.keys()
            for arg in argspec.args[
                    : -len(argspec.defaults) if argspec.defaults is not None else len(argspec.args)
                ]
            if arg not in ("self", default_arg_name)
        ): raise Exception("Missing callback args")
        # func does not have **kwargs but pass in too many kwargs
        if argspec.varkw is None and any(
            arg not in argspec.args
            for arg in kwargs.keys()
        ): raise Exception("Too many callback args")
        self.func = func
        self.kwargs = kwargs
        self.default_arg_name = default_arg_name
        self.default_arg_type = default_arg_type

    async def __call__(self, interaction = None, default_arg_value = None):
        if self.default_arg_name is not None:
            self.kwargs[self.default_arg_name] = self.default_arg_type(default_arg_value)
        if "interaction" in self.kwargs: self.kwargs["interaction"] = interaction
        if "context" in self.kwargs: self.kwargs["context"].author = interaction.user
        return await self.func(**self.kwargs)
