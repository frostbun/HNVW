from discord import ButtonStyle, Emoji, Interaction, PartialEmoji
from discord.ui import Button as _Button

from .callback import InteractionCallback


class Button(_Button):
    def __init__(
        self,
        label: str | None = None,
        emoji: str | Emoji | PartialEmoji | None = None,
        url: str | None = None,
        style: ButtonStyle = ButtonStyle.gray,
        custom_id: str | None = None,
        row: int | None = None,
        disabled: bool = False,
        callbacks: list[InteractionCallback] = [],
    ) -> None:
        super().__init__(
            label = label,
            emoji = emoji,
            url = url,
            style = style,
            custom_id = custom_id,
            row = row,
            disabled = disabled,
        )
        self.callbacks = callbacks

    async def callback(self, interaction: Interaction) -> None:
        for func in self.callbacks:
            await func(interaction)
