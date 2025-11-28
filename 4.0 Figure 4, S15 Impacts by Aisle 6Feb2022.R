###
# Fig 3
# Impacts by Aisle for Tesco

# libraries
library(dplyr)
library(plyr)
library(ggplot2)
library(ggrepel)
library(readr)

# Working directory
setwd("/Volumes/Citadel/Clark_et_al_2022_PNAS_SM")

# data
plot.dat <- read_csv(paste0(getwd(),"/Managed_Data/Impacts by Product 21January2022 Log2.csv"))

# Aggregating
plot.dat.aisle <-
  plot.dat %>%
  filter(Retailer %in% 'Tesco') %>%
  filter(!grepl('Christmas|Hallow|Beer|Wine|Liqu', Department)) %>%
  filter(!grepl('Christmas|Hallow|Beer|Wine|Liqu',Aisle,ignore.case=TRUE)) %>%
  filter(!grepl('Christmas|Hallow|Beer|Wine|Liqu',Shelf,ignore.case=TRUE)) %>%
  mutate(Aisle = ifelse(grepl('\\bbeef\\b|\\blamb\\b|\\bsheep\\b|\\bgoat\\b',Shelf, ignore.case = TRUE),'Beef and Lamb',Aisle)) %>%
  # mutate(Aisle = ifelse(grepl('\\bbeef\\b|\\blamb\\b|\\bsheep\\b|\\bgoat\\b',Shelf, ignore.case = TRUE),'Fresh Fruit',Aisle)) %>%
  mutate(Aisle = ifelse(grepl('Nut|Seed|Almond|Pecan|Walnut|Pistachio|Cashew|Chestnut|Macadmi|Maracon|Brazil|Hazel',product_name, ignore.case = TRUE) & Aisle %in% 'Fresh Fruit','Dried Fruit, Nuts, Nutrient Powders & Seeds',Aisle)) %>%
  mutate(Aisle = ifelse(Aisle %in% c('Fresh Meat & Poultry','Frozen Meat & Poultry','Cooked Meats, Sandwich Fillers & Deli'), 'Meat', Aisle)) %>%
  mutate(Aisle = ifelse(Aisle %in% c('Frozen Meat Alternatives','Fresh Meat Alternatives'), 'Meat Alternatives', Aisle)) %>%
  mutate(Aisle = ifelse(Aisle %in% c('Fresh Vegetables','Frozen Vegetables & Herbs'), 'Vegetables', Aisle)) %>%
  mutate(Aisle = ifelse(Aisle %in% c('Frozen Ready Meals','Ready Meals'), 'Ready Meals', Aisle)) %>%
  mutate(Aisle = ifelse(Aisle %in% c('Frozen Pizza & Garlic Bread','Fresh Pizza, Pasta & Garlic Bread'), 'Pizza & Garlic Bread', Aisle)) %>%
  mutate(Aisle = ifelse(Aisle %in% c('Chilled Fish & Seafood','Frozen Fish & Seafood'), 'Fish & Seafood', Aisle)) %>%
  mutate(Aisle = ifelse(Aisle %in% c('Pies, Quiches & Party Food','Frozen Pies'), 'Pies, Quiches & Party Food', Aisle)) %>%
  mutate(Aisle = ifelse(Aisle %in% 'Counters','Deli Meat and Cheese',Aisle)) %>%
  mutate(Aisle = ifelse(Aisle %in% 'Fresh Fruit','Fresh Fruit and Nuts',Aisle)) %>%
  mutate(Aisle = ifelse(Aisle %in% c('Frozen Free From','Free From Range'),'Gluten Free Range',Aisle)) %>%
  mutate(Aisle = ifelse(Aisle %in% c('Juices & Smoothies','Chilled Fruit Juice & Smoothies'),'Juices & Smoothies',Aisle)) %>%
  mutate(Aisle = ifelse(Aisle %in% c('Cereals'),'Breakfast Cereals',Aisle)) %>%
  filter(!(Aisle %in% c('Beer & Cider','Spirits','Low & No Alcohol','Wine'))) %>%
  unique(.) %>%
  filter(!grepl('Halloween',Aisle, ignore.case = TRUE)) %>%
  filter(!grepl('Christmas',Aisle, ignore.case = TRUE)) %>%
  filter(!grepl('\\bAll\\b',Aisle,ignore.case = TRUE)) %>%
  filter(!(Shelf %in% 'All')) %>%
  filter(!(Shelf %in% 'NULL')) %>%
  dplyr::select(product_name, id, Retailer, Aisle, Tot_env_100g_scaled, Tot_env_100g_scaled_lower_ci, Tot_env_100g_scaled_upper_ci, NutriScore_Scaled,NutriScoreLetter) %>%
  .[complete.cases(.),] %>%
  filter(!grepl('coffee.*maker|coffee.*filter|coffee.*press|aero.*press|coffee.*paper', product_name, ignore.case = TRUE)) %>%
  unique(.) %>%
  mutate(NutriScore_Scaled = ifelse(NutriScoreLetter %in% 'A',1,
                                    ifelse(NutriScoreLetter %in% 'B',2,
                                           ifelse(NutriScoreLetter %in% 'C',3,
                                                  ifelse(NutriScoreLetter %in% 'D',4,5))))) %>%
  group_by(Retailer, Aisle) %>%
  dplyr::summarise(sd_env = sd(Tot_env_100g_scaled),
                   Tot_env_100g_scaled = mean(Tot_env_100g_scaled),
                   Tot_env_100g_scaled_lower_ci = mean(Tot_env_100g_scaled_lower_ci),
                   Tot_env_100g_scaled_upper_ci = mean(Tot_env_100g_scaled_upper_ci),
                   mean_nutriscore = mean(NutriScore_Scaled),
                   sd_nutriscore = sd(NutriScore_Scaled),
                   n_nutriscore = n()) %>%
  as.data.frame(.) %>%
  mutate(se_nutriscore = sd_nutriscore / sqrt(n_nutriscore),
         Tot_env_100g_scaled_se = sd_env / sqrt(n_nutriscore),
         lower_ci_nutriscore = mean_nutriscore - qt(1 - (0.05 / 2), n_nutriscore - 1) * se_nutriscore,
         upper_ci_nutriscore = mean_nutriscore + qt(1 - (0.05 / 2), n_nutriscore - 1) * se_nutriscore) %>%
  mutate(Env_Quantile = ifelse(Tot_env_100g_scaled <= quantile(.$Tot_env_100g_scaled,1/3,na.rm=TRUE),1,
                               ifelse(Tot_env_100g_scaled <= quantile(.$Tot_env_100g_scaled,2/3,na.rm=TRUE),2,3))) %>%
  mutate(Nut_Quantile = ifelse(mean_nutriscore <= quantile(.$mean_nutriscore,1/3,na.rm=TRUE),1,
                               ifelse(mean_nutriscore <= quantile(.$mean_nutriscore,2/3,na.rm=TRUE),2,3)))

