import yaml
import csv
import sys
import re
import argparse
from decimal import Decimal
from math import ceil, floor, lcm
from collections import namedtuple

#Task = namedtuple('Task', ['id', 'period', 'phase', 'relative_deadline', 'cost_range', 'jitter_range'])
Job  = namedtuple('Job', ['id', 'tid', 'arrival_range', 'absolute_deadline', 'cost_range'])
verbose = False

def load_yaml(filepath):
    import re
    with open(filepath, 'r') as file:
        content = file.read()
        # Remove the custom tag !Task
        content = re.sub(r'!Task\s+', '', content)
        return yaml.safe_load(content)

def write_taskset_csv(tasks, filename='taskset.csv'):
    headers = [
        'Job Name', 'Period', 'Release Phase', 'Deadline',
        'BCET', 'WCET', 'Release Jitter'
    ]

    with open(filename, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(headers)

        for task in tasks:
            job_name = f"T({task['TaskID']} 1)"
            period = task['Period']
            phase = task['Phase']
            deadline = task['Deadline']
            bcet = f"{Decimal(task['BCET']):.9g}"
            wcet = f"{Decimal(task['WCET']):.5E}"
            jitter = f"[0 to {task['Jitter']}]"

            writer.writerow([job_name, period, phase, deadline, bcet, wcet, jitter])

def write_taskchains_yaml(chains, intype, outtype, filename='taskchains.yaml'):
    taskchains = []
    for chain in chains:
        taskchains.append({
            'Tasks': chain,
            'Buffers': ['BB'] * (len(chain) - 1),
            'InputType': intype,
            'OutputType': outtype
        })

    with open(filename, 'w') as file:
        yaml.dump({'taskchains': taskchains}, file, sort_keys=False)

def hyperperiod(tasks):
    return lcm(*{int(t['Period']) for t in tasks})

def csv_header():
    return "Task ID,Job ID,Arrival min,Arrival max, Cost min, Cost max,Deadline, Priority"
    return "{7:>10s}, {0:>10s}, {1:>20s}, {2:>20s}, {3:>20s}, {4:>20s}, {5:>20s}, {6:>20s}".format(
        "Job ID", "Arrival min", "Arrival max", "Cost min", "Cost max",
        "Deadline", "Priority", "Task ID")

def parse_range(s):
    #m = re.fullmatch('uniform params: \[([0-9.]+) to ([0-9.]+)\]', s)
    if type(s) == int or type(s)== float:
        return (0, s)
    m = re.fullmatch('\[([0-9.]+) to ([0-9.]+)\]', s)
    return (float(m.group(1)), float(m.group(2)))

def generate_jobs(t, hyperperiod):
    assert t['Phase'] == 0 # can't yet handle non-zero phase

    rel = 0.0
    id = 1
    while rel < hyperperiod:
        yield Job(id, t['TaskID'], (rel + parse_range(t['Jitter'])[0], rel + parse_range(t['Jitter'])[1]),
                  rel + t['Deadline'], (t['BCET'],t['WCET']))
        id  += 1
        rel += t['Period']

def format_csv(j, prio_fn):
    return f"{j.tid},{j.id},{j.arrival_range[0]},{j.arrival_range[1]},{j.cost_range[0]},{j.cost_range[1]},{j.absolute_deadline},{prio_fn(j)}"

def assign_edf_priority(job):
    return job.absolute_deadline

def assign_TLFP_priority(tasks):
    return lambda j: next(task['Priority'] for task in tasks if task['TaskID'] == j.tid)

def mk_rate_monotonic(tasks):
    by_period = sorted(tasks, key=lambda t: t.period)
    prios = {}
    for p, t in enumerate(by_period):
        prios[t['TaskID']] = p + 1
    return lambda j: prios[j.tid]

def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert task specification to job sets")

    parser.add_argument('input_files', nargs='*',
        help='the task sets that should contribute to this job set')

    parser.add_argument('--out_path', type=str, dest='output_path', default='./')

    parser.add_argument('--InputType', type=str, dest='InputType', default='event', help='event or sampled input')
    parser.add_argument('--OutputType', type=str, dest='OutputType', default='active', help='active or passive output')

    parser.add_argument('--prio', type=str, dest='prio_policy', default='EDF', help='EDF, TLFP')

    return parser.parse_args()

def main():
    opts = parse_args()
    output_path = opts.output_path
    input_file = sys.argv[1]
    data = load_yaml(input_file)

    chains = data.get('Chains', [])
    tasks = data.get('Tasks', [])
    task_ids = list({task['TaskID'] for task in tasks})
    for chain in chains:
        for i in range(len(chain)):
            chain[i] = task_ids.index(chain[i])

    for task in tasks:
        task['TaskID'] = task_ids.index(task['TaskID'])

    write_taskset_csv(tasks)
    write_taskchains_yaml(chains, opts.InputType, opts.OutputType, output_path+'taskchains.yaml')

    Hg = hyperperiod(tasks)
    Hc_max = []
    Tmax = []
    wcl = []

    for tasks_in_chain in chains:
        chain_tasks = [
            next((task for task in tasks if task['TaskID'] == task_id), None)
            for task_id in tasks_in_chain
        ]
        # Remove None values in case a TaskID wasn't found
        chain_tasks = [task for task in chain_tasks if task is not None]

        # Hyperperiod
        Hc_max.append(hyperperiod(chain_tasks))

        # Tmax (max period in the chain)
        Tmax.append(max(task['Period'] for task in chain_tasks))

        # WCL (twice the sum of periods)
        wcl.append(2 * sum(task['Period'] for task in chain_tasks))
    if(verbose):
        print("Hc_max:", Hc_max)
        print("Tmax:", Tmax)
        print("WCL:", wcl)


    OW = max(Hg, max(list({2*Hc_max[i]+Tmax[i]+wcl[i] for i in range(len(chains))})))

    if (opts.prio_policy == "EDF"):
        prio = assign_edf_priority
    elif (opts.prio_policy == "TLFP"):
        prio = assign_TLFP_priority(tasks)

    with open(output_path+'jobset.csv','w',newline='') as csvfile:
        writer=csv.writer(csvfile)
        writer.writerow(csv_header().split(','))
        
        jobs = []
        for t in tasks:
            for j in generate_jobs(t, OW):
                jobs.append(j)
        for j in jobs:
            writer.writerow(format_csv(j, prio).split(','))

if __name__ == '__main__':
    main()
