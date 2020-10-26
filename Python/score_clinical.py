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

from __future__ import print_function

import argparse
import json
import os
import re
import sys
import numpy as np
import scipy.io
import scipy.stats


class ScoreException(Exception):
    pass


def matchInputFile(testFile, truthDir):
    testwithoutmat = os.path.splitext(testFile)[0]
    truthPathCandidates = [
        os.path.join(truthDir, truthFile)
        for truthFile in os.listdir(truthDir)
        if  (testFile in truthFile)
    ]

    if not truthPathCandidates:
        return 0
    else:
        return truthPathCandidates


def loadFileFromPath(filePath):
    #Load a matlab file as a NumPy array, given a file path
    try:
        data = scipy.io.whosmat(filePath)
        fileMatrix= scipy.io.loadmat(filePath)[data[0][0]]
    except Exception as e:
        raise ScoreException('Could not decode matrix "%s" because: "%s"' %
                             (os.path.basename(filePath), str(e)))

    [m, n] = fileMatrix.shape
    if m < n:
        fileMatrix = np.transpose(fileMatrix)
    return fileMatrix


def computeLOC(truthPath, testPath):
    truthMatrix = loadFileFromPath(truthPath)
    testMatrix = loadFileFromPath(testPath)
    LocalizationErr = np.linalg.norm(truthMatrix - testMatrix)
    return LocalizationErr


def checkFile(truthPath, testPath):
    truthMatrix = loadFileFromPath(truthPath)
    testMatrix = loadFileFromPath(testPath)

    return testMatrix.shape == truthMatrix.shape


def score(truthDir, testDir):
    scores = []
    for testFile in sorted(os.listdir(testDir)):
        truthPaths = matchInputFile(testFile, truthDir)
        if truthPaths == 0:
            continue
        testPath = os.path.join(testDir, testFile)

        for truthPath in truthPaths:
            rtn = checkFile(truthPath, testPath)
            if not rtn:
                raise ScoreException('Error: Matrix "{}" dimension not match'.format(truthPath))
            
            metrics = computeLOC(truthPath, testPath)
            scores.append({
                'dataset': testFile,
                'localization_error': metrics
            })

    return scores


def scoreAll(truthDir, testDir, resDir=None):
    truthSubFiles = os.listdir(truthDir)
    if truthSubFiles:
        truthPath = truthSubFiles[0]
    if not truthPath:
        raise ScoreException(
            'Internal error: error reading ground truth folder: %s' % truthDir)

    testSubFiles = os.listdir(testDir)
    if testSubFiles:
        testPath = testSubFiles[0]
    if not testPath:
        raise ScoreException(
            'Internal error: error reading ground truth folder: %s' % truthDir)

    scores = score(truthDir, testDir)
    if scores==[]:
        print('Internal error: There are no matching submission')

    res = json.dumps(scores, indent=4, sort_keys=True)
    print(res)
    if resDir is not None:
        os.makedirs(resDir, exist_ok=True)
        with open(os.path.join(resDir, 'score.json'), 'w') as f:
            f.write(res)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Submission scoring helper script')
    parser.add_argument('-u', '--user', required=True,
                        help='user name')
    args = parser.parse_args()


    submission = '../../tasks/clinical/submission/{}/submission/'.format(args.user)
    results = '../../tasks/clinical/submission/{}/results/'.format(args.user)
    groundtruth = '../../tasks/clinical/data/gt/'
    try:
        scoreAll(groundtruth, submission, results)
    except ScoreException as e:
        covalicErrorPrefix = 'covalic.error: '
        print(covalicErrorPrefix + str(e), file=sys.stderr)
        exit(1)
