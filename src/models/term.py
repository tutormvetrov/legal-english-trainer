from dataclasses import dataclass, field


@dataclass
class Term:
    id: int
    term_eng: str
    term_rus: str
    definition: str
    category: str
    example: str
    starred: int = 0

    @classmethod
    def from_row(cls, row) -> "Term":
        return cls(
            id=row["id"],
            term_eng=row["term_eng"],
            term_rus=row["term_rus"],
            definition=row["definition"] or "",
            category=row["category"] or "",
            example=row["example"] or "",
            starred=row["starred"] if "starred" in row.keys() else 0,
        )
