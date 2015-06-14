# -*- coding: utf-8 -*-
from datetime import datetime 
from lxml import html
import models

class Parser():
    site_name = '' # empty
    site_url = '' # empty
    index_url = '{}'.format(site_url) # empty
    content_links_on_page = 60
    start_index = 1
    
    def __init__(self, max_content_pages = False):
        self.max_content_pages = max_content_pages
        if self.max_content_pages:
            self.extens_i = int(self.max_content_pages/self.content_links_on_page) + self.start_index
        else:
            self.extens_i = 24 + self.start_index
            
        self.index_urls = []
        for i in range(self.start_index,self.extens_i):
            self.index_urls.append(self.index_url+str(i))
        
    def set_start_index(self, start_index):
        self.start_index = start_index
            
    def get_index_urls(self):
        return self.index_urls
    
    def get_work_name(self):
        return self.site_name
    
    def get_content_urls(self, filenames = []):
        self.index_filenames = filenames
        self._parse_index_pages()
        
        return self.content_urls
    
    def _parse_index_pages(self):
        self.content_urls = []
        for filename in self.index_filenames:
            root = html.parse(filename).getroot()

            self.content_urls.extend([self.site_url+item.getchildren()[0].attrib['href'] for item in root.find_class('grid_4 view')])
            
    def get_content(self, filenames, session):
        for filename in filenames:
            food = {}
            food_text = {}
             
                        
            root = html.parse(filename).getroot()
            #Food object
            breadcrumbs = root.find_class('breadcrumbs')[0].getchildren()
            food['name'] = unicode(breadcrumbs[-1].text)
#             if session.query(models.Food).filter(models.Food.name==food['name']).count():
#                 print(food['name']+u' is exist')
#                 continue
            food['eng_name'] = ''
            food['category'] = unicode(breadcrumbs[-2].text)
            content = root.get_element_by_id('content')
            calories = content.getchildren()[3].getchildren()
            food['calories'] = float(calories[0].text.split(':')[1].split()[0])
            tmp = calories[2].text_content().strip()
            try:
                food['protein'] = float(tmp.split('\n')[0].split(':')[1].split()[0])
            except:
                food['protein'] = float(0.0)
            try:
                food['fat'] = float(tmp.split('\n')[1].split(':')[1].split()[0])
            except:
                food['fat'] = float(0.0)
            try:
                food['carb'] = float(tmp.split('\n')[2].split(':')[1].split()[0])
            except:
                food['carb'] = float(0.0)
                
            price = root.find_class('grid_6')[1]
            food['average_price'] = float(price.text.split()[0])
            counting = root.find_class('grid_13')[0]
                
            #select lowest value        
            actual_counting = []
            if len(counting.text_content().strip().split('        ')) > 1:
                for count in counting.text_content().strip().split('        '):
                    tmp = count.split('    ')
                    if len(tmp) > 1 :
                        actual_counting.extend(tmp)
                    else:
                        actual_counting.extend(tmp)
            else:
                actual_counting = counting.text_content().strip().split('   ')
            prev = []
            if not len(actual_counting) or not len(actual_counting[0]):
                food['counting'] = None
            elif len(actual_counting) == 1:
                food['counting'] = actual_counting[0].split()[-2]
            else:
                for co in actual_counting:
                    if co:
                        if not prev:
                            prev = co.split()[-2]
                            continue
                        current = co.split()[-2]
                        food['counting'] = [current, prev][prev < current]
                        prev = current
                            
            food['added'] = datetime.now()
             
            #FoodText objects
            all_p_tags = []
            after_div_attrib = False
            in_text = False
            for elem in content.getchildren():
                if after_div_attrib:
                    if elem.tag == 'div' and not in_text:
                        continue
                    if elem.tag == 'p':
                        in_text = True
                    if in_text:
                        if elem.tag == 'div':
                            break
                        all_p_tags.append(elem)
                            
                if 'class' in elem.attrib:
                    if elem.attrib['class'] == 'grid_16':
                        after_div_attrib = True        
            all_text = []
            tmp_text = []        
            for p_tag in all_p_tags:
                if p_tag.getchildren():
                    if p_tag.getchildren()[0].tag == 'a':
                        tmp_text.append(p_tag.text_content().strip())
                    elif p_tag.getchildren()[0].tag == 'em':
                        food_text['text'] = unicode('\n'.join(tmp_text))
                        all_text.append(models.FoodText(**food_text))
                        food_text = {}
                        tmp_text = []
                        food_text['header'] = unicode(p_tag.getchildren()[0].text_content().strip())
                    elif p_tag.tag == 'ul':
                        for li in p_tag.getchildren():
                            tmp_text.append(li.text_content().strip())
                else:
                    tmp_text.append(p_tag.text.strip())
                        
            food_text['text'] = unicode('\n'.join(tmp_text))
              
            all_text.append(models.FoodText(**food_text))
            food['food_text'] = all_text
             
            #FoodContent objects
            all_food_context = set()
            content_type = {'nutrition': 1,'vitamin': 2, 'mineral': 3}
            for noindex_elem in root.xpath('/html/body/div/div[5]/div[2]/div/noindex'):
                if noindex_elem.getprevious().text == u'': # empty
                    nutrition_divs = noindex_elem.getchildren()
                    for nutrition in nutrition_divs:
                        (nutrition_name, quantity) = [n.text for n in nutrition.getchildren()]
                        nutrition_params = nutrition_name.split()
                                               
                        quantity, measure = quantity.split()       
                           
                        all_food_context.add(models.FoodContent(name=unicode(nutrition_params[0]), 
                                                        chem_name=None, 
                                                        quantity=float(quantity), 
                                                        measure=unicode(measure),
                                                        type=content_type['nutrition']))
                elif noindex_elem.getprevious().text == u'': # empty
                    vitamin_divs = noindex_elem.getchildren()
                    for vitamin in vitamin_divs:
                        (vitamin_name, quantity) = [v.text for v in vitamin.getchildren()]
                        vitamin_params = vitamin_name.split()
                        quantity, measure = quantity.split()
                                      
                        if len(vitamin_params) > 1:
                            all_food_context.add(models.FoodContent(name=unicode(' '.join(vitamin_params[:2])), 
                                                             chem_name=unicode(vitamin_params[2][1:-1]), 
                                                             quantity=float(quantity),
                                                            measure=unicode(measure),
                                                             type=content_type['vitamin']))
                        elif len(vitamin_params) == 1:
                            all_food_context.add(models.FoodContent(name=unicode(vitamin_params[0]), 
                                                             chem_name=None, 
                                                             quantity=float(quantity),
                                                             measure=unicode(measure),
                                                             type=content_type['vitamin']))
                elif noindex_elem.getprevious().text == u'': # empty
                    mineral_divs = noindex_elem.getchildren()
                    for mineral in mineral_divs:
                        (mineral_name, quantity) = [m.text for m in mineral.getchildren()]
                        mineral_params = mineral_name.split()
                        measure = quantity.split()[1]
                        quantity = float(quantity.split()[0])            
                           
                        all_food_context.add(models.FoodContent(name=unicode(mineral_params[0]), 
                                                        chem_name=unicode(mineral_params[1][1:-1]), 
                                                        quantity=quantity, 
                                                        measure=unicode(measure),
                                                        type=content_type['mineral']))
            food['food_content'] = list(all_food_context)

            yield models.Food(**food)

