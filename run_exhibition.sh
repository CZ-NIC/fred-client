#
# Test EPP server access:
#

# *** CONTACT ***
echo 'Create CONTACT'
./ccreg_create.py --range=cid:exhib[$1] 'create_contact cid:exhib MyName email@email.cz Mesto CZ heslo' | ./ccreg_sender.py -s curlew --bar
echo 'Delete CONTACT'
./ccreg_create.py --range=cid:exhib[$1] 'delete_contact cid:exhib' | ./ccreg_sender.py -s curlew --bar

# *** NSSET ***
echo 'Create NSSET'
./ccreg_create.py --range=nssid:exhib[$1] 'create_nsset nssid:exhib passw ((ns1.domain.cz (217.31.207.130 217.31.207.129)) (cid:exhib:))' | ./ccreg_sender.py -s curlew --bar
echo 'Delete NSSET'
./ccreg_create.py --range=nssid:exhib[$1] 'delete_contact nssid:exhib' | ./ccreg_sender.py -s curlew --bar

# *** DOMAIN ***
./ccreg_create.py 'create_contact cid:exhibition MyName email@email.cz Mesto CZ heslo' | ./ccreg_sender.py -s curlew  --verbose=0
echo 'Create DOMAIN'
./ccreg_create.py --range=exhibition[$1] 'create_domain exhibition.cz pw cid:exhibition' | ./ccreg_sender.py -s curlew --bar
echo 'Delete DOMAIN'
./ccreg_create.py --range=exhibition[$1] 'delete_domain exhibition.cz' | ./ccreg_sender.py -s curlew --bar
./ccreg_create.py 'delete_contact cid:exhibition' | ./ccreg_sender.py -s curlew --verbose=0
