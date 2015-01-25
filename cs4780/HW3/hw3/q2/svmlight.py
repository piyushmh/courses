# svmlight.py
#
# Author: Clint Burfoot <clint@burfoot.info>
#

"""
An interface class for U{SVM light<http://svmlight.joachims.org/>}
"""

import os
import tempfile
import math
from subprocess import call

class SVMLight:
    """
    An interface class for U{SVM light<http://svmlight.joachims.org/>}
    
    This class currently supports classification with default options 
    only. It calls the SVMLight binaries as external programs.
    
    Future versions should add a SWIG interface and support for use of 
    non-default SVMlight options.
    
    C{SVMLight} reads sparse feature vectors - dictionaries with 
    numeric keys, representing features, and arbitrary numeric values.
    """
    
    learn_binary = "svm_learn"
    classify_binary = "svm_classify"
    
    def __init__(self, svm_path, labels=None, vectors=None, model=None, 
                 cleanup=False):
        """
        Trains a new classifier.
        
        @type svm_path: C{str}
        @param svm_path: The filesystem path to the SVMLight binaries
        @type labels: C{tuple}
        @param labels: A tuple of boolean training set labels.
        @type vectors: C{tuple}
        @param vectors: A tuple of sparse feature vectors.
        @type model: A C{tuple} of C{str}
        @param model: The lines from an SVMlight model file. Specify this 
        instead of C{labels} and C{vectors} to use a pre-trained classifier.
        """
        self._svm_learn = os.sep.join((svm_path, SVMLight.learn_binary))
        self._svm_classify = os.sep.join((svm_path, SVMLight.classify_binary))
        self._cleanup = cleanup
        self._devnull = None
        
        self._directory = tempfile.mkdtemp()
        self._example_fname = os.sep.join((self._directory, "example"))
        self._model_fname = os.sep.join((self._directory, "model"))
        self._input_fname = os.sep.join((self._directory, "input"))
        self._output_fname = os.sep.join((self._directory, "output"))
        
        if model is not None:
            self._write_model(self._model_fname, model)
            self.model = model
        elif len(labels) != len(vectors):
            raise ValueError("labels and vectors arrays are different lengths")
        
        self._write_vectors(self._example_fname, labels, vectors)
        ret = call((self._svm_learn, self._example_fname, self._model_fname),
                   stdout=self.devnull)
        assert ret == 0
        if model is None:
            self.model = self._read_model()

    def _get_devnull(self):
        # Return a handle to /dev/null (or windows equivalent).
        if self._devnull is None:
            if os.name == 'posix':
                self._devnull = open("/dev/null", "w")
            else:
                # Assume we're on windows.
                self._devnull = open("NUL:", "w")              
        return self._devnull
    devnull = property(_get_devnull)

    def __getstate__(self):
        state = self.__dict__.copy()
        state['_devnull'] = None
        return state
     
    def classify(self, vectors):
        """
        Classify feature vectors.
        
        @type vectors: C{tuple}
        @param vectors: A tuple of sparse binary feature vectors.
        @rtype: C{tuple}
        @return: A tuple of C{float} vector classifications.
        """
        self._write_vectors(self._input_fname, ["0" for v in vectors], vectors)
        ret = call((self._svm_classify, self._input_fname, self._model_fname, 
                    self._output_fname), stdout=self.devnull)
        assert ret == 0
        results = self._read_classification()
        assert len(results) == len(vectors)
        return results
    
    def _write_vectors(self, fname, labels, vectors):
        # Writes the given array to the given filename with the given labels.
        # Vectors are written in the SVMlight format.
        file = open(fname, "w")
        assert len(labels) == len(vectors)
        for i in range(0, len(labels)):
            label = "-1"
            if labels[i]:
                label = "1"
            feature_strings = list()
            features = vectors[i].keys()
            features.sort()
            for feature in features:
                feature_strings.append("%d:%s" % (feature + 1, 
                                                  str(vectors[i][feature])))
            file.write("%s %s\n" % (label, " ".join(feature_strings)))
        file.close()
    
    def _write_model(self, fname, model):
        # Writes the model file.
        file = open(fname, "w")
        for line in model:
            file.write("%s\n" % line)
        file.close()
        
    def _read_classification(self):
        # Reads the SVMlight output file.
        file = open(self._output_fname, "r")
        result = []
        for line in file.readlines():
            result.append(float(line))
        file.close()
        assert len(result) > 0
        return result
    
    def _read_model(self):
        # Reads the SVMlight model file.
        file = open(self._model_fname, "r")
        result = []
        for line in file.readlines():
            line = line.rstrip()
            result.append(line)
        file.close()
        assert len(result) > 0
        return result
        
    def __del__(self):
        if self._cleanup:
            for fname in os.listdir(self._directory):
                os.unlink(os.sep.join((self._directory, fname)))
            os.rmdir(self._directory)

