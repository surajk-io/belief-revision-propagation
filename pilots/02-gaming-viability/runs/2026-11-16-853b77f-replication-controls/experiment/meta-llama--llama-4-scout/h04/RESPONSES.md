# Directed controls — h04

## control_h04_15_B

To estimate the chance of finding a treasure chest, we need to consider both foggy and clear maps.

Let's define:
- P(F) = probability of a foggy map = 0.15
- P(C) = probability of a clear map = 1 - P(F) = 0.85
- P(T|F) = probability of finding treasure given a foggy map = 0.24
- P(T|C) = probability of finding treasure given a clear map = 0.76

The probability of finding a treasure chest is:
P(T) = P(T|F) * P(F) + P(T|C) * P(C)
= 0.24 * 0.15 + 0.76 * 0.85
= 0.036 + 0.646
= 0.682

So, the chance of finding a treasure chest on this run is approximately 68.2%.

## control_h04_15_C

To estimate the chance of unlocking a bonus room, we need to calculate the probability of finding treasure and then use that to find the probability of unlocking the bonus room.

Let's define:
- P(F) = probability of a foggy map = 0.15
- P(C) = probability of a clear map = 1 - P(F) = 0.85
- P(T|F) = probability of finding treasure given a foggy map = 0.24
- P(T|C) = probability of finding treasure given a clear map = 0.76

First, we calculate the probability of finding treasure:
P(T) = P(T|F) * P(F) + P(T|C) * P(C)
= 0.24 * 0.15 + 0.76 * 0.85
= 0.036 + 0.646
= 0.682

Now, we can calculate the probability of unlocking the bonus room:
P(B) = P(B|T) * P(T) + P(B|not T) * P(not T)
= 0.83 * 0.682 + 0.12 * (1 - 0.682)
= 0.56546 + 0.12 * 0.318
= 0.56546 + 0.03816
= 0.60362

So, the chance of unlocking a bonus room on this run is approximately 60.4%.

## control_h04_69_B

To estimate the chance of finding a treasure chest, we need to combine the probabilities of a foggy or clear map and the corresponding probabilities of finding a treasure chest.

Let's define:
- P(F) = probability of a foggy map = 0.69
- P(C) = probability of a clear map = 1 - P(F) = 0.31
- P(T|F) = probability of finding treasure given a foggy map = 0.24
- P(T|C) = probability of finding treasure given a clear map = 0.76

The probability of finding a treasure chest is:
P(T) = P(T|F) * P(F) + P(T|C) * P(C)
= 0.24 * 0.69 + 0.76 * 0.31
= 0.1656 + 0.2356
= 0.4012

So, the chance of finding a treasure chest on this run is approximately 40.1%.

## control_h04_69_C

To estimate the chance of unlocking a bonus room, we need to calculate the probability of finding treasure and then use that to find the probability of unlocking the bonus room.

Let's define:
- P(F) = probability of a foggy map = 0.69
- P(C) = probability of a clear map = 1 - P(F) = 0.31
- P(T|F) = probability of finding treasure given a foggy map = 0.24
- P(T|C) = probability of finding treasure given a clear map = 0.76
- P(B|T) = probability of unlocking bonus room given treasure = 0.83
- P(B|not T) = probability of unlocking bonus room given no treasure = 0.12

First, we calculate the probability of finding treasure:
P(T) = P(T|F) * P(F) + P(T|C) * P(C)
= 0.24 * 0.69 + 0.76 * 0.31
= 0.1656 + 0.2356
= 0.4012

Now, we can calculate the probability of unlocking the bonus room:
P(B) = P(B|T) * P(T) + P(B|not T) * (1 - P(T))
= 0.83 * 0.4012 + 0.12 * (1 - 0.4012)
= 0.83 * 0.4012 + 0.12 * 0.5988
= 0.3330 + 0.0718
= 0.4048

So, the chance of unlocking a bonus room on this run is approximately 40.5%.
