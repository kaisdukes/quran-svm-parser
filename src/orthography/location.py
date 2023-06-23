from dataclasses import dataclass


def parse_location(text: str):
    parts = text.split(':')
    return Location(int(parts[0]), int(parts[1]), int(parts[2]))


@dataclass
class Location:
    chapter_number: int
    verse_number: int
    token_number: int = 0

    def __str__(self):
        parts = [str(self.chapter_number), str(self.verse_number)]
        if self.token_number > 0:
            parts.append(str(self.token_number))
        return ':'.join(parts)
