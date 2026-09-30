# Where each lecture is in the textbook

An index for the study skill: the lectures so far, what each covered, and the sections of the
course textbook (in `../textbook/`) that go with them. Updated each week by the course staff.

**This is an index, not a list of what can be assessed.** The syllabus: quizzes "may draw on
anything covered in lectures, readings, weekly exercises, and past P-Sets". A topic can be
assessed without appearing here, and the textbook covers more than any one lecture did.

"Taught" means the lecture has happened and the description matches its materials. "Planned"
means it has not happened yet.

## Week 5

- **Tue 29 Sep and Thu 1 Oct: extreme values** (planned). The distribution of the largest of
  many values, fitting the tail of a distribution (block maxima and the GEV family), and why an
  estimate beyond the largest value seen is uncertain. Chapter 8, *Extreme value statistics*,
  is public (since 30 Sep) and is in `textbook/08_extreme_value_statistics.md`.
- **AM215, Fri 2 Oct: packaging a Python project** (planned). The `src/` layout and
  `pyproject.toml`. No textbook chapter.

## Week 4

- **Tue 22 Sep: diffusion and geometric Brownian motion** (taught). The continuum limit of the
  random walk and diffusive spreading ($\sqrt t$); geometric Brownian motion, Itô's lemma and why
  $\log S$ drifts at $\mu - \sigma^2/2$.
  - `textbook/05_random_walks_diffusion.md`: *The continuum limit and the diffusion equation*,
    *The fundamental solution*.
  - `textbook/06_gbm.md`: *Itô's lemma: changing variables in an SDE*, *Log returns and
    geometric Brownian motion*, *The lognormal solution*, *Fitting μ and σ from data*.
  - `textbook/sec03_drift_and_diffusion.md` (the Section 3 page).
- **Thu 24 Sep: options and the Black–Scholes price** (taught). Calls and puts and their
  payoffs; the hedging argument; why the price does not depend on the stock's expected return.
  - `textbook/07_option_pricing.md`: *Calls and puts*, *Hedging and the Black–Scholes
    equation*, *Expected payout*, *Reading the formula*, *Worked example 1*.
- **AM215, Fri 25 Sep: the Python data model** (taught). Operators and `__rmul__`, `@property`,
  decorators and `functools.wraps`. No textbook chapter.

## Week 3

- **Tue 15 Sep: random walks** (taught). Mean and variance of a step and of the walk; the walk
  that goes nowhere on average but still spreads; the assumptions behind the model; counting
  paths.
  - `textbook/05_random_walks_diffusion.md`: *Mean and variance*, *The exact distribution and
    its Gaussian approximation*, *Worked example 1*.
- **Thu 17 Sep: random walks in real data** (taught). Pearson's random-walk problem; a
  basketball game's score margin as a random walk.
  - `textbook/05_random_walks_diffusion.md`: *Worked example 3: does an observed path behave
    like diffusion?*
- **AM215, Fri 18 Sep: environments** (taught). What activating a virtual environment does;
  which files a repository keeps and which are regenerated. No textbook chapter.

## Week 2

- **Tue 8 Sep: Bernoulli trials and the best-of-seven series** (taught). The probability of a
  series from the probability of a game; the assumptions (independent games, the same
  probability in every game); estimating that probability from data.
  - `textbook/01_modeling_loop.md`: *Worked example 1: best-of-7, the full loop*, *Assumptions:
    explicit and implicit*.
  - `textbook/04_tournaments.md`; `textbook/02_mle.md` for estimating the probability.
- **Thu 10 Sep: Monte Carlo** (taught). What simulation gives you; the standard error and the
  $1/\sqrt N$ law; simulating a tournament.
  - `textbook/03_monte_carlo.md`: *The Monte Carlo estimator*, *The standard error*, *What the
    error bar tells you*, *Worked example 1*.
  - `textbook/04_tournaments.md`: *Why simulation?*, *The simulation loop*.
- **AM215, Fri 11 Sep: Git** (taught). The working directory, the staging area and commits;
  branches; `push`, `fetch`, `pull` and `origin/main`; `.gitignore`; SSH keys. No textbook
  chapter.

## Week 1

- **Thu 3 Sep: what a model is, and what to ask of one** (taught). What a model is for; the
  questions to ask before accepting a model someone else built, including one an agent built:
  is it correctly implemented, what does it assume, how is it checked against reality.
  - `textbook/01_modeling_loop.md`: *Motivation*, *The loop*.
  - `textbook/00_introduction.md`.
- **AM215, Fri 4 Sep: the shell** (taught). Standard output and standard error and redirecting
  them; quoting; pipes; the executable permission. No textbook chapter.

## P-Sets

- **P-Set 0: probability review and maximum likelihood.** `textbook/02_mle.md`,
  `textbook/A_notation.md`.
- **P-Set 1: series, a tournament competition, random walks.** `textbook/01_modeling_loop.md`
  (verification and validation), `textbook/02_mle.md`, `textbook/03_monte_carlo.md`,
  `textbook/04_tournaments.md`, `textbook/05_random_walks_diffusion.md`. The P-Set 1 solutions
  are on Canvas, which is not public: do not ask the student for them.