# Adding labels
plot.dat.aisle <-
  plot.dat.aisle %>% 
  mutate(Label = Aisle) %>%
  mutate(Label = ifelse(Label %in% c('Bottled Water','Free From Range','Frozen Free From','Easy Entertaining','Frozen Free From',
                                     'World Foods','Frozen World Foods & Halal','Home Baking',
                                     'Sugar & Sweeteners','Tins, Cans & Packets','From our Bakery','Counters',
                                     'Bakery Free From','Cooking Ingredients','Sweets, Mints & Chewing Gum','Desserts','Chilled Desserts',
                                     'Cooking Suaces & Meal Kits','Crisps, Snacks & Popcorn','Crackers & Crispbreads','Cakes, Cake Bars, Slices & Pies', 'Frozen Yorkshire Puddings & Stuffing'), ' ', Label)) %>%
  mutate(Label = ifelse(Label %in% c('Fresh Meat & Poultry','Frozen Meat & Poultry','Cooked Meats, Sandwich Fillers & Deli'), 'Meat', Label)) %>%
  mutate(Label = ifelse(Label %in% c('Frozen Meat Alternatives','Fresh Meat Alternatives'), 'Meat Alternatives', Label)) %>%
  mutate(Label = ifelse(Label %in% c('Fresh Vegetables','Frozen Vegetables & Herbs'), 'Vegetables', Label)) %>%
  mutate(Label = ifelse(Label %in% c('Frozen Pizza & Garlic Bread','Fresh Pizza, Pasta & Garlic Bread'), 'Pizza & Garlic Bread', Label)) %>%
  mutate(Label = ifelse(Label %in% c('Dried Pasta, Rice, Noodles & Cous Cous'), 'Dried Cereal Grains', Label)) %>%
  mutate(Label = ifelse(Label %in% c('Fresh Soup, Sandwiches & Salad Pots'), 'Soup, Sandwiches & Salad Pots', Label)) %>%
  mutate(Label = ifelse(Label %in% c('Frozen Party Food & Sausage Rolls'), 'Sausage Rolls &\nParty Food', Label)) %>%
  # mutate(Label = ifelse(Label %in% c('Croissants, Brioche & Pastries'), 'Pastries', Label)) %>%
  # mutate(Label = ifelse(Label %in% c('Crisps, Snacks & Popcorn'), 'Popcorn, Crisps & Snacks', Label)) %>%
  mutate(Label = ifelse(Label %in% c('Frozen Desserts, Ice Cream & Ice Lollies'), 'Frozen Desserts', Label)) %>%
  mutate(Label = ifelse(Label %in% c('Dried Fruit, Nuts, Nutrient Powders & Seeds'), 'Nuts, Dried Fruit & Nutrient Powders', Label)) %>%
  mutate(Label = ifelse(Label %in% c('Frozen Yorkshire Puddings & Stuffing'), 'Yorkshire Puddings', Label)) %>% 
  mutate(Label = ifelse(Label %in% c('Frozen Chips, Onion Rings, Potatoes & Rice'), 'Roasted Potatoes, Chips, Onion Rings, & Rice', Label)) %>% 
  mutate(Label = ifelse(Label %in% c('Jams, Sweet & Savoury Spreads'), 'Jams & Savoury Spreads', Label)) %>% 
  mutate(Label = ifelse(Label %in% c('Olives, Antipasti, Pickles & Chutneys'), 'Olives, Antipasti, Pickles & Chutney', Label)) %>%
  mutate(Label = ifelse(Label %in% c('Table Sauces, Marinades & Dressings'), 'Table Sauce, Marinade & Dressing', Label)) %>%
  # mutate(Label = ifelse(Label %in% c('Cakes, Cake Bars, Slices & Pies'), 'Cakes and Pies', Label)) %>%
  mutate(Label = ifelse(Label %in% c('Fresh Fruit and Nuts'), 'Fresh Fruit', Label)) %>%
  mutate(Label = ifelse(grepl('Dried Fruit.*Seed',Label), 'Nuts, Seeds, and Dried Fruit', Label)) %>%
  mutate(Label = ifelse(grepl('Gluten Free Range|World Food|Sausage.*Food',Label), ' ', Label)) %>%
  filter(Aisle != 'Bottled Water')

