

from maya import cmds

def reload_plugin():
    if cmds.pluginInfo('geoEmitter', q=True, l=True):
        cmds.unloadPlugin('geoEmitter')
    cmds.loadPlugin('/Users/anno/Environment/maya/emitterNode/build/src/Debug/geoEmitter.bundle')

def create_geo_emitter():
    emitter_node = cmds.createNode('simpleEmitter')
    particle_node = cmds.nParticle()
    connect_emitter(emitter_node, particle_node[1])


def connect_emitter(emitter_shape, particle_shape):
    cmds.connectAttr('{}.output[0]'.format(emitter_shape), '{}.newParticles[0]'.format(particle_shape))
    cmds.connectAttr('{}.inheritFactor'.format(particle_shape), '{}.inheritFactor[0]'.format(emitter_shape))
    cmds.connectAttr('{}.isFull'.format(particle_shape), '{}.isFull[0]'.format(emitter_shape))
    cmds.connectAttr('{}.startTime'.format(particle_shape), '{}.startTime[0]'.format(emitter_shape))
    cmds.connectAttr('{}.timeStepSize'.format(particle_shape), '{}.deltaTime[0]'.format(emitter_shape))
    cmds.connectAttr('{}.seed[0]'.format(particle_shape), '{}.seed[0]'.format(emitter_shape))

reload_plugin()
create_geo_emitter()


def reload_plugin(plugin_name, plugin_path):
    if cmds.pluginInfo(plugin_name, q=True, l=True):
        cmds.unloadPlugin(plugin_name)
    cmds.loadPlugin(plugin_path)

reload_plugin("geoEmitter", "/Users/anno/Dropbox/Anno/work/tools/sandbox/maya/emitterNode/build/src/Debug/geoEmitter.bundle")
cmds.createNode("geoEmitter")




from maya import cmds

def reload_plugin(plugin_name, plugin_path):
    if cmds.pluginInfo(plugin_name, q=True, l=True):
        cmds.unloadPlugin(plugin_name)
    cmds.loadPlugin(plugin_path)


reload_plugin("geoEmitter", "/Users/anno/Dropbox/Anno/work/tools/sandbox/maya/emitterNode/build/src/Debug/geoEmitter.bundle")


instancer = cmds.instancer()
node = cmds.createNode("affects")
cmds.connectAttr(node + '.instanceData', instancer + '.inputPoints')
