#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  2 13:04:11 2017

@author: jaume
"""

### This script runs the PVC workgroup metrics and plots the results

import sys
import matplotlib.pyplot as plt
import numpy as np

pathToScoreCode = '/Users/jaume/Documents/Research/CEI_PacingSiteLocalization/Python/'
sys.path.append(pathToScoreCode + 'Python/')

import scoreSubmission as scoreCode

mainPath  = '/Users/jaume/Desktop/PacingDataset/'

sourceModels = ['Epiout','EndoEpiout']
inverseMethods = ['tikh0','tikh1','tikh2','spline']

class inputData:
    groundtruth = ''
    submission = ''
    
# for all source models
allScores = []
for src in sourceModels:
    
    directory = mainPath + src + '/solutions/'
    
    
    gtDir = mainPath + src + '/GT/'
    inputData.groundtruth = gtDir
    
    scores = []
    # for all inverse methods
    for invM in inverseMethods:
        
        solDir = directory + invM + '/'
        
        # run metrics
        print 'Comparing source: ' + src + ' with solutions from: ' + invM
        inputData.submission = solDir
        temp = scoreCode.scoreAllReturn(inputData) 
        scores.append(temp)
        
    allScores.append(scores)
    
#%%### PLOTs
# Plot MSE
axisIx = 0
vecScoresMSE = [[],[]]
vecScoresAPOT =[[],[]]
vecScoresAT = [[],[]]
vecScoresLOC =[[],[]]
for srcScores in allScores:
    vecScoresMSE[axisIx] = []
    vecScoresAPOT[axisIx] = []
    vecScoresAT[axisIx] = []
    vecScoresLOC[axisIx] = []
    for invMScores in srcScores:
        for solScores in invMScores:
            vecScoresMSE[axisIx].append(solScores['metrics'][2]['value'])
            vecScoresAPOT[axisIx].append(solScores['metrics'][1]['value'])
            vecScoresAT[axisIx].append(solScores['metrics'][3]['value'])
            vecScoresLOC[axisIx].append(solScores['metrics'][0]['value'])
    axisIx = axisIx +1
    
#%%
axisIx = 0
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12, 12))
# pot correlation
plt.subplot(221)
plt.violinplot(vecScoresMSE,showmedians=True)
plt.subplot(222)
plt.violinplot(vecScoresAPOT)
plt.subplot(223)
plt.violinplot(vecScoresAT)
plt.subplot(224)
plt.violinplot(vecScoresLOC)

for srcScores in allScores:
    
    t = np.repeat( axisIx+1,len(vecScoresMSE[axisIx]))
    
    # MSE
    plt.subplot(221)
    plt.plot(t, vecScoresMSE[axisIx], 'k.', axisIx+1, np.average(vecScoresMSE[axisIx]),'ro')
    plt.title('MSE of potentials')
    plt.axis([ 0.5,  2.5, 0, 5])
    plt.xticks([1,2],sourceModels)
    plt.yticks(range(0,10,2))
#    plt.xlabel('Source Models')
    plt.ylabel('MSE')
    
    # pot correlation
    plt.subplot(222)
    plt.plot(t, vecScoresAPOT[axisIx], 'k.', axisIx+1, np.average(vecScoresAPOT[axisIx]),'ro')
    plt.title('Correlation of potentials')
    plt.axis([ 0.5,  2.5, -0.5, 1])
    plt.xticks([1,2],sourceModels)
    plt.yticks([ -0.5, 0, 0.5, 1])
#    plt.xlabel('Source Models')
    plt.ylabel('Corr')
    
    # activation times correlation
    plt.subplot(223)
    plt.plot(t, vecScoresAT[axisIx], 'k.', axisIx+1, np.average(vecScoresAT[axisIx]),'ro')
    plt.title('Correlation of activation times')
    plt.axis([ 0.5,  2.5, -0.5, 1])
    plt.xticks([1,2],sourceModels)
    plt.yticks([ -0.5, 0, 0.5, 1])
#    plt.xlabel('Source Models')
    plt.ylabel('Corr')
    
    # PVC localization
    plt.subplot(224)
    plt.plot(t, vecScoresLOC[axisIx], 'k.', axisIx+1, np.average(vecScoresLOC[axisIx]),'ro')
    plt.title('PVC localization error')
    plt.axis([ 0.5,  2.5, 0, 150])
    plt.xticks([1,2],sourceModels)
    plt.yticks(range(0,180,60))
#    plt.xlabel('Source Models')
    plt.ylabel('err')
    
    
    axisIx = axisIx +1

fig.show()

    