---
kernelspec:
  name: python3
  display_name: Python 3
---

# Chapter 5: Random Walks & the Diffusion Equation

> A walker taking independent random steps of fixed size along a line ends up approximately Gaussian with a width that grows like $\sqrt{t}$; in the limit of small, frequent steps its probability density obeys the diffusion equation, the book's first continuous description of a discrete random process and the basis for the stochastic models that follow.

:::{note} Running the code
The Python cells on this page run **in your browser**. Click the **power icon** at the top of the page to activate the kernel, then run — or edit — any cell. Packages (NumPy, SciPy, …) load automatically the first time you import them (a few seconds).
:::

## Motivation

A pollen grain knocked around by water molecules, a gambler's bankroll, the logarithm of a stock price, and the score difference in a basketball game seem to have nothing in common. But each quantity changes by a long sequence of small random increments, and we can ask the same question: after $n$ increments, what is the final result likely to be, and how far has it wandered from its start? Chapter 4 introduced the tournament as the book's first path-dependent random process and noted that many others are built the same way, one random step on top of another.

This chapter analyzes the simplest of such processes, the **random walk**: a walker on a line steps a fixed distance left or right at random at every tick of a clock. If the steps are biased to one side, the mean position moves in proportion to the number of steps; if not, it stays put. Either way, the standard deviation of the position grows like the square root of the number of steps. Both facts come from adding the variances of independent steps, the same arithmetic behind Chapter 2's $1/\sqrt{n}$ standard errors and Chapter 3's Monte Carlo error bars.

Those are properties of the walker's distribution after $n$ steps. The chapter then writes an exact equation for the distribution itself, a rule that gives the probabilities after step $n+1$ from those after step $n$, and takes the **continuum limit**, in which the steps become very small and very frequent. The rule becomes the **diffusion equation**, a partial differential equation for the probability density. This is the first time the book describes a discrete random process by a continuous equation, and it happens again with the log-price in Chapter 6, epidemics in Chapter 9, and traffic in Chapter 10. The worked examples then run the modeling loop of Chapter 1: comparing simulated walkers with the formula is **verification**, and comparing the diffusion model with an observed path is **validation**.

## Setup & notation

A walker starts at $X_0 = 0$ and takes one step every $\tau$ seconds. Each step moves it by $+\delta$ with probability $p$ or by $-\delta$ with probability $q = 1 - p$, independently of every other step. Its position $X_n$ after $n$ steps, at time $t = n\tau$, is the sum of all the steps $\varepsilon_i$ so far:
$$
X_n = \sum_{i=1}^{n} \varepsilon_i, \qquad \varepsilon_i \in \{-\delta, +\delta\},
\quad \mathbb{P}(\varepsilon_i = +\delta) = p .
$$

$\delta > 0$, $\tau > 0$, and $0 < p < 1$. At $p = 0$ or $p = 1$ there is no randomness and the walker just moves in one direction.

The model rests on two assumptions:

- **The steps $\varepsilon_i$ are independent.** The direction of step $i$ does not depend on anything before it, including where the walker is: this is what lets us simply add the step variances. The Intuition section explains how a violation shows up in data.
- **The steps all have the same distribution.** The size $\delta$ and the probabilities $p$ and $q$ are the same at every step and everywhere on the line, so there are no walls and no preferred region, and the step variance is fixed and finite. Worked Example 3 checks whether the increments of an observed path have the Gaussian shape required by the diffusion model. Chapter 11 adds a reflecting wall to a walk of this kind.

Together, the two assumptions say that the steps $\varepsilon_i$ are **independent and identically distributed**, or i.i.d., the same condition behind the sample means of Chapter 2 and the Monte Carlo estimates of Chapter 3.

New symbols in this chapter:

