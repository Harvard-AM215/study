---
kernelspec:
  name: python3
  display_name: Python 3
---

# Chapter 4: Tournaments & Stochastic Simulation

> When a random process is a tree of binary outcomes, as in a single-elimination tournament, Monte Carlo simulation is one practical way to replace exhaustive enumeration with a cheap loop and put numbers on questions such as how much the bracket draw matters.

:::{note} Running the code
The Python cells on this page run **in your browser**. Click the **power icon** at the top of the page to activate the kernel, then run — or edit — any cell. Packages (NumPy, SciPy, …) load automatically the first time you import them (a few seconds).
:::

## Motivation

Take a 64-team single-elimination basketball tournament: six rounds and 63 games. Suppose you have a model for every pairwise matchup, say "Duke beats Kentucky 65% of the time". What is the probability that each team wins the whole thing?

In principle you could list all $2^{63} \approx 10^{19}$ possible sets of game outcomes, compute the probability of each, and add up the ones in which a given team ends as champion. That exhaustive calculation is completely infeasible. One practical alternative is simulation: play out one bracket by drawing each game's winner at random with the model's probability, repeat many times, and count how often each team ends as champion. A million simulated brackets take a few minutes on a laptop, and Chapter 3 tells you how precise the resulting frequencies are.

This is the first substantial application of the Monte Carlo method of Chapter 3. It is also the book's first **path-dependent** stochastic process: who a team plays in round 3 depends on who won in rounds 1 and 2. The chapters on random walks, geometric Brownian motion, and option pricing follow the same pattern: a sequence of random steps, then a question about where the sequence ends up.

## Setup & notation

A single-elimination tournament with $n$ teams, where $n$ is a power of 2, lasts $\log_2 n$ rounds, and each round halves the field. We need to specify two things:

- **The bracket** and the **initial draw**: which teams meet in round 1, and how the winners are paired in each later round. We treat the draw as fixed for any one tournament, and later ask what changes when it varies.
- **The matchup matrix** $P$: an $n \times n$ matrix whose entry $P_{ij}$ is the probability that team $i$ beats team $j$ when they meet.

We assume $P_{ji} = 1 - P_{ij}$, so one of the two teams must win. Nothing besides the pairing, such as a home-court advantage, affects the game. This leaves $\binom{n}{2}$ free probabilities, one per pair. We also assume that games are independent given $P$: a team's chance in the final does not depend on how hard its semifinal was. Both assumptions, and many others left implicit, can be questioned. Exercise 6 asks where the second one fails.

Each game is then a Bernoulli trial with success probability $P_{ij}$, and the bracket determines which trials happen. The new symbols for this chapter are:

- $P_{ij}$: the probability that team $i$ defeats team $j$ in one game.
- $w_i$: the true (unknown) probability that team $i$ wins the championship.
- $\hat w_i$: a Monte Carlo estimate of $w_i$ from $N$ simulated tournaments.

## Core ideas

### Why simulation?

With 4 teams there are 3 games and $2^3 = 8$ possible outcome sequences, each with a probability you can write down, so $w_i$ has a closed form. With 64 teams there are $2^{63}$ sequences and no hope of listing them. Monte Carlo offers one feasible route around that enumeration: the standard error of an estimated probability is $\sqrt{w_i(1-w_i)/N}$ regardless of how many games each simulated tournament contains. A million simulations give a standard error of at most $0.0005$ for any bracket size. The cost of each simulation, on the other hand, does grow with bracket size. This route trades exactness for tractability, and for questions such as "how likely is this team to win" the precision is often more than enough.

### The simulation loop

One simulated tournament is a loop over rounds. Keep a list of surviving teams in bracket order. In each round: pair them off, draw each winner with the matchup probability, and keep the winners in order for the next round. In pseudocode:

