
import numpy as np
def gauss_lorentz(x, center , fwhm , fraction, amplitude):                   # x, E, F, m
    return amplitude * (
            gaussian(x, center, fwhm, fraction*100) * lorentzian(x, center, fwhm, fraction*100))

def S_gauss_lorentz(x, center , fwhm , fraction, amplitude):                   # x, E, F, m
    return amplitude * (
        (1-fraction)*gaussian(x, center, fwhm, 0) + fraction * lorentzian(x, center, fwhm, 100))

def gaussian(x, E, F, m):
    return np.exp(-4 * np.log(2) * (1 - m / 100) * ((x - E) / F)**2)

def lorentzian(x, E, F, m):             # E= position, F width, m : percent G like 40 / 100
    return 1 / (1 + 4 * m / 100 * ((x - E) / F)**2)