#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#Test on session_transfer.py

#Command name from:
#session_transfer.ManagerTransfer().grab_command_name_from_xml()
#eppdoc.Message().get_epp_command_name()
#Returns top EPP command name. 
#        Level 1: epp.greeting
#        Level 1: epp.command 
#        Level 2:     info, check, create, ....
#        Level 3:        contact:create
#        Level 4:        fred:sendauthinfo, fred:creditinfo, fred:test


"""TEST the server answers.
"""
data = ( # 0
        ('greeting',"""<?xml version='1.0' encoding='utf-8' standalone="no"?>
<epp xmlns='urn:ietf:params:xml:ns:epp-1.0' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:schemaLocation='urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'>
  <greeting>
    <svID>EPP server of cz.nic</svID>
    <svDate>2006-07-12T08:52:01.0Z</svDate>
    <svcMenu>
      <version>1.0</version>
      <lang>en</lang>
      <lang>cs</lang>
      <objURI>http://www.nic.cz/xml/epp/contact-1.0</objURI>
      <objURI>http://www.nic.cz/xml/epp/domain-1.0</objURI>
      <objURI>http://www.nic.cz/xml/epp/nsset-1.0</objURI>
      <svcExtension>
        <extURI>http://www.nic.cz/xml/epp/enumval-1.0</extURI>
      </svcExtension>
    </svcMenu>
    <dcp>
      <access>
        <all/>
      </access>
      <statement>
        <purpose>
          <admin/>
          <prov/>
        </purpose>
        <recipient>
          <public/>
        </recipient>
        <retention>
          <stated/>
        </retention>
      </statement>
    </dcp>
  </greeting>
</epp>
        """),
        # 1
        ('transfer',"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="urn:ietf:params:xml:ns:epp-1.0
     epp-1.0.xsd">
  <command>
    <transfer op="request">
      <domain:transfer
       xmlns:domain="http://www.nic.cz/xml/epp/domain-1.0"
       xsi:schemaLocation="http://www.nic.cz/xml/epp/domain-1.0
       domain-1.0.xsd">
        <domain:name>example.cz</domain:name>
        <domain:authInfo>
            <domain:pw>2fooBAR</domain:pw>
        </domain:authInfo>
      </domain:transfer>
    </transfer>
    <clTRID>ABC-12345</clTRID>
  </command>
</epp>"""),
    # 2
    ('create:domain',"""<?xml version='1.0' encoding='utf-8' standalone="no"?>
<epp xmlns='urn:ietf:params:xml:ns:epp-1.0' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:schemaLocation='urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'>
  <response>
    <result code='2005'>
      <msg lang='cs'>Chybná syntaxe hodnoty parametru</msg>
      <extValue>
        <value>
          <registrant>pepa</registrant>
        </value>
        <reason lang='en'>unknow Registrant</reason>
      </extValue>
      <extValue>
        <value>
          <nsset/>
        </value>
        <reason>unknow nsset</reason>
      </extValue>
    </result>
    <trID>
      <clTRID>dnlq003#06-07-12at11:41:05</clTRID>
      <svTRID>fred-0000010019</svTRID>
    </trID>
  </response>
</epp>
    """),
    # 3
    ('poll',"""<?xml version='1.0' encoding='utf-8' standalone="no"?>
<epp xmlns='urn:ietf:params:xml:ns:epp-1.0' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:schemaLocation='urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'>
  <response>
    <result code='2400'>
      <msg lang='cs'>Příkaz selhal</msg>
      <extValue>
        <value>
          <poll msgID='2' op='ack'/>
        </value>
        <reason>unknow msgID 2</reason>
      </extValue>
    </result>
    <trID>
      <clTRID>blig004#06-07-13at10:49:35</clTRID>
      <svTRID>fred-0000010109</svTRID>
    </trID>
  </response>
</epp>
    """),
    # 4
    ('poll',"""<?xml version='1.0' encoding='utf-8' standalone="no"?>
<epp xmlns='urn:ietf:params:xml:ns:epp-1.0' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:schemaLocation='urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'>
  <response>
    <result code='1301'>
      <msg lang='cs'>Příkaz úspěšně proveden; potvrď za účelem vyřazení z fronty</msg>
    </result>
    <msgQ count='1' id='4'>
      <qDate>2006-07-13T10:31:00.0Z</qDate>
      <msg>Je tady nejaka hlaska...</msg>
    </msgQ>
    <trID>
      <clTRID>mubd002#06-07-13at13:49:00</clTRID>
      <svTRID>fred-0000010147</svTRID>
    </trID>
  </response>
</epp>
    """),
    # 5
    ('contact:create',"""<?xml version='1.0' encoding='utf-8' standalone="no"?>
<epp xmlns='urn:ietf:params:xml:ns:epp-1.0' xmlns:contact='http://www.nic.cz/xml/epp/contact-1.0' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:schemaLocation='urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'>
  <response>
    <result code='1000'>
      <msg lang='cs'>Příkaz úspěšně proveden</msg>
    </result>
    <resData>
      <contact:creData xsi:schemaLocation='http://www.nic.cz/xml/epp/contact-1.0 contact-1.0.xsd'>
        <contact:id>lubosid</contact:id>
        <contact:crDate>2006-07-14T09:02:59.0Z</contact:crDate>
      </contact:creData>
    </resData>
    <trID>
      <clTRID>ebvg003#06-07-14at11:02:58</clTRID>
      <svTRID>fred-0000010885</svTRID>
    </trID>
  </response>
</epp>"""),
    # 6
    ('domain:create',"""<?xml version='1.0' encoding='utf-8' standalone="no"?>
<epp xmlns='urn:ietf:params:xml:ns:epp-1.0' xmlns:domain='http://www.nic.cz/xml/epp/domain-1.0' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:schemaLocation='urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'>
  <response>
    <result code='1000'>
      <msg lang='cs'>Příkaz úspěšně proveden</msg>
    </result>
    <resData>
      <domain:creData xsi:schemaLocation='http://www.nic.cz/xml/epp/domain-1.0 domain-1.0.xsd'>
        <domain:name>lusk.cz</domain:name>
        <domain:crDate>2006-07-14T11:25:55.0Z</domain:crDate>
        <domain:exDate>2006-07-14T00:00:00.0Z</domain:exDate>
      </domain:creData>
    </resData>
    <trID>
      <clTRID>ausc002#06-07-14at13:25:54</clTRID>
      <svTRID>fred-0000011001</svTRID>
    </trID>
  </response>
</epp>
"""),
    # 7
    ('domain:renew',"""<?xml version='1.0' encoding='utf-8' standalone="no"?>
<epp xmlns='urn:ietf:params:xml:ns:epp-1.0' xmlns:domain='http://www.nic.cz/xml/epp/domain-1.0' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:schemaLocation='urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'>
  <response>
    <result code='1000'>
      <msg lang='cs'>Příkaz úspěšně proveden</msg>
    </result>
    <resData>
      <domain:renData xsi:schemaLocation='http://www.nic.cz/xml/epp/domain-1.0 domain-1.0.xsd'>
        <domain:name>LUSK.CZ</domain:name>
        <domain:exDate>2008-07-14T00:00:00.0Z</domain:exDate>
      </domain:renData>
    </resData>
    <trID>
      <clTRID>koix009#06-07-14at13:40:10</clTRID>
      <svTRID>fred-0000011024</svTRID>
    </trID>
  </response>
</epp>
"""),
    # 8
    ('nsset:info',"""<?xml version='1.0' encoding='utf-8' standalone="no"?>
<epp xmlns='urn:ietf:params:xml:ns:epp-1.0' xmlns:nsset='http://www.nic.cz/xml/epp/nsset-1.0' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:schemaLocation='urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'>
  <response>
    <result code='1000'>
      <msg lang='cs'>Příkaz úspěšně proveden</msg>
    </result>
    <resData>
      <nsset:infData xsi:schemaLocation='http://www.nic.cz/xml/epp/nsset-1.0 nsset-1.0.xsd'>
        <nsset:id>one</nsset:id>
        <nsset:roid>N0000000059-CZ</nsset:roid>
        <nsset:status s='ok'>NSSET is OK</nsset:status>
        <nsset:clID>REG-LRR</nsset:clID>
        <nsset:crDate>2006-06-30T09:09:57.0Z</nsset:crDate>
        <nsset:upID>REG-LRR</nsset:upID>
        <nsset:authInfo>
          <nsset:pw>heslo</nsset:pw>
        </nsset:authInfo>
        <nsset:ns>
          <nsset:name>ns1.one.cz</nsset:name>
          <nsset:addr>192.23.54.1</nsset:addr>
        </nsset:ns>
        <nsset:ns>
          <nsset:name>ns2.one.cz</nsset:name>
          <nsset:addr>192.23.54.2</nsset:addr>
          <nsset:addr>192.23.54.3</nsset:addr>
          <nsset:addr>192.23.54.4</nsset:addr>
          <nsset:addr>192.23.54.5</nsset:addr>
        </nsset:ns>
        <nsset:tech>NECOCZ-PETR</nsset:tech>
      </nsset:infData>
    </resData>
    <trID>
      <clTRID>ljmm002#06-07-17at10:36:13</clTRID>
      <svTRID>fred-0000011281</svTRID>
    </trID>
  </response>
</epp>
"""),
    # 9
    ('contact:info',"""<?xml version='1.0' encoding='utf-8' standalone="no"?>
<epp xmlns='urn:ietf:params:xml:ns:epp-1.0' xmlns:contact='http://www.nic.cz/xml/epp/contact-1.0' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:schemaLocation='urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'>
  <response>
    <result code='1000'>
      <msg lang='cs'>Příkaz úspěšně proveden</msg>
    </result>
    <resData>
      <contact:infData xsi:schemaLocation='http://www.nic.cz/xml/epp/contact-1.0 contact-1.0.xsd'>
        <contact:id>test001</contact:id>
        <contact:roid>C0000000031-CZ</contact:roid>
        <contact:status s='ok'>Contact is OK</contact:status>
        <contact:status s='linked'>Contact is admin or tech</contact:status>
        <contact:postalInfo>
          <contact:name>Řehoř Čížek</contact:name>
          <contact:org>Čížková a spol</contact:org>
          <contact:addr>
            <contact:street>U práce</contact:street>
            <contact:street>Za monitorem</contact:street>
            <contact:street>Nad klávesnicí</contact:street>
            <contact:city>Český Krumlov</contact:city>
            <contact:sp>123</contact:sp>
            <contact:pc>12300</contact:pc>
            <contact:cc>CZ</contact:cc>
          </contact:addr>
        </contact:postalInfo>
        <contact:voice>+123.456789</contact:voice>
        <contact:fax>+321.564987</contact:fax>
        <contact:email>rehor.cizek@mail.cz</contact:email>
        <contact:crID>REG-LRR</contact:crID>
        <contact:crDate>2006-08-01T13:21:16.0Z</contact:crDate>
        <contact:disclose flag='0'>
          <contact:fax/>
          <contact:voice/>
        </contact:disclose>
        <contact:vat>963</contact:vat>
        <contact:ssn>852</contact:ssn>
        <contact:notifyEmail>info@rehorovi.cz</contact:notifyEmail>
        </contact:infData>
    </resData>
    <trID>
      <clTRID>hsrq003#06-08-01at15:58:42</clTRID>
      <svTRID>fred-0000001553</svTRID>
    </trID>
  </response>
</epp>
    """),
    # 10
    ('domain:check',"""<?xml version='1.0' encoding='utf-8' standalone="no"?>
<epp xmlns='urn:ietf:params:xml:ns:epp-1.0' xmlns:domain='http://www.nic.cz/xml/epp/domain-1.0' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:schemaLocation='urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'>
  <response>
    <result code='1000'>
      <msg lang='cs'>Příkaz úspěšně proveden</msg>
    </result>
    <resData>
      <domain:chkData xsi:schemaLocation='http://www.nic.cz/xml/epp/domain-1.0 domain-1.0.xsd'>
        <domain:cd>
          <domain:name avail='0'>nic.cz</domain:name>
          <domain:reason>In use</domain:reason>
        </domain:cd>
        <domain:cd>
        <domain:name avail='1'>myweb.cz</domain:name>
        </domain:cd>
      </domain:chkData>
    </resData>
    <trID>
      <clTRID>cemf003#06-08-08at08:48:59</clTRID>
      <svTRID>fred-0001323538</svTRID>
    </trID>
  </response>
</epp>
"""),
    # 11
    ('domain:create',"""<?xml version='1.0' encoding='utf-8' standalone="no"?>
<epp xmlns='urn:ietf:params:xml:ns:epp-1.0' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:schemaLocation='urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'>
  <response>
    <result code='2005'>
      <msg lang='cs'>Chybná syntaxe hodnoty parametru</msg>
      <extValue>
        <value>
          <registrant>reg-id</registrant>
        </value>
        <reason lang='cs'/>
      </extValue>
      <extValue>
        <value>
          <nsset>nsset1</nsset>
        </value>
        <reason lang='cs'>Hokus čuřil čeština</reason>
      </extValue>
    </result>
    <trID>
      <clTRID>qqve002#06-09-15at15:31:21</clTRID>
      <svTRID>fred-0000180139</svTRID>
    </trID>
  </response>
</epp>
    """),
    # 12
    ('contact:list',"""<?xml version='1.0' encoding='utf-8' standalone="no"?>
<epp xmlns='urn:ietf:params:xml:ns:epp-1.0' xmlns:contact='http://www.nic.cz/xml/epp/contact-1.0' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:schemaLocation='urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'>
  <response>
    <result code='1000'>
      <msg lang='cs'>Příkaz úspěšně proveden</msg>
    </result>
    <resData>
      <contact:listData xsi:schemaLocation='http://www.nic.cz/xml/epp/contact-1.0 contact-1.0.xsd'>
        <contact:id>CID:FEELA</contact:id>
        <contact:id>CID:TEST</contact:id>
      </contact:listData>
    </resData>
    <trID>
      <clTRID>jfbs002#06-09-21at17:27:25</clTRID>
      <svTRID>fred-0000014445</svTRID>
    </trID>
  </response>
</epp>
"""),
    # 13
    ('nsset:list',"""<?xml version='1.0' encoding='utf-8' standalone="no"?>
<epp xmlns='urn:ietf:params:xml:ns:epp-1.0' xmlns:nsset='http://www.nic.cz/xml/epp/nsset-1.0' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:schemaLocation='urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'>
  <response>
    <result code='1000'>
      <msg lang='cs'>Příkaz úspěšně proveden</msg>
    </result>
    <resData>
      <nsset:listData xsi:schemaLocation='http://www.nic.cz/xml/epp/nsset-1.0 nsset-1.0.xsd'>
        <nsset:id>NSSID:NTEST</nsset:id>
        <nsset:id>NSSID:AAA</nsset:id>
        <nsset:id>NSSID:FEELA</nsset:id>
        <nsset:id>NSSID:BBB</nsset:id>
        <nsset:id>NSSID:CCC</nsset:id>
      </nsset:listData>
    </resData>
    <trID>
      <clTRID>jfbs003#06-09-21at17:28:34</clTRID>
      <svTRID>fred-0000014446</svTRID>
    </trID>
  </response>
</epp>
"""),
    # 14
    ('domain:list',"""<?xml version='1.0' encoding='utf-8' standalone="no"?>
<epp xmlns='urn:ietf:params:xml:ns:epp-1.0' xmlns:domain='http://www.nic.cz/xml/epp/domain-1.0' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:schemaLocation='urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'>
  <response>
    <result code='1000'>
      <msg lang='cs'>Příkaz úspěšně proveden</msg>
    </result>
    <resData>
      <domain:listData xsi:schemaLocation='http://www.nic.cz/xml/epp/domain-1.0 domain-1.0.xsd'>
        <domain:name>test.cz</domain:name>
        <domain:name>2.1.1.5.4.7.2.2.2.0.2.4.e164.arpa</domain:name>
        <domain:name>feela.cz</domain:name>
        <domain:name>domain.cz</domain:name>
      </domain:listData>
    </resData>
    <trID>
      <clTRID>jfbs004#06-09-21at17:29:24</clTRID>
      <svTRID>fred-0000014447</svTRID>
    </trID>
  </response>
</epp>
    """),
    # 15
    ('domain:renew',"""<?xml version='1.0' encoding='utf-8' standalone="no"?>
<epp xmlns='urn:ietf:params:xml:ns:epp-1.0' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:schemaLocation='urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'>
  <response>
    <result code='2004'>
      <msg lang='cs'>Chybný rozsah parametru</msg>
      <extValue>
        <value>
          <period unit='y'>10</period>
        </value>
        <reason lang='cs'>perioda je nad maximalní dovolenou hodnotou</reason>
      </extValue>
    </result>
    <trID>
      <clTRID>zisv003#06-11-15at14:28:10</clTRID>
      <svTRID>ccReg-0000026830</svTRID>
    </trID>
  </response>
</epp>
"""),
    ('contact:sendauthinfo',"""<?xml version='1.0' encoding='utf-8' standalone="no"?>
<epp xmlns='urn:ietf:params:xml:ns:epp-1.0' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:schemaLocation='urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'>
  <response>
    <result code='1000'>
      <msg>Command completed successfully</msg>
    </result>
    <trID>
      <clTRID>zqin003#06-11-20at10:20:41</clTRID>
      <svTRID>ccReg-0000190022</svTRID>
    </trID>
  </response>
</epp>
"""),
    ('contact:delete',"""<?xml version='1.0' encoding='utf-8' standalone="no"?>
<epp xmlns='urn:ietf:params:xml:ns:epp-1.0' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:schemaLocation='urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'>
  <response>
    <result code='1000'>
      <msg>Command completed successfully</msg>
    </result>
    <trID>
      <clTRID>bmjm003#06-11-20at10:30:44</clTRID>
      <svTRID>ccReg-0000190035</svTRID>
    </trID>
  </response>
</epp>
"""),
    # fred:extcommand, fred:creditInfo
    # command: fred:creditinfo fnc_name: answer_response_fred_creditinfo
    ('fred:creditinfo',"""<?xml version='1.0' encoding='utf-8' standalone="no"?>
<epp xmlns='urn:ietf:params:xml:ns:epp-1.0' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xmlns:fred='http://www.nic.cz/xml/epp/fred-1.0' xsi:schemaLocation='urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'>
  <response>
    <result code='1000'>
      <msg lang='cs'>P\u0159\u00edkaz \u00fasp\u011b\u0161n\u011b proveden</msg>
    </result>
    <resData>
      <fred:resCreditInfo xsi:schemaLocation='http://www.nic.cz/xml/epp/fred-1.0 fred-1.0.xsd'>
        <fred:zoneCredit>
          <fred:zone>0.2.4.e164.arpa</fred:zone>
          <fred:credit>201.50</fred:credit>
        </fred:zoneCredit>
        <fred:zoneCredit>
          <fred:zone>cz</fred:zone>
          <fred:credit>603873.00</fred:credit>
        </fred:zoneCredit>
      </fred:resCreditInfo>
    </resData>
    <trID>
      <clTRID>rimq002#06-12-13at08:54:46</clTRID>
      <svTRID>ccReg-0001059227</svTRID>
    </trID>
  </response>
</epp>
"""),
    ('credit_info',"""<?xml version='1.0' encoding='utf-8' standalone="no"?>
<epp xmlns='urn:ietf:params:xml:ns:epp-1.0' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xmlns:fred='http://www.nic.cz/xml/epp/fred-1.0' xsi:schemaLocation='urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'>
  <response>
    <result code='1000'>
      <msg lang='cs'>P\u0159\u00edkaz \u00fasp\u011b\u0161n\u011b proveden</msg>
    </result>
    <resData>
      <fred:resCreditInfo xsi:schemaLocation='http://www.nic.cz/xml/epp/fred-1.0 fred-1.0.xsd'>
        <fred:zoneCredit>
          <fred:zone>0.2.4.e164.arpa</fred:zone>
          <fred:credit>201.50</fred:credit>
        </fred:zoneCredit>
        <fred:zoneCredit>
          <fred:zone>cz</fred:zone>
          <fred:credit>603873.00</fred:credit>
        </fred:zoneCredit>
      </fred:resCreditInfo>
    </resData>
    <trID>
      <clTRID>rimq002#06-12-13at08:54:46</clTRID>
      <svTRID>ccReg-0001059227</svTRID>
    </trID>
  </response>
</epp>
"""),
    ('transfer', """<?xml version='1.0' encoding='utf-8' standalone="no"?>
<epp xmlns='urn:ietf:params:xml:ns:epp-1.0' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:schemaLocation='urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'>
  <response>
    <result code='2201'>
      <msg lang='cs'>Chyba opr\u00e1vn\u011bn\u00ed</msg>
    </result>
    <trID>
      <clTRID>jaxt002#07-04-10at14:25:11</clTRID>
      <svTRID>ccReg-0000301928</svTRID>
    </trID>
  </response>
</epp>"""),
    ('transfer', """<?xml version='1.0' encoding='utf-8' standalone="no"?>
<epp xmlns='urn:ietf:params:xml:ns:epp-1.0' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:schemaLocation='urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'>
  <response>
    <result code='1000'>
      <msg lang='cs'>P\u0159\u00edkaz \u00fasp\u011b\u0161n\u011b proveden</msg>
    </result>
    <trID>
      <clTRID>jaxt003#07-04-10at14:25:12</clTRID>
      <svTRID>ccReg-0000301929</svTRID>
    </trID>
  </response>
</epp>"""),
    ('domain:info', """<?xml version="1.0" encoding="UTF-8"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd"><response><result code="1000"><msg lang="cs">P\u0159\u00edkaz \u00fasp\u011b\u0161n\u011b proveden</msg>
</result>
<resData><domain:infData xmlns:domain="http://www.nic.cz/xml/epp/domain-1.2" xsi:schemaLocation="http://www.nic.cz/xml/epp/domain-1.2 domain-1.1.xsd"><domain:name>test262403.cz</domain:name>
<domain:roid>D0000009499-CZ</domain:roid>
<domain:status s="ok">Domain is OK</domain:status>
<domain:registrant>CID:D184452</domain:registrant>
<domain:admin>CID:D184452</domain:admin>
<domain:nsset>NSSID:D1917228</domain:nsset>
<domain:clID>REG-UNITTEST1</domain:clID>
<domain:crID>REG-UNITTEST1</domain:crID>
<domain:crDate>2007-03-30T10:16:26+02:00</domain:crDate>
<domain:upID>REG-UNITTEST1</domain:upID>
<domain:upDate>2007-05-14T14:24:54+02:00</domain:upDate>
<domain:exDate>2010-03-30</domain:exDate>
<domain:authInfo>heslicko</domain:authInfo>
<domain:tempcontact>CID:D184452</domain:tempcontact>
<domain:tempcontact>CID:D184000</domain:tempcontact>
</domain:infData>
</resData>
<trID><clTRID>nfxl003#07-05-15at11:02:33</clTRID>
<svTRID>ccReg-0000314250</svTRID>
</trID>
</response>
</epp>"""), 

    ('fred:listdomains', """<?xml version='1.0' encoding='utf-8' standalone="no"?>
<epp xmlns='urn:ietf:params:xml:ns:epp-1.0' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xmlns:fred='http://www.nic.cz/xml/epp/fred-1.1' xsi:schemaLocation='urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'>
  <response>
    <result code='1000'>
      <msg lang='cs'>P\u0159\u00edkaz \u00fasp\u011b\u0161n\u011b proveden</msg>
    </result>
    <resData>
      <fred:infoResponse xsi:schemaLocation='http://www.nic.cz/xml/epp/fred-1.1 fred-1.1.xsd'>
        <fred:count>2</fred:count>
      </fred:infoResponse>
    </resData>
    <trID>
      <clTRID>ABC-12346</clTRID>
      <svTRID>ccReg-0000315538</svTRID>
    </trID>
  </response>
</epp>"""), 
    ('fred:getresults', """<?xml version='1.0' encoding='utf-8' standalone="no"?>
<epp xmlns='urn:ietf:params:xml:ns:epp-1.0' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xmlns:fred='http://www.nic.cz/xml/epp/fred-1.1' xsi:schemaLocation='urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'>
  <response>
    <result code='1000'>
      <msg lang='cs'>P\u0159\u00edkaz \u00fasp\u011b\u0161n\u011b proveden</msg>
    </result>
    <resData>
      <fred:resultsList xsi:schemaLocation='http://www.nic.cz/xml/epp/fred-1.1 fred-1.1.xsd'>
        <fred:item>CID:JEDNA</fred:item>
        <fred:item>CID:DVA</fred:item>
      </fred:resultsList>
    </resData>
    <trID>
      <clTRID>anam003#07-05-28at10:47:03</clTRID>
      <svTRID>ccReg-0000315570</svTRID>
    </trID>
  </response>
</epp>
"""), 
    ('fred:domainsbycontact', """<?xml version='1.0' encoding='utf-8' standalone="no"?>
<epp xmlns='urn:ietf:params:xml:ns:epp-1.0' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xmlns:fred='http://www.nic.cz/xml/epp/fred-1.1' xsi:schemaLocation='urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'>
  <response>
    <result code='1000'>
      <msg lang='cs'>P\u0159\u00edkaz \u00fasp\u011b\u0161n\u011b proveden</msg>
    </result>
    <resData>
      <fred:infoResponse xsi:schemaLocation='http://www.nic.cz/xml/epp/fred-1.1 fred-1.1.xsd'>
        <fred:count>1</fred:count>
      </fred:infoResponse>
    </resData>
    <trID>
      <clTRID>hqxt003#07-05-30at12:10:23</clTRID>
      <svTRID>ccReg-0000316219</svTRID>
    </trID>
  </response>
</epp>
"""), 
    ('poll', """<?xml version="1.0" encoding="UTF-8"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd"><response><result code="1301"><msg lang="cs">Prikaz uspasne proveden; potvrd za ucelem vyrazeni z fronty</msg>
</result>
<msgQ count="1" id="1025"><qDate>2007-06-26T15:45:34+02:00</qDate>
<msg><nsset:trnData  xmlns:nsset="http://www.nic.cz/xml/epp/nsset-1.3" xsi:schemaLocation="http://www.nic.cz/xml/epp/nsset-1.3 nsset-1.3.xsd"  > <nsset:id>NSSID:A</nsset:id><nsset:trDate>2007-06-26T15:39:09+02:00</nsset:trDate><nsset:clID>REG-UNITTEST2</nsset:clID></nsset:trnData>
</msg>
</msgQ>
<trID><clTRID>zpkl003#07-06-27at09:27:04</clTRID>
<svTRID>ccReg-0000319649</svTRID>
</trID>
</response>
</epp>"""), 
    ('poll', """<?xml version="1.0" encoding="UTF-8"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd"><response><result code="1301"><msg lang="cs">Prikaz uspasne proveden; potvrd za ucelem vyrazeni z fronty</msg>
</result>
<msgQ count="1" id="1025"><qDate>2007-06-26T15:45:34+02:00</qDate>
<msg><contact:trnData  xmlns:contact="http://www.nic.cz/xml/epp/contact-1.3" xsi:schemaLocation="http://www.nic.cz/xml/epp/contact-1.3 contact-1.3.xsd"  ><contact:id>CID:JARA</contact:id>
<contact:trDate>2007-06-26T15:45:34+02:00</contact:trDate>
<contact:clID>REG-UNITTEST2</contact:clID>
</contact:trnData>
</msg>
</msgQ>
<trID><clTRID>zpkl003#07-06-27at09:27:04</clTRID>
<svTRID>ccReg-0000319649</svTRID>
</trID>
</response>
</epp>
"""), 
    ('poll', """<?xml version='1.0' encoding='utf-8' standalone="no"?>
<epp xmlns='urn:ietf:params:xml:ns:epp-1.0' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:schemaLocation='urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'>
  <response>
    <result code='1000'>
      <msg lang='cs'>P\u0159\u00edkaz \u00fasp\u011b\u0161n\u011b proveden</msg>
    </result>
    <trID>
      <clTRID>uflc007#07-06-27at10:02:35</clTRID>
      <svTRID>ccReg-0000319681</svTRID>
    </trID>
  </response>
</epp>"""), 
    ('response', """<?xml version='1.0' encoding='utf-8' standalone="no"?>
<epp xmlns='urn:ietf:params:xml:ns:epp-1.0' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:schemaLocation='urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'>
  <response>
    <result code='2502'>
      <msg lang='cs'>Session limit exceeded; server closing connection</msg>
    </result>
    <trID>
      <clTRID>yltc012#07-09-24at15:31:12</clTRID>
      <svTRID>ccReg-0000705643</svTRID>
    </trID>
  </response>
</epp>
"""), 
    )

if __name__ == '__main__':
    import session_transfer
    m = session_transfer.ManagerTransfer()
    print m.grab_command_name_from_xml(data[-1][1])

