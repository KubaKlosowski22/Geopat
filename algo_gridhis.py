# -*- coding: utf-8 -*-

__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingException,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFileDestination)
from .algo_base import GeoPATBaseAlgorithm

class gridhis_Algorithm(GeoPATBaseAlgorithm):

    COMMAND = 'gpat_gridhis'

    OUTPUT = 'OUTPUT'
    INPUT1 = 'INPUT1'
    INPUT2 = 'INPUT2'
    INPUT3 = 'INPUT3'
    SIZE = 'SIZE'
    SHIFT = 'SHIFT'
    WEIGHTS = 'WEIGHTS'
    LEVEL = 'LEVEL'
    SIGNATURE = 'SIGNATURE'
    NORMALIZATION = 'NORMALIZATION'
    THREADS = 'THREADS'

    def initAlgorithm(self, config):
        #self.SIGN = ['cooc','prod','wcooc','sdec','fdec','lind','linds']
        self.SIGN = self.getGridSignatures()
        #self.NORM = ['pdf','01','N01','none']
        self.NORM = self.getGridNormalizations()
        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT1,self.tr('Input raster layer 1'),defaultValue= None, optional=False))
        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT2,self.tr('Input raster layer 2'),defaultValue='', optional=True))
        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT3,self.tr('Input raster layer 3'),defaultValue='', optional=True))
        self.addParameter(QgsProcessingParameterNumber(self.SIZE,self.tr('Motifel size'),type=QgsProcessingParameterNumber.Integer,defaultValue=150, optional=True))
        self.addParameter(QgsProcessingParameterNumber(self.SHIFT,self.tr('Motifels shift'),type=QgsProcessingParameterNumber.Integer,defaultValue=100, optional=True))
        self.addParameter(QgsProcessingParameterNumber(self.LEVEL,self.tr('Decomposition level'),type=QgsProcessingParameterNumber.Integer,defaultValue=None, optional=True))
        self.addParameter(QgsProcessingParameterRasterLayer(self.WEIGHTS,self.tr('Weights raster layer'),defaultValue='', optional=True))
        self.addParameter(QgsProcessingParameterEnum(self.SIGNATURE,self.tr('Signature'),self.SIGN,defaultValue=None, allowMultiple=False))
        self.addParameter(QgsProcessingParameterEnum(self.NORMALIZATION,self.tr('Normalization'),self.NORM,defaultValue = None, allowMultiple=False))
        self.addParameter(QgsProcessingParameterNumber(self.THREADS,self.tr('Number of threads'),type=QgsProcessingParameterNumber.Integer,defaultValue=1, optional=True))
        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,self.tr('Grid of motifels'),self.tr('Grid files (*.hdr)')))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        inLayer = self.parameterAsRasterLayer(parameters, self.INPUT1, context)
        if inLayer is None:
            raise QgsProcessingException("Brak Warstwy wejściowej (INPUT 1)")
        arguments.append("-i")
        arguments.append(inLayer.source())
        inLayer2 = self.parameterAsRasterLayer(parameters, self.INPUT2, context)
        if inLayer2 is not None and inLayer.Source():
            arguments.append("-i")
            arguments.append(inLayer.source())
        inLayer3 = self.parameterAsRasterLayer(parameters, self.INPUT3, context)
        if inLayer3 is not None and inLayer.source():
            arguments.append("-i")
            arguments.append(inLayer.source())
        size = self.parameterAsInt(parameters, self.SIZE, context)
        if size:
            arguments.append('-z')
            arguments.append(str(size))
        if int(size) < 10:
            raise QgsProcessingException("Size nie może być mniejszy niż 10")
        shift = self.parameterAsInt(parameters, self.SHIFT, context)
        if shift:
            arguments.append('-f')
            arguments.append(str(shift))
        if int(shift) > int(size):
            raise QgsProcessingException("shift nie może być większe od size")
        elif int(shift) < 5:
            raise QgsProcessingException("Shift nie może być mniejsze od 5")
        elif int(shift) < int(size) and int (shift) < 5:
            raise QgsProcessingException("Shift nie może być mniejsze od 5 i większe od Size")
        weights = self.parameterAsRasterLayer(parameters, self.WEIGHTS, context)
        if weights:
            arguments.append('-w')
            arguments.append(weights.source())
        sign = self.parameterAsEnum(parameters, self.SIGNATURE, context)
        if sign:
            arguments.append('-s')
            arguments.append(self.SIGN[sign])
        if sign == 1 and inLayer2 is None:
            raise QgsProcessingException("Dla sygnatury PROD należy podać więcej niż jedną warstwę wejściową")
        level = self.parameterAsInt ( parameters, self.LEVEL, context )
        if sign == 4:
            if level:
                arguments.append ( '--level=' + str ( level ) )
        if sign is not 4 and level:
            raise QgsProcessingException('Poziom dekompozycji podajemy tylko dla sygnatury FDEC - Ustaw wartość "Brak"')
        norm = self.parameterAsEnum(parameters, self.NORMALIZATION, context)
        if norm:
            arguments.append('-n')
            arguments.append(self.NORM[norm])
        if sign == 0 and norm is not 0:
            raise QgsProcessingException("Dla sygnatury COOC wybierz normalizacje PDF")
        elif sign == 1 and norm is not 0:
            raise QgsProcessingException("Dla sygnatury PROD wybierz normalizacje PDF")
        elif sign == 2 and norm is not 0:
            raise QgsProcessingException("Dla sygnatury WCOOC wybierz normalizacje PDF")
        elif sign == 5 and norm is not 3:
            raise QgsProcessingException("Dla sygnatury LIND wybierz normalizacje NONE")
        elif sign == 6 and norm is not 3:
            raise QgsProcessingException("Dla sygnatury LINDS wybierz normalizacje NONE")
        threads = self.parameterAsInt(parameters, self.THREADS, context)
        if threads:
            arguments.append('-t')
            arguments.append(str(threads))
        outGrid = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        if outGrid.endswith('.hdr'):
           outGrid = outGrid[:-4]
        arguments.append('-o')
        arguments.append(outGrid)
        self.runGeoPAT([self.getExecPath(self.COMMAND), self.escapeAndJoin(arguments)], feedback)
        return {self.OUTPUT: outGrid}

    def name(self):
        return 'Grid of histograms (gpat_gridhis)'

    def groupId(self):
        return 'Signatures'

    def createInstance(self):
        return gridhis_Algorithm()
