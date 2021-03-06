#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
# Copyright (C) 2014  Jamie Duncan (jamie.e.duncan@gmail.com)

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# File Name : test.py
# Creation Date : 07-02-2014
# Created By : Jamie Duncan
# Purpose : SOSCleaner unittests

from ipaddr import IPv4Network, IPv4Address, IPv6Network, IPv6Address
import shutil
import os
from soscleaner import SOSCleaner
import unittest
import sys
sys.path.append('soscleaner/')


class SOSCleanerTests(unittest.TestCase):
    def _setUpHostname(self, t='fqdn', remove=False):
        hostname_f = os.path.join(self.testdir, 'hostname')
        if remove:
            os.remove(hostname_f)
            return True
        fh = open(hostname_f, 'w')
        if t == 'non-fqdn':
            fh.write('myhost\n')
        else:
            fh.write('myhost.myserver.com\n')
        fh.close()

    def _setUpHostnamePath(self, t='fqdn', remove=False):
        hostname_f = os.path.join(self.testdir, 'hostname2')
        if remove:
            os.remove(hostname_f)
            return True
        fh = open(hostname_f, 'w')
        if t == 'non-fqdn':
            fh.write('myhost2\n')
        else:
            fh.write('myhost2.myserver2.com\n')
        fh.close()

    def setUp(self):
        self.testdir = 'testdata/sosreport_dir'
        self.cleaner = SOSCleaner(quiet=True)
        self.cleaner.origin_path, self.cleaner.dir_path, self.cleaner.session, self.cleaner.logfile, self.cleaner.uuid = self.cleaner._prep_environment()
        self.cleaner._start_logging(self.cleaner.logfile)
        self._setUpHostname()

    def _artifact_cleanup(self, directory):
        # clean up the /tmp directory between tests, when artifacts are created
        for f in os.listdir(directory):
            a = os.path.join(directory, f)
            if 'soscleaner' in f:
                if os.path.isdir(a):
                    shutil.rmtree(a)
                else:
                    os.remove(a)

    def tearDown(self):
        self._artifact_cleanup('/tmp')

    def test0_prep_environment(self):
        # _prep_environment() should create 4 values
        # * self.origin_path - path the sosreport is extracted to
        # * self.dir_path - path cleaned report is written to
        # * self.session - soscleaner-$timestamp - used for naming files/reports/etc.
        # * self.logfile - location of logfile

        self.assertTrue('soscleaner-origin' in self.cleaner.origin_path)
        self.assertTrue('soscleaner' in self.cleaner.dir_path)
        self.assertTrue('soscleaner' in self.cleaner.session)
        self.assertTrue('log' in self.cleaner.logfile)

    def test1_get_hostname_fqdn(self):
        # _get_hostname should return the hostname and domainname from the sosreport. testing with an fqdn
        self.cleaner.dir_path = 'testdata/sosreport_dir'
        self._setUpHostname(t='fqdn')
        host, domain = self.cleaner._get_hostname()
        self.assertTrue(host == 'myhost')
        self.assertTrue(domain == 'myserver.com')

    def test2_get_hostname_nonfqdn(self):
        # testing with a non-fqdn
        self.cleaner.dir_path = 'testdata/sosreport_dir'
        self._setUpHostname(t='non-fqdn')
        host, domain = self.cleaner._get_hostname()
        self.assertTrue(host == 'myhost')
        self.assertTrue(domain is None)

    def test3_get_hostname_nohostnamefile(self):
        # testing with no hostname file
        self.cleaner.dir_path = 'testdata/sosreport_dir'
        self._setUpHostname(remove=True)
        host, domain = self.cleaner._get_hostname()
        self.assertTrue(host is None)
        self.assertTrue(domain is None)

    def test4_get_hostname_path_fqdn(self):
        # _get_hostname should return the hostname and domainname from the sosreport. testing with an fqdn
        self.cleaner.dir_path = 'testdata/sosreport_dir'
        self._setUpHostnamePath(t='fqdn')
        host, domain = self.cleaner._get_hostname('hostname2')
        self.assertTrue(host == 'myhost2')
        self.assertTrue(domain == 'myserver2.com')

    def test5_get_hostname_path_nonfqdn(self):
        # testing with a non-fqdn
        self.cleaner.dir_path = 'testdata/sosreport_dir'
        self._setUpHostnamePath(t='non-fqdn')
        host, domain = self.cleaner._get_hostname('hostname2')
        self.assertTrue(host == 'myhost2')
        self.assertTrue(domain is None)

    def test6_get_hostname_path_nohostnamefile(self):
        # testing with no hostname file
        self.cleaner.dir_path = 'testdata/sosreport_dir'
        self._setUpHostnamePath(remove=True)
        host, domain = self.cleaner._get_hostname('hostname2')
        self.assertTrue(host is None)
        self.assertTrue(domain is None)

    def test8_skip_files(self):
        d = 'testdata/sosreport_dir'
        files = ['test.bin', 'test.txt']
        skip_list = self.cleaner._skip_file(d, files)
        self.assertTrue('test.bin' in skip_list)
        self.assertTrue('test.txt' not in skip_list)

    def test9_extract_sosreport_dir(self):
        d = self.cleaner._extract_sosreport(self.testdir)
        self.assertTrue(d == self.testdir)

    def test10_extract_sosreport_gz(self):
        d = self.cleaner._extract_sosreport('testdata/sosreport1.tar.gz')
        check_d = '/tmp/soscleaner-%s/soscleaner-origin-%s/sosreport_dir' % (self.cleaner.uuid, self.cleaner.uuid)
        self.assertTrue(d == check_d)

    def test11_extract_sosreport_bz(self):
        d = self.cleaner._extract_sosreport('testdata/sosreport1.tar.gz')
        check_d = '/tmp/soscleaner-%s/soscleaner-origin-%s/sosreport_dir' % (self.cleaner.uuid, self.cleaner.uuid)
        self.assertTrue(d == check_d)

    def test12_extract_sosreport_xz(self):
        d = self.cleaner._extract_sosreport('testdata/sosreport1.tar.xz')
        check_d = '/tmp/soscleaner-%s/soscleaner-origin-%s/sosreport_dir' % (self.cleaner.uuid, self.cleaner.uuid)
        self.assertTrue(d == check_d)

    def test13_clean_line(self):
        hostname = 'myhost.myservers.com'
        ip = '192.168.1.10'
        line = "foo bar %s some words %s more words" % (hostname, ip)
        self.cleaner.hostname = hostname
        self.cleaner.domainname = 'example.com'
        self.cleaner._domains2db()
        new_line = 'foo bar %s some words %s more words' % (
            self.cleaner._hn2db(hostname), self.cleaner._ip4_2_db(ip))
        self.assertTrue(self.cleaner._clean_line(line, 'foo_file') == new_line)

    def test14_make_dest_env(self):
        self.cleaner.report = self.testdir
        self.cleaner._make_dest_env()
        self.assertTrue(os.path.isdir(self.cleaner.dir_path))

    def test15_create_archive(self):
        origin_test = '/tmp/origin-testdir'
        dir_test = '/tmp/path-testdir'
        for d in origin_test, dir_test:
            if not os.path.exists(d):
                shutil.copytree(self.testdir, d)
        self.cleaner.origin_path = origin_test
        self.cleaner.dir_path = dir_test
        self.cleaner._create_archive()
        self.assertTrue(os.path.isfile(self.cleaner.archive_path))
        self.assertFalse(os.path.exists(origin_test))
        self.assertFalse(os.path.exists(dir_test))

    def test16_domains2db_fqdn(self):
        self.cleaner.domainname = 'myserver.com'
        self.cleaner.domains.extend(['foo.com', 'bar.com'])
        self.cleaner._domains2db()
        self.assertTrue(self.cleaner.domainname in list(self.cleaner.dn_db.keys()))
        self.assertTrue('foo.com' in list(self.cleaner.dn_db.keys()))
        self.assertTrue('bar.com' in list(self.cleaner.dn_db.keys()))

    def test17_file_list(self):
        x = self.cleaner._file_list('testdata/sosreport_dir')
        self.assertTrue('testdata/sosreport_dir/var/log/messages' in x)
        self.assertTrue('testdata/sosreport_dir/hostname' in x)

    def test18_create_hn_report(self):
        test_hn = 'myhost.myserver.com'
        self.cleaner.domainname = 'myserver.com'
        self.cleaner.process_hostnames = True
        test_o_hn = self.cleaner._hn2db(test_hn)
        self.cleaner._create_hn_report()
        fh = open(self.cleaner.hn_report, 'r')
        x = fh.readlines()
        self.assertTrue(test_hn in x[1])
        self.assertTrue(test_o_hn in x[1])

    def test19_create_hn_report_nohn(self):
        self.cleaner.process_hostnames = False
        self.cleaner._create_hn_report()
        fh = open(self.cleaner.hn_report, 'r')
        lines = fh.readlines()
        self.assertTrue(lines[1] == 'None,None\n')

    def test20_create_dn_report(self):
        self.cleaner.domainname = 'myserver.com'
        self.cleaner.domains.append('myserver.com')
        self.cleaner._domains2db()
        self.cleaner._create_dn_report()
        fh = open(self.cleaner.dn_report, 'r')
        x = fh.readlines()
        self.assertTrue(self.cleaner.domainname in x[1])

    def test21_create_dn_report_none(self):
        self.cleaner._create_dn_report()
        fh = open(self.cleaner.dn_report, 'r')
        x = fh.readlines()
        self.assertTrue(x[1] == 'None,None\n')

    def test22_clean_file(self):
        test_file = '/tmp/clean_file_test'
        shutil.copyfile('testdata/sosreport_dir/var/log/messages', test_file)
        self.cleaner.process_hostnames = True
        self.cleaner.domains.extend(['myserver.com', 'foo.com'])
        self.cleaner.domainname = 'myserver.com'
        self.cleaner.hostname = 'myhost'
        self.cleaner._domains2db()
        self.cleaner._clean_file(test_file)
        fh = open(test_file, 'r')
        data = ', '.join(fh.readlines())
        fh.close()
        self.assertTrue(self.cleaner._hn2db(self.cleaner.hostname) in data)
        self.assertTrue(self.cleaner._hn2db('foohost.foo.com') in data)
        os.remove(test_file)  # clean up

    def test23_sub_hostname_hyphens(self):
        self.cleaner.domains.append('myserver.com')
        self.cleaner.domainname = 'myserver.com'
        self.cleaner.hostname = 'myhost'
        self.cleaner._domains2db()
        line = 'this is myhost.myserver.com and this is my-host.myserver.com'
        new_line = self.cleaner._sub_hostname(line)
        self.assertTrue('my' not in new_line)

    def test24_extra_files(self):
        files = ['testdata/extrafile1',
                 'testdata/extrafile2', 'testdata/extrafile3']
        self.cleaner._clean_files_only(files)
        self.assertTrue(os.path.isdir(self.cleaner.dir_path))
        self.assertTrue(os.path.exists(os.path.join(
            self.cleaner.dir_path, 'extrafile3')))

    def test25_create_archive_nososreport(self):
        files = ['testdata/extrafile1',
                 'testdata/extrafile2', 'testdata/extrafile3']
        self.cleaner._clean_files_only(files)
        self.assertTrue(os.path.exists(os.path.join(
            self.cleaner.dir_path, 'extrafile3')))

    def test26_extra_files_nonexistent(self):
        files = ['testdata/extrafile1', 'testdata/extrafile2',
                 'testdata/extrafile3', 'testdata/bogusfile']
        self.cleaner._clean_files_only(files)
        self.assertTrue(os.path.exists(os.path.join(
            self.cleaner.dir_path, 'extrafile3')))
        self.assertFalse(os.path.exists(
            os.path.join(self.cleaner.dir_path, 'bogusfile')))

    def test27_clean_files_only_originexists(self):
        os.makedirs(self.cleaner.origin_path)
        files = ['testdata/extrafile1', 'testdata/extrafile2',
                 'testdata/extrafile3', 'testdata/bogusfile']
        self.cleaner._clean_files_only(files)
        self.assertTrue(os.path.exists(self.cleaner.origin_path))

    def test28_add_keywords_badfile(self):
        self.cleaner.keywords_file = ['testdata/keyword_bad.txt']
        self.cleaner._keywords2db()
        self.assertTrue(self.cleaner.kw_count == 0)

    def test29_add_keywords_file(self):
        self.cleaner.keywords_file = [
            'testdata/keyword1.txt', 'testdata/keyword2.txt']
        self.cleaner._keywords2db()
        self.assertTrue(self.cleaner.kw_count == 8)
        self.assertTrue(
            all(['foo' in list(self.cleaner.kw_db.keys()), 'some' in list(self.cleaner.kw_db.keys())]))

    def test30_sub_keywords(self):
        self.cleaner.keywords_file = ['testdata/keyword1.txt']
        self.cleaner._keywords2db()
        test_line = 'this is a sample foo bar. this should be different bar foo.'
        new_line = self.cleaner._sub_keywords(test_line)
        self.assertTrue(all(['keyword0' in new_line, 'keyword1' in new_line]))

    def test31_create_ip_report(self):
        self.cleaner._ip4_2_db('192.168.122.100')
        self.cleaner._create_ip_report()
        fh = open(self.cleaner.ip_report, 'r')
        x = fh.readlines()
        self.assertTrue('192.168.122.100' in x[1])

    def test32_sub_hostname_front_of_line(self):
        self.cleaner.domains.append('myserver.com')
        self.cleaner.domainname = 'myserver.com'
        self.cleaner.hostname = 'myhost'
        self.cleaner._domains2db()
        line = 'myhost.myserver.com and this is my-host.myserver.com'
        new_line = self.cleaner._sub_hostname(line)
        self.assertTrue('my' not in new_line)

    def test33_routes_file(self):
        self.cleaner.dir_path = 'testdata/sosreport_dir'
        self.cleaner._process_route_file()
        self.assertTrue(self.cleaner.net_db[0][0].compressed == '10.0.0.0/8')

    def test34_routes_file_absent(self):
        self.cleaner.dir_path = 'testdata/'
        self.cleaner._process_route_file()

    def test35_existing_network(self):
        self.cleaner.dir_path = 'testdata/sosreport_dir'
        self.cleaner._ip4_add_network('10.0.0.0/8')
        self.assertTrue(self.cleaner._ip4_network_in_db(
            IPv4Network('10.0.0.0/8')) is True)

    def test36_add_loopback(self):
        self.cleaner._add_loopback_network()
        self.assertTrue(
            self.cleaner.net_metadata['127.0.0.0']['host_count'] == 0)
        self.assertTrue(self.cleaner._ip4_network_in_db(
            IPv4Network('127.0.0.0/8')) is True)

    def test37_dup_networks(self):
        self.cleaner._ip4_add_network('10.0.0.0/8')
        self.cleaner._ip4_add_network('10.0.0.0/8')
        self.assertTrue(self.cleaner._ip4_network_in_db(
            IPv4Network('10.0.0.0/8')) is True)

    def test38_find_existing_network(self):
        self.cleaner._ip4_add_network('10.0.0.0/8')
        data = self.cleaner._ip4_find_network('10.0.0.1')
        self.assertTrue(data == IPv4Address('129.0.0.0'))

    def test39_add_users_from_command_line(self):
        self.cleaner._user2db('bob')
        self.assertTrue('bob' in list(self.cleaner.user_db.keys()))

    def test40_process_user_option(self):
        users = ('bob', 'sam', 'george')
        self.cleaner._process_user_option(users)
        self.assertTrue('bob' in list(self.cleaner.user_db.keys()))
        self.assertTrue('sam' in list(self.cleaner.user_db.keys()))
        self.assertTrue('george' in list(self.cleaner.user_db.keys()))

    def test41_process_users_file(self):
        self.cleaner.dir_path = 'testdata'
        self.cleaner.users_file = 'userfile1'
        self.cleaner._process_users_file()
        self.assertTrue('bob' in list(self.cleaner.user_db.keys()))
        self.assertTrue('sam' in list(self.cleaner.user_db.keys()))
        self.assertTrue('george' in list(self.cleaner.user_db.keys()))

    def test42_sub_username(self):
        self.cleaner._user2db('bob')
        test_line = 'this is a sample line with bob the user'
        new_line = self.cleaner._sub_username(test_line)
        self.assertFalse('bob' in new_line)

    def test43_sub_username_multiple_users(self):
        self.cleaner._user2db('bob')
        self.cleaner._user2db('sam')
        test_line = "this is a test line with sam and bob"
        new_line = self.cleaner._sub_username(test_line)
        self.assertFalse('bob' in new_line)
        self.assertFalse('sam' in new_line)

    def test44_sub_username_multiple_occurrences(self):
        self.cleaner._user2db('bob')
        test_line = "this test line has bob and then another bob"
        new_line = self.cleaner._sub_username(test_line)
        self.assertFalse('bob' in new_line)

    def test_45_sub_username_only_whole_word(self):
        self.cleaner._user2db('sam')
        test_line = "this line has both sam and same in it"
        new_line = self.cleaner._sub_username(test_line)
        self.assertFalse(' sam ' in new_line)
        self.assertTrue(' same ' in new_line)

    def test46_confirm_no_user_double_adds(self):
        self.cleaner._user2db('bob')
        self.assertTrue('bob' in list(self.cleaner.user_db.keys()))
        for name, o_name in list(self.cleaner.user_db.items()):
            if name == 'bob':
                test_name = name
        self.cleaner._user2db('bob')
        for name, o_name in list(self.cleaner.user_db.items()):
            if name == 'bob':
                test_name2 = name
        self.assertTrue(test_name == test_name2)

    def test47_domains2db_confirm_addition(self):
        self.cleaner.domains.append('example.com')
        self.cleaner._domains2db()

        self.assertTrue('example.com' in list(self.cleaner.dn_db.keys()))

    def test48_sub_hostname_single_3rd_level(self):
        self.cleaner.domains.append('example.com')
        self.cleaner.hostname = 'foo.example.com'
        self.cleaner.domainname = 'example.com'

        self.cleaner._domains2db()
        test_line = 'A sample line with somehost.example.com in it.'
        new_line = self.cleaner._sub_hostname(test_line)
        self.assertFalse('somehost.example.com' in new_line)

    def test49_hn2db_3rd_level_not_hostname(self):
        self.cleaner.domains.append('example.com')
        self.cleaner.hostname = 'foo.example.com'
        self.cleaner.domainname = 'example.com'

        self.cleaner._domains2db()
        test_hostname = 'somehost.example.com'
        test_domainname = self.cleaner._dn2db(self.cleaner.domainname)

        o_hostname = self.cleaner._hn2db(test_hostname)

        self.assertTrue(test_hostname in list(self.cleaner.hn_db.keys()))
        self.assertTrue(test_domainname in o_hostname)

    def test50_hn2db_2nd_level_domain(self):
        self.cleaner.domains.append('example.com')
        self.cleaner.hostname = 'foo'
        self.cleaner.domainname = 'example.com'

        self.cleaner._domains2db()
        test_hostname = 'example.com'

        o_hostname = self.cleaner._hn2db(test_hostname)
        o_hostname_2 = self.cleaner._dn2db(test_hostname)

        self.assertTrue(o_hostname_2 in o_hostname)

    def test51_hn2db_non_fqdn(self):
        self.cleaner.domains.append('example.com')
        self.cleaner.hostname = 'foo'
        self.cleaner.domainname = 'example.com'

        test_host = self.cleaner._hn2db(self.cleaner.hostname)
        self.assertTrue(self.cleaner.hostname in list(self.cleaner.hn_db.keys()))
        self.assertTrue('obfuscatedhost' in test_host)

    def test52_clean_line_multiple_same_domain(self):
        self.cleaner.hostname = 'foo'
        self.cleaner.domainname = 'example.com'
        self.cleaner._domains2db()

        test_line = 'this is host1.example.com and this is host2.example.com'
        new_line = self.cleaner._clean_line(test_line, 'foo_line')

        self.assertFalse('example.com' in new_line)
        self.assertFalse(self.cleaner._hn2db('host1.example.com')
                         == self.cleaner._hn2db('host2.example.com'))

    def test53_hn2db_high_level_host(self):
        self.cleaner.domains.extend(
            ['example.com', 'crazy.super.level.example.com'])
        self.cleaner.hostname = 'foo'
        self.cleaner.domainname = 'example.com'

        test_line = 'a line with some.crazy.super.level.example.com domain'
        new_line = self.cleaner._hn2db(test_line)
        self.assertFalse('example.com' in new_line)

    def test54_resolv_conf_check(self):
        self.cleaner.hostname = 'foo'
        self.cleaner.domainname = 'example.com'
        self.cleaner._domains2db()
        hline1 = 'search localdomain redhat.com'
        hline2 = 'nameserver 172.16.238.2'

        o_hline1 = self.cleaner._clean_line(hline1, 'foo_file')
        o_hline2 = self.cleaner._clean_line(hline2, 'foo_file')

        self.assertFalse('localdomain' in o_hline1)
        self.assertFalse('redhat.com' in o_hline2)
        self.assertTrue('search' in o_hline1)
        self.assertTrue('nameserver' in o_hline2)
        self.assertFalse('172.16.238.2' in o_hline2)

    def test55_all_caps_hostname(self):
        self.cleaner.hostname = 'foo'
        self.cleaner.domainname = 'example.com'
        self.cleaner._domains2db()
        test_line = "some log file with bob@EXAMPLE.COM in it"
        new_line = self.cleaner._clean_line(test_line, 'foo_file')
        self.assertFalse('EXAMPLE.COM' in new_line)
        self.assertTrue(self.cleaner._dn2db('example.com') in new_line)

    def test56_test_skip_file(self):
        dir_path = 'testdata/'
        fifo_file = 'fifo1'
        test_files = [fifo_file, 'extrafile1', 'extrafile2']
        test_fifo = os.path.join(dir_path, fifo_file)
        os.mkfifo(test_fifo)
        skip_list = self.cleaner._skip_file(dir_path, test_files)
        self.assertTrue(fifo_file in skip_list)
        self.assertFalse('extrafile1' in skip_list)
        self.assertFalse('extrafile2' in skip_list)
        os.remove(test_fifo)

    def test57_missing_users_file(self):
        test_run = self.cleaner._process_users_file()
        self.assertFalse(test_run)

    def test58_mac_report(self):
        mac_addy = '00:0c:29:64:72:3e'
        o_mac = self.cleaner._mac2db(mac_addy)
        self.cleaner._create_mac_report()
        fh = open(self.cleaner.mac_report, 'r')
        data = fh.readlines()
        fh.close()
        report_data = data[1].split(',')
        self.assertTrue(mac_addy == report_data[0])
        self.assertTrue(o_mac in report_data[1])

    def test59_mac_report_empty(self):
        self.cleaner._create_mac_report()
        fh = open(self.cleaner.mac_report, 'r')
        data = fh.readlines()
        fh.close()
        self.assertTrue('None,None' in data[1])

    def test60_kw_report(self):
        self.cleaner.keywords_file = ['testdata/keyword2.txt']
        self.cleaner._keywords2db()
        self.cleaner._create_kw_report()
        fh = open(self.cleaner.kw_report, 'r')
        data = fh.readlines()
        fh.close()
        report_data = data[1].split(',')
        self.assertTrue('keyword' in report_data[1])
        self.assertTrue('some' in report_data[0])
        self.assertTrue(len(data) == 5)

    def test61_kw_report_empty(self):
        self.cleaner._create_kw_report()
        fh = open(self.cleaner.kw_report, 'r')
        data = fh.readlines()
        fh.close()
        self.assertTrue('None,None' in data[1])

    def test62_un_report(self):
        """Edited for #129: obfuscateduserX is now randomized"""
        self.cleaner._user2db('user1')
        self.cleaner._create_un_report()
        fh = open(self.cleaner.un_report, 'r')
        data = fh.readlines()
        fh.close()
        user_data = data[1].split(',')
        self.assertTrue(user_data[0] == 'user1')
        self.assertTrue('obfuscateduser' in user_data[1])

    def test63_sub_mac(self):
        test_line = 'a line with a 00:0c:29:64:72:3e valid mac address'
        o_line = self.cleaner._sub_mac(test_line)
        self.assertFalse('00:0c:29:64:72:3e' in o_line)
        self.assertTrue(self.cleaner._mac2db('00:0c:29:64:72:3e') in o_line)

    def test64_add_subdomain(self):
        self.cleaner.hostname = 'foo'
        self.cleaner.domainname = 'example.com'
        self.cleaner._domains2db()
        test_line = 'a line with a subdomain.example.com domain in it'
        o_line = self.cleaner._sub_hostname(test_line)
        self.assertFalse('example.com' in o_line)

    def test65_test_output_file_mode(self):
        """From issue #90 - artifact modes are 0600"""
        self.cleaner.hostname = 'foo'
        self.cleaner.domainname = 'example.com'
        self.cleaner._domains2db()
        self.cleaner._create_dn_report()
        self.cleaner._create_hn_report()
        self.cleaner._create_ip_report()
        self.cleaner._create_kw_report()
        self.cleaner._create_un_report()
        self.cleaner._create_mac_report()
        self.assertTrue(
            oct(os.stat(self.cleaner.dn_report).st_mode)[3:] == '0600')
        self.assertTrue(
            oct(os.stat(self.cleaner.ip_report).st_mode)[3:] == '0600')
        self.assertTrue(
            oct(os.stat(self.cleaner.hn_report).st_mode)[3:] == '0600')
        self.assertTrue(
            oct(os.stat(self.cleaner.kw_report).st_mode)[3:] == '0600')
        self.assertTrue(
            oct(os.stat(self.cleaner.un_report).st_mode)[3:] == '0600')
        self.assertTrue(
            oct(os.stat(self.cleaner.mac_report).st_mode)[3:] == '0600')

    def test66_add_single_keywords(self):
        """from issue #86 - add keywords from cli parameters"""
        self.cleaner.keywords = ['foo', 'bar', 'hello', 'world']
        self.cleaner._keywords2db()
        self.assertTrue(self.cleaner.kw_count == 4)
        self.assertTrue('foo' in list(self.cleaner.kw_db.keys()))

    def test67_keywords_from_config_file(self):
        """from issue #92 - keywords not read from config file"""
        self.cleaner.config_file = 'testdata/config_file'
        self.cleaner._read_later_config_options()
        self.cleaner._keywords2db()
        self.assertTrue('keywordfromfile1' in list(self.cleaner.kw_db.keys()))
        self.assertTrue('keywordfromfile2' in list(self.cleaner.kw_db.keys()))

    def test68_quiet_mode_from_config(self):
        """from #95 - add quiet mode to config file"""
        self.cleaner.config_file = 'testdata/config_file'
        self.cleaner._read_early_config_options()
        self.assertTrue(self.cleaner.quiet)

    def test69_root_domain_from_config(self):
        self.cleaner.config_file = 'testdata/config_file'
        self.cleaner._read_early_config_options()
        self.assertTrue(self.cleaner.root_domain == 'example.com')

    def test70_log_level_from_config(self):
        self.cleaner.config_file = 'testdata/config_file'
        self.cleaner._read_early_config_options()
        self.assertTrue(self.cleaner.loglevel == 'DEBUG')

    def test71_quiet_mode_bad_conf_file(self):
        self.cleaner.config_file = '/bad/path/to/config_file'
        self.cleaner._read_early_config_options()
        self.assertFalse(self.cleaner.quiet is False)

    def test72_root_domain_bad_conf_file(self):
        self.cleaner.config_file = '/bad/path/to/config_file'
        self.cleaner._read_early_config_options()
        self.assertTrue(self.cleaner.root_domain == 'obfuscateddomain.com')

    def test73_log_level_bad_conf_file(self):
        self.cleaner.config_file = '/bad/path/to/config_file'
        self.cleaner._read_early_config_options()
        self.assertTrue(self.cleaner.loglevel == 'INFO')

    def test74_skip_mac_obfuscation(self):
        """from #98 - makes MAC obfuscation optional"""
        self.cleaner.obfuscate_macs = False
        test_line = 'a line with a 00:0c:29:64:72:3e valid mac address'
        new_line = self.cleaner._clean_line(test_line, 'somefile')
        self.assertTrue('00:0c:29:64:72:3e' in new_line)
        self.cleaner.obfuscate_macs = True
        new_line2 = self.cleaner._clean_line(test_line, 'somefile')
        self.assertFalse('00:0c:29:64:72:3e' in new_line2)

    def test75_catch_cap_usernames(self):
        """from #99 - makes username search case-insensitive"""
        self.cleaner._user2db('bob')
        test_line = 'this is a sample line with bob the user as well as BOB the user'
        new_line = self.cleaner._sub_username(test_line)
        self.assertFalse('bob' in new_line)
        self.assertFalse('BOB' in new_line)
