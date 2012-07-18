import time

from history_generator import EppCommander, EppCommanderError

class EppSpeedTester(object):
    def __init__(self):
        self.eppc = EppCommander()
        self.times = {}
        for command in ['create', 'update', 'delete']:
            self.times[command] = {}
            for obj in ['contact', 'nsset', 'keyset', 'domain']:
                self.times[command][obj] = [] # list of times of how command for that object took long.

    def print_result(self):
        for command in ['create', 'update', 'delete']:
            for obj in ['contact', 'nsset', 'keyset', 'domain']:
                time_list = self.times[command][obj]
                if time_list:
                    avg_time = sum(time_list) / len(time_list)
                    print '%-30s %.3f' % ('Avg. time for %s %s:' % (command, obj), avg_time)

    def print_result_detailed(self):
        for command in ['create', 'update', 'delete']:
            for obj in ['contact', 'nsset', 'keyset', 'domain']:
                time_list = self.times[command][obj]
                if time_list:
                    avg_time = sum(time_list) / len(time_list)
                    min_time = min(time_list)
                    max_time = max(time_list)
                    print '%-30s %.3f   <%s, %s>' % ('Avg. time for %s %s:' % (command, obj), avg_time, min_time, max_time)
                    #print '\n'.join(['%10.3f' % item for item in time_list])

    def measure_command(self, command, obj, count, *args, **kwd):
        command_func = getattr(self.eppc, command)
        for i in xrange(count):
            try:
                t_diff = command_func(obj, *args, **kwd)
                self.times[command][obj].append(t_diff)
            except EppCommanderError:
                print 'Command not accomplished due to EppError (ignoring)'


if __name__ == '__main__':
    est = EppSpeedTester()
    #est.measure_command('update', 'contact', 10, 'CID:2009-3-6-11-49-56-376201')
    est.measure_command('create', 'contact', 100)

    #est.print_result()
    est.print_result_detailed()
