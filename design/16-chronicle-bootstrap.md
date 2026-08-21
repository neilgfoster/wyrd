# Wyrd — starting a chronicle

A chronicle is created by **cloning a template and running a bootstrap**. The result is a
single self-contained repository that carries its own copy of the engine and the setting, so
it can be played, archived or moved without depending on anything else being present.

---

## The flow

```
gh repo create my-chronicle --private --template neilgfoster/wyrd-chronicle-template
cd my-chronicle
./bootstrap
```

The bootstrap:

1. **Asks which setting.** Offers the catalogue ([`settings.yaml`](../settings.yaml)); private
   settings appear only if the user can reach them.
2. **Copies the engine** at a chosen version into `engine/`.
3. **Overlays the setting** at a chosen version into `setting/`.
4. **Interviews the player.** Guided character creation using the setting's careers, names and
   calendar — and, separately, the *campaign* questions: what kind of chronicle do you want,
   what do you want it to be about, what would you like to avoid, how long are your sessions.
5. **Seeds the world.** Picks an opening situation matching the answers, sets the calendar,
   selects the threats that will run in the background at the start, and connects at least
   one to the character. Most threats in a long chronicle are not seeded here — they are
   provoked or made in play ([`05-campaign.md`](05-campaign.md)).
6. **Writes and commits** `chronicle.yaml`, the player character, the opening threads,
   `overlay/`, and the first `recap.md`.

After bootstrap the repo is self-sufficient. `/wyrd-play` needs nothing else.

## What the interview asks

Character creation is the obvious half. The campaign half matters more and is usually
skipped by tooling:

- **What do you want this to be about?** Revenge, survival, a place, a person, a question.
- **What would you like to avoid?** Recorded and honoured. This is a safety tool and a taste
  tool at once.
- **How long is a typical session?** Sets the default beat pacing.
- **How lethal?** Sets starting Fate and whether the Aftermath table is used as written.
- **Should the world act when you are not looking?** Sets whether threats activate during
  spans of *game* time the character did not witness ([`05-campaign.md`](05-campaign.md)).
  This is nothing to do with real-world time between sessions, which never advances the
  world.

Answers are written to `chronicle.yaml` as `intent:` and are read every session. They are the
closest thing Wyrd has to a session-zero conversation, and they are revisable.

## Version pinning

```yaml
engine: {repo: wyrd, version: 0.4.0}
setting: {repo: wyrd-<setting>, version: 0.3.1}
```

Both are **copies**, not references. A chronicle does not break because an upstream repo
changed, and there is no network dependency at play time.

Updating is explicit and per-source:

```
wyrd update --engine 0.5.0      # migrations run; classified per 09-evolution
wyrd update --setting 0.4.0     # new content merges; overlay is preserved
```

A setting update is nearly always additive — more beats, more characters, another adventure
converted. The chronicle's `overlay/` is never touched by either
([`14-entities.md`](14-entities.md)).

Declining an update forever is legitimate. A chronicle two years deep on an old engine is a
valid chronicle.

## Layout after bootstrap

```
my-chronicle/
├─ chronicle.yaml      # setting, versions, calendar, era, intent
├─ engine/             # copied. Do not edit.
├─ setting/            # copied. Do not edit — write overlays instead.
├─ overlay/            # what this chronicle has changed about the world
├─ entities/           # entities this chronicle created, including the PC
├─ overlay/            # deltas to setting entities
├─ log/
└─ recap.md
```

The whole thing is an Obsidian vault. `setting/`, `overlay/` and `entities/` are all entity
files, so the graph view shows the world *and* what the player has done to it.
