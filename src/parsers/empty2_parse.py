# -*- coding: utf-8 -*-
from datetime import datetime 
from lxml import html
import models

class Parser():
    site_name = '' # empty
    site_url = '' # empty
    index_url = '{}'.format(site_url) # empty
    content_links_on_page = 16
    start_index = 1
    
    def __init__(self, max_content_pages = False):
        self.max_content_pages = max_content_pages
        if self.max_content_pages:
            self.extens_i = int(self.max_content_pages/self.content_links_on_page) + self.start_index
        else:
            self.extens_i = 24 + self.start_index
            
        self.index_urls = []
        for i in range(self.start_i,self.extens_i):
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

            self.content_urls.extend([self.site_url+item.getchildren()[0].attrib['href'] for item in root.find_class('recipe-image')])
            
    def get_content(self, filenames, session):
        for filename in filenames:
            recipe = {}
            recipe_ingredients = {}
            recipe_directions = {}
            recipe_tags = {}
                        
            root = html.parse(filename).getroot()
            
            #Recipe object 
            recipe['title'] = unicode(root.find_class('title fn')[0].text)
            recipe['expl'] = unicode(root.find_class('subhead')[0].text)
            tmp_desc = root.find_class('')[0].getchildren()[0].getchildren()[0].getchildren()[:-1] # empty
            recipe['desc'] = unicode('\n\n'.join([d.text_content() for d in tmp_desc]))
            try:
                tmp_serving = root.find_class('')[0].getchildren()[0].getchildren()[1].text.split(' ', 1) # empty
                recipe['serving'] = int(tmp_serving[0])
                recipe['serving_measure'] = unicode(tmp_serving[1].strip())
            except:
                recipe['serving'] = None
                recipe['serving_measure'] = None
            try:
                recipe['difficulty'] = unicode(root.find_class('')[0].getchildren()[1].text_content().strip()) # empty
            except:
                recipe['difficulty'] = None
            try:
                tmp_prep_time = root.find_class('')[0].getchildren()[1].text_content().strip().split(' ', 1) # empty
                recipe['prep_time'] = int(tmp_prep_time[0])
                recipe['prep_time_measure'] = unicode(tmp_prep_time[1])
            except:
                recipe['prep_time'] = None
                recipe['prep_time_measure'] = None
            try:
                tmp_cooking_time = root.find_class('')[0].getchildren()[1].text_content().strip().split(' ', 1) # empty
                recipe['cooking_time'] = int(tmp_cooking_time[0])
                recipe['cooking_time_measure'] = unicode(tmp_prep_time[1])
            except:
                recipe['cooking_time'] = None
                recipe['cooking_time_measure'] = None
            recipe['language'] = 1
            recipe['added'] = datetime.now()
             
            #RecipeIngredients objects 
            all_recipe_ingredients = []
            recipe_ingredients['subtitle'] = unicode('base')
            tmp_ingrediends = root.find_class('')[0].getchildren()[1].getchildren() # empty
            for ingr in tmp_ingrediends:
                recipe_ingredients['food'] = None
                recipe_ingredients['quantity'] = None
                recipe_ingredients['measure'] = None
                if ingr.tag == 'fieldset':
                    for i in ingr.getchildren():
                        if i.tag == 'legend':
                            recipe_ingredients['subtitle'] = unicode(i.text.strip())
                        elif i.tag == 'div':
                            for ii in i.getchildren():
                                if 'class' in ii.attrib:
                                    if ii.attrib['class'] == 'amount':
                                        tmp_amount = ii.text.strip().split(' ', 1)
                                        try:
                                            if tmp_amount[0][0].isdigit():
                                                recipe_ingredients['quantity'] = unicode(tmp_amount[0])
                                                recipe_ingredients['measure'] = unicode(tmp_amount[1])
                                            else:
                                                raise
                                        except:
                                            recipe_ingredients['quantity'] = None
                                            recipe_ingredients['measure'] = unicode(' '.join(tmp_amount))
                                    elif ii.attrib['class'] == 'name':
                                        recipe_ingredients['food'] = unicode(ii.text.strip())
                else:
                    for i in ingr.getchildren():
                        if 'class' in i.attrib:
                            if i.attrib['class'] == 'amount':
                                tmp_amount = i.text.strip().split(' ', 1)
                                try:
                                    if tmp_amount[0][0].isdigit():
                                            recipe_ingredients['quantity'] = unicode(tmp_amount[0])
                                            recipe_ingredients['measure'] = unicode(tmp_amount[1])
                                    else:
                                        raise
                                except:
                                    recipe_ingredients['quantity'] = None
                                    recipe_ingredients['measure'] = unicode(' '.join(tmp_amount))
                            elif i.attrib['class'] == 'name':
                                recipe_ingredients['food'] = unicode(i.text.strip())
                                
                all_recipe_ingredients.append(models.RecipeIngredients(**recipe_ingredients))

            #RecipeDirections objects
            all_recipe_directions = []
            tmp_directions = root.find_class('')[0].getchildren()[1].getchildren()[0].getchildren() # empty
            ol_tag_first = False 
            if tmp_directions[0].tag == 'ol':
                ol_tag_first = True
            for d in tmp_directions:
                if d.tag == 'p':
                    recipe_directions['subtitle'] = unicode(d.text_content().strip())
                elif d.tag == 'ol':
                    for order, ol_child in enumerate(d.getchildren()):
                        if ol_child.tag == 'li':
                            recipe_directions['order'] = order + 1
                            recipe_directions['desc'] = unicode(ol_child.text_content().strip())
                            if ol_tag_first:
                                recipe_directions['subtitle'] = unicode('base')
                            all_recipe_directions.append(models.RecipeDirections(**recipe_directions))
                        

            #RecipeTags objects
            all_recipe_tags = []
            tmp_tags = root.find_class('tags')[0].getchildren()[0].getchildren()
            for tag in tmp_tags:
                recipe_tags['tag_name'] = tag.getchildren()[0].text.strip().lower()
                all_recipe_tags.append(models.RecipeTags(**recipe_tags))
            
            recipe['recipe_ingredients'] = all_recipe_ingredients
            recipe['recipe_directions'] = all_recipe_directions
            recipe['recipe_tags'] = all_recipe_tags
            
            yield models.Recipe(**recipe)
