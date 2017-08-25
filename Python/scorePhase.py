
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
import numpy as np

from scoreCommon import ScoreException, matchInputFile, loadFileFromPath, computePOT, computeAT, computeLOC


def checkFile(truthPath, testPath):

    truthMatrix = loadFileFromPath(truthPath)
    testMatrix = loadFileFromPath(testPath)
    #print ('TruthMatrix:')
    #print (truthMatrix.shape[0:2])
    #print ('TestMatrix:')
    #print (truthMatrix.shape)

    if testMatrix.shape[0:2] != truthMatrix.shape[0:2]:
        raise ScoreException('Matrix %s has dimensions %s; expected %s.' %
                             (os.path.basename(testPath), testMatrix.shape[0:2],
                              truthMatrix.shape[0:2]))

def scoreP1(truthPath, testPath, FileType, metrics):
    truthMatrix = loadFileFromPath(truthPath)
    testMatrix = loadFileFromPath(testPath)

    if FileType == 'POT':
        #print (FileType)
        metricsUpdate = computePOT(truthMatrix, testMatrix)
        metrics[1] = metricsUpdate[1]
        metrics[2] = metricsUpdate[2]
    elif FileType == 'AT':
        #print (FileType)
        metricsUpdate = computeAT(truthMatrix, testMatrix)
        metrics[3] = metricsUpdate[3]
    elif FileType == 'LOC':
        #print (FileType)
        metricsUpdate = computeLOC(truthMatrix, testMatrix)
        metrics[0] = metricsUpdate[0]
    else:
        raise ScoreException(
            'Internal error: unknown ground truth phase number: %s' %
            os.path.basename(truthPath))
    #metrics.extend(computeSimilarityMetrics(truthBinaryImage, testBinaryImage))
    
    return metrics

def findAllHeartbeats(truthDir):
    
    cleanTruhDir = []
    for truthFile in sorted(os.listdir(truthDir)):
        tempStr = truthFile.rsplit('_')[0] + "_" + truthFile.rsplit('_')[1] + "_" + truthFile.rsplit('_')[2]
        cleanTruhDir.append(tempStr)
    
    uniqueTruhDir = []
    for x in cleanTruhDir:
        if x not in uniqueTruhDir:
            uniqueTruhDir.append(x)
                
    return uniqueTruhDir


def score(truthDir, testDir):

    # get all the different heartbeats regardless of type of data
    uniqueTruhDir = findAllHeartbeats(truthDir)
    
    # Iterate over each file and call scoring executable on the pair
    scores = []
    for truthFile in uniqueTruhDir:

        #print ('This is File List')
        testPath = matchInputFile(truthFile, testDir)
        if testPath== 0:
            continue
        
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
                'value':  None
    
            }
        ]

        #print ('-----------------------------')

        FileName = truthFile.rsplit('_',1)[0] + "_" + testPath[0].rsplit('_')[3]
        PhaseNum = truthFile.rsplit('_')[1]
        #print('The PhaseNum is:')
        #print(PhaseNum)
        #print(testPath)
        
        
        for i in range(len(testPath)):  
            
                
            FileType = testPath[i].rsplit('_')[3]
            
            truthPath = os.path.join( truthDir, truthFile + "_" + FileType + "_GroundTruth.mat"  )
            #print (truthPath)
            #print (testPath[i])

            
            checkFile(truthPath, testPath[i])

            
            #print(FileType)
        
            if PhaseNum == '1':
                metrics=scoreP1(truthPath, testPath[i], FileType, metrics)
            else:
                raise ScoreException(
                    'Error: Phase number must be either 1 or 2 or 3')
    
            #print(metrics)
            #print(FileType)


        scores.append({
            'dataset': FileName,
            'metrics': metrics
        })

    return scores
