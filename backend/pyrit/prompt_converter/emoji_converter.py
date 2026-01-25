# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import random

from pyrit.models import PromptDataType
from pyrit.prompt_converter import ConverterResult, PromptConverter


class EmojiConverter(PromptConverter):
    emoji_dict = {
        "a": ["🅐", "🅰️", "🄰"],
        "b": ["🅑", "🅱️", "🄱"],
        "c": ["🅒", "🅲", "🄲"],
        "d": ["🅓", "🅳", "🄳"],
        "e": ["🅔", "🅴", "🄴"],
        "f": ["🅕", "🅵", "🄵"],
        "g": ["🅖", "🅶", "🄶"],
        "h": ["🅗", "🅷", "🄷"],
        "i": ["🅘", "🅸", "🄸"],
        "j": ["🅙", "🅹", "🄹"],
        "k": ["🅚", "🅺", "🄺"],
        "l": ["🅛", "🅻", "🄻"],
        "m": ["🅜", "🅼", "🄼"],
        "n": ["🅝", "🅽", "🄽"],
        "o": ["🅞", "🅾️", "🄾"],
        "p": ["🅟", "🅿️", "🄿"],
        "q": ["🅠", "🆀", "🅀"],
        "r": ["🅡", "🆁", "🅁"],
        "s": ["🅢", "🆂", "🅂"],
        "t": ["🅣", "🆃", "🅃"],
        "u": ["🅤", "🆄", "🅄"],
        "v": ["🅥", "🆅", "🅅"],
        "w": ["🅦", "🆆", "🅆"],
        "x": ["🅧", "🆇", "🅇"],
        "y": ["🅨", "🆈", "🅈"],
        "z": ["🅩", "🆉", "🅉"],
    }

    async def convert_async(
        self, *, prompt: str, input_type: PromptDataType = "text"
    ) -> ConverterResult:
        """
        Converts English text to randomly chosen circle or square character emojis.

        Inspired by https://github.com/BASI-LABS/parseltongue/blob/main/src/utils.ts
        """
        if not self.input_supported(input_type):
            raise ValueError("Input type not supported")

        prompt = prompt.lower()
        result = []
        for char in prompt:
            if char in EmojiConverter.emoji_dict:
                result.append(random.choice(EmojiConverter.emoji_dict[char]))
            else:
                result.append(char)
        ret_text = "".join(result)

        return ConverterResult(output_text=ret_text, output_type="text")

    def input_supported(self, input_type: PromptDataType) -> bool:
        return input_type == "text"
