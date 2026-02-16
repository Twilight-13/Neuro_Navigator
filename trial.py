from tools.finance_tool import FinanceTool

ft = FinanceTool()
print(ft.get_dest_id("Delhi, India"))
print(ft.get_dest_id("Delhi"))
print(ft.get_dest_id("New Delhi"))
