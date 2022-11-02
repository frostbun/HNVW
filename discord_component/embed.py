from discord import Colour as Color
from discord import Embed as _Embed


class Embed(_Embed):
    def __init__(
        self,
        title: str,
        desc: str,
        color: Color = Color.red(),
        author_text: str = "",
        author_icon: str = _Embed.Empty,
        footer_text: str = _Embed.Empty,
        footer_icon: str = _Embed.Empty,
        thumbnail: str = _Embed.Empty,
        image: str = _Embed.Empty,
    ) -> None:
        super().__init__(
            title = title,
            description = desc,
            color = color,
        )
        self.set_author(name = author_text, icon_url = author_icon)\
            .set_footer(text = footer_text, icon_url = footer_icon)\
            .set_thumbnail(url = thumbnail)\
            .set_image(url = image)
