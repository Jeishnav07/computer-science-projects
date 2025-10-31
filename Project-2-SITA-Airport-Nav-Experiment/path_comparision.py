#Compare two paths and produce a boolean change flag plus length ratio
def path_changed_and_length_ratio(true_path, reported_path):
    #true_path and reported_path are lists (may be empty)
    if not true_path:
        #if true path absent, we consider reported as 'changed' if reported exists
        changed = bool(reported_path)
        ratio = float('nan') if not reported_path else float(len(reported_path))
        return changed, ratio
    if not reported_path:
        #reported missing but true exists
        return True, float('inf')
    #compare sequences: if any cell differs -> changed
    changed = (true_path != reported_path)
    #length ratio
    ratio = len(reported_path) / len(true_path) if len(true_path) > 0 else float('nan')
    return changed, ratio

#Aggregate trial-level results into summary stats (change rate and mean length ratio)
def aggregate_trials(trial_results):
    #trial_results: list of (changed_bool, length_ratio_float)
    if not trial_results:
        return {"change_rate": 0.0, "mean_length_ratio": float('nan')}
    n = len(trial_results)
    changes = [1 if t[0] else 0 for t in trial_results]
    ratios = [t[1] for t in trial_results if t[1] == t[1]]  #filter out NaNs
    change_rate = sum(changes) / n
    mean_ratio = sum(ratios) / len(ratios) if ratios else float('nan')
    return {"change_rate": change_rate, "mean_length_ratio": mean_ratio}