- $\delta$: the step size, a length.
- $\tau$: the time between steps.
- $p$, $q = 1 - p$: the probabilities of stepping right and left. The walk is **symmetric** when $p = q = 1/2$ and **biased** otherwise.
- $n_+$: the number of rightward steps among the first $n$.
- $P_n(x)$: the probability that the walker sits at lattice position $x$ after $n$ steps.
- $\rho(x,t)$: the probability density of the continuum description, with units of one over length. $\rho(x,t)\,dx$ is the probability of finding the walker in a short interval of length $dx$ around $x$. Its integral over $x$ is $1$.
- $D$: the diffusion coefficient, defined in the continuum limit below.
- $v$: the drift velocity of a biased walk, also defined there.

## Core ideas

### Mean and variance

The position is a sum of independent steps, so its mean and variance follow from the linearity of expectation and the variance rules of [Appendix A](./A_notation.md). One step has mean $\mathbb{E}[\varepsilon_i] = \delta p - \delta q = \delta(p - q)$ and second moment $\mathbb{E}[\varepsilon_i^2] = \delta^2$, so its variance is $\delta^2 - \delta^2 (p - q)^2 = 4\delta^2 pq$, using $1 - (p-q)^2 = (1 - p + q)(1 + p - q) = (2q)(2p)$. Adding $n$ such steps gives
$$
\mathbb{E}[X_n] = n\,\delta\,(p - q),
\qquad
\mathrm{Var}(X_n) = 4\,n\,\delta^2\,p\,q .
$$
The variances add because the steps are independent. Correlated steps would bring in covariance terms and change the growth law below.

For the symmetric walk, $p = q = 1/2$, the mean is $0$ and the variance is $n\delta^2$, so **the standard deviation of the position grows like $\delta\sqrt{n}$**. On average the walker goes nowhere, but its typical distance from the origin keeps growing, more slowly than the number of steps. This is the $1/\sqrt{n}$ standard error of Chapter 2 and the $1/\sqrt{N}$ Monte Carlo error of Chapter 3 seen from the other side. There, the sum of $n$ independent terms was divided by $n$, so its spread shrank like $\sqrt{n}/n$. Here nothing is divided, and the spread grows like $\sqrt{n}$.

For a biased walk the mean grows like $n$ while the standard deviation still grows like $\sqrt{n}$, so at long times the drift wins: the walker eventually leaves its starting point in the direction of the bias, and the randomness only blurs how far it has gone. Worked Example 2 puts numbers on these two competing scales.

### The exact distribution and its Gaussian approximation

The full distribution is exact at every $n$ too, because the walk is a binomial experiment in the sense of [Appendix A](./A_notation.md). Let $n_+$ be the number of right steps among the first $n$. Then $n_+ \sim \mathrm{Binomial}(n, p)$ and $X_n = n_+\delta - (n - n_+)\delta = (2n_+ - n)\delta$, so
$$
\mathbb{P}\big(X_n = (2k - n)\delta\big) = \binom{n}{k} p^k q^{\,n-k}, \qquad k = 0, 1, \dots, n .
$$
As a check, the binomial mean $np$ and variance $npq$ give $\mathbb{E}[X_n] = (2np - n)\delta = n\delta(p - q)$ and $\mathrm{Var}(X_n) = 4\delta^2 npq$, the same formulas as before.

When both $np$ and $nq$ are large, the central limit theorem of [Appendix A](./A_notation.md) replaces the binomial by a Gaussian with the same mean and variance:
$$
X_n \;\approx\; \mathcal{N}\big(n\delta(p - q),\; 4n\delta^2 pq\big).
$$
For the symmetric walk, $X_n \approx \mathcal{N}(0, n\delta^2)$, and the approximating probability *density* at time $n\tau$ is
$$
\rho(x, n\tau) \approx \frac{1}{\sqrt{2\pi n\delta^2}} \exp\!\left(-\frac{x^2}{2n\delta^2}\right).
$$