# Adding product types and colours
plot.dat.aisle <-
  plot.dat.aisle %>%
  mutate(Food_Type = ifelse(grepl('Drinks|Cordial|Juice|Tea|Coffee|Milkshake',Aisle),'Beverages',NA)) %>%
  mutate(Food_Type = ifelse(grepl('Dessert|Croissant|Teacakes|Cakes, Cake Bars|Sweets, Mints|Biscuits & Cereal Bars|Doughnuts',Aisle),'Desserts',Food_Type)) %>%
  mutate(Food_Type = ifelse(grepl('Jams,|Cooking Sauces|Table Sauces|Sugar &|Cooking Ingredients|Home Baking',Aisle), 'Cooking Accessories',Food_Type)) %>%
  mutate(Food_Type = ifelse(grepl('Cereal|From our Bakery|Bread &|Wraps, Pittas|Crumpets|Dried Pasta|Crackers',Aisle), 'Cereal Grains and Bread',Food_Type)) %>%
  mutate(Food_Type = ifelse(grepl('Meat|Counters|Cheese|Beef', Aisle), 'Dairy, Fish, and Meat', Food_Type)) %>%
  mutate(Food_Type = ifelse(grepl('Fish', Aisle), 'Dairy, Fish, and Meat', Food_Type)) %>%
  # mutate(Food_Type = ifelse(grepl('Chocolate|Coffee|Tea^[cake]|Hot Drinks',Aisle),'Chocolate, Coffee, and Tea',Food_Type)) %>%
  mutate(Food_Type = ifelse(grepl('Yoghurts|Milk, Butter|Milkshake|Ice Cream',Aisle),'Dairy, Fish, and Meat',Food_Type)) %>%
  mutate(Food_Type = ifelse(grepl('Vegetables|Salad|Fruit[^ L]|Nuts',Aisle),'Fruit, Vegetables, and Nuts',Food_Type)) %>%
  mutate(Food_Type = ifelse(grepl('Fresh Soup|Yorkshire|Pizza|Easy|Frozen Pies|Ready Meals|Pies, Quiches|Party Food|Tins, Cans|World Foods|Frozen Breakfast',Aisle),'Prepared Foods',Food_Type)) %>%
  mutate(Food_Type = ifelse(grepl('Gluten Free',Aisle),'Prepared Foods',Food_Type)) %>%
  mutate(Food_Type = ifelse(grepl('Meat Alternative|Dairy Alternative',Aisle),'Dairy, Fish, and Meat',Food_Type)) %>%
  mutate(Food_Type = ifelse(grepl('Frozen Chips|Popcorn|Olives|Chocolate', Aisle),'Snacks',Food_Type)) %>%
  # mutate(Food_Type = ifelse(Aisle %in% 'Tea','Chocolate, Coffee, and Tea', Food_Type)) %>%
  mutate(Food_Type = ifelse(Aisle %in% 'Fresh Fruit','Fruit, Vegetables, and Nuts', Food_Type)) %>%
  mutate(Food_Type = ifelse(Aisle %in% 'Bakery Free From','Cereal Grains and Bread', Food_Type)) %>%
  mutate(Food_Type = ifelse(Aisle %in% 'Free From Range','Cooking Accessories', Food_Type)) %>%
  mutate(Food_Type = ifelse(Aisle %in% 'Frozen Free From','Prepared Foods', Food_Type)) %>%
  mutate(Food_Type = ifelse(Aisle %in% 'Hot Chocolate & Malted Drinks','Beverages', Food_Type)) %>%
  mutate(Food_Type = ifelse(Aisle %in% 'Frozen Desserts, Ice Cream & Ice Lollies','Desserts', Food_Type)) %>%
  mutate(Food_Type = ifelse(Aisle %in% 'Biscuits & Cereal Bars','Desserts', Food_Type)) %>%
  mutate(Food_Type = ifelse(Aisle %in% 'Milkshake','Beverages', Food_Type)) %>%
  mutate(plot_colour = ifelse(Food_Type %in% 'Beverages','#0072b2', NA)) %>%
  # mutate(plot_colour = ifelse(Food_Type %in% 'Chocolate, Coffee, and Tea','#654321', plot_colour)) %>%
  mutate(plot_colour = ifelse(Food_Type %in% 'Cereal Grains and Bread','#e69f00', plot_colour)) %>%
  mutate(plot_colour = ifelse(Food_Type %in% 'Cooking Accessories','#000000', plot_colour)) %>%
  # mutate(plot_colour = ifelse(Food_Type %in% 'Plant-based alternatives','#4fa64f', plot_colour)) %>%
  mutate(plot_colour = ifelse(Food_Type %in% 'Fruit, Vegetables, and Nuts','#009e73', plot_colour)) %>%
  mutate(plot_colour = ifelse(Food_Type %in% 'Dairy, Fish, and Meat','#ed2939', plot_colour)) %>%
  # mutate(plot_colour = ifelse(Food_Type %in% 'Milk and Eggs','#a9a9a9', plot_colour)) %>%
  mutate(plot_colour = ifelse(Food_Type %in% 'Desserts','#cc79a7', plot_colour)) %>%
  mutate(plot_colour = ifelse(Food_Type %in% 'Prepared Foods','#d55e00', plot_colour)) %>%
  mutate(plot_colour = ifelse(Food_Type %in% 'Snacks','#b79268', plot_colour)) %>%
  # mutate(plot_colour = ifelse(Food_Type %in% 'Plant-based alternatives','#495e35', plot_colour)) %>%
  # mutate(plot_colour = ifelse(Food_Type %in% 'Gluten Free Range','#f6f2cd', plot_colour)) %>%
  mutate(plot_colour = ifelse(Food_Type %in% 'Seafood','#0072b2', plot_colour))


