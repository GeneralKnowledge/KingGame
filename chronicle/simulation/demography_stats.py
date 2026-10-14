from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from chronicle.models.character import Sex
from chronicle.models.events import EventKind
from chronicle.models.world import WorldState


@dataclass(frozen=True)
class DemographyReport:
    seed: int
    years: float
    living: int
    total_births: int
    total_deaths: int
    mean_births_per_married_woman_per_year: float
    death_age_counts: dict[str, int]
    marriage_events: int
    mean_age_at_first_marriage: float | None
    infant_child_mortality_share: float
    share_fertile_women_married: float
    never_married_adults_25_plus_share: float

    def format_text(self) -> str:
        lines = [
            f"seed={self.seed} years={self.years:.1f} living={self.living}",
            f"  births={self.total_births} deaths={self.total_deaths}",
            f"  mean births/married woman/year={self.mean_births_per_married_woman_per_year:.3f}",
            f"  infant+child mortality (deaths age<5 / births)={self.infant_child_mortality_share:.1%}",
            f"  fertile women (18-42) married share={self.share_fertile_women_married:.1%}",
            f"  adults 25+ never married share={self.never_married_adults_25_plus_share:.1%}",
            f"  marriage events={self.marriage_events} mean age first marriage="
            f"{self.mean_age_at_first_marriage if self.mean_age_at_first_marriage is not None else 'n/a'}",
            "  deaths by age bucket:",
        ]
        for bucket, count in sorted(self.death_age_counts.items()):
            lines.append(f"    {bucket}: {count}")
        return "\n".join(lines)


def _age_bucket(age: int) -> str:
    if age < 5:
        return "0-4"
    if age < 15:
        return "5-14"
    if age < 25:
        return "15-24"
    if age < 40:
        return "25-39"
    if age < 55:
        return "40-54"
    if age < 70:
        return "55-69"
    return "70+"


def analyze_demography(world: WorldState) -> DemographyReport:
    years = world.day / 365.0
    births = [e for e in world.events if e.kind == EventKind.BIRTH]
    deaths = [e for e in world.events if e.kind == EventKind.DEATH]
    marriages = [e for e in world.events if e.kind == EventKind.MARRIAGE]

    births_by_mother: Counter[str] = Counter()
    for e in births:
        if e.actor_id:
            births_by_mother[e.actor_id] += 1

    first_marriage_day: dict[str, int] = {}
    for e in marriages:
        for cid in (e.actor_id, e.target_id):
            if cid and cid not in first_marriage_day:
                first_marriage_day[cid] = e.day

    married_woman_ids = {
        cid
        for cid, c in world.characters.items()
        if c.sex == Sex.FEMALE and births_by_mother[cid] > 0
    }
    married_woman_ids.update(
        cid
        for cid in first_marriage_day
        if world.characters.get(cid) and world.characters[cid].sex == Sex.FEMALE
    )

    woman_years_married = 0.0
    for cid in married_woman_ids:
        c = world.characters[cid]
        start = first_marriage_day.get(cid, 0)
        end = c.death_day if c.death_day is not None else world.day
        woman_years_married += max(0, end - start) / 365.0

    total_maternal_births = sum(births_by_mother.values())
    mean_bpw = (
        total_maternal_births / woman_years_married if woman_years_married > 0 else 0.0
    )

    death_ages: Counter[str] = Counter()
    under5_deaths = 0
    for e in deaths:
        age = int(e.effects.get("age", -1))
        if age >= 0:
            death_ages[_age_bucket(age)] += 1
            if age < 5:
                under5_deaths += 1

    first_marriage_ages: list[float] = []
    for cid, day in first_marriage_day.items():
        c = world.characters.get(cid)
        if not c:
            continue
        age_at = c.age_years - (world.day - day) / 365.0
        if age_at >= 0:
            first_marriage_ages.append(age_at)

    mean_first_marriage = (
        sum(first_marriage_ages) / len(first_marriage_ages) if first_marriage_ages else None
    )

    fertile = [
        c
        for c in world.living_characters()
        if c.sex == Sex.FEMALE and 18 <= c.age_years <= 42
    ]
    fertile_married = sum(1 for c in fertile if c.spouse_id is not None)
    share_fertile_married = fertile_married / len(fertile) if fertile else 0.0

    adults_25_plus = [
        c for c in world.living_characters() if c.age_years >= 25
    ]
    never_married = sum(
        1
        for c in adults_25_plus
        if c.id not in first_marriage_day and c.spouse_id is None
    )
    never_married_share = never_married / len(adults_25_plus) if adults_25_plus else 0.0

    infant_share = under5_deaths / len(births) if births else 0.0

    return DemographyReport(
        seed=world.seed,
        years=years,
        living=len(world.living_characters()),
        total_births=len(births),
        total_deaths=len(deaths),
        mean_births_per_married_woman_per_year=mean_bpw,
        death_age_counts=dict(death_ages),
        marriage_events=len(marriages),
        mean_age_at_first_marriage=mean_first_marriage,
        infant_child_mortality_share=infant_share,
        share_fertile_women_married=share_fertile_married,
        never_married_adults_25_plus_share=never_married_share,
    )
