#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#  Copyright Kitware Inc.
#
#  Licensed under the Apache License, Version 2.0 ( the "License" );
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
###############################################################################

import os
import scipy.io
import scipy.stats
import numpy as np
import math



class ScoreException(Exception):
    pass

def magnitudesqure(vector):
    return np.sum([a ** 2 for a in vector])

def matchInputFile(truthFile, testDir):

    truthwithoutmat=os.path.splitext(truthFile)[0]

    #print(truthwithoutmat[:-12])

    testPathCandidates = [
        os.path.join(testDir, testFile)
        for testFile in os.listdir(testDir)
        if  (truthwithoutmat[:-12] in testFile)
    ]
    ##print(testPathCandidates)
    if not testPathCandidates:
        return(0)
        #raise ScoreException('No matching submission for: %s' % truthFile)
    elif len(testPathCandidates) > 1:
        raise ScoreException(
            'Multiple matching submissions for: %s' % truthFile)
    else:
        return testPathCandidates[0]
    #print(testPathCandidates[0])



def loadFileFromPath(filePath):
    #Load a matlab file as a NumPy array, given a file path
    try:
        #print('Reached .mat reading part')
        file = scipy.io.whosmat(filePath)
        #print(file)
        #print(file[0][0])

        fileMatrix= scipy.io.loadmat(filePath)[file[0][0]]
        #print(fileMatrix)
    except Exception as e:
        raise ScoreException('Could not decode matrix "%s" because: "%s"' %
                             (os.path.basename(filePath), str(e)))

    return fileMatrix




def computeLOC(truthVector, testVector):

    LocalizationErr = np.linalg.norm(truthVector - testVector)

    #print(truthVector,testVector)
    #print(LocalizationErr)
    #print(metric)
    metrics = [
        {
            'name': 'localization_error',
            'value': LocalizationErr
        },
        {
            'name':  'potential_correlation',
            'value': None
        },
        {
            'name': 'potential_RMSE',
            'value': None
        },
        {
            'name': 'AT_correlation',
            'value':  None

        }
    ]
    return metrics


def computeAT(truthVector, testVector):
    (CorrelationAT,p_val) = scipy.stats.pearsonr(truthVector, testVector)
    #print(truthVector,testVector)
    #print(CorrelationAT)
    #print(metric)

    metrics = [
        {
            'name': 'localization_error',
            'value': None
        },
        {
            'name':  'potential_correlation',
            'value': None
        },
        {
            'name': 'potential_RMSE',
            'value': None
        },
        {
            'name': 'AT_correlation',
            'value': CorrelationAT[0]

        }
    ]
    return metrics

def computePOT(truthMatrix, testMatrix):
    T=truthMatrix.shape[1]
    N=truthMatrix.shape[0]
    
    
    
    ## MEAN SQUARED ERROR
    sumError=0
    for t in range(T):
        truthVec=(truthMatrix[:,t])
        testVec=(testMatrix[:,t])   
        Error_t = math.pow(np.linalg.norm(truthVec-testVec),2)
        #magtruthVect = math.pow(np.linalg.norm(truthVec),2)
        magtruthVect = magnitudesqure(truthVec)
        sumError= sumError + Error_t/magtruthVect
        #print('Individual vectors:')
        #print(truthVec)
        #print(testVec)
        #print(Error_t)
        #print(np.array(truthVec-testVec))
        
    RMSEr=sumError/T
    #print('Average relative error is:')
    #print(RMSEr)
    
    ## CORRELATION OF TEMPORAL SIGNALS
    sumCorrelation=0
    for n in range(N):
        truthVec=(truthMatrix[n,:])
        testVec=(testMatrix[n,:])
        
        # TODO: find more eleigant solution than just 0 for constant inputs
        if np.sum(np.abs(truthVec-truthVec.mean()))>0 and np.sum(np.abs(testVec-testVec.mean()))>0:
            sumCorrelation= sumCorrelation + scipy.stats.pearsonr(truthVec, testVec)[0]
            
        elif np.sum(np.abs(truthVec-truthVec.mean()))==0 and np.sum(np.abs(testVec-testVec.mean()))==0:
            sumCorrelation= sumCorrelation + 1
        
        
    avgCorrelation = sumCorrelation/N
    #print('Average Correlation is:')
    #print(avgCorrelation)



    metrics = [
        {
            'name': 'localization_error',
            'value': None
        },
        {
            'name':  'potential_correlation',
            'value': avgCorrelation
        },
        {
            'name': 'potential_RMSE',
            'value': RMSEr
        },
        {
            'name': 'AT_correlation',
            'value': None

        }
    ]
    return metrics