One detail here matters when comparing the formula with a simulation. The formula is a density, but the walker lives on a lattice: after $n$ steps it can only be at $x = (2k - n)\delta$, which are the even multiples of $\delta$ when $n$ is even and the odd multiples when $n$ is odd, spaced $2\delta$ apart either way. The probability of a reachable position is therefore approximately $\rho(x,n\tau)\,2\delta$, the density times the spacing, and the probability of any position in between is exactly zero. A histogram with bins that ignore the lattice can look jagged even when the Gaussian approximation is accurate, because some bins contain a reachable position and their neighbors contain none. Bins of width $2\delta$ centered on the reachable positions fix it.

The central limit theorem gives the shape after many steps, from a point start, for these particular steps. It gives no equation to solve from a different starting distribution, with a wall in the way, or with step probabilities that vary from place to place. The next two sections build that equation.

### The master equation

We now follow the probabilities from one step to the next instead of describing $X_n$ directly. If the walker is at position $x$ after step $n + 1$, there are only two possibilities: the walker must have been at $x - \delta$ after step $n$ and stepped right, or at $x + \delta$ and stepped left. The two routes cannot both happen, so their probabilities add:
$$
P_{n+1}(x) = p\,P_n(x - \delta) + q\,P_n(x + \delta).
$$
This is the **master equation** of the random walk. It is exact at every $n$, assumes nothing about the shape of $P_n$, and uses only the step probabilities $p$ and $q$. Summing both sides over all $x$ gives $1 = p + q$: total probability is conserved from step to step.

Given $P_0$, applying the master equation repeatedly produces $P_n$ for every $n$, from *any* starting distribution, not only a point. A wall is a modified equation at one site. A position-dependent bias uses the probabilities at the sites the walker *leaves from*: the incoming terms become $p(x-\delta)P_n(x-\delta) + [1-p(x+\delta)]P_n(x+\delta)$. The recursion gives you something that the central limit theorem does not: a rule you can adapt.

### The continuum limit and the diffusion equation

Now let the steps become small and frequent, $\delta\to0$ and $\tau\to0$, while keeping the elapsed time $t$ fixed. A symmetric walker takes $n=t/\tau$ steps, giving
$$
\mathrm{Var}(X_n)=\frac{\delta^2}{\tau}\,t.
$$
To keep the spread finite and nonzero, we must hold $\delta^2/\tau$ fixed: halving the step size requires four times as many steps per unit time. We now derive this relation more formally, together with an equation for the probability density.

We replace the discrete $P_n(x)$ by a smooth density $\rho(x,t)$ that approximates the walk in this limit. At reachable sites, spaced $2\delta$ apart, $P_n(x)\approx2\delta\,\rho(x,n\tau)$. The exact lattice probabilities alternate between zero and nonzero.

For $p = q = 1/2$, replacing the probabilities in the master equation by their smooth approximation and canceling $2\delta$ gives
$$
\rho(x,t+\tau) \approx \tfrac12\rho(x-\delta,t) + \tfrac12\rho(x+\delta,t).
$$
Now use Taylor expansions to write the nearby values in terms of the density at $(x,t)$:
$$
\begin{aligned}
\rho(x,t+\tau) &\approx \rho + \tau\,\frac{\partial \rho}{\partial t},\\
\rho(x\pm\delta,t) &\approx \rho \pm \delta\,\frac{\partial \rho}{\partial x}
    + \tfrac12\delta^2\,\frac{\partial^2 \rho}{\partial x^2}.
\end{aligned}
$$
Here $\frac{\partial \rho}{\partial t}$ means the rate of change with time at a fixed position, and $\frac{\partial \rho}{\partial x}$ the rate of change with position at a fixed time.

