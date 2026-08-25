# A crowd fight, played out

Run against the drafted crowd rule before it was settled. The engine has been playtested once, and
that session corrected the resolution mechanic three times inside two rolls; the sequencing feature
found three missing rules the same way. This is the same exercise for the crowd rule.

**Not a probability check.** The numbers live in [`check_mobs.py`](check_mobs.py). This is here to
find the questions the rule does not answer, and it found four.

## The scene

A yard behind a warehouse. Three characters, cornered by a gang and the person who sent them.

| | Skill | Stamina | Armour |
|---|---|---|---|
| **The player's character** | 45% | 6 | modest |
| **First companion** | 35% | 6 | light |
| **Second companion** | 25% | 6 | none |
| **The one who sent them** | 45% | 6 | light |
| **Nine of the gang**, each | untrained, 10% | 1 | none |

The gang qualifies on all three tests: Stamina 1, no armour, and 20 or more points below every
character's skill — except the second companion, at 25%, who is only 15 points ahead. **The second
companion clears nobody.** That fell out of the rule without anyone deciding it, which is what a
lookup is supposed to feel like.

The one who sent them qualifies on nothing. Stamina 6 alone disqualifies them, and they remain an
opponent who has to be fought.

## Round one

The gang started it, so they act first (ADR 0018). Nine bodies, three targets: three each, which is
exactly the ceiling. Each character takes **one** attack at 10% eased by +20 — the crowd at 30%.

Rolls: 71 against the player's character (miss), 22 against the first companion (hit, 4 damage,
1 through light armour), 68 against the second (miss).

The characters answer. Each clears at the start of their turn:

- **The player's character** clears one body, then attacks the one who sent them. 45% against 45%,
  rolls 31 — one degree; the resister rolls 12, two degrees. Ties and betters go to the resisting
  side. No effect.
- **The first companion** clears one body, then closes with the gang.
- **The second companion** clears nothing and attacks a gang member: 25% against 10%, rolls 09.
  A hit, and 4 damage takes a Stamina-1 body well below zero. Out of action.

Seven left. **The second companion removed a body by rolling for it, in the same round the others
removed theirs for free.** That is the rule working as designed: the free clear is not a different
outcome, it is the same outcome without the roll.

## Round two

Seven bodies, three targets. The GM puts three on the player's character, three on the first
companion, one on the second — the last of those at a flat 10%, no easing, and it misses.

Three characters, two clears. Five left. The player's character lands on the one who sent them this
time: three degrees, a telling blow, doubled damage, 5 through light armour. One point of Stamina
left.

## Round three

Five bodies. Two clears, and the second companion drops another with a roll. Two left, and the one
who sent them goes down to the player's character.

The remaining two run. Nobody rolls anything for it.

## What the play found

**One.** *Nothing in the drafted rule said the character had to be engaged with the crowd.* As
written, a character could stand at the far side of the yard shooting and still clear a body a round
by existing. Fixed: **the clear requires close engagement with the crowd.**

**Two.** *Nothing said whether companions clear.* They are characters, so they do — but the rule
said "a character" and left it to be argued. Fixed: stated as each character **and companion**.

**Three.** *Breaking off from a crowd reintroduced the roll the rule exists to remove.* Every
opponent still engaged attacks a departing combatant (ADR 0018), and with seven bodies that is seven
parting blows. Fixed: **a crowd's parting blow is one attack on the same terms as its turn.**

**Four.** *The second companion is the interesting case and nearly did not exist.* At 25% they are
15 points ahead of an untrained gang member — inside the crowd's own definition, outside the rule's
reach. Rolling for each body they wanted to remove felt like a penalty in play, and it is the
correct one: the rule is for characters who are plainly better than what they are wading through,
and they are not yet. Nothing was changed.

None of the first three was visible while the rule was being written.
