---
kernelspec:
  name: python3
  display_name: Python 3
---

# Chapter 6: Geometric Brownian Motion

> If a price's random changes are proportional to the price itself, its logarithm performs the biased random walk of Chapter 5; the resulting model, geometric Brownian motion, makes future prices lognormal, makes the average price grow faster than the typical price by $\sigma^2/2$ per year, and has two parameters that market data determine very unequally.

:::{note} Running the code
The Python cells on this page run **in your browser**. Click the **power icon** at the top of the page to activate the kernel, then run — or edit — any cell. Packages (NumPy, SciPy, …) load automatically the first time you import them (a few seconds).
:::

## Motivation

A $\$1$ move in a $\$10$ stock is a dramatic day; in a $\$1000$ stock it is barely visible. Chapter 5's random walk cannot tell the two apart, because its steps have the same size wherever the walker is, and it lets the walker go below zero, which a price cannot. For prices the natural unit is the *fraction*: a 1% move means the same thing at any price. So the question is: what random process describes a quantity whose random changes are proportional to its size?

Answering it takes two tools. The first is the **stochastic differential equation** (SDE), a compact way of writing Chapter 5's random walk in continuous time that also lets the size and bias of the steps depend on where the walker is. The second is **Itô's lemma**, the rule for changing variables in an SDE, which differs from the ordinary chain rule by one term. Applied to the logarithm of a price, the two give **geometric Brownian motion** (GBM), the baseline model for asset prices and the basis of Chapter 7. The extra term of Itô's lemma has a consequence that is easy to get wrong: the average price and the typical price grow at rates that differ by $\sigma^2/2$. The worked examples follow the modeling loop: Example 1 **verifies** a simulator, Example 2 **estimates** the parameters from market data, and Example 3 **validates** an assumption.

## Setup & notation

We describe a quantity $X_t$ that changes randomly in continuous time $t$. Over each short interval $dt$ its change is assumed to be the sum of a deterministic part proportional to $dt$ and a random part whose variance is proportional to $dt$, with three further assumptions:

- **Independence.** The random parts over non-overlapping intervals are independent, so their variances add, as in Chapter 5.
- **Dependence on the present only.** The size of both parts may depend on the current value $X_t$ and on $t$, but not on the path that led there. Both are evaluated at the *start* of each interval (the Itô convention).
- **Gaussian noise.** The random parts are Gaussian. For many small independent steps this follows from the central limit theorem, as in Chapter 5; Chapter 5's Worked Example 3 already found fatter tails than a Gaussian in real daily data, and Chapter 8 takes them up.

For prices we add one more: the *fractional* change of the price has the same mean and variance at every date and price level. Worked Example 3 tests whether its variance is really constant.

New symbols in this chapter:

- $a(x,t)$, $b(x,t)$: the **drift coefficient** and **noise amplitude** of an SDE: the mean rate of change and the size of the random kicks when $X_t = x$.
- $W_t$: a **standard Wiener process** (Brownian motion), Chapter 5's symmetric walk in the continuum limit with $D = 1/2$: $W_0 = 0$ and $W_t - W_s \sim \mathcal{N}(0, t-s)$, independent over non-overlapping intervals. Its change over a short interval is $dW_t \sim \mathcal{N}(0, dt)$, or $\sqrt{dt}\,Z$ with $Z \sim \mathcal{N}(0,1)$.
- $S_t$: a price, with known starting value $S_0 > 0$; $t$ is in years.
- $\mu$: the **drift** of a price, per year: the growth rate of its *expected* value, $\mathbb{E}[S_t] = S_0 e^{\mu t}$. It is **not** the mean log return, which is $\mu - \sigma^2/2$ per year. Confusing the two is this chapter's trap.
- $\sigma$: the **volatility**: the standard deviation of the log return over one year, or $\sigma\sqrt{\Delta t}$ over an interval $\Delta t$.
- $r_i$, $m$, $s^2$: $N$ observed log returns at spacing $\Delta t$, their sample mean, and their sample variance (divided by $N$).

## Core ideas

### Stochastic differential equations: the random walk in continuous time

