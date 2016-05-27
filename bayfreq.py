import numpy as np
from scipy import stats


import matplotlib.pyplot as plt


np.random.seed(1)

F_true = 1000
N = 50
F = stats.poisson(F_true).rvs(N)
e = np.sqrt(F)


fig, ax = plt.subplots()
ax.errorbar(F, np.arange(N), xerr=e, fmt='ok', ecolor='gray', alpha=0.5)
ax.vlines([F_true], 0, N, linewidth=5, alpha=0.2)
ax.set_xlabel("Flux")
ax.set_ylabel("measurement number")

'''These measurements each have a different error eiei which is estimated from Poisson statistics using the standard
square-root rule. In this toy example we already know the true flux FtrueFtrue, but the question is this: given our
measurements and errors, what is our best estimate of the true flux?'''

# plt.show()

'''Frequentist
the frequency of any given value indicates the probability of measuring that value. For frequentists probabilities are
fundamentally related to frequencies of events. This means, for example, that in a strict frequentist view, it is
meaningless to talk about the probability of the true flux of the star: the true flux is (by definition) a single fixed
value, and to talk about a frequency distribution for a fixed value is nonsense.'''

'''Classical frequentist maximum likelihood approach:
 Given a single observation Di=(Fi,ei) - compute the probdistribution of the measurement given the true flux Ftrue
 given our assumption of Gaussian errors'''
w = 1. / e ** 2
print("""
      F_true = {0}
      F_est  = {1:.0f} +/- {2:.0f} (based on {3} measurements)
      """.format(F_true, (w * F).sum() / w.sum(), w.sum() ** -0.5, N))

'''Bayesian
probabilities are fundamentally related to our own knowledge about an event. This means, for example, that in a
Bayesian view, we can meaningfully talk about the probability that the true flux of a star lies in a given range.
That probability codifies our knowledge of the value based on prior information and/or available data.
Bayes Theorem    P(Ftrue | D) = [P(D | Ftrue) * P(Ftrue)] / P(D)'''

source activate my_root

import emcee


# Model prior: what we knew about the model prior to the application of the data D
def log_prior(theta):
    return 1  # flat prior


# Likelihood
def log_likelihood(theta, F, e):
    return -0.5 * np.sum(np.log(2 * np.pi * e ** 2) + (F - theta[0]) ** 2 / e ** 2)


# Posterior: the probability of the model parameters given the data: the result to be computed
def log_posterior(theta, F, e):
    return log_prior(theta) + log_likelihood(theta, F, e)


ndim = 1  # number of parameters in the model
nwalkers = 50  # number of MCMC walkers
nburn = 1000  # "burn-in" period to let chains stabilize
nsteps = 2000  # number of MCMC steps to take

# we'll start at random locations between 0 and 2000
starting_guesses = 2000 * np.random.rand(nwalkers, ndim)


sampler = emcee.EnsembleSampler(nwalkers, ndim, log_posterior, args=[F, e])
sampler.run_mcmc(starting_guesses, nsteps)

sample = sampler.chain  # shape = (nwalkers, nsteps, ndim)
sample = sampler.chain[:, nburn:, :].ravel()  # discard burn-in points

# plot a histogram of the sample
plt.hist(sample, bins=50, histtype="stepfilled", alpha=0.3, normed=True)

# plot a best-fit Gaussian
F_fit = np.linspace(975, 1025)
pdf = stats.norm(np.mean(sample), np.std(sample)).pdf(F_fit)

plt.plot(F_fit, pdf, '-k')
plt.xlabel("F"); plt.ylabel("P(F)")