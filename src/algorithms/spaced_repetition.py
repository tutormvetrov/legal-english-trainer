from datetime import date


class SpacedRepetitionScheduler:
    def __init__(self, db_manager):
        self.db = db_manager

    def review(self, term_id: int, quality: int) -> int:
        """
        quality: 0–5 (0=полный провал, 5=идеально).
        Возвращает новый интервал в днях.
        """
        progress = self.db.get_progress(term_id)

        if progress:
            ease_factor = progress["ease_factor"]
            repetition = progress["repetition"]
            interval = progress["interval"]
            correct_count = progress["correct_count"]
        else:
            ease_factor = 2.5
            repetition = 0
            interval = 1
            correct_count = 0

        if quality >= 3:
            if repetition == 0:
                interval = 1
            elif repetition == 1:
                interval = 6
            else:
                interval = round(interval * ease_factor)
            repetition += 1
            correct_count += 1
        else:
            repetition = 0
            interval = 1

        ease_factor = max(1.3, ease_factor + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))

        today = date.today().isoformat()
        self.db.upsert_progress(term_id, today, ease_factor, interval, repetition, correct_count)
        return interval

    def get_due_terms(self, category: str | None = None, limit: int = 10) -> list[int]:
        return self.db.get_due_terms(category=category, limit=limit)

    def get_stats(self) -> dict:
        return self.db.get_stats()
