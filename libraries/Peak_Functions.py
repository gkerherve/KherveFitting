
import numpy as np
import lmfit
from lmfit.models import VoigtModel

import numpy as np


class PeakFunctions:

    @staticmethod
    def gaussian_other(x, E, F, m):
        return np.exp(-4 * np.log(2) * ((x - E) / F)**2) * (1 - m / 100)

    @staticmethod
    def gaussian(x, E, F, m):
        return np.exp(-4 * np.log(2) * (1 - m / 100) * ((x - E) / F)**2)

    @staticmethod
    def lorentzian(x, E, F, m):
        return 1 / (1 + 4 * m / 100 * ((x - E) / F)**2)

    @staticmethod
    def gauss_lorentz_OLD(x, center, fwhm, fraction, amplitude):
        return amplitude * (
            PeakFunctions.gaussian(x, center, fwhm, fraction*1) *
            PeakFunctions.lorentzian(x, center, fwhm, fraction*1))

    @staticmethod
    def S_gauss_lorentz(x, center, fwhm, fraction, amplitude):
        return amplitude * (
            (1-fraction/100) * PeakFunctions.gaussian(x, center, fwhm, 0) +
            fraction/100 * PeakFunctions.lorentzian(x, center, fwhm, 100))

    @staticmethod
    def gauss_lorentz(x, center , fwhm, fraction, amplitude):
        peak = amplitude * (
                PeakFunctions.gaussian(x, center, fwhm, fraction * 1) *
                PeakFunctions.lorentzian(x, center, fwhm, fraction * 1))
        return peak


    @staticmethod
    def gauss_lorentz_Area(x, center, area, fwhm, fraction):
        sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
        height = area / (sigma * np.sqrt(2 * np.pi))
        return height * (
                PeakFunctions.gaussian(x, center, fwhm, fraction * 1) *
                PeakFunctions.lorentzian(x, center, fwhm, fraction * 1))

    @staticmethod
    def S_gauss_lorentz_Area(x, center, area, fwhm, fraction):
        sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
        height = area / (sigma * np.sqrt(2 * np.pi))
        return height * (
                (1 - fraction / 100) * PeakFunctions.gaussian(x, center, fwhm, 0) +
                fraction / 100 * PeakFunctions.lorentzian(x, center, fwhm, 100))


    # SHALL NOT BE USEFUL
    @staticmethod
    def tail(x, center, tail_mix, tail_exp, fwhm):

        # Avoid division by zero and negative exponents
        safe_exp = np.maximum(tail_exp, 1e-5)
        safe_mix = np.maximum(tail_mix, 1e-5)
        return np.where(x > center,     np.exp(-safe_exp * np.abs(x - center) ** safe_mix), 0)

    @staticmethod
    def filter_func(x, center):
        return np.where(x <= center, 1, 0)



    @staticmethod
    def S_gauss_lorentz_tail(x, center, fwhm, fraction, amplitude, tail_mix, tail_exp):
        peak = amplitude * (
                (1 - fraction/100) * PeakFunctions.gaussian(x, center, fwhm, 0) +
                fraction/100 * PeakFunctions.lorentzian(x, center, fwhm, 100))
        tail = PeakFunctions.tail(x, center, tail_mix, tail_exp)
        return peak * (1 - tail_mix) + amplitude * tail

    @staticmethod
    def pseudo_voigt(x, center, amplitude, sigma, fraction):
        """
        Custom Pseudo-Voigt function.

        Parameters:
        x : array
            The x values
        center : float
            The peak center
        amplitude : float
            The peak height
        sigma : float
            The peak width (standard deviation for Gaussian component)
        fraction : float
            The fraction of Lorentzian component (0 to 1)

        Returns:
        array : The y values of the Pseudo-Voigt function
        """
        sigma2 = sigma ** 2
        gamma = sigma * np.sqrt(2 * np.log(2))

        gaussian = (1 - fraction/100) * np.exp(-((x - center) ** 2) / (2 * sigma2))
        lorentzian = fraction/100 * (gamma ** 2 / ((x - center) ** 2 + gamma ** 2))

        return amplitude * (gaussian + lorentzian)

    @staticmethod
    def pseudo_voigt_fwhm(x, center, amplitude, fwhm, fraction):
        """
        Custom Pseudo-Voigt function using FWHM.

        Parameters:
        x : array
            The x values
        center : float
            The peak center
        amplitude : float
            The peak height
        fwhm : float
            Full Width at Half Maximum of the peak
        fraction : float
            The fraction of Lorentzian component (0 to 1)

        Returns:
        array : The y values of the Pseudo-Voigt function
        """
        sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))  # Convert FWHM to sigma for Gaussian
        gamma = fwhm / 2  # Convert FWHM to gamma for Lorentzian

        z = (x - center) / sigma

        gaussian = (1 - fraction/100) * np.exp(-z ** 2 / 2) / (sigma * np.sqrt(2 * np.pi))
        lorentzian = fraction/100 * gamma / (np.pi * (gamma ** 2 + (x - center) ** 2))

        return amplitude * (gaussian + lorentzian) * sigma * np.sqrt(2 * np.pi)

    @staticmethod
    def voigt_fwhm(sigma, gamma):
        """
        Approximate the FWHM of a Voigt profile.

        This uses an approximation that is accurate to within a few percent.

        Parameters:
        sigma : float
            The sigma parameter of the Gaussian component
        gamma : float
            The gamma parameter of the Lorentzian component

        Returns:
        float : The approximate FWHM of the Voigt profile
        """
        fg = 2 * sigma * np.sqrt(2 * np.log(2))
        fl = 2 * gamma
        return 0.5346 * fl + np.sqrt(0.2166 * fl ** 2 + fg ** 2)


    @staticmethod
    def pseudo_voigt_amplitude_to_height(amplitude, sigma, fraction):
        """
        Convert amplitude to height for a Pseudo-Voigt profile.

        Parameters:
        amplitude : float
            The amplitude of the Pseudo-Voigt profile
        sigma : float
            The sigma parameter of the profile (related to FWHM)
        fraction : float
            The fraction of Lorentzian component (0 to 1)

        Returns:
        float : The height of the Pseudo-Voigt profile
        """
        sqrt2pi = np.sqrt(2 * np.pi)
        sqrt2ln2 = np.sqrt(2 * np.log(2))

        gaussian_height = amplitude / (sigma * sqrt2pi)
        lorentzian_height = 2 * amplitude / (np.pi * sigma * 2 * sqrt2ln2)

        height = (1 - fraction/100) * gaussian_height + fraction/100 * lorentzian_height

        return height

    @staticmethod
    def pseudo_voigt_height_to_amplitude(height, sigma, fraction):
        """
        Convert height to amplitude for a Pseudo-Voigt profile.

        Parameters:
        height : float
            The height of the Pseudo-Voigt profile
        sigma : float
            The sigma parameter of the profile (related to FWHM)
        fraction : float
            The fraction of Lorentzian component (0 to 1)

        Returns:
        float : The amplitude of the Pseudo-Voigt profile
        """
        sqrt2pi = np.sqrt(2 * np.pi)
        sqrt2ln2 = np.sqrt(2 * np.log(2))

        gaussian_amplitude = height * sigma * sqrt2pi
        lorentzian_amplitude = height * np.pi * sigma * 2 * sqrt2ln2 / 2

        amplitude = (1 - fraction/100) * gaussian_amplitude + fraction/100 * lorentzian_amplitude

        return amplitude

    def voigt_area(height, sigma, gamma):
        from scipy.special import wofz

        # Convert sigma to Gaussian FWHM
        fwhm_g = 2 * sigma * np.sqrt(2 * np.log(2))

        # Convert gamma to Lorentzian FWHM
        fwhm_l = 2 * gamma

        # Calculate the Voigt function at its center
        voigt_max = np.real(wofz((0 + 1j * gamma) / (sigma * np.sqrt(2))))

        # Calculate the area
        area = height * (np.pi * fwhm_l / 2 + np.sqrt(np.pi * np.log(2)) * fwhm_g) / voigt_max

        return area

    @staticmethod
    def get_voigt_height(amplitude, sigma, gamma):
        """
        Calculate the height of a Voigt profile directly using the lmfit model.
        """
        model = lmfit.models.VoigtModel()
        params = model.make_params(amplitude=amplitude, center=0, sigma=sigma, gamma=gamma)
        return model.eval(params, x=0)

    @staticmethod
    def voigt_height_to_area(height, sigma, gamma):
        voigt = VoigtModel()
        x = np.linspace(-10 * sigma, 10 * sigma, 1000)
        params = voigt.make_params(center=0, sigma=sigma, gamma=gamma, amplitude=1)
        y = voigt.eval(params, x=x)
        max_y = np.max(y)
        amplitude = height / max_y
        return amplitude  # For distribution models, amplitude is equivalent to area


    @staticmethod
    def get_pseudo_voigt_height(amplitude, sigma, fraction):
        """
        Calculate the height of a Pseudo-Voigt profile directly using the lmfit model.
        """
        model = lmfit.models.PseudoVoigtModel()
        params = model.make_params(amplitude=amplitude, center=0, sigma=sigma, fraction=fraction/100)
        return model.eval(params, x=0)


