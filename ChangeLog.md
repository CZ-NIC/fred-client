# ChangeLog

## 2.12.4 (2019-11-20)
 * Update spec file for F31 and Centos/RHEL 8

## 2.12.3 (2019-06-28)
 * Fix rpm deps

## 2.12.2 (2019-06-13)
 * Fix rpm build

## 2.12.1 (2019-05-10)
 * Rework README and ChangeLog

## 2.12.0 (2019-04-10)
 * License source code with GNU GPLv3+
 * Use setuptools for distribution

## 2.11.0 (2018-09-18)
 * Remove unmaintained GUI
 * Remove EPP schemas from installation process
 * Fix check of configured epp schemas against greeting response from server

## 2.10.1 (2018-06-19)
 * Fix `fred_create.py` script - configuration of server default disclose flag policy

## 2.10.0 (2018-04-20)
 * Fix `info_contact` response - disclose flags evaluation based on server default policy

## 2.9.0 (2018-01-03)
 * Add mailing address to contact - extend interface of `create_contact`, `update_contact`, `info_contact` commands

## 2.8.0 (2017-01-10)
 * Allow keysets to contain up to 10 dnskeys
 * Add comments to configuration options
 * Add spec file

## 2.7.0 (2013-06-07)
 * Fix build process (new version of `fred-distutils`)
 * Fix README

## 2.6.0 (2012-11-21)
 * Allow to change `discloseaddress` in `update_contact` command

## 2.5.0 (2012-10-24)
 * Fix some grammar mistakes and examples
 * Fix build process (path to EPP schemas, translations generation)

## 2.4.0 (2012-05-15)
 * Upgrade EPP schemas to a new version
 * Display `discloseaddress` flag in `info_contact` command
