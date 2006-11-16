# -*- coding: utf8 -*-
#!/usr/bin/env python
"""TEST the server answers.
"""
data = (
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
        <nsset:status s='ok'/>
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
        <contact:status s='ok'/>
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
        <contact:ident>852</contact:ident>
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
    )