# Adding colour scale
my.palette <- c('#5f6ac1', # Blue
                '#6cad5e', # Green
                '#aa539e', # Purple
                '#bb8c3c', # Yellow/Orange
                '#ba494e') # Red

plot.dat.aisle <-
  plot.dat.aisle %>%
  mutate(colour_4 = ifelse(Tot_env_100g_scaled < median(Tot_env_100g_scaled,na.rm = TRUE) & mean_nutriscore < median(mean_nutriscore),my.palette[2],
                           ifelse(Tot_env_100g_scaled < median(Tot_env_100g_scaled,na.rm = TRUE) & mean_nutriscore >= median(mean_nutriscore),my.palette[1],
                                  ifelse(Tot_env_100g_scaled >= median(Tot_env_100g_scaled,na.rm = TRUE) & mean_nutriscore < median(mean_nutriscore),my.palette[4], my.palette[5])))) %>%
  mutate(grouping = ifelse(Tot_env_100g_scaled < median(Tot_env_100g_scaled, na.rm = TRUE) & mean_nutriscore < median(mean_nutriscore,na.rm = TRUE), 'Low_Low',
                           ifelse(Tot_env_100g_scaled < median(Tot_env_100g_scaled,na.rm = TRUE) & mean_nutriscore >= median(mean_nutriscore, na.rm = TRUE),'Low_High',
                                  ifelse(Tot_env_100g_scaled >= median(Tot_env_100g_scaled,na.rm = TRUE) & mean_nutriscore < median(mean_nutriscore, na.rm = TRUE),'High_Low','High_High'))))