In Chapter 5's continuum limit, where the steps become small and frequent, a biased walker moves on average by $v\,dt$ in a short interval $dt$, and its position spreads with variance $2D\,dt$. Both statements fit in one line:
$$
dX_t = v\,dt + \sqrt{2D}\,dW_t .
$$
Read it as the rule for one short step: move by $v\,dt$, then add a Gaussian kick with mean zero and standard deviation $\sqrt{2D\,dt}$. This is a stochastic differential equation. The generalization lets the drift and the size of the kicks depend on where the walker is and when:
$$
\boxed{\ dX_t = a(X_t, t)\,dt + b(X_t, t)\,dW_t\ }
$$
To simulate it, replace $dt$ by a small step $\Delta t$ and $dW_t$ by $\sqrt{\Delta t}\,Z$:
$$
X_{k+1} = X_k + a(X_k, t_k)\,\Delta t + b(X_k, t_k)\,\sqrt{\Delta t}\,Z_k ,
\qquad Z_k \sim \mathcal{N}(0,1) \text{ independent}.
$$
This is the **Euler–Maruyama scheme**, and it is a random walk with Gaussian steps whose bias and size change from place to place. An SDE is exactly that walk in the limit $\Delta t \to 0$. Notice that the kick is of size $\sqrt{\Delta t}$, much larger than the drift's $\Delta t$ when $\Delta t$ is small. Over short times noise dominates, and that is what will make ordinary calculus need a correction.

The SDE describes one path. Chapter 5 also described the whole distribution, through the diffusion equation, and the same can be done here: the same Taylor expansion of the master equation gives, for the probability density $\rho(x,t)$ of $X_t$,
$$
\frac{\partial \rho}{\partial t} = -\frac{\partial}{\partial x}\big[a\,\rho\big] + \frac12\,\frac{\partial^2}{\partial x^2}\big[b^2 \rho\big],
$$
called the **Fokker–Planck equation**. With constant $a = v$ and $b^2 = 2D$ it is exactly Chapter 5's drift–diffusion equation. So one process now has three descriptions: a random walk, which you simulate; an SDE, which describes one path; and a partial differential equation, which describes the distribution. Chapter 7 uses the third.

### Itô's lemma: changing variables in an SDE

