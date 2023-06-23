from typing import Dict


class LemmaService:
    PREFIX_WA = 'w'
    PREFIX_FA = 'f'
    PREFIX_BI = 'b'
    PREFIX_KA = 'k'
    PREFIX_TA = 't'
    PREFIX_LA = 'l'
    PREFIX_SA = 's'
    PREFIX_YA = 'yaA'
    PREFIX_HA = 'haA'
    SUFFIX_NOON = 'n'
    VOCATIVE_SUFFIX = 'hum~a'

    def __init__(self):
        self.lemmas: Dict[str, int] = {}
        self.add(self.PREFIX_WA)
        self.add(self.PREFIX_FA)
        self.add(self.PREFIX_BI)
        self.add(self.PREFIX_KA)
        self.add(self.PREFIX_TA)
        self.add(self.PREFIX_LA)
        self.add(self.PREFIX_SA)
        self.add(self.PREFIX_YA)
        self.add(self.PREFIX_HA)
        self.add(self.SUFFIX_NOON)
        self.add(self.VOCATIVE_SUFFIX)

    def add(self, lemma: str):
        if lemma not in self.lemmas:
            self.lemmas[lemma] = len(self.lemmas)

    @property
    def count(self):
        return len(self.lemmas)

    def value_of(self, lemma: str):
        if lemma not in self.lemmas:
            raise ValueError(f'Unrecognized lemma: {lemma}')
        return self.lemmas[lemma]
