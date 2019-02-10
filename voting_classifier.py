#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 10 00:07:37 2019

@author: evrardgarcelon
"""

import numpy as np

class VotingClassifier(object) :
    
    def __init__(self,base_classifiers,weights = None, hard_pred = False) :
        
        self.base_classifiers = base_classifiers
        self.n_clfs = len(self.base_classifiers)
        if weights is None :
            self.weights = 1/self.n_clfs
        else :
            if np.sum(weights) != 1. :
                raise Exception('Error weights do not sum to 1')
            self.weights = weights
        self.hard_pred = hard_pred
        
    def predict(self,X) :
        
        n_test,_ = X.shape 
        predictions_base_clfs = np.zeros((n_test,self.n_clfs))
        for j in range(self.n_clfs) :
            if self.hard_pred :
                predictions_base_clfs[:,j] = self.base_classifiers[j].predict(X)
            else :
                predictions_base_clfs[:,j] = self.base_classifiers[j].predict_proba(X)
        predictions = np.average(predictions_base_clfs, axis = 1, weights = self.weights)
        return 1*(predictions >= 1/2)
    
    def score(self,X,y) :
        predictions = self.predict(X)
        return np.sum(y == predictions)/X.shape[0]
    
    def recall_and_precision(self,X,y) :
        y = self.transform_label(y)
        predictions = self.predict(X).astype('int')
        tp = np.sum((predictions == 1)*(y == 1))
        fn = np.sum((predictions == -1)*(y == 1))
        fp = np.sum((predictions == 1)*(y == -1))
        return tp/(fn+tp),tp/(fp+tp)

        
        
            