Often the quantity we care about is a function of the one the SDE describes, such as the logarithm of a price, $Y_t = f(X_t)$. Ordinary calculus would give $dY = f'(X)\,dX$. To see what that misses, expand $f$ to second order, the same step that produced the diffusion coefficient in Chapter 5:
$$
dY \approx f'(X)\,dX + \tfrac12 f''(X)\,(dX)^2 .
$$
In ordinary calculus $(dX)^2$ is of order $dt^2$ and is dropped. Here $dX$ contains the kick $b\,dW_t$, of size $\sqrt{dt}$, so $(dX)^2 \approx b^2 (dW_t)^2$ is of order $dt$, the same order as the drift, and cannot be dropped. Moreover $(dW_t)^2$ has mean exactly $dt$, and its fluctuations average out: over $n$ intervals covering a time $t$, the sum of the $(dW)^2$ has mean $t$ and standard deviation $t\sqrt{2/n}$, which vanishes as $n$ grows, like Chapter 3's $1/\sqrt{N}$. So we may replace $(dW_t)^2$ by $dt$, and collecting terms gives **Itô's lemma**:
$$
\boxed{\ dY_t = \Big[f'(X_t)\,a + \tfrac12 f''(X_t)\,b^2\Big]\,dt + f'(X_t)\,b\,dW_t\ }
$$
The only difference from the ordinary chain rule is the term $\tfrac12 f'' b^2$ in the drift. Two checks: if $f$ is a straight line, $f'' = 0$ and the ordinary rule holds; if there is no noise, $b = 0$ and the ordinary rule holds. The correction needs both curvature and noise. Its sign follows the curvature: **a concave function of a noisy quantity drifts down by $\tfrac12 |f''| b^2$ per unit time, and a convex one drifts up**, because the kicks in both directions do not cancel once they pass through a curved function.

Chapter 7 needs one extension. The value of an option depends on both the price and the time, so it is a function $f(X_t, t)$ of two variables. Time carries no noise, so expanding in $t$ adds only the ordinary first-order term $\frac{\partial f}{\partial t}\,dt$, and Itô's lemma becomes
$$
df(X_t, t) = \left[\frac{\partial f}{\partial t} + a\,\frac{\partial f}{\partial x} + \frac12\, b^2\,\frac{\partial^2 f}{\partial x^2}\right] dt + b\,\frac{\partial f}{\partial x}\,dW_t ,
$$
with every derivative evaluated at $(X_t, t)$. Chapter 7 applies it to an option's value, with $X_t = S_t$, $a = \mu S_t$ and $b = \sigma S_t$.

> **Aside: Itô and Stratonovich.** Stratonovich's convention evaluates the coefficients at the midpoint of each interval instead of its start. The ordinary chain rule then holds, and the same process is written with a different drift. If another book's formula differs from this chapter's by $\sigma^2/2$, check its convention.

### Log returns and geometric Brownian motion

For a price, there are two ways to measure the change over an interval $\Delta t$. The **simple return** is the fractional change $R = (S_{t+\Delta t} - S_t)/S_t$; the **log return** is $r = \log S_{t+\Delta t} - \log S_t = \log(1+R)$. They agree for small moves, since $\log(1+R) \approx R$, but not for large ones: a 50% fall has $R = -0.5$ and $r = -0.69$.

The assumption that fractional changes have the same mean and variance at every price level says $dS_t/S_t = \mu\,dt + \sigma\,dW_t$, or
$$
\boxed{\ dS_t = \mu\, S_t\, dt + \sigma\, S_t\, dW_t\ }
$$
This is **geometric Brownian motion**, the SDE with $a = \mu S$ and $b = \sigma S$. Both coefficients are proportional to the price, so the noise is multiplicative instead of additive; that is what "geometric" means. With $\sigma = 0$ it becomes $dS/dt = \mu S$, whose solution is $S_0 e^{\mu t}$.

Now apply Itô's lemma with $f(S) = \log S$, for which $f' = 1/S$ and $f'' = -1/S^2$:
$$
d(\log S_t) = \Big[\tfrac{1}{S}\,\mu S - \tfrac12\,\tfrac{1}{S^2}\,\sigma^2 S^2\Big]dt + \tfrac1S\,\sigma S\,dW_t
= \left(\mu - \tfrac12\sigma^2\right)dt + \sigma\,dW_t .
$$
The factors of $S$ cancel, leaving constant coefficients. **The log price performs Chapter 5's drift–diffusion walk, with $v = \mu - \sigma^2/2$ and $D = \sigma^2/2$**, and the $-\sigma^2/2$ is Itô's correction for the concave logarithm: a rise by a fraction $R$ adds less than $R$ to $\log S$, and an equal fall subtracts more. Integrating a walk with constant coefficients is immediate:
$$
\log S_t - \log S_0 \sim \mathcal{N}\!\left(\left(\mu - \tfrac12\sigma^2\right)t,\; \sigma^2 t\right).
$$

### The lognormal solution

Exponentiating gives the solution of the GBM equation:
$$
\boxed{\ S_t = S_0 \exp\!\left[\left(\mu - \tfrac{1}{2}\sigma^2\right) t \;+\; \sigma\, W_t\right]\ }
$$
Because $\log S_t$ is Gaussian, $S_t$ is **lognormally distributed** (density by the change of variables in [Appendix A](./A_notation.md)). Three consequences:

- $\mathrm{Median}(S_t) = S_0\, e^{(\mu - \sigma^2/2)\, t}$: the exponential is increasing, so it maps the median of $\log S_t$ to the median of $S_t$. The *typical* price grows at $\mu - \sigma^2/2$.
- $\mathbb{E}[S_t] = S_0\, e^{\mu t}$, from $\mathbb{E}[e^X] = e^{a + b^2/2}$ for $X \sim \mathcal{N}(a, b^2)$ (Exercise 2): the spread of the log price adds back $\sigma^2 t/2$. The *average* price grows at $\mu$.
- $\mathrm{Var}(S_t) = S_0^2\, e^{2\mu t}\, (e^{\sigma^2 t} - 1)$.

The mean can be checked a second way. By assumption each interval multiplies the expected price by $1 + \mu\,\Delta t$, so $\mathbb{E}[S_t] = S_0(1 + \mu\,\Delta t)^{t/\Delta t} \to S_0 e^{\mu t}$, which agrees with the lognormal only because of the $-\sigma^2/2$. At $t = 0$ the formulas give $S_0$ with zero variance, and at $\sigma = 0$ mean and median both equal $S_0 e^{\mu t}$. Otherwise the mean is above the median, and the gap widens: the fraction of paths ending below the mean is $\mathbb{P}(\sigma W_t < \sigma^2 t/2) = \Phi(\sigma\sqrt{t}/2)$, with $\Phi$ the standard Gaussian CDF, which at $\sigma = 0.20$ is 54% after one year and 69% after 25. **Because the mean grows at $\mu$ and the median at $\mu - \sigma^2/2$, the longer the horizon, the larger the share of outcomes below the mean**, which is held up by a shrinking minority of very good paths. Any formula or code that moves between $S$ and $\log S$ must carry the $-\sigma^2/2$.

### Fitting $\mu$ and $\sigma$ from data

Under GBM, log returns at any spacing $\Delta t$ are independent draws from $\mathcal{N}\big((\mu - \sigma^2/2)\Delta t,\ \sigma^2\Delta t\big)$: the Gaussian model of Chapter 2's Exercise 2, with maximum-likelihood estimates $m$ and $s^2$. Solving for the GBM parameters,
$$
\hat\sigma = \frac{s}{\sqrt{\Delta t}}, \qquad
\hat\mu = \frac{m}{\Delta t} + \frac{\hat\sigma^2}{2}.
$$
For modern daily data $\Delta t = 1/252$ year (about 252 trading days); Worked Example 2 meets a series where the spacing changed over time. This is where the trap usually appears: $m/\Delta t$, the annualized mean log return, estimates $\mu - \sigma^2/2$, not $\mu$.

Since $m$ averages $N$ values of variance $\sigma^2\Delta t$, with $T = N\Delta t$ the span in years,
$$
\mathrm{SE}(\hat\mu) \approx \frac{\sigma}{\sqrt{T}} .
$$
$N$ has cancelled because $Nm = \sum_i r_i = \log S_{\text{end}} - \log S_{\text{start}}$: the intermediate log prices cancel in pairs, so the drift estimate uses only the first and last prices, and sampling more often does not help. The volatility is built from $N$ squared deviations, and for Gaussian data $\hat\sigma$ has relative standard error about $1/\sqrt{2N}$. **The standard error of $\hat\mu$ depends only on the years spanned, while that of $\hat\sigma$ shrinks with the number of observations, so a few years of daily data determine $\sigma$ well and $\mu$ hardly at all.**

## Worked example 1: simulating GBM and checking the lognormal solution

Does a simulator built on the log-price random walk reproduce the lognormal predictions? With $S_0 = 100$, $\mu = 0.10$, $\sigma = 0.20$ and $T = 1$ year in daily steps, the theory gives $\mathbb{E}[S_T] = 100\,e^{0.10} = 110.52$, $\mathrm{Median}(S_T) = 100\,e^{0.08} = 108.33$, and a standard deviation of $0.20$ for $\log S_T$.

```{code-cell} python
import numpy as np

def simulate_gbm(S0, mu, sigma, T, dt, n_paths, rng):
    n_steps = round(T / dt)
    Z = rng.standard_normal((n_paths, n_steps))
    log_increments = (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z
    log_paths = np.cumsum(log_increments, axis=1)
    return S0 * np.exp(np.hstack([np.zeros((n_paths, 1)), log_paths]))

rng = np.random.default_rng(seed=0)
S0, mu, sigma, T = 100.0, 0.10, 0.20, 1.0
paths = simulate_gbm(S0, mu, sigma, T, dt=1/252, n_paths=10_000, rng=rng)
S_T = paths[:, -1]

sem = S_T.std(ddof=1) / np.sqrt(len(S_T))
print(f"mean of S_T   : {S_T.mean():.2f} +/- {sem:.2f}   (theory: {S0 * np.exp(mu * T):.2f})")
print(f"median of S_T : {np.median(S_T):.2f}           (theory: {S0 * np.exp((mu - sigma**2 / 2) * T):.2f})")
print(f"SD of log S_T : {np.log(S_T).std(ddof=1):.4f}         (theory: {sigma * np.sqrt(T):.4f})")

# mean of S_T   : 110.61 +/- 0.22   (theory: 110.52)
# median of S_T : 108.46           (theory: 108.33)
# SD of log S_T : 0.1987         (theory: 0.2000)
```

Stepping the *log* price and exponentiating is exact at any step size, because GBM's log price really is a walk with constant Gaussian steps, and it keeps the price positive; applying Euler–Maruyama to $S$ itself is exact only as $\Delta t \to 0$. All three numbers agree with theory: the mean within half a standard error, the median within its noise (a sample median fluctuates more than a mean), and the spread of $\log S_T$ within its relative standard error of $1/\sqrt{20{,}000} = 0.7\%$. This is **verification**: the code reproduces the model's formulas, which says nothing about whether real prices follow GBM.

A verification check is only worth running if it would catch a mistake. The next cell makes the most common one on purpose, leaving out the $-\sigma^2/2$; it draws $S_T$ from the solution in one step, since the terminal value needs no path:

```{code-cell} python
rng = np.random.default_rng(seed=1)
Z = rng.standard_normal(10_000)
S_T_bug = S0 * np.exp(mu * T + sigma * np.sqrt(T) * Z)      # the -sigma^2/2 left out

sem = S_T_bug.std(ddof=1) / np.sqrt(len(S_T_bug))
print(f"mean of S_T   : {S_T_bug.mean():.2f} +/- {sem:.2f}   (theory: {S0 * np.exp(mu * T):.2f})")

# mean of S_T   : 112.50 +/- 0.23   (theory: 110.52)
```

The mean is now more than eight standard errors too high, near $100\,e^{0.12} = 112.75$: a 2% error that is easy to miss in a plot and obvious against a standard error. The [companion script](./code/06_gbm/simulate_gbm.py) plots paths with the mean and median curves.

## Worked example 2: fitting GBM to a market series

Given a daily price series, what are $\hat\mu$ and $\hat\sigma$, and how well does the data determine each? The first cell fetches the book's data loader. In the browser it returns the dollar price of one euro, daily since 1999 (Federal Reserve data, as in Chapter 5's Worked Example 3). In Colab it downloads a century of daily US stock returns from Kenneth French's data library, which the book may not redistribute.

