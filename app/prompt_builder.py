import copy


class BlockInfo():
    def __init__(self, content: str, show: bool = True):
        self.content = content
        self.show = show


class PromptBuilder:

    def __init__(self, separator: str = "\n\n"):
        self._block_names: list[str] = []
        self._block_dict: dict[str, BlockInfo] = dict()

        self._separator = separator

    def separator(self, new_separator: str) -> 'PromptBuilder':
        self._separator = new_separator
        return self

    def append_block(self, content: str, name: str) -> 'PromptBuilder':
        if name in self._block_dict:
            raise ValueError(f"Duplicate name exists in the builder - {name}")
        else:
            self._block_dict[name] = BlockInfo(content, show=True)

        self._block_names.append(name)

        return self

    def append_builder(self, builder: 'PromptBuilder') -> 'PromptBuilder':
        self._block_names += builder._block_names  # Concat names
        self._block_dict |= builder._block_dict  # Merge dicts
        return self

    def toggle_block(self, name: str, show: bool) -> 'PromptBuilder':
        if name in self._block_dict:
            self._block_dict[name].show = show
        return self

    def build(self) -> str:
        return self._separator.join(
            [self._block_dict[name].content for name in self._block_names if self._block_dict[name].show == True])


    def copy(self) -> 'PromptBuilder':
        return copy.deepcopy(self)