The first derivatives of the spatial expansions cancel out. Then subtract $\rho$ from both sides and divide by $\tau$. As the steps shrink with $\delta^2/\tau$ fixed, the higher-order terms vanish, giving the **diffusion equation**:
$$
\frac{\partial \rho}{\partial t}=\frac{\delta^2}{2\tau}\,\frac{\partial^2 \rho}{\partial x^2}.
$$
The coefficient comes directly from the second-order Taylor term. We call it the **diffusion coefficient**,
$$
D\equiv\frac{\delta^2}{2\tau},
\qquad
\boxed{\ \frac{\partial \rho}{\partial t}=D\,\frac{\partial^2 \rho}{\partial x^2}.\ }
$$
Its units are length squared per time, and the variance grows as $2Dt$.

The second derivative $\frac{\partial^2 \rho}{\partial x^2}$ measures the curvature of the density profile. At a peak, the density curves downward and decreases over time; at a dip, it curves upward and increases. $D$ sets how fast probability mass spreads from high density to low density regions.

For a biased walk, the first-order spatial terms no longer cancel. Exercise 2 derives the **drift–diffusion equation**:
$$
\frac{\partial \rho}{\partial t} = -v\,\frac{\partial \rho}{\partial x} + D\,\frac{\partial^2 \rho}{\partial x^2},
\qquad
v = \frac{(p-q)\delta}{\tau}.
$$
The drift term translates the whole density at velocity $v$ while diffusion spreads it. Using $D=\delta^2/(2\tau)$, we can write
$$
\frac{p-q}{\delta}=\frac{v}{2D}.
$$
The right-hand side is finite. Therefore, as $\delta$ goes to zero, $p-q$ must also go to zero to keep the ratio finite. This may seem paradoxical: if each step becomes unbiased, why does the drift not disappear? The bias contributes a mean displacement $(p-q)\delta$ per step, which shrinks like $\delta^2$, but the number of steps per unit time grows like $1/\delta^2$. These two effects balance, leaving a finite drift velocity $v$.

> **Convention for $D$.** Some texts put $\tfrac12 D$ in the equation, making the variance grow at rate $D$. Our convention gives $2D$.

### The fundamental solution

Suppose the continuum model is defined on the entire line and all probability is initially concentrated at the origin. We write this as $\rho(x,0)=\delta_{\mathrm D}(x)$, where the **Dirac delta** $\delta_{\mathrm D}$ represents a unit point mass. The subscript distinguishes it from the discrete step size. The solution of the drift–diffusion equation is
$$
G_v(x,t)=\frac{1}{\sqrt{4\pi Dt}}
\exp\!\left[-\frac{(x-vt)^2}{4Dt}\right].
$$
This is a Gaussian with mean $vt$, variance $2Dt$, and integral one. Drift moves its center at velocity $v$, while diffusion makes it wider. Setting $v=0$ gives the solution of the diffusion equation.

For a symmetric random walk, substituting $D=\delta^2/(2\tau)$ and $t=n\tau$ gives $2Dt=n\delta^2$, the discrete variance. The fundamental solution agrees with our earlier binomial approximation: it is exact for the continuous model and approximate for a finite number of steps.

The equation is **linear**: if $\rho_1$ and $\rho_2$ are solutions, then $a\rho_1+b\rho_2$ is also a solution. This is the **superposition principle**. It allows us to build solutions for more general initial distributions by adding shifted copies of $G_v$.

For example, if half the probability starts at $-1$ and half at $1$, then for $t>0$
$$
\rho(x,t)=\frac12G_v(x+1,t)+\frac12G_v(x-1,t).
$$
More generally, if the initial density is $\rho_0(y)$, then
$$
\rho(x,t)=\int_{-\infty}^{\infty}G_v(x-y,t)\,\rho_0(y)\,dy.
$$
Each starting point $y$ contributes a Gaussian centered at $y+vt$, weighted by the probability of starting there.

These formulas assume the entire real line, so there are no endpoints. On a finite interval, **boundary conditions** specify what happens when probability reaches an endpoint. For example, a wall changes the solution because probability cannot continue through it.

## Worked example 1: simulating the symmetric walk

