# Appendix A: Notation & Probability Primer

This chapter fixes the notation used across the textbook and refreshes the probability concepts every later chapter assumes. It is meant to be skimmable; if a symbol or fact is unfamiliar, this is where to look first.

## Notation

### Random variables and samples

| Symbol | Meaning |
|---|---|
| $X$, $Y$, $Z$ | random variables (capitals) |
| $x$, $y$, $z$ | particular realizations / sample values (lowercase) |
| $X_i$ | the $i$-th of $n$ IID observations |
| $\{X_i\}_{i=1}^{n}$ | a sample of size $n$ |
| $X \sim D$ | "$X$ is distributed as $D$" |
| $X_i \overset{\text{iid}}{\sim} D$ | $X_1, \dots, X_n$ independent and identically distributed |
| $\mathbb{E}[X]$, $\langle X \rangle$ | expectation (both notations appear in lectures) |
| $\mathrm{Var}(X)$ | variance |
| $\mathrm{Cov}(X, Y)$ | covariance |
| $\mathbb{P}(A)$ | probability of event $A$ |

### Distributions

| Symbol | Meaning |
|---|---|
| $f(x \mid \theta)$ | probability density (continuous) or mass (discrete) of $X$ given parameter(s) $\theta$ |
| $F(x)$ | cumulative distribution function: $F(x) = \mathbb{P}(X \le x)$ |
| $\mathcal{N}(\mu, \sigma^2)$ | Normal/Gaussian, mean $\mu$, variance $\sigma^2$ |
| $\mathrm{Bernoulli}(p)$ | Bernoulli, success probability $p$ |
| $\mathrm{Binomial}(n, p)$ | sum of $n$ IID Bernoulli$(p)$ |
| $\mathrm{Geometric}(p)$ | geometric, success probability $p$ |
| $\mathrm{Poisson}(\lambda)$ | Poisson, rate $\lambda$ per unit interval |
| $\mathrm{Exp}(\lambda)$ | exponential, rate $\lambda$ |
| $\mathrm{Uniform}(a, b)$ | uniform on $[a, b]$ |

### Inference and estimation

| Symbol | Meaning |
|---|---|
| $\theta$ | (vector of) model parameters |
| $\hat{\theta}$ | an estimate of $\theta$ from data |
| $L(\theta)$ | likelihood: $L(\theta) = \prod_i f(X_i \mid \theta)$ |
| $\ell(\theta) = \log L(\theta)$ | log-likelihood |
| $-\ell(\theta)$ | negative log-likelihood (NLL); what numerical solvers minimize |

### Stochastic processes

| Symbol | Meaning |
|---|---|
| $X_t$ | random variable indexed by (discrete or continuous) time $t$ |
| $W_t$ | standard Wiener process (Brownian motion); $W_0 = 0$, and $W_t - W_s \sim \mathcal{N}(0, t-s)$ for $s < t$ |
| $dW_t$ | infinitesimal Brownian increment |
| $\mu$, $\sigma$ | drift and volatility of a stochastic process (Chs. 6–7) |

## Common distributions

A reference, not a tutorial: these are assumed prerequisites (Stat 110 level), collected
here so you can check a form or a moment without hunting. The last column is the one to read
if you are trying to *recognise* which distribution a described situation calls for — the
question is always what mechanism generates the randomness.

| Distribution | pmf / pdf | Support | Mean | Variance | Arises when |
|---|---|---|---|---|---|
| $\mathrm{Bernoulli}(p)$ | $p^{x}(1-p)^{1-x}$ | $x \in \{0,1\}$ | $p$ | $p(1-p)$ | one yes/no trial |
| $\mathrm{Binomial}(n,p)$ | $\binom{n}{k} p^{k}(1-p)^{n-k}$ | $k = 0,\dots,n$ | $np$ | $np(1-p)$ | successes in a **fixed** number $n$ of independent trials |
| $\mathrm{Geometric}(p)$ | $(1-p)^{k-1}p$ | $k = 1,2,\dots$ | $1/p$ | $(1-p)/p^{2}$ | trials up to and including the first success |
| $\mathrm{Poisson}(\lambda)$ | $\dfrac{\lambda^{k}e^{-\lambda}}{k!}$ | $k = 0,1,2,\dots$ | $\lambda$ | $\lambda$ | **counts** of rare independent events at a constant average rate, over a fixed interval |
| $\mathrm{Exp}(\lambda)$ | $\lambda e^{-\lambda x}$ | $x \ge 0$ | $1/\lambda$ | $1/\lambda^{2}$ | **waiting time** between those same events; memoryless |
| $\mathcal{N}(\mu,\sigma^{2})$ | $\dfrac{1}{\sqrt{2\pi\sigma^{2}}}\exp\!\left(-\dfrac{(x-\mu)^{2}}{2\sigma^{2}}\right)$ | $x \in \mathbb{R}$ | $\mu$ | $\sigma^{2}$ | many small independent effects add up (CLT) |
| $\mathrm{Uniform}(a,b)$ | $\dfrac{1}{b-a}$ | $a \le x \le b$ | $\dfrac{a+b}{2}$ | $\dfrac{(b-a)^{2}}{12}$ | no value in the range is preferred over another |

