import re

with open('views/stock_views.xml', 'r') as f:
    c = f.read()

# Model
c = c.replace('<field name="model">assetflow.stock</field>', '<field name="model">stock.quant</field>')
c = c.replace('<field name="res_model">assetflow.stock</field>', '<field name="res_model">stock.quant</field>')

# Tree View Decorations
c = c.replace('decoration-danger="inventory_status == \'critical\'"', 'decoration-danger="needs_reorder == True"')
c = c.replace('decoration-warning="inventory_status == \'low\'"', '')

# Fields
c = c.replace('<field name="qty_available"', '<field name="quantity"')
c = c.replace('<field name="forecast_demand" string="Forecast Demand"/>', '<field name="monthly_consumption" string="Monthly Consumption"/>')
c = c.replace('<field name="forecast_demand"/>', '<field name="monthly_consumption"/>')
c = c.replace('<field name="avg_consumption"', '<field name="avg_monthly_consumption"')
c = c.replace('<field name="avg_consumption"/>', '<field name="avg_monthly_consumption"/>')

# Health Status to Boolean
status_field_regex = r'<field name="inventory_status".*?/>'
c = re.sub(status_field_regex, '<field name="needs_reorder" string="Needs Reorder"/>', c, flags=re.DOTALL)

# Search View
c = c.replace('domain="[(\'inventory_status\',\'in\',(\'low\',\'critical\'))]"', 'domain="[(\'needs_reorder\',\'=\',True)]"')
c = c.replace('<filter string="Critical" name="filter_critical" domain="[(\'inventory_status\',\'=\',\'critical\')]"/>\n', '')
c = c.replace('<filter string="Healthy" name="filter_healthy" domain="[(\'inventory_status\',\'=\',\'healthy\')]"/>\n', '')
c = c.replace('context="{\'group_by\': \'inventory_status\'}"', 'context="{\'group_by\': \'needs_reorder\'}"')

with open('views/stock_views.xml', 'w') as f:
    f.write(c)