The cell simulates $M=5{,}000$ walkers for $N=400$ steps with $\delta=1$, then compares the sample mean and variance with the predictions $0$ and $N\delta^2$:

```{code-cell} python
import numpy as np

rng = np.random.default_rng(seed=0)
N, M, delta = 400, 5_000, 1.0                     # steps, walkers, step size

steps = rng.choice([-delta, delta], size=(M, N))   # each entry +delta or -delta, p = q = 1/2
X = np.cumsum(steps, axis=1)                       # position of every walker after each step

x = X[:, -1]                                      # positions after all N steps
sem = x.std(ddof=1) / np.sqrt(M)
print(f"mean = {x.mean():+.2f} +/- {sem:.2f}   (theory: 0)")
print(f"variance = {x.var(ddof=1):.1f}          (theory: {N * delta**2:.0f})")

# mean = +0.07 +/- 0.28   (theory: 0)
# variance = 404.7        (theory: 400)
```

The standard error of the mean is the sample standard deviation divided by $\sqrt M$, as in Chapter 2. The simulated mean is well within one standard error of zero, and the variance is close to $N\delta^2=400$. As usual, increasing $M$ would reduce these fluctuations.

This is **verification**: the code reproduces the model's predicted moments. Whether a real process follows that model requires observations, as in Worked Example 3.

The [companion script](./code/05_random_walks_diffusion/symmetric_walk.py) adds the pictures: histograms of the walker positions after $50$, $150$, and $400$ steps against the corresponding Gaussian approximations, and the empirical standard deviation against the number of steps on log-log axes, a straight line of slope $1/2$.

## Worked example 2: a biased walk, and drift against spread

Consider a biased walk with $p=0.55$, $q=0.45$, and $\delta=1$. After $N=1000$ steps, its mean position is
$$
\mathbb{E}[X_N]=(p-q)\delta N=100,
$$
while its standard deviation is
$$
\mathrm{SD}(X_N)=\delta\sqrt{4Npq}=\sqrt{990}\approx31.5.
$$
The walkers are therefore centered near $100$, with a typical spread of about $31.5$ around that value.

```{code-cell} python
import numpy as np

rng = np.random.default_rng(seed=0)
N, M, p = 1000, 5_000, 0.55
q = 1 - p
X_N = rng.choice([-1, 1], size=(M, N), p=[q, p]).sum(axis=1)

print(f"mean = {X_N.mean():.1f}   (theory: {(p-q) * N:.1f})")
print(f"SD   = {X_N.std(ddof=1):.1f}    (theory: {np.sqrt(4 * N * p * q):.1f})")

# mean = 100.2   (theory: 100.0)
# SD   = 31.6    (theory: 31.5)
```

The mean grows in proportion to $N$, while the standard deviation grows only as $\sqrt N$. To find when the drift becomes as large as the spread, set the two expressions equal:
$$
|p-q|\delta N=\delta\sqrt{4Npq}.
$$
Solving gives
$$
N^\ast=\frac{4pq}{(p-q)^2}=99.
$$
Before about $99$ steps, the random spread is larger than the expected displacement. After that, the drift is larger, although the paths continue to fluctuate.

The [companion script](./code/05_random_walks_diffusion/biased_walk.py) simulates this example and plots the mean and standard deviation as the number of steps grows. The same comparison helps explain why a slightly better basketball team can still lose a single game: its expected advantage accumulates linearly, but random scoring fluctuations can initially be larger. Exercise 4 uses this idea to connect a score model with Elo win probabilities.

## Worked example 3: does an observed path behave like diffusion?

For the drift–diffusion model developed above, the change over a time interval $\Delta t$ is
$$
\Delta Y\sim\mathcal N(v\Delta t,2D\Delta t).
$$
Thus Gaussian increments are a necessary prediction of the model.

