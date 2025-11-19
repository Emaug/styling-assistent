from Stylist.get_info_db import load_by_attribute

def load_answer_from_lines(lines, count=1):
    all_results = []
    for line in lines:
        line = line.strip()
        if not line or "no" in line:
            continue
        words = line.replace(":", "").replace(",", "").split()
        args = [None if w == "None" else w for w in words]

        for i in range(min(4, len(args)), 0, -1):
            subset_args = args[:i]
            results = load_by_attribute(*subset_args, count=count)
            if results:
                all_results.append(results)
                break
    return all_results
