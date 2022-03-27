from discord import Interaction
from discord.ui import Select as _Select

class Select(_Select):
    def __init__(
        self,
        placeholder,
        options,
        custom_id = None,
        row = None,
        disabled = False,
        callbacks = (),
    ) -> None:
        super().__init__(
            placeholder = placeholder,
            options = options,
            custom_id = custom_id,
            row = row,
            disabled = disabled,
        )
        self.callbacks = callbacks

    async def callback(self, interaction: Interaction) -> None:
        for func in self.callbacks:
            await func(interaction, self.values[0])
