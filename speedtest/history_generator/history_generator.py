#!/usr/bin/env python

import time
import datetime
import random

import fred

OBJECT_NAMES = {
    'contact': 'CID:%s',
    'domain': '%s.cz',
    'nsset': 'NSSID:%s',
    'keyset': 'KEYID:%s',
}

class EppCommanderError(Exception):
    pass

class PropabilityList(list):
    ''' Inherited from python list, where items of this list must be couples (item, propability_weight),
        added methond get_random_by_weight, which returns random first value of couple, with propability
        computed as weight_of_item/sum_of_weights_of_all_items.
    '''
    def get_random_key_by_weight(self):
        weight_sum = sum(item[1] for item in self)
        roll = random.randint(1, weight_sum)
        sub_sum = 0
        for i in range(len(self)):
            sub_sum += self[i][1]
            if roll <= sub_sum:
                return self[i][0]
        raise EppCommanderError('Wrong roll index or wrong content of PropabilityList') # should not ever occure

def time_measure(func, *args, **kwd):
    t1 = time.time()
    result = func(*args, **kwd)
    t_diff = time.time() - t1
    return result, t_diff

class EppCommander(object):

    def __init__(self):
        self.epp = fred.Client()
        self.epp.load_config()
        self.epp.login(username=self.epp._epp.get_config_value('connect', 'username'),
                       password=self.epp._epp.get_config_value('connect', 'password'))

        #cache for all objects,:
        self.cache = {
            'contact': [],
            'domain': [],
            'nsset': [],
            'keyset': [],
        }
        self.cache_valid = {
            'contact': False,
            'domain': False,
            'nsset': False,
            'keyset': False,
        }

    def get_date_str(self):
        dat = datetime.datetime.now()
        dat_list = [dat.year, dat.month, dat.day, dat.hour, dat.minute, dat.second, dat.microsecond]
        long_str = '-'.join([str(item) for item in dat_list])
        short_str = '-'.join([str(item) for item in dat_list[:3]])
        return long_str, short_str

    def get_random_handle(self, object_type):
        ''' Returns random handle, object_type is string (e.g. 'contatct'). '''
        if self.cache_valid[object_type]:
            return random.choice(self.cache[object_type])
        else:
            prep_objects = getattr(self.epp, 'prep_%ss' % object_type)
            prep_objects()
            objects = []

            result = self.epp.get_results()
            while result['data']:
                objects.extend(result['data']['list'])
                result = self.epp.get_results()

            self.cache[object_type] = objects
            self.cache_valid[object_type] = True
            if not object:
                raise EppCommanderError('There is no %s in database yet' % object_type)
            return random.choice(objects)


    def create(self, object_type, handle=None):
        long_name, short_name = self.get_date_str()
        if not handle:
            handle = OBJECT_NAMES[object_type] % long_name

        if object_type == 'contact':
            result, t_diff = time_measure(self.epp.create_contact,
                handle,
                'Maniasek D%s' % short_name,
                'Maniasek@%s.cz' % short_name,
                'Zabredlicka', 'Bohumin', '22334', 'CZ'
            )
        elif object_type == 'nsset':
            result, t_diff = time_measure(self.epp.create_nsset, handle, ({'name':'ns1.test.cz'}, {'name':'ns2.test.cz'}), self.get_random_handle('contact'))
        elif object_type == 'keyset':
            result, t_diff = time_measure(self.epp.create_keyset,
                'KEYID:%s' % long_name,
                [{'flags': '257', 'alg': '7', 'protocol': '3', 'pub_key': 'AwEAAddt2AkLfYGKgiEZB5SmIF8EvrjxNMH6HtxWEA4RJ9Ao6LCWheg8'}],
                [], [self.get_random_handle('contact')]
            )
        elif object_type == 'domain':
            registrant_handle = self.get_random_handle('contact')
            result, t_diff = time_measure(self.epp.create_domain, '%s.cz' % long_name, registrant_handle)
        else:
            raise EppCommanderError('There is no such object type "%s"' % object_type)

        if result['code'] >= 2000:
            raise EppCommanderError('Action create %s %s ended with errorcode %s, full result:\n %s' % (object_type, handle, result['code'], str(result)))

        self.cache_valid[object_type] = False
        #print 'Created %s %s' % (object_type, handle)

        return t_diff

    def update(self, object_type, handle=None):
        long_name, short_name = self.get_date_str()
        if not handle:
            handle = self.get_random_handle(object_type)

        if object_type == 'contact':
            result, t_diff = time_measure(self.epp.update_contact, handle, chg={'email': '%s@updatle.cz' % short_name})
        elif object_type == 'nsset':
            result, t_diff = time_measure(self.epp.update_nsset, handle, auth_info='passwd' + long_name)
        elif object_type == 'keyset':
            result, t_diff = time_measure(self.epp.update_keyset, handle, auth_info='passwd' + long_name)
        elif object_type == 'domain':
            result, t_diff = time_measure(self.epp.update_domain, handle, chg={'auth_info': 'passwd' + long_name})
        else:
            raise EppCommanderError('There is no such object type "%s"' % object_type)

        if result['code'] >= 2000:
            print result
            raise EppCommanderError('Action update %s %s ended with errorcode %s, full result:\n %s' % (object_type, handle, result['code'], str(result)))

        #print 'Updated %s %s' % (object_type, handle)
        return t_diff


    def delete(self, object_type, handle=None):
        if not handle:
            handle = self.get_random_handle(object_type)
        delete = getattr(self.epp, 'delete_%s' % object_type)
        result, t_diff = time_measure(delete, handle)

        if result['code'] >= 2000:
            raise EppCommanderError('Action delete %s %s ended with errorcode %s, full result:\n %s' % (object_type, handle, result['code'], str(result)))

        print 'Deleted %s %s' % (object_type, handle)
        return t_diff


class EppGeneral(object):
    def __init__(self, command_table=None):
        self.eppc = EppCommander()
        if not command_table:
            # key is propability of command (command propability is actually key/sum_of_all_keys)
            self.command_table = PropabilityList([
                (self.eppc.create, 20),
                (self.eppc.update, 70),
                (self.eppc.delete, 10),
            ])
            self.object_table = PropabilityList([
                ('contact', 30),
                ('nsset', 20),
                ('keyset', 10),
                ('domain', 40),
            ])
        else:
            self.command_table = command_table

        self.sum_command_table = None
        self.sum_object_table = None

    def make_commands(self, count=100):
        for i in xrange(count):

            command = self.command_table.get_random_key_by_weight()
            object = self.object_table.get_random_key_by_weight()
            print 'Command %d: %s %s' % (i, command.im_func.func_name, object)
            try:
                command(object)
            except EppCommanderError:
                print 'Not accomplished due to EppError'






if __name__ == "__main__":
    general = EppGeneral()
    #general.make_commands(100)

    #commander = EppCommander()
    #commander.create('nsset')
    #commander.create('keyset')
    #commander.create('domain')
    #
    #commander.update('contact')
    #commander.update('nsset')
    #commander.update('keyset')
    #commander.update('domain')
    #
    #commander.delete('contact')
    #commander.delete('nsset')
    #commander.delete('keyset')
    #commander.delete('domain')

    #print commander.get_random_handle('contact')
    #print commander.get_random_handle('contact')

    print "Exiting..."