The fit measures time from the dates instead of assuming 252 returns a year. Until May 1952 the US market also traded on Saturdays, giving 280 to 300 returns a year, so $\Delta t = 1/252$ would stretch the century of stock data to 104 years and understate both $\hat\mu$ and $\hat\sigma$.

```{code-cell} python
# Fetch the book's market-data loader. Two lines of plumbing because the in-browser
# kernel and Colab reach the network differently -- everything after this is identical.
import sys, pathlib, urllib.request

_url = "https://harvard-am215.github.io/textbook/code/common/equity_data.py"
if sys.platform == "emscripten":                 # in-browser (Pyodide) kernel
    from pyodide.http import open_url
    _src = open_url(_url).read()
else:                                            # Colab, or a local Python
    _src = urllib.request.urlopen(_url).read().decode()
pathlib.Path("equity_data.py").write_text(_src)
```

```{code-cell} python
import numpy as np
from equity_data import price_series

prices, source = price_series(quiet=True)
r = np.log(prices).diff().dropna().values
years = (prices.index[-1] - prices.index[0]).days / 365.25
dt = years / len(r)                           # 1/252 today; less before 1952

m, s = r.mean(), r.std(ddof=0)                # the MLE divides by N
sigma_hat = s / np.sqrt(dt)
mu_hat = m / dt + sigma_hat**2 / 2

print(f"source    : {source}")
print(f"span      : {len(r)} daily returns, {years:.1f} years")
print(f"m / dt    : {m / dt:+.4f}   (estimates mu - sigma^2/2)")
print(f"mu_hat    : {mu_hat:+.4f} +/- {sigma_hat / np.sqrt(years):.4f}")
print(f"sigma_hat : {sigma_hat:.4f}")

# source    : USD/EUR exchange rate, 1999-present (FRED, public domain)
# span      : 6920 daily returns, 27.6 years
# m / dt    : -0.0008   (estimates mu - sigma^2/2)
# mu_hat    : +0.0034 +/- 0.0174
# sigma_hat : 0.0912
```