```
def simulate_tournament(draw, P, rng):
    survivors = list(draw)
    while len(survivors) > 1:
        next_round = []
        for (i, j) in pair_up(survivors):
            winner = i if rng.uniform() < P[i, j] else j
            next_round.append(winner)
        survivors = next_round
    return survivors[0]   # champion
```

Run this $N$ times and count championships. Team $i$'s estimated win probability is $\hat w_i$, the fraction of simulated tournaments it won. This is the hit-counting estimator of Chapter 3, so its standard error is $\sqrt{\hat w_i (1 - \hat w_i) / N}$. Worked Example 1 runs it and checks it against the closed form.

### The effect of the draw

The first thing you notice when you simulate is that **the same matchup matrix gives different championship probabilities under different draws**. A team that meets the strongest opponent in round 1 has a very different path than one that meets the weakest. To measure how much this matters, hold $P$ fixed, sample many random draws, estimate $w_i$ under each, and look at the spread across draws.

That spread has two sources, and separating them is the point of Worked Example 2. Part of it is Monte Carlo noise from the finite number of simulations per draw, which Chapter 3's standard error quantifies. The rest is the genuine effect of the bracket. For real tournaments, where a committee builds the draw from seeds rather than at random, the same comparison tests whether seeding gives top teams an advantage beyond what their matchup probabilities already imply. Exercise 1 asks you to design that test.

### The Bradley–Terry model and Elo updates

Nobody hands you $P$. With $n$ teams it has $\binom{n}{2}$ free entries, and most pairs have played each other rarely or never, so separate head-to-head estimates would be extremely noisy. The **Bradley–Terry model** replaces those pair-specific parameters with one rating $R_i$ per team:

$$
P_{ij}
= \sigma(R_i-R_j),
\qquad
\sigma(x)=\frac{1}{1+e^{-x}}.
$$

The model depends only on the rating gap. Equal ratings give $P_{ij}=1/2$, a large positive gap makes team $i$ very likely to win, and $P_{ji}=1-P_{ij}$ holds automatically because $\sigma(-x)=1-\sigma(x)$. It also pools information: a game between teams $i$ and $j$ helps estimate both ratings, which in turn inform their probabilities against every other team.

To fit all ratings at once, let $S=1$ if team $i$ beat team $j$ and $S=0$ otherwise. That game contributes

$$
S\log P_{ij}+(1-S)\log(1-P_{ij})
$$

to the log-likelihood. Summing this expression over the observed games and maximizing it gives the batch maximum-likelihood fit. There is no closed-form solution, so the maximization is numerical. Only differences between ratings are identifiable: adding the same constant to every $R_i$ changes no probability. We therefore fix one rating or impose a constraint such as $\sum_i R_i=0$, leaving $n-1$ free parameters.

**Elo scores use the same logistic probability model with an online update rule.** On the conventional Elo scale,

$$
P_{ij}
= \frac{1}{1+10^{(R_j-R_i)/400}}
= \sigma\!\left((R_i-R_j)\frac{\ln 10}{400}\right),
$$

so a $400$-point advantage corresponds to $10$-to-$1$ odds. After each game, the ratings are updated immediately:

$$
R_i \leftarrow R_i+K(S-P_{ij}),
\qquad
R_j \leftarrow R_j-K(S-P_{ij}).
$$

The residual $S-P_{ij}$ measures the surprise in the result. A predictable win produces a small update, while an upset produces a large one. This update points in the direction of the gradient of the game's log-likelihood, with the gradient magnitude factor absorbed into $K$. Thus Elo can be viewed as stochastic gradient ascent, processing one game at a time. It is not generally identical to recomputing the batch maximum-likelihood estimate: the step size and the order of the games matter. A large $K$ reacts quickly to changes in team strength but produces noisier ratings, whereas a small $K$ is steadier but adapts slowly. Chapter 5 shows how modeling the score within one game as a random walk produces a different sigmoid win-probability curve. Exercise 5 below uses the conventional Elo scale.

