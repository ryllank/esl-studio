#! /usr/bin/python

from .simulationentity import SimulationEntity
from .port import Port

class ArrayOperatorEntity(SimulationEntity):

    SpecialTypes = [
        "Array Scalar Multiplication", "Array Addition", "Array Multiplication",
        "Matrix Inverse", "Matrix Transpose", "Matrix Determinant",
        "Vector Merge", "Vector Split", "Vector Dot Product", "Vector Cross Product",
    ]

    def __init__(self, parent, type="", objectId=""):
        SimulationEntity.__init__(self, parent, type, objectId)

    # Array operator entities are special to validate new links (connections).
    # Also where an output port's dimensions may be resolved from (resolved) inputs.
    # In other respects they are handled as normal Simulation entities.

    def validateEntityLinks(self, entityPortsConnectionsDict={}, portResolveDimensionsDict={}) -> (bool, str):   # Override this in any special types of simulation entity that need linkages validating.
        """ returns: valid:bool, msg:str """
        valid = True
        msg = ''
        specialType = self.specialType()
        if specialType not in ["Vector Merge", "Vector Split", "Vector Dot Product", "Vector Cross Product"]: # these need no special linkage validation
            resolvedPortDimensionsData = {}
            diagramInfo = self.parent()
            entitysPortsConnections = entityPortsConnectionsDict.get(self)
            if entitysPortsConnections is None:
                entitysPortsConnections = diagramInfo.canvas().EstablishPortsConnections(self.objectId())
                entityPortsConnectionsDict[self] = entitysPortsConnections

            for port in self._ports.values():
                portResolveDimensionsData = port.resolvePortDimensions(entityPortsConnectionsDict, portResolveDimensionsDict)
                resolvedDimensionality = None
                if portResolveDimensionsData.resolvedDimensions is not None and not portResolveDimensionsData.resolvedRejectMsg:
                    resolvedPortDimensionsData[port.id()] = portResolveDimensionsData
                    #print(" port id="+str(port.id())+" datetype="+str(port.datatype())+" dimensions="+str(port.dimensions())+
                    #      " portResolveDimensionsData="+str(portResolveDimensionsData))

            # Applies to dimensionality fixed (or resolved) ports.
            portData1 = resolvedPortDimensionsData.get('1')
            if portData1:
                if portData1.resolvedState in Port.UnresolvedStates:
                    portData1 = None
            portData2 = None
            if portData1 is not None:
                portData2 = resolvedPortDimensionsData.get('2')
                if portData2:
                    if portData2.resolvedState in Port.UnresolvedStates:
                        portData2 = None
            if specialType == "Array Scalar Multiplication":
                # resolved input and output ports (ids 1 & 2) must have same array dimensionality sizes
                if portData1 and portData2:
                    port1_sizes = portData1.resolvedDimensionality.sizes()
                    port2_sizes = portData2.resolvedDimensionality.sizes()
                    if port1_sizes != port2_sizes:
                        msg = "resolved input and output ports must have the same dimensionality sizes"
                        valid = False
                pass
            elif specialType == "Array Addition":
                # resolved input and output ports (ids 1 & 2) must have same array dimensionality sizes
                if portData1 and portData2:
                    port1_sizes = portData1.resolvedDimensionality.sizes()
                    port2_sizes = portData2.resolvedDimensionality.sizes()
                    if port1_sizes != port2_sizes:
                        msg = "resolved input and output ports must have the same dimensionality sizes"
                        valid = False
                pass
            elif specialType == "Array Multiplication":
                # "the number of columns in the first matrix must be equal to the number of rows in the second matrix.
                # The resulting matrix, known as the matrix product, has the number of rows of the first and the number of columns of the second matrix"
                # i.e. (r,n) * (n,c) => (r,c) - ??? to include a 1D array (r) as a "2D" column array (1,r) if needed.
                # resolved first input port dimensions must have same number of rows as number of columns of 2nd input
                # and resolved output port dimensions must have same number of rows as first input and columns of 2nd input
                if portData1 and portData2:
                    port1_sizes = portData1.resolvedDimensionality.sizes()
                    port2_sizes = portData2.resolvedDimensionality.sizes()
                    # Handle sizes of len 1 as column array -> append a 1 to its sizes
                    if len(port1_sizes) == 1:
                        port1_sizes.append(1)
                    if len(port2_sizes) == 1:
                        port2_sizes.append(1)
                    if port1_sizes[1] != port2_sizes[0]:
                        msg = "resolved first input port dimensions must have same number of rows as number of columns of 2nd input"
                        valid = False
                    portData3 = resolvedPortDimensionsData.get('3')
                    if portData3:
                        if portData3.resolvedState in Port.UnresolvedStates:
                            portData3 = None
                    if portData3:
                        port3_sizes = portData3.resolvedDimensionality.sizes()
                        if len(port3_sizes) == 1:
                            port3_sizes.append(1)
                        if port3_sizes[0] != port1_sizes[0] or port3_sizes[1] != port2_sizes[1]:
                            if msg: msg += " and "
                            msg += "resolved output port dimensions must have same number of rows as first input and columns of 2nd input"
                            valid = False
                pass
            elif specialType == "Matrix Inverse":
                # resolved input must be square
                # and resolved output must have the same dimensionality sizes
                if portData1:
                    port1_sizes = portData1.resolvedDimensionality.sizes()
                    if port1_sizes[0] != port1_sizes[1]:
                        msg = "resolved input port dimensions must have same number of rows as number of columns (i.e. be square)"
                        valid = False
                    if portData2:
                        port2_sizes = portData2.resolvedDimensionality.sizes()
                        if port1_sizes != port2_sizes:
                            if msg: msg += " and "
                            msg += "resolved output port dimensions sizes must have same number of rows and columns as for the input port"
                            valid = False
                pass
            elif specialType == "Matrix Transpose":
                # resolved output must have transposed dimensionality sized of resolved input
                if portData1 and portData2:
                    port1_sizes = portData1.resolvedDimensionality.sizes()
                    port2_sizes = portData2.resolvedDimensionality.sizes()
                    if port2_sizes[0] != port1_sizes[1] or port2_sizes[1] != port1_sizes[0]:
                        msg = "resolved output port dimensions must have same number of rows and columns as the number of columns and rows of the input port dimensions (i.e. swapped)"
                        valid = False
                pass
            elif specialType == "Matrix Determinant":
                # resolved input must be square
                if portData1:
                    port1_sizes = portData1.resolvedDimensionality.sizes()
                    if port1_sizes[0] != port1_sizes[1]:
                        msg = "resolved input port dimensions must have same number of rows as number of columns (i.e. be square)"
                        valid = False
                pass
            if msg:
                msg = self.identification() + " " + msg + "\n"
        return valid, msg

    def entityResolvePortDimensions(self, port, entityPortsConnectionsDict={}, portResolveDimensionsDict={}) -> str:  # Override this in any special types of simulation entity that can (sometimes) resolve port dimensions
        """ returns: portDimensions:str """
        dimensions = None
        specialType = self.specialType()
        #print(">ArrayOperatorEntity.entityResolvePortDimensions "+str(self)+" portId="+port.entityPortId())
        if specialType not in ["Vector Merge", "Vector Split", "Vector Dot Product", "Vector Cross Product", "Matrix Determinant"]: # these need no special output port resolving
            if (specialType == "Array Multiplication" and port.id() == '3') or port.id() == '2':
                diagramInfo = self.parent()
                entitysPortsConnections = entityPortsConnectionsDict.get(self)
                if entitysPortsConnections is None:
                    entitysPortsConnections = diagramInfo.canvas().EstablishPortsConnections(self.objectId())
                    entityPortsConnectionsDict[self] = entitysPortsConnections
                port1ResolveDimensionsData = self._ports['1'].resolvePortDimensions(entityPortsConnectionsDict, portResolveDimensionsDict)
                resolvedPort1Dimensions = port1ResolveDimensionsData.resolvedDimensions
                resolvedPort2Dimensions = None
                if resolvedPort1Dimensions:
                    if specialType == "Array Multiplication":
                        port2ResolveDimensionsData = self._ports['2'].resolvePortDimensions(entityPortsConnectionsDict, portResolveDimensionsDict)
                        resolvedPort2Dimensions = port2ResolveDimensionsData.resolvedDimensions
                    if specialType in ["Array Scalar Multiplication", "Array Addition", "Matrix Inverse"]:
                        dimensions = resolvedPort1Dimensions
                    elif specialType == "Array Multiplication" and resolvedPort2Dimensions:
                        port1RowBounds = resolvedPort1Dimensions.split(",")[0]
                        port2ColBoundsSplit = resolvedPort2Dimensions.split(",")
                        if len(port1RowBounds) == 2:
                            port2ColBounds = port2ColBoundsSplit[1]
                            dimensions = port1RowBounds + "," + port2ColBounds
                        else:
                            dimensions = port1RowBounds
                    elif specialType == "Matrix Transpose":
                        port1Bounds = resolvedPort1Dimensions.split(",")
                        dimensions = port1Bounds[1] + "," + port1Bounds[0]
            #print("<ArrayOperatorEntity.entityResolvePortDimensions "+str(self)+" portId="+port.entityPortId()+" dimensions="+str(dimensions))
        return dimensions
