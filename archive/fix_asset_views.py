import re

with open('views/asset_views.xml', 'r') as f:
    c = f.read()

# Fields and status -> state mappings
c = c.replace('decoration-muted="status == \'retired\'"', 'decoration-muted="state == \'retired\'"')
c = c.replace('<field name="department_id"/>\n', '')
c = c.replace('<field name="assigned_to_id"/>', '<field name="assigned_to"/>')
c = c.replace('<field name="assigned_to_id"', '<field name="assigned_to"')
c = c.replace('<field name="status" widget="badge"', '<field name="state" widget="badge"')
c = c.replace('<field name="status" widget="statusbar"', '<field name="state" widget="statusbar"')
c = c.replace('statusbar_visible="available,allocated,maintenance,retired"', 'statusbar_visible="active,allocated,maintenance,retired"')

c = c.replace("status == 'available'", "state == 'active'")
c = c.replace("status == 'allocated'", "state == 'allocated'")
c = c.replace("status == 'maintenance'", "state == 'maintenance'")
c = c.replace("status == 'retired'", "state == 'retired'")

c = c.replace("risk_level == 'healthy'", "risk_level == 'low'")
c = c.replace("risk_level == 'monitor'", "risk_level == 'medium'")
c = c.replace("risk_level in ('warning','critical')", "risk_level in ('high','critical')")
c = c.replace("risk_level in ('monitor','warning')", "risk_level in ('medium','high')")

c = c.replace('<field name="image_1920"', '<field name="image"')
c = c.replace('<field name="image_128"', '<field name="image"')

c = c.replace('<field name="location_id"/>', '<field name="current_location_id"/>')
c = c.replace('<field name="vendor_id"/>\n', '')
c = c.replace('<field name="maintenance_ids">', '<field name="maintenance_request_ids">')

# Remove audit page
audit_page_regex = r'<page string="Audit History">.*?</page>'
c = re.sub(audit_page_regex, '', c, flags=re.DOTALL)

# Fix kanban <field name="status"/>
c = c.replace('<field name="status"/>', '<field name="state"/>')

# Search view
c = c.replace('<filter string="Available" name="filter_available" domain="[(\'status\',\'=\',\'available\')]"/>', '<filter string="Available" name="filter_available" domain="[(\'state\',\'=\',\'active\')]"/>')
c = c.replace('domain="[(\'status\',\'=\',\'allocated\')]"', 'domain="[(\'state\',\'=\',\'allocated\')]"')
c = c.replace('domain="[(\'status\',\'=\',\'maintenance\')]"', 'domain="[(\'state\',\'=\',\'maintenance\')]"')
c = c.replace('domain="[(\'status\',\'=\',\'retired\')]"', 'domain="[(\'state\',\'=\',\'retired\')]"')

c = c.replace('<filter string="Department" name="group_department" context="{\'group_by\': \'department_id\'}"/>\n', '')
c = c.replace('context="{\'group_by\': \'status\'}"', 'context="{\'group_by\': \'state\'}"')

with open('views/asset_views.xml', 'w') as f:
    f.write(c)