For tournament prediction, either fitting method supplies the ratings, the logistic formula turns them into $P$, and the bracket simulation turns $P$ into championship probabilities. Any bias or missing variable in the rating model is inherited by the simulation.

## Worked example 1: a four-team tournament

How well does the simulation reproduce an answer we can compute exactly? Take 4 teams with a random matchup matrix and the fixed draw: $(0 \text{ vs } 1)$, $(2 \text{ vs } 3)$, winners meet in the final. The cell below simulates $10^5$ tournaments and prints each team's estimated championship probability with a two-standard-error band:

```{code-cell} python
import numpy as np

def random_P(n, rng):
    """Random matchup matrix with P[j, i] = 1 - P[i, j]."""
    U = np.triu(rng.uniform(size=(n, n)), k=1)
    P = U + np.tril(1 - U.T, k=-1)
    np.fill_diagonal(P, 0.5)
    return P

def simulate(draw, P, rng):
    """One single-elimination tournament; returns the champion."""
    survivors = list(draw)
    while len(survivors) > 1:
        next_round = []
        for i, j in zip(survivors[::2], survivors[1::2]):
            next_round.append(i if rng.uniform() < P[i, j] else j)
        survivors = next_round
    return survivors[0]

rng = np.random.default_rng(0)
n, N = 4, 100_000
P = random_P(n, rng)
champs = np.array([simulate([0, 1, 2, 3], P, rng) for _ in range(N)])

for i in range(n):
    p = (champs == i).mean()
    se = np.sqrt(p * (1 - p) / N)
    print(f"team {i}: win prob = {p:.4f} +/- {2*se:.4f}")

# team 0: win prob = 0.0044 +/- 0.0004
# team 1: win prob = 0.5316 +/- 0.0032
# team 2: win prob = 0.0015 +/- 0.0002
# team 3: win prob = 0.4625 +/- 0.0032
```

Two teams dominate this random instance, and the estimates sum to $1$, as they must. That sum is a cheap consistency check on the loop, but the real check is the closed-form solution. With 4 teams, team 0 wins if it beats team 1 and then beats whoever wins the other semifinal:

$$
w_0 = P_{01}\,\bigl(P_{23}\,P_{02} + P_{32}\,P_{03}\bigr),
$$

and the other three teams follow the same pattern. For this $P$ the exact values are $w = (0.0045,\ 0.5324,\ 0.0015,\ 0.4616)$. Every simulated value is within one standard error of its exact value, so the agreement is as good as the sample size allows. This is **verification** in the sense of Chapter 3: it shows that the loop computes the probabilities implied by $P$. It says nothing about whether $P$ describes any real teams, which would be **validation** and would need results of actual games.

The largest error bars here are about $\pm 0.003$ at $N = 10^5$; the rare teams have smaller absolute error bars. Halving any of them takes $4 \times 10^5$ simulations, the $1/\sqrt N$ rule again. The [companion script](./code/04_tournaments/simulate_4team.py) contains the same functions and adds a 16-team bracket.

## Worked example 2: how much does the draw matter?

For a fixed matchup matrix, how much does a team's championship probability depend on the bracket it is placed in? Take 8 teams, identify the strongest by the sum of its row of $P$, and estimate its championship probability under 50 random draws with $2000$ simulated tournaments each:

```{code-cell} python
import numpy as np

rng = np.random.default_rng(1)
n, n_draws, N = 8, 50, 2000
P = random_P(n, rng)
strength = P.sum(axis=1) - 0.5           # expected wins against the field
star = int(np.argmax(strength))

probs = []
for _ in range(n_draws):
    draw = list(rng.permutation(n))
    champs = np.array([simulate(draw, P, rng) for _ in range(N)])
    probs.append((champs == star).mean())
probs = np.array(probs)

print(f"team {star}: mean {probs.mean():.3f}, "
      f"SD across draws {probs.std(ddof=1):.3f}, "
      f"range [{probs.min():.3f}, {probs.max():.3f}]")

# team 7: mean 0.198, SD across draws 0.125, range [0.007, 0.453]
```

