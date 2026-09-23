# Fluent Stationarity Analysis

Small Python tool for analysing transient `Cl` and `Cd` report-file data from ANSYS Fluent.

The problem it fixes is that when you are simulating geometry that does not have a stable solution, fx. due to vortex shedding the solution oscillates, this tool makes it so the results only come from the part of the solution where the oscillation is stable. 

The goal is to avoid averaging over the initial transient part of a CFD run. The script finds a stationary region and calculates the mean, standard deviation and oscillation characteristics of the signal.

## Input format

The parser expects a Fluent report file with exactly three header lines, followed by data in the form:

```text
<step> <value> <flow-time>
```

For example:

```text
1569 0.04151902868739497 0.39225
1570 0.04148731222183104 0.39250
```

The three header lines are skipped by count, so the input file should follow the same structure as the included Fluent report files.

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py cl-rfile.out
```

or:

```bash
python main.py cd-rfile.out
```

Running the script also opens a matplotlib plot of the signal and selected stationary region. The program waits until the plot window is closed before finishing.

## How it works

The beginning of a transient CFD run may still be settling, so averaging the whole simulation can bias the result.

The signal is split into smaller time windows and their mean values are compared. The stationary region begins when those window means stop showing significant drift.

The averaging region is chosen from the behaviour of the CFD signal itself, not from how closely the result matches expected or experimental values.

## Output

The program reports:

- mean
- standard deviation
- period
- frequency
- oscillation amplitude, defined as half of the peak-to-peak amplitude
- stationary cutoff time

`cutoff_sensitivity` can be used to check how much the final mean changes when the averaging start time is moved.

`z_score` can be used to compare two CFD runs, for example in timestep or mesh sensitivity studies.

## Tuning

The main stationarity settings are `k` and `frac` in `derive_stationary_params`.

`k` controls how wide the averaging bins are relative to the oscillation period.

`frac` controls how much drift between bins is allowed before the signal is considered stationary.

If the program gives:

```text
ValueError: no stationary region found
```

the stationarity condition is probably too strict. Increasing `frac` slightly makes the condition less strict.

## Validation

The code was checked against a separate reference analysis of the same CFD data.

| Quantity | Python | Reference |
|---|---:|---:|
| Cl | 1.17621 | 1.17784 |
| Cd | 0.023353 | 0.02329 |
| Cl period | 0.00837 s | 0.00836 s |
| Cd period | 0.00835 s | 0.00836 s |

The purpose of the tool is to make transient CFD averaging more systematic and reproducible.

Attached are two files from a prior run that have been tested.