For the exchange rate, $\hat\sigma = 0.091$: the euro's dollar price moves about 9% in a typical year. The drift's standard error is five times its size, so 27 years of daily data cannot say whether the euro tends to rise or fall against the dollar.

In Colab, US stocks through July 2026 give $m/\Delta t = 0.098$, $\hat\mu = 0.113 \pm 0.017$ and $\hat\sigma = 0.175$. Because log returns telescope, $0.098$ is the rate, continuously compounded, at which the market actually grew; $\hat\mu$, larger by $\hat\sigma^2/2 = 0.015$, is the model's growth rate for the *expected* price, an average over histories that might have happened. Reporting $0.098$ as $\hat\mu$ is the trap. And the drift is well determined only because the series is a century long: from five years, its standard error would be $0.175/\sqrt{5} = 0.078$, leaving a drift of $0.113$ only 1.4 standard errors from zero. The [companion script](./code/06_gbm/fit_market.py) prints both fits (`--fx` for the browser's) and a Q–Q plot.

## Worked example 3: is the volatility constant?

GBM assumes the same $\sigma$ in every year. To test it, fit $\sigma$ in each calendar year and compare the scatter with what sampling noise alone would produce. A year of about 252 returns estimates $\sigma$ with standard error $\sigma/\sqrt{2 \times 252} \approx 0.045\,\sigma$, so with constant $\sigma$ only about one year in twenty should fall more than two standard errors from the overall value. The cell does the same for the drift, whose one-year standard error is $\sigma/\sqrt{1} = \sigma$.

