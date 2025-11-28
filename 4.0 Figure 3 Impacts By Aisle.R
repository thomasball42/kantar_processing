###
# Fig 3
# Impacts by Aisle for Tesco

# libraries
library(plyr)
library(dplyr)
library(ggplot2)
library(readr)
library(cowplot)

# Working directory
setwd("/Volumes/Citadel/Clark_et_al_2022_PNAS_SM")

# data
plot.dat <- read_csv(paste0(getwd(),"/Managed_Data/Impacts by Product 18Feb2022 Log2.csv"))

# Aggregating
plot.dat.aisle <-
  plot.dat %>%
  filter(Retailer %in% 'Tesco') %>%
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
                                     'Cooking Suaces & Meal Kits','Crisps, Snacks & Popcorn','Crackers & Crispbreads','Cakes, Cake Bars, Slices & Pies'), ' ', Label)) %>%
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
  filter(Aisle != 'Bottled Water')


# Clustering analysis if you want to do this
# cluster.df <- plot.dat.aisle[,grepl('mean_[^nut]',names(plot.dat.aisle))]
# cluster.df <- scale(cluster.df)
# # Getting optimal number of clusters
# fviz_nbclust(cluster.df, FUNcluster = kmeans)
# tmp <- kmeans(cluster.df, 8)
# plot.dat.aisle$cluster <- tmp$cluster

# Adding product type
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


# Ordering impacts by Aisle
# Average impacts by category
dat.avg <- 
  plot.dat.aisle %>%
  group_by(Food_Type) %>%
  dplyr::summarise(env = mean(Tot_env_100g_scaled),
                   env_min = min(Tot_env_100g_scaled),
                   env_median = median(Tot_env_100g_scaled)) %>%
  arrange(env_median)

plot.dat.aisle <- 
  plot.dat.aisle %>% 
  transform(Food_Type = factor(Food_Type, levels = dat.avg$Food_Type)) %>%
  arrange(Food_Type, Tot_env_100g_scaled) %>%
  mutate(Aisle = ifelse(Label %in% ' ' | is.na(Label),Aisle,Label)) %>%
  transform(Aisle = factor(Aisle, levels = .$Aisle))

# Getting lowest impact aisles
dat.low <- plot.dat.aisle[1:10,]
# Getting other aisles
dat.other <-
  plot.dat.aisle[11:nrow(plot.dat.aisle),] %>%
  mutate(panel_num = rank(Tot_env_100g_scaled, ties.method = 'first')) %>%
  mutate(panel_num = ifelse(panel_num < nrow(.)/2,1,2)) #
                            # ifelse(panel_num <= (nrow(.)/6)*2,2,
                            #        ifelse(panel_num <= (nrow(.)/6)*3,3,
                            #               ifelse(panel_num <= (nrow(.)/6)*4,4,
                            #                      ifelse(panel_num <= (nrow(.)/6)*5,5,6))))))