# Looking for e.g. high impact products in low impact aisles
plot.dat <-
  plot.dat %>%
  mutate(upper_quantile_nut = ifelse(NutriScore_Scaled >= quantile(plot.dat.aisle$NutriScore_Scaled,2/3),'yes','no')) %>%
  mutate(upper_quantile_env = ifelse(Tot_env_100g_scaled >= quantile(plot.dat.aisle$Tot_env_100g_scaled,2/3),'yes','no')) %>%
  mutate(low_quantile_env = ifelse(Tot_env_100g_scaled <= quantile(plot.dat.aisle$Tot_env_100g_scaled,1/3),'yes','no'))

View(plot.dat %>% filter(Retailer %in% 'Tesco') %>%
       dplyr::select(product_name, Aisle, upper_quantile_env, low_quantile_env) %>%
       unique())

plot.dat.aisle <-
  plot.dat.aisle %>%
  arrange(Tot_env_100g_scaled) %>%
  mutate(rank_impact = 1:nrow(.))

# And plotting
ggplot(plot.dat.aisle %>% filter(Retailer %in% 'Tesco'), aes(x = mean_nutriscore, y = Tot_env_100g_scaled)) +
  theme_classic() +
  # geom_hline(yintercept = quantile(dat.fig3$Tot_env_100g_scaled,1/3, na.rm = TRUE), colour = 'grey', alpha = .5, linetype = 2) +
  # geom_hline(yintercept = quantile(dat.fig3$Tot_env_100g_scaled,2/3, na.rm = TRUE), colour = 'grey', alpha = .5, linetype = 2) +
  # geom_vline(xintercept = quantile(dat.fig3$NutriScore_Scaled,1/3, na.rm = TRUE), colour = 'grey', alpha = .5, linetype = 2) +
  # geom_vline(xintercept = quantile(dat.fig3$NutriScore_Scaled,2/3, na.rm = TRUE), colour = 'grey', alpha = .5, linetype = 2) +
  # geom_vline(xintercept = .34) +
  # geom_vline(xintercept = .52) +
  # geom_hline(yintercept = quantile(dat.fig3$Tot_env_100g_scaled,1/3, na.rm = TRUE), colour = 'grey', alpha = .5, linetype = 2) +
  # geom_hline(yintercept = quantile(dat.fig3$Tot_env_100g_scaled,2/3, na.rm = TRUE), colour = 'grey', alpha = .5, linetype = 2) +
  # geom_vline(xintercept = quantile(dat.fig3$NutriScore_Scaled,1/3, na.rm = TRUE), colour = 'grey', alpha = .5, linetype = 2) +
  # geom_vline(xintercept = quantile(dat.fig3$NutriScore_Scaled,2/3, na.rm = TRUE), colour = 'grey', alpha = .5, linetype = 2) +
  # geom_smooth(method = 'lm') +
