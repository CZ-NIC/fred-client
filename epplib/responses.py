# -*- coding: utf8 -*-
#!/usr/bin/env python
#
# $Id$
#
# Zde jsou všechna EPP hlášení podle RFC 3730
#
from gettext import gettext as _T

msg = {
   #----------------------------------------- 
   # Successful command completion responses:
   #-----------------------------------------

   1000:   _T("Command completed successfully"),
   #This is the usual response code for a successfully completed command
   #that is not addressed by any other 1xxx-series response code.
   #
   1001:    _T("Command completed successfully; action pending"),
   #This response code MUST be returned when responding to a command the
   #requires offline activity before the requested action can be
   #completed.  See section 2 for a description of other processing
   #requirements.
   #
   1300:    _T("Command completed successfully; no messages"),
   #This response code MUST be returned when responding to a <poll>
   #request command and the server message queue is empty.
   #
   1301:    _T("Command completed successfully; ack to dequeue"),
   #This response code MUST be returned when responding to a <poll>
   #request command and a message has been retrieved from the server
   #message queue.
   #
   1500:    _T("Command completed successfully; ending session"),
   #This response code MUST be returned when responding to a successful
   #<logout> command.
   
   #-----------------------------------------
   #Command error responses:
   #-----------------------------------------

   2000:    _T("Unknown command"),
   #This response code MUST be returned when a server receives a command
   #element that is not defined by EPP.

   2001:    _T("Command syntax error"),
   #This response code MUST be returned when a server receives an
   #improperly formed command element.
   # example:
   #correct: <epp><command><info/></command></epp>
   #wrong:   <epp><info/></epp>

   2002:    _T("Command use error"),
   #This response code MUST be returned when a server receives a properly
   #formed command element, but the command can not be executed due to a
   #sequencing or context error.  For example, a <logout> command can not
   #be executed without having first completed a <login> command.

   2003:    _T("Required parameter missing"),
   #This response code MUST be returned when a server receives a command
   #for which a required parameter value has not been provided.

   2004:    _T("Parameter value range error"),
   #This response code MUST be returned when a server receives a command
   #parameter whose value is outside the range of values specified by the
   #protocol.  The error value SHOULD be returned via a <value> element
   #in the EPP response.

   2005:    _T("Parameter value syntax error"),
   #This response code MUST be returned when a server receives a command
   #containing a parameter whose value is improperly formed.  The error
   #value SHOULD be returned via a <value> element in the EPP response.
   # example:
   # correct: <svDate>2000-06-08T22:00:00.0Z</svDate>
   # wrong:   <svDate>00-06-08T22:00:00.0Z</svDate>

   2100:    _T("Unimplemented protocol version"),
   #This response code MUST be returned when a server receives a command
   #element specifying a protocol version that is not implemented by the
   #server.
   # <login> ... <version>1.0</version>

   2101:    _T("Unimplemented command"),
   #This response code MUST be returned when a server receives a valid
   #EPP command element that is not implemented by the server.  For
   #example, a <transfer> command can be unimplemented for certain object
   #types.

   2102:    _T("Unimplemented option"),
   #This response code MUST be returned when a server receives a valid
   #EPP command element that contains a protocol option that is not
   #implemented by the server.

   2103:    "Unimplemented extension",
   #This response code MUST be returned when a server receives a valid
   #EPP command element that contains a protocol command extension that
   #is not implemented by the server.

   2104:    _T("Billing failure"),
   #This response code MUST be returned when a server attempts to execute
   #a billable operation and the command can not be completed due to a
   #client billing failure.

   2105:    _T("Object is not eligible for renewal"),
   #This response code MUST be returned when a client attempts to <renew>
   #an object that is not eligible for renewal in accordance with server
   #policy.

   2106:    _T("Object is not eligible for transfer"),
   #This response code MUST be returned when a client attempts to
   #<transfer> an object that is not eligible for transfer in accordance
   #with server policy.

   2200:    _T("Authentication error"),
   #This response code MUST be returned when a server notes an error when
   #validating client credentials.
   # login: username, password

   2201:    _T("Authorization error"),
   #This response code MUST be returned when a server notes a client
   #authorization error when executing a command.  This error is used to
   #note that a client lacks privileges to execute the requested command.

   2202:    _T("Invalid authorization information"),
   #This response code MUST be returned when a server receives invalid
   #command authorization information required to confirm authorization
   #to execute a command.  This error is used to note that a client has
   #the privileges required to execute the requested command, but the
   #authorization information provided by the client does not match the
   #authorization information archived by the server.

   2300:    _T("Object pending transfer"),
   #This response code MUST be returned when a server receives a command
   #to transfer an object that is pending transfer due to an earlier
   #transfer request.

   2301:    _T("Object not pending transfer"),
   #This response code MUST be returned when a server receives a command
   #to confirm, reject, or cancel the transfer an object when no command
   #has been made to transfer the object.

   2302:    _T("Object exists"),
   #This response code MUST be returned when a server receives a command
   #to create an object that already exists in the repository.

   2303:    _T("Object does not exist"),
   #This response code MUST be returned when a server receives a command
   #to query or transform an object that does not exist in the
   #repository.

   2304:    _T("Object status prohibits operation"),
   #This response code MUST be returned when a server receives a command
   #to transform an object that can not be completed due to server policy
   #or business practices.  For example, a server can disallow <transfer>
   #commands under terms and conditions that are matters of local policy,
   #or the server might have received a <delete> command for an object
   #whose status prohibits deletion.

   2305:    _T("Object association prohibits operation"),
   #This response code MUST be returned when a server receives a command
   #to transform an object that can not be completed due to dependencies
   #on other objects that are associated with the target object.  For
   #example, a server can disallow <delete> commands while an object has
   #active associations with other objects.

   2306:    _T("Parameter value policy error"),
   #This response code MUST be returned when a server receives a command
   #containing a parameter value that is syntactically valid, but
   #semantically invalid due to local policy.  For example, the server
   #can support a subset of a range of valid protocol parameter values.
   #The error value SHOULD be returned via a <value> element in the EPP
   #response.

   2307:    _T("Unimplemented object service"),
   #This response code MUST be returned when a server receives a command
   #to operate on an object service that is not supported by the server.

   2308:    _T("Data management policy violation"),
   #This response code MUST be returned when a server receives a command
   #whose execution results in a violation of server data management
   #policies.  For example, removing all attribute values or object
   #associations from an object might be a violation of a server's data
   #management policies.

   2400:    _T("Command failed"),
   #This response code MUST be returned when a server is unable to
   #execute a command due to an internal server error that is not related
   #to the protocol.  The failure can be transient.  The server MUST keep
   #any ongoing session active.

   2500:    _T("Command failed; server closing connection"),
   #This response code MUST be returned when a server receives a command
   #that can not be completed due to an internal server error that is not
   #related to the protocol.  The failure is not transient, and will
   #cause other commands to fail as well.  The server MUST end the active
   #session and close the existing connection.

   2501:    _T("Authentication error; server closing connection"),
   #This response code MUST be returned when a server notes an error when
   #validating client credentials and a server-defined limit on the
   #number of allowable failures has been exceeded.  The server MUST
   #close the existing connection.

   2502:    _T("Session limit exceeded; server closing connection"),
   #This response code MUST be returned when a server receives a <login>
   #command, and the command can not be completed because the client has
   #exceeded a system-defined limit on the number of sessions that the
   #client can establish.  It might be possible to establish a session by
   #ending existing unused sessions and closing inactive connections.

}