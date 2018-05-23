# Spore

Paintable particle node for Maya

Spore is a set of Maya plug-ins and scripts.
The Spore toolset is based on the **sporeNode** and **sporeContext**.

The **sporeNode** is a custom locator node that produces an *instanceData*
attribute which is designed to be hooked to Maya's particle instancer node.

The **sporeContext** is designed to place and manipulate points in the *instanceData* attribute.

# Motivation

While particle instancing in Maya is an popular way to populate environments,
the means of manipulating per particle attributes with particles are limited
and require some specific knowledge.

Spore tries to create a more intuitive interface to manipulating points that drive
Maya's particles instancer.


# Installation

1. clone the git repo
```
git clone https://github.com/wiremas/spore
```
2. edit the spore.mod file to match the location on you machine:
```
spore any /path/to/spore/spore
```
3. make sure the spore.mod file is in your MAYA_MODULE_PATH


# Dependencies
In order to run **spore** you need scypy and numpy



# SporeNode

The **sporeNode** produces an **instanceData** attribute that is designed to be hooked
to an instancer node.

In order for the node to work it needs a poly mesh connected to the inMesh attribute.

### Brush Menu

### Emit Menu

The *sporeNode* features three different sampling types:
1. random sampling
2. jitter grid 
3. poisson disk sampling

For now all sampler are implemented in Python which is not really ideal in terms
of speed. To accelerate sampling, meshes that are connected to a sporeNode will cached
as triangle meshs in memory. These cache objects are shared between nodes which means
that you have to cache each mesh only once even if you create multiple sporeNode instances
for a single mesh.
Note: When the mesh deformes or moves the cache is not updated automatically. To force a
cache update uncheck the sporeNode's "isCached" attribute.
Note: Depending on your mesh size, caching might take a few seconds.

### Instance Objects Menu

Quick acces to adding/removing objects to the instancer
The list mirrors the list of source objects usually displayed in the instancer node.
The *sporeNode* allows to directly add and remove instances.

Selecting objects from the list while painting enable *Exclusive Mode*.
In *Exclusive Mode* only the selected objects IDs are considered for painting.

# sporeContex

The *sporeContext* is an interactive brush tool that can manipulate the sporeNode's 
"instanceData" attributes. The context features six differen modes + modifiers.
Depending on the active context mode different brush controls are available directly
on the sporeNode.

### Place Mode

Place a singe instance per brush tick
Shift: activate drag mode
Meta: align to stroke direction

### Spray Mode

Place n instances per brush tick within the given radius
Shift: activate drag mode
Meta: align to stroke direction

### Scale Mode

Scale all instance within the given radius
Shift: smooth scale
Meta: randomize scale

### Align Mode

Align all instances within the given radius to the specified axis

### Id Mode

Set the objectIndex of all instance within the radius to the specified ID

### Delete Mode

Remove all instances within the given radius

### Exclusive Mode
In **Exclusive Mode** the context works only on certain objectIndex IDs.
To activate **Exclusive Mode** select the desired sources objects in the
sporeNode's instance object list.


# sporeManager
The **sporeManager** is a handy little gui to interface to all available *sporeNodes* 
in the scene. This allows artists to rapidly switch between different setups.