# geom_text(aes(label = substr(Aisle,1,5))) +
  theme(axis.text = element_text(size = 7)) +
  theme(axis.title = element_text(size = 7)) +
  theme(legend.text = element_text(size = 7, hjust = 0)) +
  theme(legend.title = element_text(size = 7, hjust = 0)) +
  geom_point(dat = plot.dat.aisle %>% filter(Label %in% ' '), aes(x = mean_nutriscore, y = Tot_env_100g_scaled), alpha = .5, fill = plot.dat.aisle$colour_4[plot.dat.aisle$Label %in% ' '], colour = plot.dat.aisle$plot_colour[plot.dat.aisle$Label %in% ' ']) +
  geom_text_repel(aes(label = Label), size = 2.75, box.padding = 0.075, point.padding = 0.075, colour = plot.dat.aisle$plot_colour) +
  # scale_x_continuous(limits = c(10,70), expand = c(0,0)) +
  scale_x_continuous(expand = c(0,0), limits = c(.75,5.25),breaks = 1:5, labels = c('A','B','C','D','E')) +
  scale_y_continuous(trans = 'log10', limits = c(.15, 40), expand = c(0,0)) +
  # scale_y_continuous(trans = 'log10') +
  labs(x = 'Nutrition Impact Score', y = 'Environmental Impact Score')

Sys.sleep(10)
ggsave(paste0(getwd(),"/Figures/Fig 4 Impacts 100g Aisles NutriScoreLetter 6Feb2022.pdf"),
       width = 18.2, height = 14, units = 'cm')

# Saving data files
if(!('Figure Data' %in% list.files(getwd()))) {
  dir.create(paste0(getwd(),'/Figure Data'))
}

write.csv(plot.dat.aisle %>% dplyr::select(Aisle, Tot_env_100g_scaled, NutriScore_Scaled = mean_nutriscore, Colour = colour_4),
          paste0(getwd(),'/Figure Data/Data Fig 4 6Feb2022.csv'), row.names = FALSE)

# setOptions("ggrepel.max.overlaps", default = 50)

