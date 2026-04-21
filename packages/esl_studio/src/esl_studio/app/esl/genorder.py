#! /usr/bin/python

class GenOrder:

    def __init__(self, generate):
        self._generate = generate
        self._allModules = [] #all application modules to be sorted: models, submodels & segments and code imports (but not "diagram" packages)
        self._orderedUsedApplicationModules = []
        self._unusedApplicationModules = []

    def orderedUsedApplicationModules(self): # valid after establishOrder
        return self._orderedUsedApplicationModules
    def unusedApplicationModules(self):
        return self._unusedApplicationModules

    def establishOrder(self):
        errMsg = ""
        self.clearOrders()
        self.resetAllModules()
        trail = []
        for model in self._generate.genModels():
            for module in model.calledModules():
                errMsg = self.pushRank(trail, module, 1)
                if errMsg: break
        if not errMsg:
            self._allModules.sort(key=lambda modl: modl.eslname())
            self._allModules.sort(key=lambda modl: modl.rank(), reverse=True)
            for modl in self._allModules:
                if modl.subType() != 'model':
                    if modl.rank() == 0:
                        self._unusedApplicationModules.append(modl)
                    else:
                        self._orderedUsedApplicationModules.append(modl)
        return errMsg

    def resetAllModules(self):
        for genModule in self._generate.genModels() + self._generate.genSubmodels() + \
                         self._generate.genSegments() + self._generate.genCodes():
            self._allModules.append(genModule)
            genModule.set_rank(0)

    def clearOrders(self):
        self._allModules = []
        self._orderedUsedApplicationModules = []
        self._unusedApplicationModules = []

    def pushRank(self, trail, thisModule, nextRank):
        errMsg = ""
        if nextRank > thisModule.rank():
            thisModule.set_rank(nextRank)
        trail.append(thisModule)
        for calledModule in thisModule.calledModules():
            if calledModule in trail:
                ok = False
                trailStrList = []
                for m in trail: trailStrList.append(m.identification())
                trailStr = ", ".join(trailStrList)
                errMsg = "Error: Cyclic subprogram dependency - "+calledModule.identification()+" invoked in "+thisModule.identification()+" in sequence "+trailStr+"\n"
            else:
                errMsg = self.pushRank(trail, calledModule, thisModule.rank() + 1)
            if errMsg:
                break
        trail.pop()
        return errMsg

class GenResolveSimulationEntitiesOrder:

    def __init__(self, genDiagramInfo):
        self._genDiagramInfo = genDiagramInfo

    def generate(self):
        return self._genDiagramInfo.generate()

    def establishSimulationEntitiesOrder(self):
        if self.generate().debugging:
            print(">GenResolveSimulationEntitiesOrder.establishSimulationEntitiesOrder " + str(self._genDiagramInfo.module().appModule().eslname()))
        simulationEntitiesOrder = self._genDiagramInfo.toResolveSimulationEntities().copy()
        orderedSimEntities = []
        errMsg = ""
        trail = []
        for genSimEntity in simulationEntitiesOrder:
            for upLinkedGenSimEntity in genSimEntity.upLinkedSimulationEntities():
                errMsg = self.pushRank(trail, upLinkedGenSimEntity, 1)
                if errMsg: break
        if not errMsg:
            simulationEntitiesOrder.sort(key=lambda item: item.rank(), reverse=True)
            for genSimEntity in simulationEntitiesOrder:
                orderedSimEntities.append(genSimEntity)
        if self.generate().debugging:
            print("<GenResolveSimulationEntitiesOrder.establishSimulationEntitiesOrder " + str(self._genDiagramInfo.module().appModule().eslname())
                  +" orderedSimEntities="+" ".join([str(s) for s in orderedSimEntities])+" errMsg="+errMsg)
        return orderedSimEntities, errMsg

    def pushRank(self, trail, thisGenSimEntity, nextRank):
        errMsg = ""
        if nextRank > thisGenSimEntity.rank():
            thisGenSimEntity.set_rank(nextRank)
        trail.append(thisGenSimEntity)
        for upLinkedGenSimEntity in thisGenSimEntity.upLinkedSimulationEntities():
            if upLinkedGenSimEntity in trail:
                ok = False
                errMsg = "Error: Cyclic connection link - "+upLinkedGenSimEntity.identification()+" for "+thisGenSimEntity.identification()+"\n"
            else:
                errMsg = self.pushRank(trail, upLinkedGenSimEntity, thisGenSimEntity.rank() + 1)
            if errMsg:
                break
        trail.pop()
        return errMsg
