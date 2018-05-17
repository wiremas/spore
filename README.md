# spore
paintable particle node for Maya

Spore is a set of Maya plug-ins and scripts. The Spore toolset is centered
around the **sporeNode** and **sporeContext**.

The **sporeNode** is a custom locator node that produces an *instanceData*
attribute which is designed to be hooked to Maya's particle instancer node.

The **sporeContext** is designed to place and manipulate points in the *instanceData* attribute.


# motivation

While particle instancing in Maya is an popular way to populate environments,
the means of manipulating per particle attributes with particles are limited
and require some specific knowledge.

Spore tries to create a more intuitive interface to manipulating points.


# installation

1. clone the git repo
```
git clone https://github.com/wiremas/spore
```
2. edit the spore.mod file to match the location on you machine:
```
+ spore any /path/to/spore/spore
```
3. make sure the spore.mod file is in you MAYA_MODULE_PATH


# sporeNode

#h3 Brush Menu

#h3 Emit Menu

The *sporeNode* features three different sampling types:
1. random sampling
2. jitter grid 
3. poisson disk sampling

#h3 Instance Objects Menu

Quick acces to adding/removing objects to the instancer
note: selecting items in the list activates *Exclusive Paint*

# sporeContex

#h3 Place Mode

Place a singe instance per brush tick
Shift: activate drag mode
Meta: align to stroke direction

#h3 Spray Mode

Place n instances per brush tick within the given radius
Shift: activate drag mode
Meta: align to stroke direction

#h3 Scale Mode

Scale all instance within the given radius
Shift: smooth scale
Meta: randomize scale

#h3 Align Mode

Align all instances within the given radius to the specified axis

#h3 Id Mode

Set the objectIndex of all instance within the radius to the specified ID

#h3 Delete Mode

Remove all instances within the given radius

#h3 Exclusive Mode
In **Exclusive Mode** the context works only on certain objectIndex IDs.
To activate **Exclusive Mode** select the desired sources objects in the
sporeNode's instance object list.


# sporeManager
The **sporeManager** is a handy little gui to interface to all *sporeNodes* available
in the scene. Since it's all about having many differen *sporeNodes* that drive different
instancer nodes to create a diverse environment the **sporeManager** lists all *sporeNodes*
connected to a singe object. This allows artist to rapidly switch between different setups.


# Known issues
- pressure mapping not yet implemented
- 

