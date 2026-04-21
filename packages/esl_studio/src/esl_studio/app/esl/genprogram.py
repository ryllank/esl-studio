#! /usr/bin/python

class GenProgram():
    def __init__(self, generate, appProgram):
        self._generate = generate
        self._appProgram = appProgram

    def setupProgram(self):
        pass

    def generate(self):
        return self._generate
    def appProgram(self):
        return self._appProgram

    def appModel(self):
        model = self._appProgram.model()
        if not model:
            if len(self._generate.genModels()) > 0:
                model = self._generate.genModels()[0].appModule()
        return model

    def genModel(self):
        result = None
        appModel = self.appModel()
        if appModel:
            for genModel in self._generate.genModels():
                if genModel.appModule() == appModel:
                    result = genModel
                    break
        return result

    def experiment(self):
        experiment = self._appProgram.experiment()
        return experiment
