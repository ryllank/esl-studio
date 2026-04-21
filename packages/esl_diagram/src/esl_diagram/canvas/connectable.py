#! /usr/bin/python

import wx

class Connectable(object):
    # _links: list of Links for the connectable
    # _linkConnectsAtEnds: dict(Link) bool: the Link is connected here at its end
    def __init__(self):
        self._defn = None
        self._links = []
        self._linkConnectsAtEnds = {}

    def startLink(self):
        return None, ""

    def links(self):
        return self._links

    def linkConnectsAtEnd(self, link):
        return self._linkConnectsAtEnds.get(link)

    def addLink(self, link, linkConnectsAtEnd):
        result = False
        errorMsg = ""
        # check if at max links
        maxLinks = ""
        if self._defn:
            maxLinks = self._defn.getAttribute("max-links")
        if not maxLinks or int(maxLinks) > len(self._links):
            # prevent duplicates
            if link not in self._links:
                self._links.append(link)
                self._linkConnectsAtEnds[link] = linkConnectsAtEnd
                result = True
            else:
                errorMsg = "Attempt to add duplicate link"
        else:
            errorMsg = "At maximum number of links allowed ("+maxLinks+")"
        return result, errorMsg

    def detachLink(self, link):
        if link in self._links:
            self._links.remove(link)
        if link in self._linkConnectsAtEnds:
            del self._linkConnectsAtEnds[link]

    def establishConnections(self, initialEntity, connections, sourcePort, inputLink=None):
        for link in self._links:
            if link != inputLink:
                otherEnd = link.otherEnd(self)
                if otherEnd and otherEnd != sourcePort:
                    if otherEnd.objectId() not in connections:
                        if otherEnd.category() == "node":
                            otherEnd.establishConnections(initialEntity, connections, sourcePort, link)
                        elif otherEnd.category() == "port":
                            connections.append(otherEnd.objectId())
                            if (otherEnd.parent().category() != "display" and # Don't track connections through displays
                                    (not initialEntity or initialEntity.category() != "display")): # For a display can stop at the first port
                                otherEnd.establishConnections(initialEntity, connections, sourcePort, link)
