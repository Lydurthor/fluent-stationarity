import sys

from src import stationarity as st


def main():
    # Run: python main.py your-rfile.out
    # Everything else is automated. If it fails, try changing k and frac in stationarity.py or contact lydur.lydsson@gmail.com
    if len(sys.argv) < 2:
        print("usage: python main.py <rfile.out>")
        return

    step, value, t = st.load(sys.argv[1])

    bin_width, diff_thresh = st.derive_stationary_params(value, t)

    t0 = st.find_stationary_cutoff(value, t, bin_width, diff_thresh)
    t1 = t.max()

    mean, std, n = st.final_stats(value, t, t0, t1)

    peak_times, peak_vals, avg_period, avg_frequency, avg_amplitude = st.peak_trough_analysis(value, t, t0)


    print(f"t0={t0:.5f}, mean={mean:.5f}, std={std:.5f}")
    print(f"period={avg_period:.5f}, freq={avg_frequency:.5f}, amp = {avg_amplitude:.5f}")

    st.plot_signal_with_cutoff(value, t, t0, sys.argv[1])

if __name__ == "__main__":
    main()