We check this prediction using a prepared daily data series. Let $Y_t$ be its value on day $t$ and form the daily increments
$$
\Delta Y_t=Y_t-Y_{t-1}.
$$
After subtracting their sample mean and dividing by their sample standard deviation, Gaussian increments should place about $68\%$ of the observations within one standard deviation of zero. Only about $0.0063\%$ should lie more than four standard deviations away.

```{code-cell} python
import pandas as pd
from scipy.stats import norm

url = "https://harvard-am215.github.io/textbook/data/public/fx_usd_eur.csv"
path = pd.read_csv(url, index_col="Date", parse_dates=["Date"])["Close"]
increments = path.diff().dropna()

z = (increments - increments.mean()) / increments.std(ddof=0)
observed_big = int((z.abs() > 4).sum())
expected_big = len(z) * 2 * norm.sf(4)

print(f"increments  : {len(increments)}")
print(f"within 1 SD : {(z.abs() < 1).mean():.0%}   (Gaussian: 68%)")
print(f"beyond 4 SD : {observed_big}     (Gaussian: {expected_big:.1f})")

# increments  : 6920
# within 1 SD : 75%   (Gaussian: 68%)
# beyond 4 SD : 23     (Gaussian: 0.4)
```

The diffusion model predicts only $0.4$ increments beyond four standard deviations, but the data contain $23$. It also predicts $68\%$ of the increments near the center, compared with the observed $75\%$. The observed distribution has both a sharper center and more extreme changes than a Gaussian.

We therefore reject the simple drift–diffusion model for this path. This check tests only one necessary prediction, the shape of the increments. Since that prediction already fails, the path cannot be described by diffusion with constant $v$ and $D$.

## Intuition

> **Why does the mean stay at zero while the variance grows?** For an unbiased walk, each independent step adds zero to the mean and $\delta^2$ to the variance. The average position stays at the origin, but the probability of being within a fixed distance of it decreases at long times.

> **Why $\sqrt t$, and what could change it?** Independent steps with the same finite variance give variance proportional to $t$. Drift changes the mean, not this spread around it. Correlations, changing step variance, or a pull toward a target can alter the scaling. The exponent alone cannot identify the cause; short-lived correlations can even preserve $\sqrt t$ and change only its coefficient.

> **Why not hold the speed $\delta/\tau$ fixed?** If $\delta/\tau=s$, then $\delta^2/\tau=s\delta\to0$. The symmetric walk's variance at any fixed time tends to zero. Holding $\delta^2/\tau$ fixed keeps a nonzero spread.

> **Where does the Gaussian approximation fail?** For a finite walk it works best near the center when both $np$ and $nq$ are large. It can be poor in the tails: the walker cannot pass $|X_n|=n\delta$, while the Gaussian extends forever. Worked Example 3 also shows that observed data need not follow a Gaussian distribution.

> **Why is this also the heat equation?** In a uniform rod, heat flows down the temperature gradient. Conservation of energy gives $\frac{\partial T}{\partial t}=D\,\frac{\partial^2 T}{\partial x^2}$, with $D$ the thermal diffusivity. Up to a factor setting the total heat, the Gaussian describes a point heat pulse spreading along an infinite rod.

## Connections

- **Builds on:** Chapters 2–3 for binomial and Gaussian distributions, variance arithmetic, and verification versus validation; Chapter 4 for sequential random processes and Elo; Appendix A for the central limit theorem.
- **Used in:** Chapters 6–7 for price models and option pricing; Chapter 8 for extremes; Chapters 9–11 for epidemics, continuum traffic models, and queues.
- **Further directions:** walks with correlated steps; first-passage problems, which ask when a walker first reaches a point; and models in which drift or diffusion varies with position.

## Exercises