Three things worth fixing in memory, because they are the usual slips:

- **Poisson and exponential are the same process seen two ways.** If events arrive at
  constant rate $\lambda$, the *count* in a fixed window is Poisson and the *gap* between
  consecutive events is exponential. "Number of X per Y" is a count; "time until the next X"
  is a waiting time.
- **A binomial count requires the number of trials $n$ to be fixed before you start.** If the
  number of trials is itself the random thing you are counting, the count is not binomial.
- **$\mathcal{N}$ takes the variance, not the standard deviation**, throughout this book —
  $\mathcal{N}(\mu, \sigma^2)$. Misreading $\sigma^2 = 4$ as $\sigma = 4$ is the single most
  common error with this notation.

**Geometric convention.** The form above counts *trials including the first success*, so
$k \ge 1$ and the mean is $1/p$. The other common convention counts *failures before* it,
giving $k \ge 0$ and mean $(1-p)/p$. Both are called geometric; state which you are using.

## Probability facts used everywhere

### Independence

Two random variables $X, Y$ are **independent** iff their joint mass function (discrete) or density (continuous) factorizes:
$$
f_{X,Y}(x, y) = f_X(x)\, f_Y(y).
$$
Both cases matter here: the sample in P-Set 0's joint-pmf item is discrete, and the MLE examples in Chapter 2 include both.
Independence makes the likelihood of a sample factor into a product — the starting point of MLE (Ch. 2).

### Linearity of expectation

For any $X, Y$ and constants $a, b$:
$$
\mathbb{E}[a X + b Y] = a\, \mathbb{E}[X] + b\, \mathbb{E}[Y].
$$
This holds even when $X$ and $Y$ are *dependent* — a frequent source of slick arguments.

### Variance arithmetic

$$
\mathrm{Var}(aX + bY) = a^2 \mathrm{Var}(X) + b^2 \mathrm{Var}(Y) + 2ab\, \mathrm{Cov}(X, Y).
$$

For IID samples (so $\mathrm{Cov} = 0$, all $\mathrm{Var} = \sigma^2$), the variance of the sample mean is
$$
\mathrm{Var}\!\left(\frac{1}{n}\sum_{i=1}^n X_i\right) = \frac{\sigma^2}{n},
$$
giving the famous $1/\sqrt{n}$ shrinkage of the standard error. This is the workhorse fact behind both Monte Carlo error analysis (Ch. 3) and the $\sqrt{t}$ scaling of random walks (Ch. 5).

### Law of large numbers (LLN)

For IID $X_i$ with finite mean $\mu$:
$$
\bar X_n = \frac{1}{n}\sum_{i=1}^n X_i \xrightarrow[n \to \infty]{} \mu.
$$
"Sample averages converge to expectations." Justifies estimating expectations by simulation.

### Central limit theorem (CLT)

For IID $X_i$ with mean $\mu$ and finite variance $\sigma^2$:
$$
\sqrt{n}\,(\bar X_n - \mu) \xrightarrow[n \to \infty]{d} \mathcal{N}(0, \sigma^2).
$$
"Sample means are approximately Gaussian, with width $\sigma/\sqrt{n}$." Underwrites confidence intervals, the diffusion limit of random walks (Ch. 5), and the lognormal model of stock prices (Ch. 6).

> **CLT vs. extreme value theory.** The CLT describes the *bulk* (sample averages). Extreme value theory (Ch. 8) describes the *tail* — the maximum or minimum of $n$ samples. They have different limiting distributions and very different scaling.

### Change of variables

If $Y = g(X)$ with $g$ smooth and monotone, the density of $Y$ is
$$
f_Y(y) = f_X(g^{-1}(y))\, \left|\frac{d g^{-1}}{dy}\right|.
$$
Used to derive the lognormal density (Ch. 6) from a Gaussian via $Y = e^X$.

### A note on $\log$

Throughout, $\log = \ln$ (natural log). The base only matters when reporting nats vs. bits; for optimization, derivatives, etc., it is a multiplicative constant that does not change the argmax.

## Conventions for code

Every code example in the textbook uses:
- **NumPy** for arrays and random sampling (`numpy.random.default_rng(seed)`, not the legacy global `np.random.seed`).
- **SciPy** for distributions (`scipy.stats`) and optimization (`scipy.optimize`).
- **Matplotlib** for plots.
- A passed-in `rng` argument for any function that consumes randomness — never module-level seeding. This matches the style we expect from student projects.

```python
import numpy as np

rng = np.random.default_rng(seed=42)
samples = rng.binomial(n=10, p=0.3, size=1000)
```
