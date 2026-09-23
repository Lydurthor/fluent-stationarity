# Stationarity analysis for Fluent cl/cd report-file data.

import numpy as np
from scipy.signal import find_peaks
import matplotlib.pyplot as plt


def load(filename):
    step = []
    value = []
    t = []

    with open(filename, "r") as skra:
        for i in range (3):
          skra.readline()

        while True:
            lina = skra.readline()
            if lina == "":
                break

            hlutar = lina.split()
            step.append(int(hlutar[0]))
            value.append(float(hlutar[1]))
            t.append(float(hlutar[2]))

    step = np.array(step)
    value = np.array(value)
    t = np.array(t)

    return step, value, t




def window_mean(sig, t, t0, t1):
    mask = (t >= t0) & (t <= t1)
    value_window = sig[mask]

    mean = np.mean(value_window)
    std = np.std(value_window, ddof=1)
    n = len(value_window)

    return mean, std, n


def cutoff_sensitivity(sig, t, cutoffs):
    pairs = []
    means = []

    for cutoff in cutoffs:
        mean, x1, x2 = window_mean(sig, t, cutoff, t.max())
        pairs.append((cutoff, mean))
        means.append(mean)

    slope = np.polyfit(cutoffs, means, 1)[0]

    return pairs, slope


def peak_trough_analysis(sig, t, cutoff, min_prom_frac=0.15):
    mask = (t >= cutoff)
    sig = sig[mask]
    t = t[mask]

    prominence = min_prom_frac*(sig.max()-sig.min())
    peaks, properties_peaks = find_peaks(sig, prominence=prominence)
    troughs, properties_throughs = find_peaks((-sig), prominence=prominence)

    peak_times = t[peaks]
    peak_vals = sig[peaks]

    trough_times = t[troughs]
    trough_vals = sig[troughs]

    avg_period = float(np.mean(np.diff(peak_times)))
    avg_frequency = float(1/avg_period)
    avg_amplitude = float((np.mean(peak_vals)-np.mean(trough_vals))/2)

    return peak_times, peak_vals, avg_period, avg_frequency, avg_amplitude


def subwindow_means(sig, t, bin_width):
    bin_edges = np.arange(t.min(),t.max(), bin_width)
    bin_means = []

    for n in range (len(bin_edges)-1):
        t1, t2 = bin_edges[n], bin_edges[n+1]
        mask = (t >= t1) & (t < t2)
        mean = np.mean(sig[mask])
        bin_means.append(mean)

    bin_means =  np.array(bin_means)

    return bin_edges, bin_means


def final_stats(sig, t, t0, t1):
    mean, std, n = window_mean(sig, t, t0, t1)
    return mean, std, n


def z_score(mean1, std1, n_cycles1, mean2, std2, n_cycles2):
    SE1 = std1/np.sqrt(n_cycles1)
    SE2 = std2/np.sqrt(n_cycles2)

    SE = np.sqrt(SE1**2+SE2**2)

    Z = abs(mean1 - mean2)/SE

    return Z


def find_stationary_cutoff(sig, t, bin_width, diff_thresh):
    bin_edges, bin_means = subwindow_means(sig, t, bin_width)
    bin_diff = np.diff(bin_means)
    mask = (abs(bin_diff) <= diff_thresh)

    if np.any(mask):
        i = np.flatnonzero(mask)[0]

        while (np.all(mask[i:])==False):
            i = i + 1

        if i >= len(mask):
            raise ValueError("no stationary region found, try a larger threshold or bin width") 
        
        t0 = float(bin_edges[i])

        return t0

    else:
        raise ValueError("no stationary region found, try a larger threshold or bin width")


def derive_stationary_params(sig, t, k=4, frac=0.005):
    peak_times, peak_vals, avg_period, avg_frequency, avg_amplitude = peak_trough_analysis(sig, t, t.max()*0.7)
    # 0.7 kemur þannig að bara er tekið tillit til síðasta 30% af runninu.
    bin_width = float(avg_period * k)
    diff_thresh = float((sig.max()-sig.min())*frac)

    return bin_width, diff_thresh

def plot_signal_with_cutoff(sig, t, t0, label):
    plt.plot(t,sig)
    plt.axvline(x=t0)
    plt.xlabel("Time [s]")
    plt.ylabel("Value")
    plt.title(label)
    plt.show()