1. **Conceptual.** A friend says: "If I flip a fair coin enough times, the number of heads will equal the number of tails; heads eventually catch up." Use what you know about the growth of the variance of a random walk to explain what is right and what is wrong in this statement. (Hint: consider the walk $X_n = \#\text{heads} - \#\text{tails}$.)

2. **Derivation.** Repeat the expansion of the master equation for the *biased* walk, $p \ne q$. Show that
$$
\tau\,\frac{\partial \rho}{\partial t} \approx -(p - q)\,\delta\,\frac{\partial \rho}{\partial x} + \tfrac{1}{2}\,\delta^2\,\frac{\partial^2 \rho}{\partial x^2},
$$
identify the drift velocity $v$ and the diffusion coefficient $D$ in the resulting drift–diffusion equation, and explain how $p - q$ must behave as $\delta \to 0$ for $v$ to stay finite.

3. **Computational.** A symmetric random walk starts at $X_0=0$ and stops the first time it reaches either $-L$ or $L$. Simulate $20{,}000$ walks for each of $L=10,20,40$.
   (a) Report the mean stopping time for each value of $L$.
   (b) Plot the mean stopping time against $L$ on log-log axes and fit a straight line. What slope do you find?
   (c) Use the fact that a random walk typically travels a distance of order $\sqrt n$ in $n$ steps to explain the scaling you observe.

4. **Computation and modeling: from a score random walk to Elo.** Hold the ratings of teams A and B fixed during one game, and write their rating difference as $\Delta R=R_A-R_B$. Model the score difference after $n$ scoring events as
$$
X_n=\varepsilon_1+\cdots+\varepsilon_n,
$$
where the increments are independent, with mean $a\Delta R$ and variance $s^2$.

(a) Show that
$$
P_{\mathrm{RW}}(\text{A wins})\approx
\Phi(b\Delta R),
\qquad
b=\frac{a\sqrt n}{s},
$$
where $\Phi$ is the standard Gaussian CDF. Explain why this probability is a sigmoid function of $\Delta R$.

(b) Chapter 4 gave the Elo probability
$$
P_{\mathrm{Elo}}(\text{A wins})=\frac{1}{1+10^{-\Delta R/400}}.
$$
To put the two curves on the same scale, choose $b$ so that both give the same probability at $\Delta R=400$. Find $b$, then plot both curves for $-800\leq\Delta R\leq800$. Where do they differ most?

(c) Take $n=100$, $s=1$, and $a=b/10$. For several rating differences, simulate $20{,}000$ complete games by drawing and summing $100$ Gaussian increments. Keep the ratings fixed: each path represents a new realization of the same game. Compare the fraction with $X_n>0$ with both curves. Does this agreement show that the random-walk model describes real games?

:::{admonition} Solutions
:class: dropdown

**1.** The count difference $X_n$ has mean zero but standard deviation $\sqrt n$, so its typical distance from zero grows rather than shrinks. More flips therefore do not force the counts to become equal. What does settle down is the relative difference: $X_n/n\to0$, so the fraction of heads approaches $1/2$. The proportions become nearly equal even while the count difference keeps fluctuating.

**2.** Insert the Taylor expansions into the biased master equation. The terms proportional to $\rho$ cancel because $p+q=1$, leaving
$$
\tau\frac{\partial \rho}{\partial t}
\approx-(p-q)\delta\frac{\partial \rho}{\partial x}
+\frac{\delta^2}{2}\frac{\partial^2 \rho}{\partial x^2}.
$$
Dividing by $\tau$ and comparing with the drift–diffusion equation gives
$$
v=\frac{(p-q)\delta}{\tau},
\qquad
D=\frac{\delta^2}{2\tau}.
$$
Since $D$ is fixed, $\tau=\delta^2/(2D)$, and therefore
$$
\frac{p-q}{\delta}=\frac{v}{2D}.
$$
To keep $v$ finite as $\delta\to0$, the difference $p-q$ must also approach zero. The bias of one step vanishes, but the number of steps per unit time grows, leaving a finite drift velocity.

**3.** The [companion script](./code/05_random_walks_diffusion/exit_times.py) gives mean stopping times $100.1$, $403.2$, and $1625.2$ steps for $L=10,20,40$, with a fitted slope of $2.011$. Since a walk travels a typical distance $L\sim\sqrt n$, reaching a boundary a distance $L$ away should take about $n\sim L^2$ steps. The small deviations come from simulating finitely many walks.

**4.** (a) The mean of the final score difference is $na\Delta R$ and its standard deviation is $s\sqrt n$. The Gaussian approximation therefore gives
$$
P(X_n>0)
\approx\Phi\!\left(\frac{na\Delta R}{s\sqrt n}\right)
=\Phi(b\Delta R),
\qquad
b=\frac{a\sqrt n}{s}.
$$
As $\Delta R$ increases, the argument of $\Phi$ moves from negative to positive, so the probability traces an S-shaped, or sigmoid, curve.

(b) Elo gives $P_{\mathrm{Elo}}=10/11$ at $\Delta R=400$, so the matching scale satisfies
$$
\Phi(400b)=\frac{10}{11},
\qquad
b=\frac{\Phi^{-1}(10/11)}{400}\approx0.00334.
$$
Both curves equal $1/2$ at zero and, by construction, agree again at $\Delta R=\pm400$. Their largest difference in the plotted range is about $0.012$, near $|\Delta R|=180$. Beyond $400$ points, the Gaussian CDF approaches $0$ and $1$ faster than the Elo curve.

(c) The [companion script](./code/05_random_walks_diffusion/elo_random_walk.py) simulates the score one increment at a time. The win fractions follow $\Phi(b\Delta R)$ closely. Elo remains similar near the center but differs in the tails because it uses a logistic CDF rather than a Gaussian CDF. This is verification against the model used to generate the simulations; it does not show that either curve describes real games. That requires observed score paths and outcomes.

:::

## Further reading

- Howard C. Berg, [*Random Walks in Biology*](https://www.jstor.org/stable/jj.32726718),
  Princeton Science Library edition (2025) — an accessible next step for diffusion, drift,
  and random motion in biological systems. ISBN 9780691279893 ·
  [HOLLIS](https://hollis.harvard.edu/discovery/search?query=any,contains,Random%20Walks%20in%20Biology%20Berg&tab=LibraryCatalog&search_scope=MyInstitution&vid=01HVD_INST:HVD2&offset=0).
- Albert Einstein,
  [1905 paper on Brownian motion](https://doi.org/10.1002/andp.19053220806),
  *Annalen der Physik* 322(8):549–560 — the original derivation connecting molecular motion
  with a measurable displacement that grows like $\sqrt t$.
  [Public-domain German scan](https://archive.org/details/annalenderphysi108unkngoog) ·
  [HOLLIS](https://hollis.harvard.edu/discovery/search?query=any,contains,10.1002%2Fandp.19053220806&tab=Everything&search_scope=MyInst_and_CI&vid=01HVD_INST:HVD2&offset=0).
- Hal S. Stern,
  ["A Brownian Motion Model for the Progress of Sports Scores"](https://doi.org/10.1080/01621459.1994.10476851),
  *Journal of the American Statistical Association* 89(427):1128–1134 (1994) — applies the
  model behind Exercise 4 to professional basketball scores and win probabilities.
  [HOLLIS](https://hollis.harvard.edu/discovery/search?query=any,contains,10.1080%2F01621459.1994.10476851&tab=Everything&search_scope=MyInst_and_CI&vid=01HVD_INST:HVD2&offset=0).
- Crispin Gardiner,
  [*Stochastic Methods: A Handbook for the Natural and Social Sciences*](https://link.springer.com/book/9783540707127),
  4th ed. (2009) — a more advanced reference for master equations, diffusion, and related
  stochastic processes. ISBN 9783540707127 ·
  [HOLLIS](https://hollis.harvard.edu/discovery/search?query=any,contains,Gardiner%20stochastic%20methods%20handbook&tab=LibraryCatalog&search_scope=MyInstitution&vid=01HVD_INST:HVD2&offset=0).