The strongest team's championship probability ranges from under $1\%$ to about $45\%$ depending only on the draw. Before calling that a real effect, check that it is not sampling noise. At a representative probability of $0.2$, a per-draw estimate based on $N = 2000$ tournaments has Monte Carlo standard error $\sqrt{0.2 \times 0.8 / 2000} \approx 0.009$; for any probability, it is at most $1/(2\sqrt{2000}) \approx 0.011$. The spread across draws is $0.125$, more than ten times larger, so **almost all of the spread comes from the bracket, not from the simulation**. Had the two been comparable, the experiment would have said nothing about the draw until $N$ was increased.

Why is the effect so large here? The random matrix is deliberately heterogeneous and need not describe a perfectly transitive ranking: even the team with the largest row sum can have unfavorable specific matchups. Reaching the title requires surviving three opponents in sequence, so a draw that places difficult matchups on the team's path can more than halve its odds. Real tournaments seed the bracket to keep the top teams apart, which generally shrinks the effect but does not remove it. The [companion script](./code/04_tournaments/draw_effect.py) runs a larger version with 100 draws and 5000 tournaments each.

## Intuition

> **Why are most upsets observed early in a tournament?** Mainly because round 1 contains half of all the games. The upset *rate per game* need not decrease: in a seeded bracket, early games often have the largest rating gaps and hence the smallest underdog win probabilities, while later games match more evenly rated teams. Whether an outcome counts as an upset also becomes less clear when the teams are evenly matched. The matchup model lets you put a precise number on your surprise: the pre-game probability assigned to the winner.

> **Why can the draw change a team's odds so much?** Because the process is path-dependent: who you play in round 1 decides who you can meet in round 2. If the draw puts the two strongest teams in the same half, only one of them can reach the final, and the other half is guaranteed a weaker finalist. Seeding is designed to prevent exactly this. When the draw is random, as with group assignments drawn from pots, the effect is real and can change a team's championship odds by a factor of two or more.

> **Why model the matchups and simulate the bracket, rather than model the tournament directly?** Two reasons. The matchup model can be fitted, in principle, to every game ever played, not only tournament games, so it has far more data behind it. And once you have it, the bracket question needs no new data at all, only simulation. Fitting a model directly on past tournament outcomes throws away most of the information and learns from a sample of a few dozen tournaments.

## Connections

- **Builds on:** Chapter 2 for Bernoulli trials and maximum likelihood, which is how ratings are fitted. Chapter 3 for the hit-counting Monte Carlo estimator, its $\sqrt{p(1-p)/N}$ standard error, and the distinction between verifying a simulation against a closed form and validating its inputs against the world.
- **Used in:** Chapter 5, where Exercise 4 compares Elo's logistic win probability with the Gaussian CDF produced by a random-walk model of one game's score. More broadly, any stochastic process that is a tree of binary choices can be simulated with this chapter's loop.
- **Related but not required:** Bayesian rating systems such as Glicko and TrueSkill, which replace each point rating $R_i$ with a posterior distribution. The Plackett–Luce model, which extends Bradley–Terry from pairwise outcomes to full rankings of many competitors, as in a race. Rao–Blackwellization, which lowers the variance of the bracket simulation by replacing the last coin flip with its exact probability.

## Exercises

1. **Conceptual.** A friend insists that "the seeding system is rigged, because top seeds win more often than skill alone would predict." Sketch how you would quantify the advantage created by seeding using historical game results and bracket data. Explain why observing that top seeds win often is not, by itself, evidence that the system is unfair.

2. **Computational.** Simulate a 16-team bracket with a random matchup matrix, generated as in Worked Example 1, and a random draw. Run $5 \times 10^4$ tournaments and report the championship probabilities and two-standard-error bands of the four highest-skill teams, defining skill as the row sum $\sum_j P_{ij}$. Is the highest-skill team necessarily the most likely champion? Explain any discrepancy.

