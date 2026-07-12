import re

with open('views/forecast_views.xml', 'r') as f:
    c = f.read()

# Fields
c = c.replace('forecast_qty', 'predicted_qty')
c = c.replace('period_date', 'forecast_date')

c = c.replace('<field name="average_consumption"/>\n', '')
c = c.replace('<field name="predicted_reorder_date"/>\n', '')

# Inventory Health -> Reorder Suggested
health_regex = r'<field name="inventory_health" widget="badge"\s+decoration-success="inventory_health == \'healthy\'"\s+decoration-warning="inventory_health == \'monitor\'"\s+decoration-danger="inventory_health in \(\'warning\', \'critical\'\)"/>'
c = re.sub(health_regex, '<field name="reorder_suggested" widget="boolean_toggle"/>', c, flags=re.DOTALL)

# Complex decoration
c = c.replace('decoration-danger="predicted_qty - actual_qty and abs(predicted_qty - actual_qty) &gt; predicted_qty * 0.2"', 'decoration-danger="accuracy &lt; 80"')

# Search View Filters
c = c.replace('domain="[(\'inventory_health\',\'in\',(\'warning\',\'critical\'))]"', 'domain="[(\'reorder_suggested\',\'=\',True)]"')
c = c.replace('context="{\'group_by\': \'inventory_health\'}"', 'context="{\'group_by\': \'reorder_suggested\'}"')

with open('views/forecast_views.xml', 'w') as f:
    f.write(c)