```{code-cell} python
import numpy as np
from equity_data import price_series

prices, source = price_series(quiet=True)
r = np.log(prices).diff().dropna()
years = (prices.index[-1] - prices.index[0]).days / 365.25
sigma_all = r.std(ddof=0) / np.sqrt(years / len(r))

by_year = r.groupby(r.index.year)
n = by_year.size()                            # returns in each calendar year: dt = 1/n
full = n >= 200                               # drop the partial first and last years
sigma_year = (by_year.std(ddof=0) * np.sqrt(n))[full]
drift_year = (by_year.mean() * n)[full]

band = 2 * sigma_all / np.sqrt(2 * n[full])   # two standard errors if sigma were constant
outside = int((abs(sigma_year - sigma_all) > band).sum())

print(f"full years          : {len(sigma_year)}")
print(f"yearly sigma_hat    : {sigma_year.min():.3f} ({sigma_year.idxmin()}) to {sigma_year.max():.3f} ({sigma_year.idxmax()})")
print(f"constant-sigma band : {sigma_all:.3f} +/- {band.mean():.3f}")
print(f"years outside band  : {outside}   (constant sigma: about {0.05 * len(sigma_year):.0f})")
print(f"SD of yearly m / dt : {drift_year.std(ddof=1):.3f}   (noise alone: {sigma_all:.3f})")

# full years          : 27
# yearly sigma_hat    : 0.047 (2019) to 0.142 (2008)
# constant-sigma band : 0.091 +/- 0.008
# years outside band  : 20   (constant sigma: about 1)
# SD of yearly m / dt : 0.096   (noise alone: 0.091)
```

Twenty of 27 years lie outside the band, where a constant $\sigma$ would put about one. First check the yardstick: the band uses the Gaussian standard error, and fat tails make $\hat\sigma$ noisier. Allowing for the measured excess kurtosis of $2.5$ widens the band by half, to $\pm 0.012$, and the same 20 years stay outside ([companion script](./code/06_gbm/volatility_by_year.py)). The volatility changes by far more than noise can explain, so we reject constant $\sigma$ for this series. This is **validation**: an assumption compared with observations, and found to fail. The equity series in Colab agrees, with yearly $\hat\sigma$ from $0.050$ (1964) to $0.474$ (1932), and 63 of its 99 full years outside even the widened band.

The drift gives the opposite picture: its yearly estimates scatter by $0.096$, about what noise alone produces. That does not show the drift is constant. It shows a year is too short to tell, since a year measures $\sigma$ to about 5% but the drift only to $\pm\sigma$.

## Intuition

> **Why log returns and not simple returns?** Log returns add over time, so Chapter 5's variance arithmetic applies to them directly. They are symmetric: a 50% gain then a 33.3% loss returns the price to its start, and the log returns are $+0.405$ and $-0.405$. And no Gaussian log return can make $S_t = e^{\log S_t}$ negative.

