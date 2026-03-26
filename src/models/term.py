from dataclasses import dataclass


@dataclass
class Term:
    id: int
    term_eng: str
    term_rus: str
    definition: str
    category: str
    example: str

    @classmethod
    def from_row(cls, row) -> "Term":
        return cls(
            id=row["id"],
            term_eng=row["term_eng"],
            term_rus=row["term_rus"],
            definition=row["definition"] or "",
            category=row["category"] or "",
            example=row["example"] or "",
        )
