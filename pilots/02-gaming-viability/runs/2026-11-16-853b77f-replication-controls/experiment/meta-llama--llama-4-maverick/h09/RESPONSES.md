# Directed controls — h09

## control_h09_15_B

To determine the probability of finding a treasure chest, we need to consider the probability of a foggy map and a clear map, and their respective probabilities of having a treasure chest.

Given:
- P(Foggy) = 0.15
- P(Clear) = 1 - P(Foggy) = 0.85
- P(Treasure|Foggy) = 0.24
- P(Treasure|Clear) = 0.76

P(Treasure) = P(Treasure|Foggy) * P(Foggy) + P(Treasure|Clear) * P(Clear)
= 0.24 * 0.15 + 0.76 * 0.85
= 0.036 + 0.646
= 0.682

So, our chances of finding a treasure chest are approximately 68.2%.

## control_h09_15_C

To determine the probability of unlocking a bonus room, we need to first find the probability of finding treasure.

Given P(Foggy) = 0.15, we can find P(Clear) = 1 - 0.15 = 0.85.

P(Treasure) = P(Treasure|Foggy) * P(Foggy) + P(Treasure|Clear) * P(Clear)
= 0.24 * 0.15 + 0.76 * 0.85
= 0.036 + 0.646
= 0.682

P(Bonus Room) = P(Bonus Room|Treasure) * P(Treasure) + P(Bonus Room|No Treasure) * P(No Treasure)
= 0.83 * 0.682 + 0.12 * (1 - 0.682)
= 0.566 + 0.12 * 0.318
= 0.566 + 0.0382
= 0.6042

So, our chances of unlocking a bonus room are approximately 60.4%.

## control_h09_69_B

To determine the probability of finding a treasure chest, we need to consider the probability of a foggy map and the given probabilities of finding treasure in foggy and clear maps.

Given:
- P(Foggy) = 0.69
- P(Clear) = 1 - P(Foggy) = 0.31
- P(Treasure|Foggy) = 0.24
- P(Treasure|Clear) = 0.76

P(Treasure) = P(Treasure|Foggy) * P(Foggy) + P(Treasure|Clear) * P(Clear)
= 0.24 * 0.69 + 0.76 * 0.31
= 0.1656 + 0.2356
= 0.4012

So, our chances of finding a treasure chest are approximately 40.1%.

## control_h09_69_C

To determine the probability of unlocking a bonus room, we first need to find the probability of finding treasure.

Given P(Foggy) = 0.69, we can find P(Clear) = 1 - 0.69 = 0.31.

P(Treasure) = P(Treasure|Foggy) * P(Foggy) + P(Treasure|Clear) * P(Clear)
= 0.24 * 0.69 + 0.76 * 0.31
= 0.1656 + 0.2356
= 0.4012

P(Bonus Room) = P(Bonus Room|Treasure) * P(Treasure) + P(Bonus Room|No Treasure) * P(No Treasure)
= 0.83 * 0.4012 + 0.12 * (1 - 0.4012)
= 0.3330 + 0.12 * 0.5988
= 0.3330 + 0.0719
= 0.4049

So, our chances of unlocking a bonus room are approximately 40.5%.