> **Why does the typical outcome fall below the average one?** Take a gamble that multiplies your wealth by $1.5$ or $0.5$ with equal probability each round. The expected multiplier is exactly $1$, so expected wealth stays at $\$1$. But a win and a loss together leave $0.75$, so median wealth after $n$ rounds is about $0.866^n$, which goes to zero; a few very long winning streaks hold the mean at $\$1$. The mean log return per round, $\tfrac12\log 0.75 = -0.144$, is near $-\sigma^2/2 = -0.125$ with $\sigma = 0.5$, but not equal, because 50% moves are not small. In finance this gap is called **volatility drag**.

> **What does GBM claim, and what does it not?** It gets two structural facts right: prices stay positive, and their random changes scale with their level. It gets two quantitative facts wrong: daily returns have fatter tails than a Gaussian, and volatility changes over time. So "prices follow GBM" is too strong; GBM is the simplest model with positivity and proportional noise, and its errors are in large moves and in periods of changing volatility. Chapter 7's Black–Scholes formula inherits both.

## Connections

- **Builds on:** Chapter 5 for the biased random walk and the second-order Taylor step; Chapter 2 for Gaussian maximum likelihood and standard errors; Chapter 3 for Monte Carlo error bars; Appendix A for the central limit theorem and the lognormal density.
- **Used in:** Chapter 7, which prices options over GBM paths with the same $-\sigma^2/2$; Chapter 8, on the fat tails GBM misses; Appendix B, where the noisy $\hat\mu$ makes portfolio optimization fragile.
- **Further directions:** Itô's lemma in general; stochastic volatility models such as Heston's, in which $\sigma$ follows its own random process; GARCH models, in which volatility depends on recent returns; jump-diffusion and Lévy models for the tails.

## Exercises

1. **Conceptual.** Two reports describe the same stock over the same ten years. One gives a mean daily *log* return of 0.05%; the other an "average annual return" of 14.6%, from averaging daily *simple* returns and multiplying by 252. Daily log returns have standard deviation 1.26%. Show that both reports can be right, and say which GBM quantity each estimates. Which tells you how much the price actually grew?

2. **Derivation.** Starting from $\log S_t \sim \mathcal{N}(\mu_{\log}, \sigma_{\log}^2)$, show that $\mathbb{E}[S_t] = e^{\mu_{\log} + \sigma_{\log}^2/2}$. (Complete the square in the exponent.)

3. **Computational.** Simulate $10{,}000$ GBM paths with $S_0 = 100$, $\mu = 0.05$, $\sigma = 0.30$, $T = 1$ year, $\Delta t = 1/252$. Compare the empirical mean, median, and variance of $S_T$ with the lognormal predictions. Which agrees least precisely, and why?

4. **Computational.** Fit GBM by maximum likelihood to a daily price series: the one `price_series()` returns, or a stock of your choice downloaded in Colab. Report $\hat\mu$ with its standard error, and $\hat\sigma$. Then make a Q–Q plot of the standardized log returns against the standard Gaussian. Where does it deviate, and are the tails heavier or lighter?

5. **Computational.** Using the same series, fit $\hat\mu$ and $\hat\sigma$ on rolling 5-year windows and plot both. Compare the range of each with its one-window standard error. Which estimate can you trust from a single window, and trust for what?

6. **Modeling judgment.** A trader claims her strategy "averages 30% annual return at 25% volatility, beating the S&P." Take the S&P's drift to be exactly 10%. Using $\mathrm{SE}(\hat\mu) \approx \sigma/\sqrt{T}$, how many years of results would you need before the claim is two standard errors from a null of "identical to the S&P"?

:::{admonition} Solutions
:class: dropdown

**1.** The log return annualizes to $0.0005 \times 252 = 0.126$, estimating $\mu - \sigma^2/2$. With $\hat\sigma = 0.0126\sqrt{252} = 0.200$, $\hat\mu = 0.126 + 0.020 = 0.146$. A daily simple return has mean $e^{\mu\Delta t} - 1 \approx \mu\,\Delta t$, so the 14.6% estimates $\mu$, and the reports agree. The first describes what happened: log returns telescope, so the price grew exactly $e^{1.26} = 3.53$ times. The factor $e^{1.46} = 4.31$ is the *expected* growth over histories that did not all happen. Before comparing two "average returns", ask which average each is; here they differ by $\sigma^2/2$.

