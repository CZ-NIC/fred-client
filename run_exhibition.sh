#
# Test EPP server access:
#

# *** CONTACT ***
echo 'Create CONTACT'
./fred_create.py --range=cid:exhib[$1] 'create_contact cid:exhib MyName email@email.cz Mesto CZ heslo' | ./fred_sender.py -s curlew --bar
echo 'Delete CONTACT'
./fred_create.py --range=cid:exhib[$1] 'delete_contact cid:exhib' | ./fred_sender.py -s curlew --bar

# *** NSSET ***
echo 'Create NSSET'
./fred_create.py --range=nssid:exhib[$1] 'create_nsset nssid:exhib passw ((ns1.domain.cz (217.31.207.130 217.31.207.129)) (cid:exhib:))' | ./fred_sender.py -s curlew --bar
echo 'Delete NSSET'
./fred_create.py --range=nssid:exhib[$1] 'delete_contact nssid:exhib' | ./fred_sender.py -s curlew --bar

# *** DOMAIN ***
./fred_create.py 'create_contact cid:exhibition MyName email@email.cz Mesto CZ heslo' | ./fred_sender.py -s curlew  --verbose=0
echo 'Create DOMAIN'
./fred_create.py --range=exhibition[$1] 'create_domain exhibition.cz pw cid:exhibition' | ./fred_sender.py -s curlew --bar
echo 'Delete DOMAIN'
./fred_create.py --range=exhibition[$1] 'delete_domain exhibition.cz' | ./fred_sender.py -s curlew --bar
./fred_create.py 'delete_contact cid:exhibition' | ./fred_sender.py -s curlew --verbose=0