plot.dat.aisle1 <-
  plot.dat.aisle %>%
  mutate(Label = ifelse(grepl('hot.*choc',Aisle, ignore.case=TRUE),'Hot Chocolate',Label)) %>%
  mutate(Label = ifelse(grepl('bakery free from',Aisle, ignore.case=TRUE),'Gluten Free Bakery',Label)) %>%
  mutate(Label = ifelse(grepl('crack.*crisp',Aisle, ignore.case=TRUE),Aisle,Label)) %>%
  mutate(Label = ifelse(grepl('dried pasta',Aisle, ignore.case=TRUE),'Dried Cereal Grains',Label)) %>%
  mutate(Label = ifelse(grepl('frozen.*sausage.*roll',Aisle, ignore.case=TRUE),'Party Food & Sausage Rolls',Label)) %>%
  mutate(Label = ifelse(grepl('yorkshire',Aisle, ignore.case=TRUE),'Yorkshire Puddings',Label)) %>%
  mutate(Label = ifelse(grepl('frozen.*dessert',Aisle, ignore.case=TRUE),'Frozen Desserts',Label)) %>%
  mutate(Label = ifelse(grepl('dried.*fruit.*seed',Aisle, ignore.case=TRUE),'Dried Fruit, Nuts & Nutrient Powders',Label)) %>%
  mutate(Label = ifelse(grepl('our.*bakery|cook.*ingredi|home.*bak|sug.*swe|cake.*bar.*pie|chil.*dess|sweet.*mint|easy.*ent|
                              frozen.*halal|gluten.*range|tin.*pack|crisp.*popcorn',Aisle, ignore.case=TRUE),Aisle,Label)) %>% 
  mutate(Label = ifelse(Aisle %in% 'Desserts',Aisle,Label)) %>%
  mutate(Label = ifelse(Aisle %in% 'World Foods',Aisle,Label)) %>%
  mutate(Label = ifelse(Aisle %in% 'Fresh Fruit',Aisle,Label))
  

ggplot(plot.dat.aisle1 %>% filter(Retailer %in% 'Tesco'), aes(x = mean_nutriscore, y = Tot_env_100g_scaled)) +
  theme_classic() +
  # geom_hline(yintercept = quantile(dat.fig3$Tot_env_100g_scaled,1/3, na.rm = TRUE), colour = 'grey', alpha = .5, linetype = 2) +
  # geom_hline(yintercept = quantile(dat.fig3$Tot_env_100g_scaled,2/3, na.rm = TRUE), colour = 'grey', alpha = .5, linetype = 2) +
  # geom_vline(xintercept = quantile(dat.fig3$NutriScore_Scaled,1/3, na.rm = TRUE), colour = 'grey', alpha = .5, linetype = 2) +
  # geom_vline(xintercept = quantile(dat.fig3$NutriScore_Scaled,2/3, na.rm = TRUE), colour = 'grey', alpha = .5, linetype = 2) +
  # geom_vline(xintercept = .34) +
  # geom_vline(xintercept = .52) +
  # geom_hline(yintercept = quantile(dat.fig3$Tot_env_100g_scaled,1/3, na.rm = TRUE), colour = 'grey', alpha = .5, linetype = 2) +
  # geom_hline(yintercept = quantile(dat.fig3$Tot_env_100g_scaled,2/3, na.rm = TRUE), colour = 'grey', alpha = .5, linetype = 2) +
  # geom_vline(xintercept = quantile(dat.fig3$NutriScore_Scaled,1/3, na.rm = TRUE), colour = 'grey', alpha = .5, linetype = 2) +
  # geom_vline(xintercept = quantile(dat.fig3$NutriScore_Scaled,2/3, na.rm = TRUE), colour = 'grey', alpha = .5, linetype = 2) +
  # geom_smooth(method = 'lm') +
# geom_text(aes(label = substr(Aisle,1,5))) +
  theme(axis.text = element_text(size = 7)) +
  theme(axis.title = element_text(size = 7)) +
  theme(legend.text = element_text(size = 7, hjust = 0)) +
  theme(legend.title = element_text(size = 7, hjust = 0)) +
  # geom_point(dat = plot.dat.aisle %>% filter(Label %in% ' '), aes(x = mean_nutriscore, y = Tot_env_100g_scaled), alpha = .5, fill = plot.dat.aisle$colour_4[plot.dat.aisle$Label %in% ' '], colour = plot.dat.aisle$plot_colour[plot.dat.aisle$Label %in% ' ']) +
  geom_text_repel(aes(label = Label), box.padding = 0.35, point.padding = 0.35, size = 2.5, colour = plot.dat.aisle$plot_colour, max.overlaps = 50) +
  # scale_x_continuous(limits = c(10,70), expand = c(0,0)) +
  scale_x_continuous(expand = c(0,0), limits = c(.75,5.25),breaks = 1:5, labels = c('A','B','C','D','E')) +
  scale_y_continuous(trans = 'log10', limits = c(.15, 40), expand = c(0,0)) +
  # scale_y_continuous(trans = 'log10') +
  labs(x = 'Nutrition Impact Score', y = 'Environmental Impact Score') +
  facet_wrap(.~Food_Type)

Sys.sleep(10)
# ggsave(paste0(getwd(),"/Figures/Fig S15 Impacts 100g Aisles NutriScoreLetter Faceted 6Feb2022.pdf"),
#        width = 30, height = 30, units = 'cm')
