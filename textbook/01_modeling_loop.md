---
kernelspec:
  name: python3
  display_name: Python 3
---

# Chapter 1: The Modeling Loop — What a Model Is

> A model is a deliberately simplified, computable story about a phenomenon, and building one is a loop — **formulate** a question and assumptions, **implement** them, **verify** the code against known mathematics, **validate** the model against reality, and **iterate** — with verification and validation being two different checks that beginners constantly confuse.

:::{note} Running the code
The Python cells on this page run **in your browser**. Click the **power icon** at the top of the page to activate the kernel, then run — or edit — any cell. Packages (NumPy, SciPy, …) load automatically the first time you import them (a few seconds).
:::

## Motivation

Every other chapter in this book builds a specific model: an epidemic curve, a diffusing particle, a stock price, a tournament bracket. This chapter is about the thing they have in common — the *process* of turning a messy real-world phenomenon into something you can compute with, and knowing how much to trust the answer.

A model is not the phenomenon. It is a chosen simplification: you throw away almost everything and keep the few features you think drive the behavior you care about. "The better team wins the World Series" is not a fact about baseball; it is a *question* you can only answer once you have committed to a model of what "better" means and how a series unfolds. The commitment is where the intellectual work lives, and it is exactly the part a coding agent will happily skip if you let it.

That last point matters more in this course than it used to. You will use coding agents to implement your models, and an agent is very good at producing plausible code fast. What it cannot do for you is decide *what question you are asking*, *what you are willing to assume*, and *how you would know if the answer were wrong*. Those three decisions are the model. This chapter is a framework for making them deliberately — before you prompt — and a running example, the baseball best-of-7 series, small enough to walk end to end.

## Setup & notation

We use very little new machinery here; the point is conceptual. The running example needs only:

- $p$ — the probability the **favorite** (the "better" team) wins a single game, with $0 \le p \le 1$. We assume $p > 1/2$ when we call one team "better."
- A **best-of-7 series**: the two teams play until one has won $w = 4$ games; that team wins the series. At most 7 games are played.

We treat individual games as independent Bernoulli$(p)$ trials — see [`A_notation.md`](./A_notation.md) for Bernoulli and binomial notation. Whether that independence is *true* is precisely the kind of assumption this chapter teaches you to make explicit and then question.

## Core ideas

### The loop

Modeling is not a straight line from question to answer; it is a loop you traverse several times, each pass sharpening the model.

1. **Formulate.** Turn a vague phenomenon into a precise question, a set of simplifying assumptions, and a mathematical structure that could answer it. ("How often does the better team win?" $\to$ "Given per-game win probability $p$ and independent games, what is $\mathbb{P}(\text{favorite reaches 4 wins first})$?") This is the **formulation** skill, and it is the hardest, least automatable stage.
2. **Implement.** Turn the structure into something computable — a formula, a simulation, a fitted routine. This is the stage a coding agent can do most of for you.
3. **Verify.** Check that the implementation faithfully computes the mathematics you specified. *Did I solve the equations I wrote down correctly?*
4. **Validate.** Check that the model — assumptions and all — actually describes reality. *Did I write down the right equations?*
5. **Iterate.** Verification and validation both feed back into formulation. A failed verification means a bug; a failed validation means the *model* is wrong (or the question was), and you revise assumptions and go around again.

Every later chapter runs through these five stages once, on a harder phenomenon. The chapters differ in the mathematics; the sequence of steps does not.

### Verification and validation: two different checks

These two words sound like synonyms and are not. Keeping them apart is one of the ideas the rest of the book depends on most, and this chapter is where the distinction is introduced; it comes back in force in the Monte Carlo & Estimation chapter and again in the Queuing chapter.

> **Verification: am I solving the equations right?** Check the implementation against *known mathematics* — a closed-form solution, a limiting case, a conservation law, an invariant. Verification never looks at real-world data. It asks only whether your code faithfully computes the model you specified.

> **Validation: am I solving the right equations?** Check the *model* against *reality* — compare predictions to data the model was not built to reproduce, look at residual structure, test out-of-sample. Validation is the only stage that can tell you your assumptions are wrong.