import numpy as np
from scipy.signal import savgol_filter


class BackgroundCalculations:
    @staticmethod
    def calculate_linear_background(x, y, start_offset, end_offset):
        """
        Calculate a linear background between the start and end points of the data.

        Args:
            x (array): X-axis values
            y (array): Y-axis values
            start_offset (float): Offset to add to the start point
            end_offset (float): Offset to add to the end point

        Returns:
            array: Linear background
        """
        y_start = y[0] + start_offset
        y_end = y[-1] + end_offset
        return np.linspace(y_start, y_end, len(y))

    @staticmethod
    def calculate_smart_background(x, y, offset_h, offset_l):
        """
        Calculate a 'smart' background by choosing between Shirley and linear backgrounds.

        Args:
            x (array): X-axis values
            y (array): Y-axis values
            offset_h (float): High offset
            offset_l (float): Low offset

        Returns:
            array: Smart background
        """
        shirley_bg = BackgroundCalculations.calculate_shirley_background(x, y, offset_h, offset_l)
        linear_bg = BackgroundCalculations.calculate_linear_background(x, y, offset_h, offset_l)

        # Choose background type based on first and last y-values
        background = shirley_bg if y[0] > y[-1] else linear_bg

        # Ensure background does not exceed raw data
        return np.minimum(background, y)

    @staticmethod
    def calculate_smart2_background(x, y, threshold=0.01):
        """
        Calculate an improved 'smart' background using derivative analysis.

        Args:
            x (array): X-axis values
            y (array): Y-axis values
            threshold (float): Threshold for determining flat regions

        Returns:
            array: Smart2 background
        """
        dy = np.gradient(y, x)
        threshold = 0.001 * (max(y) - min(y))

        # Smooth the derivative
        dy_smooth = savgol_filter(dy, window_length=30, polyorder=3)

        background = np.zeros_like(y)
        flat_mask = np.abs(dy_smooth) < threshold

        # Set background to raw data in flat regions
        background[flat_mask] = y[flat_mask]

        # For non-flat regions, decide between linear and Shirley
        for i in range(1, len(y)):
            if not flat_mask[i]:
                if y[i] < y[i - 1]:  # Data going down
                    background[i] = background[i - 1] + (y[i] - y[i - 1])
                else:  # Data going up
                    A = np.trapz(y[:i + 1] - background[:i + 1], x[:i + 1])
                    B = np.trapz(y[i:] - background[i:], x[i:])
                    background[i] = y[-1] + (y[0] - y[-1]) * B / (A + B)

        return background

    @staticmethod
    def calculate_adaptive_smart_background(x, y, x_range, previous_background, offset_h, offset_l):
        """
        Calculate an adaptive smart background for a selected range.

        Args:
            x (array): X-axis values
            y (array): Y-axis values
            x_range (tuple): Range of x values to calculate background for
            previous_background (array): Previous background calculation
            offset_h (float): High offset
            offset_l (float): Low offset

        Returns:
            array: Adaptive smart background
        """
        previous_background = np.array(previous_background)
        mask = (x >= x_range[0]) & (x <= x_range[1])
        new_background = np.copy(previous_background)
        x_selected, y_selected = x[mask], y[mask]

        # Determine background type for selected range
        if y_selected[0] > y_selected[-1]:
            new_background[mask] = BackgroundCalculations.calculate_shirley_background(x_selected, y_selected, offset_h,
                                                                                       offset_l)
        else:
            new_background[mask] = BackgroundCalculations.calculate_linear_background(x_selected, y_selected, offset_h,
                                                                                      offset_l)

        return new_background

    @staticmethod
    def calculate_shirley_background(x, y, start_offset, end_offset, max_iter=100, tol=1e-6, padding_factor=0.01):
        """
        Calculate the Shirley background.

        Args:
            x (array): X-axis values
            y (array): Y-axis values
            start_offset (float): Offset to add to the start point
            end_offset (float): Offset to add to the end point
            max_iter (int): Maximum number of iterations
            tol (float): Tolerance for convergence
            padding_factor (float): Factor for padding the data

        Returns:
            array: Shirley background
        """
        x, y = np.asarray(x), np.asarray(y)

        # Add padding to the data
        x_min, x_max = x[0], x[-1]
        padding_width = padding_factor * (x_max - x_min)
        x_padded = np.concatenate([[x_min - padding_width], x, [x_max + padding_width]])
        y_padded = np.concatenate([[y[0] + start_offset], y, [y[-1] + end_offset]])

        background = np.zeros_like(y_padded)
        I0, Iend = y_padded[0], y_padded[-1]

        # Iterative calculation of Shirley background
        for _ in range(max_iter):
            prev_background = background.copy()
            for i in range(1, len(y_padded) - 1):
                A1 = np.trapz(y_padded[:i] - background[:i], x_padded[:i])
                A2 = np.trapz(y_padded[i:] - background[i:], x_padded[i:])
                background[i] = Iend + (I0 - Iend) * A2 / (A1 + A2)
            if np.all(np.abs(background - prev_background) < tol):
                break

        return background[1:-1]  # Remove padding before returning



# ------------------------------ HISTORY CHECK -----------------------------------------------
# --------------------------------------------------------------------------------------------