3. **Computational.** Hold the matchup matrix and draw from Exercise 2 fixed, and choose one target team before running any simulations. For $N = 10^2, 10^3, 10^4, 10^5$, repeat the estimate of that team's championship probability 30 times and compute the standard deviation across repeats. Plot that standard deviation against $N$ on log-log axes and fit a line. Does its slope match the predicted $-1/2$?

4. **Computational.** Hold one matchup matrix fixed and choose one team before examining any draws. Estimate its championship probability under 100 independently sampled random draws, using $5000$ simulated tournaments per draw. Plot a histogram of the 100 estimates and compute their standard deviation. Compare that across-draw standard deviation with the typical Monte Carlo standard error of one estimate. Is the draw a meaningful source of variation for this team?

5. **Computational.** Suppose matchup probabilities follow the conventional Elo formula $P_{ij} = \sigma\bigl((R_i-R_j)\ln 10/400\bigr)$. Fix seven opponents with ratings $0,100,\ldots,600$ and fix their bracket positions. Vary the rating of an eighth, focal team from $0$ to $700$ in steps of $100$. At each value, rebuild $P$ and estimate the focal team's championship probability from $10^5$ tournaments using the same draw. Plot the result on both linear and semilogarithmic vertical axes. Is the relationship exactly linear or exponential? Explain its shape.

6. **Modeling judgment.** A colleague proposes to predict the World Cup champion by training a neural network directly on past World Cup outcomes, treating each tournament as one data point and obtaining only about 20 data points in total. Give three problems with this approach. Then propose an alternative based on fitting a match-level model and simulating the tournament format, noting one feature that a World Cup match model needs beyond the binary $P$ used in this chapter. Finally, give one way in which the independence-of-games assumption could fail.

:::{admonition} Solutions
:class: dropdown

**1.** Fit a matchup model $P$ using only games available before each historical tournament. For each tournament and each top seed, simulate both the actual seeded bracket and many counterfactual random draws with the same teams and the same $P$. The paired difference between the championship probability under the actual bracket and its average under random draws estimates the advantage created by seeding while holding modeled skill fixed. Aggregate those paired differences across teams and tournaments and report an uncertainty interval. A positive advantage is expected because protecting strong teams is the stated purpose of seeding; it does not by itself show unfair manipulation. Separately comparing actual-bracket predictions with observed outcomes checks the calibration of the whole model, but does not isolate the effect of seeding.

**2.** In the fixed-seed run of [the companion script](./code/04_tournaments/simulate_4team.py), the four highest-skill teams are teams 14, 1, 12, and 7. Their estimated championship probabilities, in that order, are $0.1427\pm0.0031$, $0.1852\pm0.0035$, $0.0806\pm0.0024$, and $0.2185\pm0.0037$, where each band is two standard errors. Thus the highest-skill team is not the most likely champion in this instance; team 7 is. The row sum measures average performance against the whole field, whereas the championship probability depends on the particular opponents reachable along a team's path. This example proves that the two rankings need not agree, although other random matrices and draws will give different numbers.

**3.** For fixed $P$, draw, and target team, each run is a mean of $N$ Bernoulli championship indicators, so its standard deviation is $\sqrt{p(1-p)/N}$. Taking logarithms gives a line with slope $-1/2$. One reproducible run of [the companion script](./code/04_tournaments/convergence.py), which generates and then holds its own $P$ and draw fixed, gives empirical standard deviations $0.0204$, $0.0084$, $0.0024$, and $0.00074$, with fitted slope $-0.486$. The precise values vary across sets of 30 repeats, but the slope is consistent with $-1/2$.