A slogan (Boehm's): **verification is "did we build the thing right?"; validation is "did we build the right thing?"** You can have a perfectly verified implementation of a completely wrong model. That is the trap Worked Example 2 is built around.

### Assumptions: explicit and implicit

Every model rests on assumptions, and they come in two kinds:

- **Explicit assumptions** are the ones you write down: "games are independent," "$p$ is the same every game." You can see them, so you can question them.
- **Implicit assumptions** are the ones baked in silently by your modeling choices: that home-field advantage doesn't matter, that pitching rotations don't shift the win probability from game to game, that no player gets injured mid-series, that both teams try equally hard in every game. You didn't decide these; you just failed to *not* assume them.

The dangerous assumptions are almost always the implicit ones, because you can't validate against a possibility you never noticed. A coding agent is especially prone to adding implicit assumptions without telling you — it will pick a reasonable-looking default and not mention that it chose one. Half of "modeling judgment" is surfacing implicit assumptions and promoting them to explicit ones so they can be checked.

### Think before prompting

This is an agent-era course. You will hand implementation to a coding agent constantly, and you should. But the agent operates *inside* step 2 of the loop; the value you add is steps 1, 3, and 4. So before you type a prompt, do the pre-agent thinking on paper:

1. **State the question precisely.** Not "model the World Series" but "compute $\mathbb{P}(\text{favorite wins best-of-7} \mid p)$."
2. **List the assumptions** — explicit *and* the implicit ones you're choosing to accept — so the agent's silent defaults become your deliberate choices.
3. **Decide a verification check and a validation check in advance.** "The code must return $0.5$ at $p = 0.5$" (verification, a known limiting case). "The predicted share of 7-game series should be near the historical $\sim 35\%$" (validation, external data). If you don't fix these before implementing, you will accept whatever the agent produces because it looks plausible.

The discipline is: **a prompt should encode a question and its checks, not just a request for code.** An agent that is told the limiting case and the validation target will write better code and you will catch its mistakes. An agent handed "simulate the World Series" will confidently return something, and you will have no independent way to know if it's right.

## Worked example 1: best-of-7, the full loop

**The phenomenon.** Sports fans say a seven-game series "rewards the better team" more than a single game. Is that true, and by how much?

**Formulate.** Precise question: if the better team wins each game independently with probability $p > 1/2$, what is the probability it wins a best-of-7 series? *Explicit assumptions:* games are IID Bernoulli$(p)$; the series ends at 4 wins. *Implicit assumptions we're accepting for now:* no home-field effect, no game-to-game change in $p$, no momentum. We'll revisit these in validation.

**Implement — closed form.** The favorite wins the series exactly when its 4th win arrives no later than game 7. Condition on the game $k+1$ in which that 4th win lands: the preceding $k$ games contain exactly 3 wins, then game $k+1$ is a win. Summing over $k$:

$$
\mathbb{P}(\text{favorite wins}) = \sum_{k=3}^{6} \binom{k}{3}\, p^{4}\, (1-p)^{\,k-3}.
$$

```{code-cell} python
from math import comb

def p_series_closed_form(p, n_games=7):
    w = n_games // 2 + 1               # wins needed: 4
    return sum(comb(k, w - 1) * p**w * (1 - p)**(k - (w - 1))
               for k in range(w - 1, n_games))
```

**Implement — Monte Carlo.** Independently, simulate the series directly under the *same* assumptions and count how often the favorite wins. The full script is in [`code/01_modeling_loop/best_of_7.py`](./code/01_modeling_loop/best_of_7.py).

**Verify.** Two independent checks, both against *known mathematics*, no data:

1. *Limiting cases.* At $p = 0.5$ the formula must give exactly $0.5$ (symmetry); at $p = 1$ it must give $1$; at $p = 0$, $0$. The script asserts all three.
2. *Cross-check.* The closed form and the Monte Carlo estimate must agree within Monte Carlo error. Running the script:

| $p$ | closed form | Monte Carlo ($N = 2\times10^5$) |
|-----|-------------|-------------------------|
| 0.50 | 0.5000 | $0.500 \pm 0.001$ |
| 0.55 | 0.6083 | $0.608 \pm 0.001$ |
| 0.60 | 0.7102 | $0.710 \pm 0.001$ |
| 0.70 | 0.8740 | $0.874 \pm 0.001$ |

They agree. **This is verification, not validation** — both computations encode the identical IID model, so their agreement only tells us the code is right, not that baseball is IID.

**Validate.** Now step outside the model. The answer says a 55%-per-game team wins the series only 61% of the time, and a 60% team wins 71% — the series *does* amplify the favorite's edge, but far less than fans imagine. Two moves, and only one of them is validation: (a) a **check that the model behaves sensibly** — a best-of-7 clearly discriminates better than one game (where 55% is 55%) but can't manufacture certainty from a small edge; the numbers match that intuition. That is reassuring, but no outside data has entered, so by this chapter's own definition it is not validation. (b) **Validation proper, against data** — we take this up in Example 2, which is where the IID assumption meets reality.

**Iterate.** The verification passed, so there is no bug to fix. The validation is only partial, which points us at the assumptions — the natural next lap tests whether real series behave like IID games at all.

## Worked example 2: why a simulation cannot validate its own assumptions

Here is the wrinkle, and it is the single most common mistake in the course. Suppose instead of the win *probability* you care about series *length* — how many games a best-of-7 tends to last. Under the IID model with $p = 0.5$, the distribution of the length $g$ has a closed form (negative-binomial): the series clinches in game $g$ when one team gets its 4th win there while the other has $g - 4$.

```{code-cell} python
from math import comb

def series_length_pmf(p, n_games=7):
    w = n_games // 2 + 1
    pmf = {}
    for g in range(w, n_games + 1):
        fav = comb(g - 1, w - 1) * p**w * (1 - p)**(g - w)
        dog = comb(g - 1, w - 1) * (1 - p)**w * p**(g - w)
        pmf[g] = fav + dog
    return pmf
```

Now a student writes a simulator, runs it, and gets ([`code/01_modeling_loop/series_length.py`](./code/01_modeling_loop/series_length.py)):

| games | closed form | Monte Carlo |
|-------|-------------|-------------|
| 4 | 0.125 | 0.126 |
| 5 | 0.250 | 0.250 |
| 6 | 0.313 | 0.312 |
| 7 | 0.313 | 0.312 |

The simulation matches the formula beautifully, and the student writes: *"I validated my model — the simulation agrees with the analytic distribution."* **This is wrong, and it is exactly the verification/validation confusion.** The simulator and the formula both assume IID $p = 0.5$ games. Of course they agree — they are two computations of the same model. Nothing about real baseball has entered the picture. This is **verification** being reported as validation. Simulating your own assumptions can only confirm that you implemented those assumptions correctly.

To actually **validate**, you need a number the model did *not* get to choose. Of the 115 best-of-7 World Series played from 1905 to 2023, **40 needed all seven decisive games — 34.8%**. The IID $p = 0.5$ model predicts **31.3%**. So the model looks like it *underpredicts* long series — and the tempting next move is to start explaining why: home-field structure, momentum, managers resting stars when ahead, teams more evenly matched than a fixed $p$ captures.

**Resist that, and do the arithmetic first.** A proportion measured on $n = 115$ carries a standard error, under the model's own $p_0 = 0.3125$, of $\sqrt{0.3125 \times 0.6875 / 115} \approx 0.043$ — more than four percentage points. The observed gap is 3.5 points. That is **0.8 standard errors**, an exact two-sided binomial $p$-value of $0.42$: entirely consistent with chance.

So the honest conclusion is *not* "the model is wrong and here is why." It is: **this comparison does not have the resolution to say.** A century of baseball sounds like a lot of data, and for this question it is not. To have an 80% chance of detecting a gap of even 5.75 points — the discrepancy people usually claim is there — you would need about 530 series, roughly 4.6 times the entire history of the event. That is the real lesson, and it is a validation result: you compared against a number the model did not choose, and learned that the comparison is inconclusive. Reporting the 3.5-point gap as evidence of a modelling failure would be exactly the overreach this chapter is about.

:::{note} Where these numbers come from
The counts are recomputed from [`data/public/world_series.csv`](./data/public/world_series.csv) by [`code/01_modeling_loop/series_length_data.py`](./code/01_modeling_loop/series_length_data.py), which prints the exclusions it applies — 1903 and 1919–1921 were best-of-nine, and there was no Series in 1904 or 1994 — and refuses to run unless the same parse reproduces Mosteller's published 1905–1951 table exactly. One wrinkle worth the footnote: the 1912 Series ended 4–3 but took **eight** games, because game 2 was called a tie. So 40 series needed a seventh decisive game while only 39 were literally seven games long.

Earlier printings of this chapter said 37%, and before that divided by 119. Both were wrong. That is the honest reason the derivation is committed rather than the number asserted.
:::

**Now the more interesting question: what could possibly close the gap?** Before reaching for data, notice that the model's prediction is *bounded*. Writing $P(7 \mid p)$ for the chance a best-of-7 goes the distance, the first six games must split 3–3, so

$$P(7 \mid p) = \binom{6}{3} p^3 (1-p)^3 = 20\,p^3(1-p)^3 \le 20 \left(\tfrac12\right)^6 = 0.3125,$$

with the maximum at $p = 1/2$. **Evenly matched teams give the model its best chance of a long series, so 31.25% is the largest seven-game rate this model can produce for any $p$** — it is an upper bound, not a point prediction. That rules out one popular revision immediately. If you say matchups vary from year to year and draw each series' $p$ from some distribution, you are averaging $P(7 \mid p)$ over that distribution, and an average cannot exceed a maximum: $\mathbb{E}[P(7 \mid p)] \le 0.3125$, with equality only if every series really is a coin flip. A mixture over $p$ moves the prediction *down*, away from the data.

What the ceiling does **not** rule out is games that are independent but not *identically* distributed. If the six games carry different probabilities $p_1, \dots, p_6$ — a 2-3-2 home-field pattern, or an ace pitching games 1 and 5 — then the chance of a 3–3 split is a Poisson-binomial, and it can exceed 0.3125. Alternating $p_i$ between $0.54$ at home and $0.46$ away gives $0.3137$; a plausible rotation pattern gives $0.3167$. Real, and far too small to see in 115 series. Keep the three cases straight, because they behave differently: **one constant $p$** (and mixtures over it) is capped; **independent games with different $p_i$** is not; **genuinely dependent games** — momentum, a rattled bullpen — is a different model again.

> **How to tell which one you did.** If the check uses only quantities you put into the model, it is verification. If it uses a number from the outside world that the model had no say in, it is validation. A simulation is your assumptions executed, so it can never validate the assumptions it was built from.

## Intuition

> **If verification never uses data, what good is it?** Verification catches the enormous class of errors where your *code* doesn't match your *math* — off-by-one bugs, wrong array indexing, a sign error, an agent that quietly changed your specification. Those bugs are invisible to validation (a buggy implementation of a good model can look "close enough" to data and hide the bug). You verify first so that when validation fails, you know it's the *model* that's wrong, not the code.

> **Why can't a simulation validate my model?** Because a simulation is just your assumptions, executed. It can only tell you what your assumptions imply — never whether your assumptions are true. Matching a simulation to a formula built from the same assumptions checks the two computations against each other, and both of them encode the same assumptions, so neither can test those assumptions. Validation requires an *independent* source of truth: real data the model did not get to see.

> **Isn't the best-of-7 "better team wins" answer just... the answer?** No — it's the answer *conditional on the model*. The 71%-at-$p{=}0.6$ figure is exactly right for IID games and possibly quite wrong for baseball. Every model output carries an implicit "...assuming the model is right," and a good modeler says that clause out loud. The number is a claim about the model; validation is what upgrades it (partially) to a claim about the world.

> **Why do the pre-agent thinking if the agent writes the code anyway?** Because the agent operates only inside the *implement* step. It cannot choose your question, cannot know which implicit assumptions you're willing to accept, and cannot invent a validation check against data it's never seen. If you skip formulation and checks, you've delegated the two stages an agent *can* do and abandoned the three it *can't* — and you'll accept plausible-looking wrong answers because you built no way to catch them.

## Connections

- **Builds on:** basic probability — Bernoulli/binomial trials from [`A_notation.md`](./A_notation.md). Nothing heavier; this is the conceptual anchor for the book.
- **Used in:** *every* later chapter is one traversal of this loop. The verify-vs-validate distinction introduced here gets its first *formal* workout in the Monte Carlo & Estimation chapter (Monte Carlo agreeing with a closed form = verification; comparing to real outcomes = validation) and is stress-tested in the Queuing chapter, where simulation and steady-state theory are used to check *each other*. The best-of-7 example continues directly into the Monte Carlo chapter (estimating $p$ from series data) and the Tournaments & Stochastic Simulation chapter (the series as an absorbing Markov chain).
- **Related but not required:** the software-engineering track's testing lecture is verification-as-engineering; this chapter is verification-as-science. Same instinct — check your instrument — at two levels.

## Exercises

These are deliberately judgment-heavy: this is the framing chapter, so the exercises are about *reasoning about models*, not grinding math.

1. **Verify or validate?** For each check below, say whether it is verification or validation, and why. (a) Your epidemic simulation conserves total population at every timestep. (b) Your epidemic model's predicted case curve is compared to reported case counts from a city it wasn't fit on. (c) Your option-pricing code reproduces the Black–Scholes formula in the zero-volatility limit. (d) A colleague reruns your Monte Carlo with a different seed and gets a statistically consistent answer. (e) Your traffic model predicts stop-and-go waves, and dashcam footage shows them.

2. **Explicit vs. implicit.** For the best-of-7 model, list three *explicit* assumptions and three *implicit* ones. For each implicit assumption, name one real-world situation where it fails badly enough to matter.

3. **Diagnose the confusion.** A student writes: "I validated my dice simulator: I simulated 10,000 rolls and the frequency of each face was within 1% of $1/6$, matching the theoretical probability." Is this verification or validation? What would a genuine *validation* of a physical die look like?

4. **Formulate before prompting.** You want to model whether a basketball team should intentionally foul when leading by 3 with 10 seconds left. Without writing code: state the precise question, list four assumptions (mark each explicit or implicit), and propose one verification check and one validation check you'd fix *before* prompting an agent.

5. **Iterate.** In Example 2 the IID $p = 0.5$ model predicts 31.3% seven-game series against an observed 34.8% — a gap the chapter argues is not distinguishable from chance. Suppose you wanted to close it anyway. Consider two revisions: (A) let $p$ differ game to game to encode home-field advantage on the 2-3-2 schedule; (B) draw each series' $p$ from a distribution across matchups. One of these *cannot* work, and you can show it in a line of algebra before touching any data — which one, and why? For the other, state what new check would tell you the revision genuinely helped rather than just fitting the one number you already saw.

6. **Modeling judgment.** An agent, prompted "predict who wins the series," returns code that fits a per-game $p$ to the two teams' full regular-season records and reports the series-win probability. Identify two implicit assumptions the agent has silently made, and explain why its "the simulation matches my fitted model" is not evidence the prediction is any good.

:::{admonition} Solutions
:class: dropdown

**1.** (a) **Verification** — conservation is *known mathematics* internal to the model; no real data involved. (b) **Validation** — comparison to real, out-of-sample data. (c) **Verification** — a known analytic limiting case. (d) **Verification** — seed-independence checks that the code computes the intended model, not that the model is true. (e) **Validation** — an emergent prediction confronted with real observation.

**2.** *Explicit:* games IID; win probability exactly $p$; series ends at 4 wins. *Implicit (with failure modes):* no home-field advantage (fails — home teams have won about 54% of MLB regular-season games since 1901, so $p$ isn't constant across games); fixed rosters (fails on a key injury); both teams equally motivated every game (fails when one team rests starters); pitching rotation doesn't shift $p$ game to game (fails badly — a team's ace vs. its 4th starter is a large swing in $p$); no momentum or psychological carry-over (plausible, but note this one is a *candidate* mechanism rather than an established effect — it is much easier to assert after a dramatic game than to demonstrate). The pitching-rotation one is the most consequential and the least obvious. Note that the first and last of these break *identical distribution* but not *independence* — which, as Example 2 shows, matters for what they can explain.

**3.** **Verification.** Matching simulated frequencies to the theoretical $1/6$ only confirms the simulator correctly implements a fair-die *model* — both are "assume $1/6$." Genuine validation uses a *physical* die: roll a real die thousands of times and test whether the observed face frequencies are consistent with $1/6$ (a chi-squared goodness-of-fit test). Only the physical die can reveal that the die is loaded — the simulator never can.

**4.** *Question:* "Given a 3-point lead with 10s left, does intentionally fouling (sending the opponent to the line, down 3, up 2 after) raise the leading team's win probability versus playing straight defense?" *Assumptions:* opponent's free-throw make probability is known/estimable (explicit); no offensive rebounds off a missed second free throw (implicit, and false); the leading team can inbound and be fouled without a turnover (implicit); clock/possession dynamics reduce to a fixed number of opponent possessions (explicit simplification). *Verification:* in the degenerate case where the opponent shoots 0% from three, fouling and not-fouling should both give win probability $1$. *Validation:* compare the model's recommended strategy against play-by-play data on teams that actually fouled vs. didn't. But note this is **observational, and confounded**: coaches choose to foul in particular situations, so the two groups differ in more than the strategy — score, time remaining, foul counts, opponent free-throw quality. A raw comparison of win rates measures the selection as much as the tactic. To make it a real validation you would need to match on game state (or otherwise adjust for it), and even then you should report it as suggestive rather than causal.

**5.** **Revision B cannot work, and the algebra says so before any data.** With one constant $p$ per series, $P(7 \mid p) = 20p^3(1-p)^3$, which is maximised at $p = 1/2$ with value $0.3125$. Drawing $p$ from any distribution averages that function, and an average cannot exceed a maximum: $\mathbb{E}[P(7 \mid p)] \le 0.3125$, with equality only if every series is exactly a coin flip. So "matchups vary in how lopsided they are" pushes the predicted seven-game rate *down*, away from the observed 34.8%. It is the intuitive revision and it moves the wrong way. (It also *raises* the predicted sweep rate, $p^4 + (1-p)^4$, which is minimised at $p = 1/2$ — so a mixture gets that statistic wrong too.)

**Revision A survives, because the ceiling does not apply to it.** Independent games with *different* probabilities $p_1, \dots, p_6$ give a Poisson-binomial 3–3 split, which can exceed $0.3125$: alternating $0.54$/$0.46$ gives $0.3137$. But look at the size — about $0.1$ of a percentage point against a standard error of $4.3$ points. It is real and it is invisible at $n = 115$.

**The lesson is the ordering.** Both revisions were motivated by the 34.8% figure, so matching it is not evidence for either — that is fitting the number you already saw. But you did not need data to eliminate B; you needed one inequality. Cheap analysis before expensive fitting. If you did want to test A honestly, you would hold out a statistic it was not tuned on — the sweep rate, or the game-7 rate in a different league or era — and check it predicts that better than the baseline. Predicting a number you didn't fit to is the validation.

**6.** Implicit assumptions: (i) regular-season performance transfers unchanged to the playoffs (playoff pitching usage, matchups, and intensity differ); (ii) a single scalar $p$ summarizes the matchup, ignoring which pitcher starts which game. "The simulation matches my fitted model" is pure **verification** — the simulator just re-executes the fitted assumptions, so agreement is guaranteed and says nothing about predictive accuracy. To argue the prediction is *good*, you'd need out-of-sample validation: does this fitting procedure correctly predict *past* series it wasn't fit on, better than a naive baseline (e.g., "the team with the better record wins")?

:::

## Further reading

- Box, G. E. P. (1976), "Science and Statistics", *JASA* 71:791–799 — the origin of "all
  models are wrong, but some are useful." Short and worth reading in full.
  [doi:10.1080/01621459.1976.10480949](https://doi.org/10.1080/01621459.1976.10480949) ·
  [HOLLIS](https://hollis.harvard.edu/discovery/search?query=any,contains,10.1080/01621459.1976.10480949&tab=Everything&search_scope=MyInst_and_CI&vid=01HVD_INST:HVD2&offset=0). No free version exists; the PDF that
  tops search results is an unsanctioned scan on an unrelated personal page.
- Boehm, B. (1981), *Software Engineering Economics* — the source of the "build the thing
  right" (verification) vs. "build the right thing" (validation) framing borrowed here.
  ISBN 9780138221225 · [HOLLIS](https://hollis.harvard.edu/discovery/search?query=any,contains,Software%20Engineering%20Economics%20Boehm&tab=LibraryCatalog&search_scope=MyInstitution&vid=01HVD_INST:HVD2&offset=0). Long out of
  print, with no live publisher page.
- Weisberg, M., *Simulation and Similarity: Using Models to Understand the World* (Oxford,
  2013) — a philosopher's careful account of what a model *is* and how idealization works.
  ISBN 9780199933662 · [HOLLIS](https://hollis.harvard.edu/discovery/search?query=any,contains,Simulation%20and%20Similarity%20Weisberg&tab=LibraryCatalog&search_scope=MyInstitution&vid=01HVD_INST:HVD2&offset=0).
