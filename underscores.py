from scipy.stats import poisson
import numpy as np

def under05(homeS, awayS):
    result = 100 * ((poisson.pmf(0, homeS) * poisson.pmf(0, awayS)))
    return round(float(np.array2string(result)), 2)

def under15(homeS, awayS):
    result = 100 * ((poisson.pmf(0, homeS) * poisson.pmf(0, awayS)) +
                    (poisson.pmf(1, homeS) * poisson.pmf(0, awayS)) +
                    (poisson.pmf(0, homeS) * poisson.pmf(1, awayS)))
    return round(float(np.array2string(result)), 2)

def under25(homeS, awayS):
    result = 100 * ((poisson.pmf(0, homeS) * poisson.pmf(0, awayS)) +
                    (poisson.pmf(1, homeS) * poisson.pmf(0, awayS)) +
                    (poisson.pmf(0, homeS) * poisson.pmf(1, awayS)) +
                    (poisson.pmf(1, homeS) * poisson.pmf(1, awayS)) +
                    (poisson.pmf(2, homeS) * poisson.pmf(0, awayS)) +
                    (poisson.pmf(0, homeS) * poisson.pmf(2, awayS)))
    return round(float(np.array2string(result)), 2)

def btts(homeS, awayS):
    result = 100 * ((poisson.pmf(0, homeS) * poisson.pmf(0, awayS)) +
                    (poisson.pmf(1, homeS) * poisson.pmf(0, awayS)) +
                    (poisson.pmf(0, homeS) * poisson.pmf(1, awayS)))
    return round(float(np.array2string(result)), 2)

def bttsno(homeS, awayS):
    result = 100 * ((poisson.pmf(0, homeS) * poisson.pmf(0, awayS)) +
                    (poisson.pmf(1, homeS) * poisson.pmf(0, awayS)) +
                    (poisson.pmf(0, homeS) * poisson.pmf(1, awayS)))
    return round(float(np.array2string(result)), 2)

if __name__ == "__main__":
    under05()
    under15()
    under25()
    btts()
    bttsno()