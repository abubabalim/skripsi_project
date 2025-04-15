from pandas import DataFrame
import pandas as pd

class AnalysisResults:
    def __init__(self):
        self._basket = DataFrame()
        self._itemsets = DataFrame()
        self._rules = DataFrame()
        self._items = DataFrame()
        self._transactions = DataFrame()
        self._support = 0.0
        self._confidence = 0.0
        
    @property
    def basket(self):
        return self._basket
    
    @basket.setter
    def basket(self, df):
        self._basket = df
        
    @property
    def itemsets(self):
        return self._itemsets
    
    @itemsets.setter
    def itemsets(self, df):
        self._itemsets = df
        
    @property
    def rules(self):
        return self._rules
    
    @rules.setter
    def rules(self, df):
        self._rules = df
        
    @property
    def items(self):
        return self._items
    
    @items.setter
    def items(self, df):
        self._items = df
        
    @property
    def transactions(self):
        return self._transactions
    
    @transactions.setter
    def transactions(self, df):
        self._transactions = df
        
    @property
    def support(self):
        return self._support
    
    @support.setter
    def support(self, sup):
        self._support = sup
        
    @property
    def confidence(self):
        return self._confidence
    
    @confidence.setter
    def confidence(self, conf):
        self._confidence = conf
        
    
    
    
    