out.dat <- data.frame()
  tmp.dat <- 
    rbind(dat.low,dat.other %>% dplyr::select(-panel_num)) %>%
    # mutate(Aisle = ifelse(Label != ' ',Label, Aisle)) %>%
    mutate(Retailer_Department_Aisle = paste0(Aisle)) %>%
    transform(Retailer_Department_Aisle = factor(Retailer_Department_Aisle, levels = plot.dat.aisle$Aisle)) %>%
    # mutate(panel_num = i) %>%
    mutate(position_x = 1:nrow(.))
  
  out.dat <- rbind(out.dat, tmp.dat)
  
    out.plot <-
      ggplot(tmp.dat, aes(x = Retailer_Department_Aisle, y = Tot_env_100g_scaled, Food_Type)) +
      theme_classic() +
      geom_point(alpha = .75, colour = tmp.dat$plot_colour) +
      # geom_point(alpha = .5) +
    # geom_errorbar(aes(ymin = (Tot_env_100g_scaled-Tot_env_100g_scaled_se), ymax = (Tot_env_100g_scaled+Tot_env_100g_scaled_se)), colour = tmp.dat$colour, alpha = .5) +
      geom_errorbar(aes(ymin = (Tot_env_100g_scaled-Tot_env_100g_scaled_se), ymax = (Tot_env_100g_scaled+Tot_env_100g_scaled_se)), alpha = .75, colour = tmp.dat$plot_colour) +
    # geom_point(aes(y = overlap),shape = 8, colour = 'black') +
    # geom_point(aes(x = Department_Aisle_Shelf, y = scaled_tot_env), colour = 'blue') +
    # geom_errorbar(aes(ymin = scaled_tot_env_lower, ymax = scaled_tot_env_upper), colour = 'blue') +
    # scale_x_discrete(labels = substr(tmp.dat$Aisle,1,10)) +
      # scale_x_discrete(labels = substr(tmp.dat$Aisle,1,20)) +
      scale_colour_manual(values = unique(tmp.dat$plot_colour)) +
      # scale_colour_manual(values = sort(unique(dat.other$colour[dat.other$Retailer %in% tmp.dat$Retailer]))) +
    # scale_y_continuous(trans = 'log10') +
    # theme(legend.position = NULL) +
      theme(axis.text.x = element_text(angle = 90, hjust = 1, vjust = .5, size = 6)) +
      labs(x = NULL,y = 'Environmental Impact Score', colour = NULL) +
      # geom_vline(xintercept = 10, linetype = 2) +
      theme(legend.position = 'bottom') +
      # scale_y_continuous(trans = 'log2')
      coord_cartesian(ylim = c(0,40), expand = FALSE)
    # 
    # ggplot(tmp.dat, aes(x = Retailer_Department_Aisle, y = Tot_env_100g_scaled, Food_Type)) +
    #   theme_classic() +
    #   geom_point(alpha = .75, colour = tmp.dat$plot_colour) +
    #   # geom_point(alpha = .5) +
    #   # geom_errorbar(aes(ymin = (Tot_env_100g_scaled-Tot_env_100g_scaled_se), ymax = (Tot_env_100g_scaled+Tot_env_100g_scaled_se)), colour = tmp.dat$colour, alpha = .5) +
    #   geom_errorbar(aes(ymin = (Tot_env_100g_scaled-Tot_env_100g_scaled_se), ymax = (Tot_env_100g_scaled+Tot_env_100g_scaled_se)), alpha = .75, colour = tmp.dat$plot_colour) +
    #   # geom_point(aes(y = overlap),shape = 8, colour = 'black') +
    #   # geom_point(aes(x = Department_Aisle_Shelf, y = scaled_tot_env), colour = 'blue') +
    #   # geom_errorbar(aes(ymin = scaled_tot_env_lower, ymax = scaled_tot_env_upper), colour = 'blue') +
    #   # scale_x_discrete(labels = substr(tmp.dat$Aisle,1,10)) +
    #   scale_x_discrete(labels = substr(tmp.dat$Aisle,1,20)) +
    #   scale_colour_manual(values = unique(tmp.dat$plot_colour)) +
    #   # scale_colour_manual(values = sort(unique(dat.other$colour[dat.other$Retailer %in% tmp.dat$Retailer]))) +
    #   # scale_y_continuous(trans = 'log10') +
    #   # theme(legend.position = NULL) +
    #   theme(axis.text.x = element_text(angle = 90, hjust = 1, vjust = .5, size = 6)) +
    #   labs(x = NULL,y = 'Environmental Impact Score', colour = NULL) +
    #   geom_vline(xintercept = 10, linetype = 2) +
    #   theme(legend.position = 'bottom') +
    #   coord_cartesian(ylim = c(0,40), expand = FALSE)

# ggplot(out.dat, aes(x = position_x, y = Tot_env_100g_scaled, colour = Retailer)) +
#   theme_classic() +
#   # geom_point(alpha = .5, colour = tmp.dat$colour) +
#   geom_point(alpha = .5) +
#   # geom_errorbar(aes(ymin = (Tot_env_100g_scaled-Tot_env_100g_scaled_se), ymax = (Tot_env_100g_scaled+Tot_env_100g_scaled_se)), colour = tmp.dat$colour, alpha = .5) +
#   geom_errorbar(aes(ymin = (Tot_env_100g_scaled-Tot_env_100g_scaled_se), ymax = (Tot_env_100g_scaled+Tot_env_100g_scaled_se)), alpha = .5) +
#   # geom_point(aes(y = overlap),shape = 8, colour = 'black') +
#   # geom_point(aes(x = Department_Aisle_Shelf, y = scaled_tot_env), colour = 'blue') +
#   # geom_errorbar(aes(ymin = scaled_tot_env_lower, ymax = scaled_tot_env_upper), colour = 'blue') +
#   # scale_x_discrete(labels = substr(tmp.dat$Aisle,1,10)) +
#   scale_x_continuous(breaks = out.dat$position_x,labels = substr(out.dat$Aisle,1,20)) +
#   scale_colour_manual(values = unique(tmp.dat$colour)) +
#   # scale_y_continuous(trans = 'log10') +
#   theme(legend.position = NULL) +
#   theme(axis.text.x = element_text(angle = 90, hjust = 1, vjust = 0, size = 6)) +
#   labs(x = NULL,y = 'Environmental Impact Score', colour = NULL) +
#   geom_vline(xintercept = 10, linetype = 2) +
#   theme(legend.position = 'bottom') +
#   facet_wrap(.~panel_num, nrow = 5, scales = 'free_y')


dev.off()
out.plot

# Sys.sleep(15)

ggsave(paste0(getwd(),'/Figures/Figure 3 Impacts by Aisle 6Feb2022.pdf'),
       width = 7.2, height = 5, units = 'in')

# And saving data
if(!('Figure Data' %in% list.files(getwd()))) {
  dir.create(paste0(getwd(),'/Figure Data'))
}

write.csv(rbind(tmp.dat %>% dplyr::select(Aisle, Food_Type, plot_colour, Tot_env_100g_scaled, Tot_env_100g_scaled_se),dat.other %>% dplyr::select(Aisle,Food_Type, plot_colour, Tot_env_100g_scaled, Tot_env_100g_scaled_se)) %>% unique(.),
          paste0(getwd(),'/Figure Data/Data Fig 3 6Feb2022.csv'),row.names = FALSE)

