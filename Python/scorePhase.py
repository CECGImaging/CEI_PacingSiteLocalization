
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

def scoreP1(truthPath, testPath, FileType):
    truthMatrix = loadFileFromPath(truthPath)
    testMatrix = loadFileFromPath(testPath)

    if FileType == 'POT':
        #print (FileType)
        metrics = computePOT(truthMatrix, testMatrix)
    elif FileType == 'AT':
        #print (FileType)
        metrics = computeAT(truthMatrix, testMatrix)
    elif FileType == 'LOC':
        #print (FileType)
        metrics = computeLOC(truthMatrix, testMatrix)
    else:
        raise ScoreException(
            'Internal error: unknown ground truth phase number: %s' %
            os.path.basename(truthPath))
    #metrics.extend(computeSimilarityMetrics(truthBinaryImage, testBinaryImage))
    return metrics

def scoreP2(truthPath, testPath, FileType):
    truthMatrix = loadFileFromPath(truthPath)
    testMatrix = loadFileFromPath(testPath)

    if FileType == 'LOC':
        #print (FileType)
        metrics = computeLOC(truthMatrix, testMatrix)
    else:
        raise ScoreException(
            'Internal error: unknown ground truth phase number: %s' %
            os.path.basename(truthPath))
    #metrics.extend(computeSimilarityMetrics(truthBinaryImage, testBinaryImage))
    return metrics
# todo, implement when phase is available


#    if FileType == 'POT':
#        #print (FileType)
#        metrics = computePOT(truthMatrix, testMatrix)
#    elif FileType == 'AT':
#        #print (FileType)
#        metrics = computeAT(truthMatrix, testMatrix)
#    elif FileType == 'LOC':
#        #print (FileType)
#        metrics = computeLOC(truthMatrix, testMatrix)
#    else:
#        raise ScoreException(
#            'Internal error: unknown ground truth phase number: %s' %
#            os.path.basename(truthPath))
    #metrics.extend(computeSimilarityMetrics(truthBinaryImage, testBinaryImage))
#    return metrics

def scoreP3(truthPath, testPath, FileType):
    truthMatrix = loadFileFromPath(truthPath)
    testMatrix = loadFileFromPath(testPath)

# todo, implement when phase is available


#    if FileType == 'POT':
#        #print (FileType)
#        metrics = computePOT(truthMatrix, testMatrix)
#    elif FileType == 'AT':
#        #print (FileType)
#        metrics = computeAT(truthMatrix, testMatrix)
#    elif FileType == 'LOC':
#        #print (FileType)
#        metrics = computeLOC(truthMatrix, testMatrix)
#    else:
#        raise ScoreException(
#            'Internal error: unknown ground truth phase number: %s' %
#            os.path.basename(truthPath))
#metrics.extend(computeSimilarityMetrics(truthBinaryImage, testBinaryImage))
#    return metrics


def score(truthDir, testDir):
    # Iterate over each file and call scoring executable on the pair
    scores = []
    for truthFile in sorted(os.listdir(truthDir)):

        #print ('This is File List')
        testPath = matchInputFile(truthFile, testDir)
        if testPath== 0:
            continue

       # print(testPath)
        truthPath = os.path.join(truthDir, truthFile)
        #print (truthPath)
        #print (testPath)

        #print ('-----------------------------')
        for testFile in testPath:
            #print('Test file is :', testFile)
            FileName = testFile.rsplit('/',1)[1]
            FileName=FileName[:-4]
            #print('File name is:', FileName)
            FileType = truthFile.rsplit('_')[3]
            PhaseNum = truthFile.rsplit('_')[1]
            #print('The PhaseNum is:')
            #print(PhaseNum)

            checkFile(truthPath, testFile)

            if PhaseNum == '1':
                metrics=scoreP1(truthPath, testFile, FileType)
            elif PhaseNum=='2':
                # raise ScoreException('Error: Phase 2 not implemented yet')
                metrics = scoreP2(truthPath, testPath, FileType)
            elif PhaseNum=='3':
                #metrics = scoreP3(truthPath, testPath, FileType)
                raise ScoreException('Error: Phase 3 not implemented yet')
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
