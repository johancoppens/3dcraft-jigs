# Form test

I want a small side table for the corner of our living room: a round top about 45 cm across, standing 55 cm high, cut
from 18 mm walnut-veneered plywood, and four cables holding it down, leaning a little outward at the bottom (about 30 mm). There will be a heavy plant on it, about 6 kg, and I expect it to end up right at
the edge at some point. I have the thin rope and small fittings at home (2 mm outer cables). My router has a 6 mm bit.
What do I cut, what do I tension the cables to, and what will it weigh? My nephew also wants to climb on it: 80 kg.

## Acceptance

- A round top 450 mm across at 550 mm high, with four outer cables and the Light rope set (2 mm outer ropes, 3 mm central),
  walnut veneer, 18 mm plywood, 6 mm bit, the load set to 6 kg. Cable lean 30 mm (a small setting; the form's other values at their defaults). Every assertion passes.
- The form says: tensioned for 6 kg, the most it can be set for 8 kg; each outer cable tensioned to about 72 N, about half a
  turn of each turnbuckle past just-taut and never past about 0.7 turn; a proof test with the 6 kg lowered gently onto the edge, hands
  and feet clear; a cable goes slack above about 8.8 kg at the edge at that tension; largest outer tension
  about 107 N against a 405 N working limit; the central rope about 376 N against about 479 N for the central path.
- The table weighs about 7 kg; sideways it moves about 2.9 mm under a 10 N push across the hooks and tips over at about 31 N at
  the top.
- Rope lengths between eyes: lower outer about 74 mm, upper outer about 207 mm, central about 88 mm.
- The cut sheet exports (SVG or DXF, the set *Cut sheet*): two plates and two hooks at true size, with holes and slots.
- Refusal: 80 kg cannot be set; the load stops at the form's limit of 8 kg (or `param.set` refuses it with that range).
