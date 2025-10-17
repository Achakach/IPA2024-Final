from ncclient import manager
import xmltodict


ROUTER_IP = "192.168.1.104"
NETCONF_PORT = 830
USERNAME = "admin"
PASSWORD = "cisco"

m = manager.connect(
    host= ROUTER_IP,
    port= NETCONF_PORT,
    username= USERNAME,
    password= PASSWORD,
    hostkey_verify=False
    )

def get_ip_and_prefix(student_id):
    """Generates IP address and prefix based on the last 3 digits of student ID."""
    last_three_digits = student_id[-3:]
    x = last_three_digits[0]
    y = last_three_digits[1:]
    ip_address = f"172.{x}.{y}.1"
    prefix = "24"
    return ip_address, prefix

def create(student_id):
    ip_address, prefix = get_ip_and_prefix(student_id)
    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>Loopback{student_id}</name>
          <description>Created by NETCONF</description>
          <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
          <enabled>true</enabled>
          <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
            <address>
              <ip>{ip_address}</ip>
              <netmask>255.255.255.0</netmask>
            </address>
          </ipv4>
        </interface>
      </interfaces>
    </config>
    """

    try:
        netconf_reply = netconf_edit_config(netconf_config)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            return f"Interface loopback {student_id} is created successfully"
    except Exception as e:
            if "data-exists" in str(e):
                return f"Cannot create: Interface loopback {student_id}"
            return "Error: " + str(e)


def delete(student_id):
    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface operation="delete">
          <name>Loopback{student_id}</name>
        </interface>
      </interfaces>
    </config>
    """
    try:
        netconf_reply = netconf_edit_config(netconf_config)
        xml_data = netconf_reply.xml
        if '<ok/>' in xml_data:
           return f"Interface loopback {student_id} is deleted successfully"
    except Exception as e:
        if "data-missing" in str(e):
            return f"Cannot delete: Interface loopback {student_id}"
        return "Error: " + str(e)


def enable(student_id):
    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>Loopback{student_id}</name>
          <enabled>true</enabled>
        </interface>
      </interfaces>
    </config>
    """

    try:
        # Check status first to return the correct message
        if "No Interface" in status(student_id):
            return f"Cannot enable: Interface loopback {student_id}"
            
        netconf_reply = netconf_edit_config(netconf_config)
        xml_data = netconf_reply.xml
        if '<ok/>' in xml_data:
            return f"Interface loopback {student_id} is enabled successfully"
    except Exception as e:
        return "Error: " + str(e)


def disable(student_id):
    """Disables a Loopback interface."""
    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>Loopback{student_id}</name>
          <enabled>false</enabled>
        </interface>
      </interfaces>
    </config>
    """
    try:
         # Check status first to return the correct message
        if "No Interface" in status(student_id):
            return f"Cannot shutdown: Interface loopback {student_id}"

        netconf_reply = netconf_edit_config(netconf_config)
        xml_data = netconf_reply.xml
        if '<ok/>' in xml_data:
            return f"Interface loopback {student_id} is shutdowned successfully"
    except Exception as e:
        return "Error: " + str(e)

def netconf_edit_config(netconf_config):
    """Sends an edit-config operation to the device."""
    return m.edit_config(target="running", config=netconf_config)


def status(student_id):
    """Retrieves the status of a Loopback interface."""
    netconf_filter = f"""
    <filter>
      <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces-state">
        <interface>
          <name>Loopback{student_id}</name>
        </interface>
      </interfaces-state>
    </filter>
    """
    try:
        netconf_reply = m.get(filter=netconf_filter)
        netconf_reply_dict = xmltodict.parse(netconf_reply.xml)

        interface_data = netconf_reply_dict.get('data', {}).get('interfaces-state', {}).get('interface')

        if interface_data:
            admin_status = interface_data.get('admin-status')
            oper_status = interface_data.get('oper-status')
            
            if admin_status == 'up' and oper_status == 'up':
                return f"Interface loopback {student_id} is enabled"
            elif admin_status == 'down' and oper_status == 'down':
                return f"Interface loopback {student_id} is disabled"
        else:
            return f"No Interface loopback {student_id}"
    except Exception as e:
       return "Error: " + str(e)