**4.** [The companion script](./code/04_tournaments/draw_effect.py) chooses the strongest-by-row-sum team before sampling the draws. Across 100 draws, its estimated championship probability has mean $0.365$, standard deviation $0.105$, and range $0.161$ to $0.565$. The root-mean-square Monte Carlo standard error across the 100 estimates is about $0.0066$, roughly sixteen times smaller than the across-draw standard deviation. Finite-$N$ noise therefore contributes very little to the observed spread. The histogram shows that the heterogeneous matchup matrix can place unfavorable specific opponents on even the strongest team's path; the draw is a meaningful source of variation here.

**5.** With the fixed opponents and draw in [the companion script](./code/04_tournaments/elo_to_winprob.py), focal-team ratings $0,100,\ldots,700$ give estimated championship probabilities $0.0077$, $0.0242$, $0.0625$, $0.1363$, $0.2463$, $0.3900$, $0.5387$, and $0.6809$. The curve is increasing but is neither a line nor an exact exponential. At low ratings, the logistic probability of beating a much stronger opponent is approximately exponential in the rating gap, so the semilog plot is closer to linear. As the focal rating rises, its per-game win probabilities approach $1$ and the championship probability bends toward its upper bound. The overall curve is sigmoid-like because it combines three sequential logistic matchups and averages over the possible opponents in later rounds.

**6.** Three problems are: (i) about 20 observations cannot constrain a flexible neural network; (ii) retaining only the champion discards the much richer match-by-match evidence within each tournament; and (iii) teams, tournament formats, and the strength of the field change over time, so those tournaments are not identically distributed observations. A better approach fits a match-level model to the many international matches available before the tournament, using team ratings and other pregame covariates, and then simulates the actual competition rules. Because World Cup group matches can end in draws, the match model must predict at least win/draw/loss probabilities, or a score distribution, rather than only the binary $P$ used for knockout games. The simulator must also implement group standings, tiebreakers, and the knockout bracket. Independence can fail through fatigue: a team that plays extra time in one knockout round may have a lower probability of winning the next match, even against the same opponent.

:::

## Further reading

- Bradley and Terry, "Rank Analysis of Incomplete Block Designs: I. The Method of Paired
  Comparisons", *Biometrika* 39(3/4):324–345 (1952) — the original paper for the rating
  model of this chapter; the first sections are readable with Chapter 2's maximum likelihood.
  [doi:10.2307/2334029](https://doi.org/10.2307/2334029) ·
  [HOLLIS](https://hollis.harvard.edu/discovery/search?query=any,contains,10.2307/2334029&tab=Everything&search_scope=MyInst_and_CI&vid=01HVD_INST:HVD2&offset=0).
  No free version; JSTOR access through Harvard.
- Elo, *The Rating of Chessplayers, Past and Present* (1978) — the rating system's own
  account, including the choice of the 400-point scale and of $K$. ISBN 9780668047216 ·
  [HOLLIS](https://hollis.harvard.edu/discovery/search?query=any,contains,Rating%20of%20Chessplayers%20Elo&tab=LibraryCatalog&search_scope=MyInstitution&vid=01HVD_INST:HVD2&offset=0).
- For the deeper view of paired-comparison models: Stern, "A Brownian Motion Model for the
  Progress of Sports Scores", *JASA* 89(427):1128–1134 (1994) — connects directly to Chs. 5
  and 6 of this book.
  [doi:10.1080/01621459.1994.10476851](https://doi.org/10.1080/01621459.1994.10476851) ·
  [HOLLIS](https://hollis.harvard.edu/discovery/search?query=any,contains,10.1080/01621459.1994.10476851&tab=Everything&search_scope=MyInst_and_CI&vid=01HVD_INST:HVD2&offset=0). Full-text access may require a Harvard login.
- Silver, *The Signal and the Noise* (2012), Ch. 3 (on baseball) — popular treatment of the
  "probabilistic forecast → tournament simulation" pipeline. ISBN 9781594204111 ·
  [HOLLIS](https://hollis.harvard.edu/discovery/search?query=any,contains,Signal%20and%20the%20Noise%20Silver&tab=LibraryCatalog&search_scope=MyInstitution&vid=01HVD_INST:HVD2&offset=0).
