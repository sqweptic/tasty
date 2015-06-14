# -*- coding: utf-8 -*-
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import relation, relationship, backref
import config as cfg

Base = declarative_base()    

class Food(Base):
    __tablename__ = 'food'
     
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(length=100), unique=True)
    eng_name = Column(String(length=100), nullable=True)
    calories = Column(Float, nullable=True)
    protein = Column(Float, nullable=True)
    fat = Column(Float, nullable=True)
    carb = Column(Float, nullable=True)
    category = Column(Unicode(length=100), nullable=True)
    average_price = Column(Float, nullable=True)
    counting = Column(Float, nullable=True)
    added = Column(DateTime)

    def __repr__(self):
        return "Food: '{!s}'".format(self.name)
        
        
class FoodText(Base):
    __tablename__ = 'food_text'
    
    id = Column(Integer, primary_key=True)
    food_id = Column(Integer, ForeignKey('food.id'))
    food = relationship("Food", backref=backref('food_text'))
    header = Column(Unicode(length=100), nullable=True, default=u'Описание')
    text = Column(UnicodeText, nullable=True)

class FoodContent(Base):
    __tablename__ = 'food_content'
    
    id = Column(Integer, primary_key=True)
    food_id = Column(Integer, ForeignKey('food.id'))
    food = relationship("Food", backref=backref('food_content'))
    name = Column(Unicode(length=40), nullable=True)
    chem_name = Column(Unicode(length=40), nullable=True)
    quantity = Column(Float, nullable=True)
    measure = Column(Unicode(length=20), nullable=True)
    type = Column(Integer, nullable=True)
    

class Recipe(Base):
    __tablename__ = 'recipe'
    
    id = Column(Integer, primary_key=True)
    title = Column(Unicode(length=100), unique=True)
    expl = Column(Unicode(length=200), nullable=True)
    desc = Column(UnicodeText, nullable=True)
    serving = Column(Integer, nullable=True)
    serving_measure = Column(Unicode(length=100), nullable=True)
    difficulty = Column(Unicode(length=50), nullable=True)
    prep_time = Column(Integer, nullable=True)
    prep_time_measure = Column(Unicode(length=100), nullable=True)
    cooking_time = Column(Integer, nullable=True)
    cooking_time_measure = Column(Unicode(length=100), nullable=True)
    language = Column(Integer, nullable=True)
    added = Column(DateTime)
    
class RecipeIngredients(Base):
    __tablename__ = 'recipe_ingredients'
    
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipe.id'))
    recipe = relationship("Recipe", backref=backref('recipe_ingredients'))
    subtitle = Column(Unicode(length=200), nullable=True)
    quantity = Column(Unicode(length=30), nullable=True)
    measure = Column(Unicode(length=100), nullable=True)
    food = Column(Unicode(length=300), nullable=True)
    
    
    
class RecipeDirections(Base):
    __tablename__ = 'recipe_directions'
    
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipe.id'))
    recipe = relationship("Recipe", backref=backref('recipe_directions'))
    subtitle = Column(Unicode(length=200), nullable=True)
    order = Column(Integer, nullable=True)
    desc = Column(UnicodeText, nullable=True)
    
    
class RecipeTags(Base):
    __tablename__ = 'recipe_tags'
    
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipe.id'))
    recipe = relationship("Recipe", backref=backref('recipe_tags'))
    tag_name = Column(Unicode(length=200), nullable=True)
        
    
    
if __name__ == '__main__':
    engine = create_engine(cfg.MYSQL_CONNECTION, echo=False, encoding='utf8')
    engine.execute("CREATE DATABASE {} DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;".format(cfg.MYSQL_DBNAME))
    engine.execute('USE {}'.format(cfg.MYSQL_DBNAME))
    
    Base.metadata.create_all(engine)
    