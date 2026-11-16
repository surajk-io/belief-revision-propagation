# Directed controls — h03

## control_h03_15_B

To estimate the chance of finding a treasure chest, we need to consider both foggy and clear maps.

Let's define:
- P(F) = probability of a foggy map = 0.15
- P(C) = probability of a clear map = 1 - P(F) = 0.85
- P(T|F) = probability of treasure given foggy map = 0.24
- P(T|C) = probability of treasure given clear map = 0.76

The probability of finding a treasure chest is:
P(T) = P(T|F) * P(F) + P(T|C) * P(C)
= 0.24 * 0.15 + 0.76 * 0.85
= 0.036 + 0.646
= 0.682

So, the chance of finding a treasure chest on this run is approximately 68.2%.

## control_h03_15_C

To estimate the chance of unlocking a bonus room, we need to calculate the probability of finding treasure and then use that to find the probability of unlocking a bonus room.

Let's define:
- P(F) = probability of a foggy map = 0.15
- P(C) = probability of a clear map = 1 - P(F) = 0.85
- P(T|F) = probability of finding treasure given foggy map = 0.24
- P(T|C) = probability of finding treasure given clear map = 0.76

First, we calculate the probability of finding treasure:
P(T) = P(T|F) * P(F) + P(T|C) * P(C)
= 0.24 * 0.15 + 0.76 * 0.85
= 0.036 + 0.646
= 0.682

Now, we can calculate the probability of unlocking a bonus room:
P(B) = P(B|T) * P(T) + P(B|not T) * P(not T)
= 0.83 * 0.682 + 0.12 * (1 - 0.682)
= 0.56586 + 0.12 * 0.318
= 0.56586 + 0.03816
= 0.60402

So, the chance of unlocking a bonus room on this run is approximately 60.4%.

## control_h03_69_B

To estimate the chance of finding a treasure chest, we need to calculate the weighted probability of finding treasure on a foggy map and a clear map.

Let's define:
- P(F) = probability of a foggy map = 0.69
- P(C) = probability of a clear map = 1 - P(F) = 0.31
- P(T|F) = probability of finding treasure given foggy map = 0.24
- P(T|C) = probability of finding treasure given clear map = 0.76

The probability of finding treasure is:
P(T) = P(T|F) * P(F) + P(T|C) * P(C)
= 0.24 * 0.69 + 0.76 * 0.31
= 0.1656 + 0.2356
= 0.4012

So, the chance of finding a treasure chest on this run is approximately 40.1%.

## control_h03_69_C

To estimate the chance of unlocking a bonus room, we need to calculate the probability of finding treasure and then use that to find the probability of unlocking the bonus room.

Let's define:
- P(F) = probability of a foggy map = 0.69
- P(C) = probability of a clear map = 1 - P(F) = 0.31
- P(T|F) = probability of finding treasure given foggy map = 0.24
- P(T|C) = probability of finding treasure given clear map = 0.76

First, we calculate the probability of finding treasure:
P(T) = P(T|F) * P(F) + P(T|C) * P(C)
= 0.24 * 0.69 + 0.76 * 0.31
= 0.1656 + 0.2356
= 0.4012

Now, we know that we unlock a bonus room on 83% of runs where we find treasure and 12% otherwise. 
P(B|T) = 0.83 (probability of bonus room given treasure)
P(B|not T) = 0.12 (probability of bonus room given no treasure)

The probability of unlocking a bonus room is:
P(B) = P(B|T) * P(T) + P(B|not T) * P(not T)
= 0.83 * 0.4012 + 0.12 * (1 - 0.4012)
= 0.3330 + 0.12 * 0.5988
= 0.3330 + 0.0719
= 0.4049

So, the chance of unlocking a bonus room on this run is approximately 40.5%.
