from __future__ import annotations

import streamlit as st

from chronicle.character_ai.traits import derived_highlights, normalize_core_traits
from chronicle.generation.realm import generate_world
from chronicle.history.chronicle import render_recent_chronicle
from chronicle.history.story import story_importance
from chronicle.history.threads import (
    build_causal_thread,
    format_thread_line,
    recent_story_threads,
)
from chronicle.models.house import TitleKind
from chronicle.persistence.sqlite_store import load_world, save_world
from chronicle.simulation.engine import SimulationEngine


def _ensure_state() -> None:
    if "world" not in st.session_state:
        loaded = load_world()
        st.session_state.world = loaded or generate_world(seed=42, population_target=200)
        st.session_state.engine = SimulationEngine(st.session_state.world)


def _character_options():
    world = st.session_state.world
    living = sorted(world.living_characters(), key=lambda c: c.name)
    return {f"{c.name} ({c.age_years}, {c.role})": c.id for c in living}


def main() -> None:
    st.set_page_config(page_title="The Chronicle", layout="wide")
    st.title("The Chronicle")
    st.caption("A living medieval realm — simulation first, spectacle second.")

    _ensure_state()
    world = st.session_state.world
    engine: SimulationEngine = st.session_state.engine

    col_time, col_save = st.columns([3, 1])
    with col_time:
        c1, c2, c3, c4, c5 = st.columns(5)
        if c1.button(" +1 day"):
            engine.tick()
        if c2.button(" +7 days"):
            engine.advance_days(7)
        if c3.button(" +30 days"):
            engine.advance_days(30)
        if c4.button(" +1 year"):
            engine.advance_days(365)
        if c5.button("New world (seed 42)"):
            st.session_state.world = generate_world(seed=42, population_target=200)
            st.session_state.engine = SimulationEngine(st.session_state.world)
            st.rerun()
    with col_save:
        if st.button("Save to SQLite"):
            save_world(st.session_state.world)
            st.success("Saved.")

    year = world.day // 365
    day_of_year = world.day % 365
    living = len(world.living_characters())
    st.metric(
        "Realm date",
        f"Year {year + 1}, day {day_of_year + 1}",
        f"{living} living souls · {len(world.events)} recorded events",
    )

    left, right = st.columns([1, 1])

    with left:
        st.subheader("Realm hierarchy")
        _render_hierarchy(world)
        st.subheader("Living chronicle")
        named_only = st.checkbox("Named cast only", value=False)
        for line in render_recent_chronicle(world, limit=35, named_cast_only=named_only):
            st.write(line)

        st.subheader("Story threads")
        threads = recent_story_threads(world, limit=4, min_length=2)
        if not threads:
            st.caption("No multi-step social threads yet — feuds and responses will appear here.")
        for idx, thread in enumerate(threads, start=1):
            with st.expander(f"Thread {idx} ({len(thread)} events)", expanded=idx == 1):
                for line in [format_thread_line(world, e) for e in thread]:
                    st.write(line)

    with right:
        st.subheader("Follow a life")
        options = _character_options()
        if not options:
            st.info("No living characters.")
            return
        label = st.selectbox("Character", list(options.keys()))
        char = world.characters[options[label]]

        st.markdown(f"**{char.name}** · {char.sex.value} · age {char.age_years}")
        st.write(f"Role: {char.role} · House: {_house_label(world, char.house_id)}")
        if char.spouse_id and char.spouse_id in world.characters:
            st.write(f"Spouse: {world.characters[char.spouse_id].name}")
        if char.parent_ids:
            parents = [world.characters[pid].name for pid in char.parent_ids if pid in world.characters]
            st.write(f"Parents: {', '.join(parents) or 'unknown'}")

        st.caption(f"Story importance: {story_importance(world, char.id):.2f}")
        if char.tags:
            st.write("Tags:", ", ".join(char.tags))
        highlights = derived_highlights(char.traits)
        if highlights:
            st.write("Highlights:", ", ".join(highlights))
        st.write("Core temperament")
        cores = normalize_core_traits(char.traits)
        trait_items = sorted(cores.items(), key=lambda x: -x[1])[:8]
        for trait, value in trait_items:
            st.progress(min(1.0, max(0.0, value)), text=f"{trait}: {value:.2f}")
        if char.goals:
            st.write("Active goals:")
            for goal in sorted(char.goals, key=lambda g: -g.priority)[:5]:
                target_label = ""
                if goal.target_id and goal.target_id in world.characters:
                    target_label = f" → {world.characters[goal.target_id].name}"
                elif goal.target_id and goal.target_id in world.houses:
                    target_label = f" → {world.houses[goal.target_id].name}"
                st.caption(f"{goal.kind}{target_label} (priority {goal.priority:.2f})")
        claims = [c for c in world.claims.values() if c.character_id == char.id]
        if claims:
            st.write("Claims:")
            for claim in claims[:5]:
                title = world.titles.get(claim.title_id)
                st.caption(f"→ {title.name if title else claim.title_id} ({claim.reason})")

        if char.memories:
            st.subheader("Memories")
            for mem in sorted(char.memories, key=lambda m: (-m.day, -m.severity))[:8]:
                tags = ", ".join(mem.emotional_tags) if mem.emotional_tags else "—"
                st.caption(
                    f"Day {mem.day} · severity {mem.severity:.2f} · {tags}: {mem.summary}"
                )
                if mem.source_event_id:
                    thread = build_causal_thread(world, mem.source_event_id, max_nodes=6)
                    if len(thread) > 1:
                        for line in [format_thread_line(world, e) for e in thread]:
                            st.text(f"  {line}")

        st.subheader("Relationships (outgoing)")
        rels = [
            r
            for k, r in world.relationships.items()
            if r.from_id == char.id and (r.affection > 60 or r.resentment > 40 or r.trust < 40)
        ]
        rels.sort(key=lambda r: -(r.resentment + r.affection))
        for rel in rels[:8]:
            other = world.characters.get(rel.to_id)
            if not other:
                continue
            st.write(
                f"→ **{other.name}**: affection {rel.affection:.0f}, "
                f"trust {rel.trust:.0f}, resentment {rel.resentment:.0f}"
            )

        st.subheader("Events involving this character")
        related = [
            e
            for e in reversed(world.events)
            if e.actor_id == char.id or e.target_id == char.id or char.id in e.participant_ids
        ][:15]
        for e in related:
            st.caption(f"Day {e.day} · {e.kind.value}: {e.summary or '(no summary)'}")


def _render_hierarchy(world) -> None:
    county = world.titles.get(world.realm.county_title_id)
    if county:
        holder = world.characters.get(county.holder_id or "")
        st.write(f"**County:** {county.name} — {holder.name if holder else 'vacant'}")
    for title in sorted(world.titles.values(), key=lambda t: t.name):
        if title.kind != TitleKind.LORDSHIP:
            continue
        holder = world.characters.get(title.holder_id or "")
        st.write(f"  Lordship: {title.name} — {holder.name if holder else 'vacant'}")
    for house in sorted(world.houses.values(), key=lambda h: h.name):
        head = world.characters.get(house.head_character_id or "")
        st.write(f"  House {house.name} — {head.name if head else 'vacant'}")


def _house_label(world, house_id: str | None) -> str:
    if not house_id:
        return "—"
    return world.houses[house_id].name


if __name__ == "__main__":
    main()