**2.** With $X = \log S_t$, $\mathbb{E}[e^X] = \int e^x \frac{1}{\sqrt{2\pi}\sigma_{\log}} e^{-(x - \mu_{\log})^2/(2\sigma_{\log}^2)}\, dx$. Completing the square, $x - \frac{(x - \mu_{\log})^2}{2\sigma_{\log}^2} = -\frac{(x - \mu_{\log} - \sigma_{\log}^2)^2}{2\sigma_{\log}^2} + \mu_{\log} + \frac{\sigma_{\log}^2}{2}$. What remains is a Gaussian density integrating to 1, so $\mathbb{E}[e^X] = e^{\mu_{\log} + \sigma_{\log}^2/2}$, which for GBM is $S_0 e^{\mu t}$.

**3.** The [solution script](./code/06_gbm/terminal_distribution_check.py) measures each statistic's Monte Carlo standard error by repeating the experiment 200 times. Mean $105.29$ vs. $105.13$ ($+0.16\%$, standard error $0.34\%$); median $100.22$ vs. $100.50$ ($-0.28\%$, $0.40\%$); variance $1026$ vs. $1041$ ($-1.39\%$, $1.95\%$). All agree within one standard error. The variance is least precise because a few very large $S_T$ in the right tail dominate it. Judge agreement against a standard error, not by matching decimals.

**4.** The [solution script](./code/06_gbm/fit_market.py) gives $\hat\mu = 0.113 \pm 0.017$, $\hat\sigma = 0.175$ for US stocks and $0.003 \pm 0.017$, $0.091$ for USD/EUR (`--fx`). Both Q–Q plots bend away from the diagonal at *both* ends: large moves in either direction exceed the Gaussian quantiles, so the tails are heavier. The excess kurtosis (0 for a Gaussian) is $17.0$ and $2.5$. Chapter 8 takes this up.

**5.** The [solution script](./code/06_gbm/window_stability.py) plots each estimate with the $\pm 2$ standard-error band a constant parameter would allow. For US stocks, $\hat\mu$ ranges from $-0.18$ to $+0.35$ with one-window standard error $0.175/\sqrt 5 = 0.078$, so a single window's drift is uncertain by $\pm 0.16$, more than the drift itself; $\hat\sigma$ ranges from $0.082$ to $0.384$ against a standard error of about $0.01$, even allowing for fat tails. A window measures its own volatility precisely, but volatility moves between windows, so it forecasts the next window poorly; a window's drift is not a reliable measurement at all.

**6.** Separating 30% from 10% at two standard errors needs $2 \times 0.25/\sqrt T < 0.20$, so $T > 6.25$ years. Three years give a standard error of $0.144$, leaving the 20-point gap at 1.4 standard errors, which luck produces often. Treating the S&P's 10% as exact makes even 6.25 years optimistic.

:::

## Further reading

- Hull, *Options, Futures, and Other Derivatives*, Ch. 14 — the standard textbook treatment
  of GBM in finance, including a derivation of Itô's lemma, which this chapter only
  sketches. Use the **US 11th edition**, ISBN 9780136939979 · [HOLLIS](https://hollis.harvard.edu/discovery/search?query=any,contains,Options%20Futures%20and%20Other%20Derivatives%20Hull&tab=LibraryCatalog&search_scope=MyInstitution&vid=01HVD_INST:HVD2&offset=0).
  (The Global edition renumbers the end-of-chapter problems.)
- Wilmott, *Paul Wilmott Introduces Quantitative Finance* (2nd ed., 2007), Ch. 4 —
  friendlier and more intuition-led on the SDE step. ISBN 9780470319581 ·
  [HOLLIS](https://hollis.harvard.edu/discovery/search?query=any,contains,Paul%20Wilmott%20Introduces%20Quantitative%20Finance&tab=LibraryCatalog&search_scope=MyInstitution&vid=01HVD_INST:HVD2&offset=0) ·
  [free sample chapter](https://media.wiley.com/product_data/excerpt/85/04703195/0470319585.pdf).
- For a careful but readable walk through Itô calculus: Mikosch, *Elementary Stochastic
  Calculus, with Finance in View* (1998), Ch. 2. ISBN 9789810235437. Harvard does not appear
  to hold this one — check [HOLLIS](https://hollis.harvard.edu/discovery/search?query=any,contains,Elementary%20Stochastic%20Calculus%20with%20Finance%20in%20View%20Mikosch&tab=LibraryCatalog&search_scope=MyInstitution&vid=01HVD_INST:HVD2&offset=0)
  before relying on it.
