# spore
paintable particle node for Maya

Spore is a set of Maya plug-ins and scripts. The main element of spore is the sporeNode.
The sporeNode is a custom particle node. The readable "instanceData" attribute is designed
to be connected to Maya's particle instancer node.

To add, remove or manipulate spores (particles) a array of different contexts is provided:
- place
- spray
- align
- scale
- move

Each context has a number of different shortcuts to provide a more interactive user experience


# philosophy
spore is ment to allow artist to very quickly populate their scene.
To keep Maya as performant as possible the idea is to have multiple spore nodes.

Note that a sporeNode's compute is only triggered when we modify spores.
If nothing is modified the node state will be cached. 
Hence, the underlying idea is to have a lot of sporeNodes, each connected to it's own
instancer node. This breaks up computation into small chunks and prevents long computation
times even if you have millions of points distributed over all your sporeNodes.
Since each sporeNode has its own instancer node attached, viewport preview can optimized
with by simply switching the instancer's LoD mode to bounding box or bounding boxes.
This allows tho hold a large amount of instances without slowing down the viewport too much.

 



# brush shortcuts
- b: modify radius
<!-- - l: draw straight line from point A to point B -->
