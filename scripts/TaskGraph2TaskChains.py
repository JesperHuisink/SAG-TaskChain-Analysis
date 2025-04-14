import csv
import argparse

class TaskChain():
    def __init__(self):
        pass

class Task():
    def __init__(self,ID,successors=[],predecessors=[],output_buffer_type='b'):
        self.ID = ID
        self.successors = successors
        self.predecessors = predecessors
        self.output_buffer_type = output_buffer_type

def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert task graph to task chains")

    parser.add_argument('input_file',
        help='the task graph that is used for analysis')

    return parser.parse_args()

def parse_file(file):
    tasks=[]
    f = open(file, 'r')
    data = csv.DictReader(f,skipinitialspace=True)
    for row in data:
        producer = row['from']
        consumer = row['to']
        buffer_type = row['buffer_type']
        tasks[producer] = Task(producer,consumer,output_buffer_type=buffer_type)


def main():
    opts = parse_args()
    tasks = []
    tasks = parse_file(opts.input_files).tasks
    with csv.open() as f:
        pass
if __name__ == '__main__':
    main()