# Directed controls — h11

## control_h11_15_B

Given:

- P(Foggy) = 0.15
- P(Clear) = 0.85
- P(Treasure | Foggy) = 0.24
- P(Treasure | Clear) = 0.76

Calculate overall chance of treasure:

\[
P(Treasure) = P(Treasure | Foggy) \times P(Foggy) + P(Treasure | Clear) \times P(Clear)
\]

\[
= 0.24 \times 0.15 + 0.76 \times 0.85 = 0.036 + 0.646 = 0.682
\]

**Answer:** About 68.2% chance of finding a treasure chest on this run.

## control_h11_15_C

Given:

- P(Foggy) = 0.15, so P(Clear) = 0.85
- P(Treasure | Foggy) = 0.24
- P(Treasure | Clear) = 0.76
- P(Bonus | Treasure) = 0.83
- P(Bonus | No Treasure) = 0.12

First, find overall P(Treasure):

\[
P(Treasure) = P(Treasure | Foggy) \times P(Foggy) + P(Treasure | Clear) \times P(Clear) = 0.24 \times 0.15 + 0.76 \times 0.85 = 0.036 + 0.646 = 0.682
\]

Then, P(No Treasure) = 1 - 0.682 = 0.318

Now, overall P(Bonus):

\[
P(Bonus) = P(Bonus | Treasure) \times P(Treasure) + P(Bonus | No Treasure) \times P(No Treasure) = 0.83 \times 0.682 + 0.12 \times 0.318 = 0.566 + 0.038 = 0.604
\]

**Answer:** About 60.4% chance of unlocking a bonus room on this run.

## control_h11_69_B

Given:

- P(Foggy) = 0.69
- P(Clear) = 1 - 0.69 = 0.31
- P(Treasure | Foggy) = 0.24
- P(Treasure | Clear) = 0.76

We want P(Treasure):

\[
P(Treasure) = P(Treasure | Foggy) \times P(Foggy) + P(Treasure | Clear) \times P(Clear)
\]

Calculate:

\[
= 0.24 \times 0.69 + 0.76 \times 0.31 = 0.1656 + 0.2356 = 0.4012
\]

**Answer:** About 40.1% chance of finding a treasure chest on this run.

## control_h11_69_C

Given:

- P(Foggy) = 0.69, so P(Clear) = 0.31
- P(Treasure | Foggy) = 0.24
- P(Treasure | Clear) = 0.76
- P(Bonus | Treasure) = 0.83
- P(Bonus | No Treasure) = 0.12

First, find overall P(Treasure):

\[
P(Treasure) = P(Treasure | Foggy) \times P(Foggy) + P(Treasure | Clear) \times P(Clear) = 0.24 \times 0.69 + 0.76 \times 0.31 = 0.1656 + 0.2356 = 0.4012
\]

Then, P(No Treasure) = 1 - 0.4012 = 0.5988

Now, overall P(Bonus):

\[
P(Bonus) = P(Bonus | Treasure) \times P(Treasure) + P(Bonus | No Treasure) \times P(No Treasure) = 0.83 \times 0.4012 + 0.12 \times 0.5988 = 0.3329 + 0.0719 = 0.4048
\]

**Answer:** About 40.5% chance of unlocking a bonus room on this run.
