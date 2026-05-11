import os

from preprocessing.add_tag_to_attr_all_fixed import main as main1
from preprocessing.create_composite_composition_matrix import main as main2
from preprocessing.create_product_breakdown_matrix import main as main3
from preprocessing.calculate_item_impacts import main as main4

from preprocessing import concat_pan_th
app_str = "WAVE1"

os.makedirs(os.path.join("data", app_str), exist_ok=True)

concat_pan_th.main()

main1(app_str=app_str)
print(1)
main2(app_str=app_str)
print(2)
main3(app_str=app_str)
print(3)
main4(app_str=app_str)
print(4)
