from discord import SelectOption
from discord.ui import Select as _Select

from .callback import Interaction, InteractionCallback


class Select(_Select):
    def __init__(
        self,
        placeholder: str,
        options: list[SelectOption],
        custom_id: str | None = None,
        row: int | None = None,
        disabled: bool = False,
        callbacks: list[InteractionCallback] = [],
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
