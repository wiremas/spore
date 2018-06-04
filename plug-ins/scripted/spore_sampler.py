import math, sys, random
import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx

import instance_data
import node_utils
import mesh_utils
import brush_state
reload(instance_data)


K_SAMPLET_TYPE_FLAG = '-t'
K_SAMPLE_TYPE_LONG_FLAG = '-type'
K_NUM_SAMPLES_FLAG = '-n'
K_NUM_SAMPLES_LONG_FLAG = '-numberOfSamples'
K_CELL_SIZE_FLAG = '-c'
K_CELL_SIZE_LONG_FLAG = '-cellSize'
K_MIN_DISTANCE_FLAG = '-r'
K_MIN_DISTANCE_LONG_FLAG = '-minimumRadius'

class Points(object):
    def __init__(self):
        self.position = om.MPointArray()
        self.normal = om.MVectorArray()
        self.poly_id = om.MIntArray()
        self.u_coord = om.MDoubleArray()
        self.v_coord = om.MDoubleArray()

    def set_length(self, length):
        self.position.setLength(length)
        self.normal.setLength(length)
        self.poly_id.setLength(length)
        self.u_coord.setLength(length)
        self.v_coord.setLength(length)

    def set(self, index, position, normal, poly_id, u_coord, v_coord):
        self.position.set(position, index)
        self.normal.set(normal, index)
        self.poly_id.set(poly_id, index)
        self.u_coord.set(u_coord, index)
        self.v_coord.set(v_coord, index)

    def __iter__(self):
        for i in xrange(self.position.length()):
            yield ((self.position[i].x,
                    self.position[i].y,
                    self.position[i].z),
                   (self.normal[i].x,
                    self.normal[i].y,
                    self.normal[i].z),
                   self.poly_id[i])

    def __len__(self):
        return self.position.length()


# command
class SporeSampler(ompx.MPxCommand):
    name = 'sporeSampleCmd'

    def __init__(self):
        ompx.MPxCommand.__init__(self)
        self.target = None
        self.settings = None

        self.sample_type = None
        self.num_samples = None
        self.cell_size = None
        self.min_distance = None

    def doIt(self, args):
        self.parse_args(args)
        self.redoIt()

    def redoIt(self):
        print self.sample_type, self.num_samples, self.cell_size, self.min_distance

        # check if we can find a geo cache on the node we operate on
        # else build a new one
        obj_handle = om.MObjectHandle(self.target)
        if hasattr(sys, '_global_spore_tracking_dir'):
            if sys._global_spore_tracking_dir.has_key(obj_handle.hashCode()):
                spore_locator = sys._global_spore_tracking_dir[obj_handle.hashCode()]
                self.geo_cache = spore_locator.geo_cache
                instance_data = spore_locator._state
            else:
                raise RuntimeError('Could not link to spore node')
        else:
            raise RuntimeError('There is no sporeNode in the scene')

        # get sample settings from the spore node
        node_name = om.MFnDependencyNode(self.target).name()
        mode = cmds.getAttr('{}.emitType'.format(node_name))
        use_tex = cmds.getAttr('{}.emitFromTexture'.format(node_name))
        tex = cmds.getAttr('{}.emitTexture'.format(node_name))
        num_samples = cmds.getAttr('{}.numSamples'.format(node_name))
        cell_size = cmds.getAttr('{}.cellSize'.format(node_name))
        min_radius = cmds.getAttr('{}.minRadius'.format(node_name))
        align_modes = ['normal', 'world', 'object', 'stroke']
        align_id = cmds.getAttr('{}.alignTo'.format(node_name))
        strength = cmds.getAttr('{}.strength'.format(node_name))
        min_rot = cmds.getAttr('{}.minRotation'.format(node_name))[0]
        max_rot = cmds.getAttr('{}.maxRotation'.format(node_name))[0]
        uni_scale = cmds.getAttr('{}.uniformScale'.format(node_name))
        min_scale = cmds.getAttr('{}.minScale'.format(node_name))[0]
        max_scale = cmds.getAttr('{}.maxScale'.format(node_name))[0]
        scale_factor = cmds.getAttr('{}.scaleFactor'.format(node_name))
        scale_amount = cmds.getAttr('{}.scaleAmount'.format(node_name))
        min_offset = cmds.getAttr('{}.minOffset'.format(node_name))
        max_offset = cmds.getAttr('{}.maxOffset'.format(node_name))
        sel = cmds.textScrollList('instanceList', q=True, si=True)
        if sel:
            object_index = [int(s.split(' ')[0].strip('[]:')) for s in sel]
        else:
            elements = cmds.textScrollList('instanceList', q=True, ai=True)
            object_index = [int(e.split(' ')[0].strip('[]:')) for e in elements]
        ids = object_index


        #  self.point_data = instance_data.InstanceData(self.target)
        self.point_data = Points()

        if mode == 0: #'random':
            self.random_sampling(num_samples, evaluate_uvs=use_tex)

        elif mode == 1: #'jitter':
            self.random_sampling(num_samples, evaluate_uvs=use_tex)
            #  print len(self.point_data)
            grid_partition = self.voxelize(cell_size)
            for key, val in grid_partition.iteritems():
                print key, val
            valid_points = self.grid_sampling(grid_partition)
            print 'valid pts', valid_points

        elif mode == 2: #'poisson3d':
            self.random_sampling(num_samples, evaluate_uvs=use_tex)
            cell_size = min_radius / math.sqrt(3)
            grid_partition = self.voxelize(cell_size)
            for key, val in grid_partition.iteritems():
                print key, val
            valid_points = self.disk_sampling(min_radius, grid_partition, cell_size)

        elif mode == 3: #'poisson2d':
            pass

        else:
            raise RuntimeError('Invalid sample mode. Legal keys are \'random\', \'jitter\', \'poisson2d\' or \'poisson3d\'')

        # get sampled points from disk or grid sampling
        if mode == 1 or mode == 2:
            point_data = Points()
            point_data.set_length(len(valid_points))
            for i, index in enumerate(valid_points):
                point_data.set(i,
                               self.point_data.position[index],
                               self.point_data.normal[index],
                               self.point_data.poly_id[index],
                               self.point_data.u_coord[index],
                               self.point_data.v_coord[index])

            self.point_data = point_data

        # get final rotation, scale and position values
        old_len = len(instance_data)
        instance_data.set_length(old_len + len(self.point_data))

        for i, (position, normal, poly_id) in enumerate(self.point_data):
            position = om.MPoint(position[0], position[1], position[2])
            normal = om.MVector(normal[0], normal[1], normal[2])

            direction = self.get_alignment(align_modes[align_id], normal)
            rotation = self.get_rotation(direction, strength, min_rot, max_rot)
            scale = self.get_scale(min_scale, max_scale, uni_scale)
            position = self.get_offset(position, min_offset, max_offset, normal)
            tangent = mesh_utils.get_tangent(normal)
            instance_id = random.choice(ids)
            index = old_len + i

            instance_data.set_point(index,
                                    om.MVector(position),
                                    scale,
                                    rotation,
                                    instance_id,
                                    1,
                                    normal,
                                    tangent,
                                    0, 0,
                                    poly_id,
                                    om.MVector(0, 0, 0))

        instance_data.set_state()

    """ ---------------------------------------------------------------- """
    """ random sampler """
    """ ---------------------------------------------------------------- """

    def random_sampling(self, num_points, seed=-1, evaluate_uvs=False):
        """ sample a given number of points on the previously cached triangle
        mesh. note: evaluating uvs on high poly meshes may take a long time """

        random.seed(seed)
        self.point_data.set_length(num_points)
        [self.sample_triangle(random.choice(self.geo_cache.weighted_ids), i, evaluate_uvs) for i in xrange(num_points)]

    def sample_triangle(self,triangle_id, point_id, evaluate_uvs):
        """ sample a random point on a the given triangle """

        r = random.random()
        s = random.random()

        if r + s >= 1:
            r = 1 - r
            s = 1 - s

        r = om.MScriptUtil(r).asFloat()
        s = om.MScriptUtil(s).asFloat()

        r = self.geo_cache.AB[triangle_id] * r
        s = self.geo_cache.AC[triangle_id] * s

        p = om.MPoint(r + s + om.MVector(self.geo_cache.p0[triangle_id]))

        if evaluate_uvs:
            uv_coord = self.util.asFloat2Ptr()
            self.mesh_fn.getUVAtPoint(p, uv_coord, om.MSpace.kWorld, None,
                                      om.MScriptUtil().createFromInt(self.geo_cache.poly_id[triangle_id]))

            u = om.MScriptUtil.getFloat2ArrayItem(uv_coord, 0, 0)
            v = om.MScriptUtil.getFloat2ArrayItem(uv_coord, 0, 1)

        else:
            u = 0
            v = 0

        self.point_data.set(point_id, p, self.geo_cache.normals[triangle_id],
                            self.geo_cache.poly_id[triangle_id], u, v)

    """ ---------------------------------------------------------------- """
    """ grid sampling """
    """ ---------------------------------------------------------------- """

    def grid_sampling(self, grid_partition):
        """ randomly choose one point from each grid cell and
        return a list of ids that associate a point in the point_data obj """

        #  point_data = Points()
        #  point_data.set_length(len(grid_partition))

        ids = []
        for key, val in grid_partition.iteritems():
            ids.append(random.choice(val))

        return sorted(ids)

    """ ---------------------------------------------------------------- """
    """ disk sampling """
    """ ---------------------------------------------------------------- """

    def disk_sampling(self, min_radius, grid_partition, cell_size):

        in_mesh = node_utils.get_connected_in_mesh(self.target, False)
        bb = om.MFnDagNode(in_mesh).boundingBox()

        # pick randomly an initial point from where we start sampling
        initial_key = random.choice(grid_partition.keys())
        init_p_ref = random.choice(grid_partition[initial_key])

        # create two list for active (not yet processed) and valid (sampled) points
        active = []
        valid_points = [None] * self.w_count * self.h_count * self.d_count
        print grid_partition
        print len(valid_points)

        # append the first point to both lists
        active.append(init_p_ref)
        valid_points[initial_key] = init_p_ref

        while len(active) > 0:

            # pick a random point from the active points list
            p_active = random.choice(active)

            # normalize the point and get it's x,y,z index in the grid
            p_normalized = self.point_data.position[p_active] - bb.min()
            p_grid_x = int(p_normalized[0] / cell_size)
            p_grid_y = int(p_normalized[1] / cell_size)
            p_grid_z = int(p_normalized[2] / cell_size)

            # assume no point will be found
            found = False

            # try k times to find a new point to  test against
            k = 30
            for i in xrange(k):

                # get a random nearby cell
                new_p_x = p_grid_x + random.randrange(-1,2,1)
                new_p_y = p_grid_y + random.randrange(-1,2,1)
                new_p_z = p_grid_z + random.randrange(-1,2,1)

                # get grid cell index from x,y,z position. index serves as key for id_table
                key = new_p_x + new_p_y * self.w_count + new_p_z * self.w_count * self.h_count

                # check if key is valid otherwise try again
                if grid_partition.has_key(key)\
                and not valid_points[key]:

                    # get a random point from the list associated with the key
                    new_index = int((len(grid_partition[key]) - 1) * random.random())
                    point = self.point_data.position[new_index]

                else: continue

                valid = True

                # check against all nearby cells if the sample is valid
                for x in xrange(new_p_x - 1, new_p_x + 2):
                    for y in xrange(new_p_y - 1, new_p_y + 2):
                        for z in xrange(new_p_z - 1, new_p_z + 2):

                            # get the index for the current cell
                            index = x + y * self.w_count + z * self.w_count * self.h_count
                            # TODO if index == key > sample invalid

                            # check if there is already a valid point in the cell
                            if index >= 0 and index <= len(valid_points) - 1:
                                if valid_points[index]:
                                    neighbor = self.point_data.position[valid_points[index]]

                                else: continue
                            else: continue

                            # check distance to the next neighbour
                            # if it conflicts tag the point invalid and break
                            # out of the loop
                            distance = point.distanceTo(neighbor)
                            if distance < min_radius:
                                valid = False

                                if grid_partition[key] == []:
                                    grid_partition.pop(key)

                                break
                        if not valid: break
                    if not valid: break

                if valid:
                    found = True
                    valid_points[key] = grid_partition[key][new_index]
                    active.append(grid_partition[key][new_index])

            if not found:
                # TODO remove invalid points from dict
                active.remove(p_active)

        return [i for i in valid_points if i]

    """ ---------------------------------------------------------------- """
    """ spatial utils """
    """ ---------------------------------------------------------------- """

    def voxelize(self, cell_size):
        """ partition the spatial domain with the given cellsize.
        than assign each point to the cell is spatialy belongs to.
        :return dict: where:
                      key == the cell index
                      value == list of points indexes from the point_data obj """

        partition = {}

        in_mesh = node_utils.get_connected_in_mesh(self.target, False)
        bb = om.MFnDagNode(in_mesh).boundingBox()

        self.w_count = int(math.ceil(bb.width() / cell_size))
        self.h_count = int(math.ceil(bb.height() / cell_size))
        self.d_count = int(math.ceil(bb.depth() / cell_size))

        bb_min = bb.min()
        for i in xrange(self.point_data.position.length()):
            p_normalized = self.point_data.position[i] - bb_min
            p_x = int(p_normalized.x / cell_size)
            p_y = int(p_normalized.y / cell_size)
            p_z = int(p_normalized.z / cell_size)

            index = p_x + p_y * self.w_count + p_z * self.w_count * self.h_count
            partition.setdefault(index, []).append(i)

        return partition

    """ ---------------------------------------------------------------- """
    """ transformation utils """
    """ ---------------------------------------------------------------- """

    def get_alignment(self, alignment, normal):
        """ get a vector representing th current alignment mdoe """

        if alignment == 'normal':
            return normal
        elif alignment == 'world':
            return om.MVector(0, 1, 0)
        elif alignment == 'object':
            return node_utils.get_local_rotation(self.target)


    def get_rotation(self, direction, weight, min_rot, max_rot):
        """ get rotation from a matrix pointing towards the given direction
        slerped by the given weight into the world up vector and added a random
        rotation between min and max rotation """

        r_x = math.radians(random.uniform(min_rot[0], max_rot[0]))
        r_y = math.radians(random.uniform(min_rot[1], max_rot[1]))
        r_z = math.radians(random.uniform(min_rot[2], max_rot[2]))
        util = om.MScriptUtil()
        util.createFromDouble(r_x, r_y, r_z)
        rotation_ptr = util.asDoublePtr()

        matrix = om.MTransformationMatrix()
        matrix.setRotation(rotation_ptr, om.MTransformationMatrix.kXYZ)
        world_up = om.MVector(0, 1, 0)
        rotation = om.MQuaternion(world_up, direction, weight)
        matrix = matrix.asMatrix() * rotation.asMatrix()
        rotation = om.MTransformationMatrix(matrix).rotation().asEulerRotation()

        return om.MVector(math.degrees(rotation.x),
                          math.degrees(rotation.y),
                          math.degrees(rotation.z))

    def get_scale(self, min_scale, max_scale, uniform=True):
        """ get scale values between min and max scale """

        if uniform:
            scale_x = scale_y = scale_z = random.uniform(min_scale[0], max_scale[0])
        else:
            scale_x = random.uniform(min_scale[0], max_scale[0])
            scale_y = random.uniform(min_scale[1], max_scale[1])
            scale_z = random.uniform(min_scale[2], max_scale[2])

        return om.MVector(scale_x, scale_y, scale_z)

    def get_offset(self, position, min_offset, max_offset, direction):
        """ get position offest between min and max in a given direction """
        if min_offset != 0 and max_offset != 0:
            offset = random.uniform(min_offset, max_offset)
            return position + direction * offset
        else:
            return position

    def instance_id(self, ids):
        return random.choice(ids)




    def parse_args(self, args):
        """ parse command arguments """

        mode_map = {0: 'random',
                    1: 'jitter',
                    2: 'poisson3d',
                    4: 'poisson2d'}

        arg_data = om.MArgDatabase(self.syntax(), args)

        if arg_data.isFlagSet(K_SAMPLET_TYPE_FLAG):
            self.sample_type = arg_data.flagArgumentString(K_SAMPLET_TYPE_FLAG, 0)
        if arg_data.isFlagSet(K_NUM_SAMPLES_FLAG):
            self.num_samples = arg_data.flagArgumentInt(K_NUM_SAMPLES_FLAG, 0)
        if arg_data.isFlagSet(K_CELL_SIZE_FLAG):
            self.cell_size = arg_data.flagArgumentDouble(K_CELL_SIZE_FLAG, 0)
        if arg_data.isFlagSet(K_MIN_DISTANCE_FLAG):
            self.min_distance = arg_data.flagArgumentDouble(K_MIN_DISTANCE_FLAG, 0)

        selection = om.MSelectionList()
        arg_data.getObjects(selection)
        if selection.length() == 1:
            found = False
            node = om.MObject()
            selection.getDependNode(0, node)
            if node.hasFn(om.MFn.kDependencyNode):
                dg_fn = om.MFnDependencyNode(node)
                if dg_fn.typeName() == 'sporeNode':
                    self.target = node

                    if not self.sample_type:
                        type_plug = dg_fn.findPlug('emitType')
                        self.sample_type = mode_map[type_plug.asShort()]
                    if not self.num_samples:
                        num_plug = dg_fn.findPlug('numSamples')
                        self.num_samples = num_plug.asInt()
                    if not self.cell_size:
                        cell_plug = dg_fn.findPlug('cellSize')
                        self.cell_size = num_plug.asDouble()
                    if not self.min_distance:
                        radius_plug = dg_fn.findPlug('minRadius')
                        self.cell_size = radius_plug.asDouble()

                    found = True

            if not found:
                raise RuntimeError('The sample command only works on sporeNodes')


def creator():
    return ompx.asMPxPtr(SporeSampler())


# Syntax creator
def syntax():
    syntax = om.MSyntax()
    syntax.setObjectType(om.MSyntax.kSelectionList, 1, 1)
    syntax.useSelectionAsDefault(True)
    syntax.addFlag(K_SAMPLET_TYPE_FLAG, K_SAMPLE_TYPE_LONG_FLAG, om.MSyntax.kString)
    syntax.addFlag(K_NUM_SAMPLES_FLAG, K_NUM_SAMPLES_LONG_FLAG, om.MSyntax.kLong)
    syntax.addFlag(K_CELL_SIZE_FLAG, K_CELL_SIZE_LONG_FLAG, om.MSyntax.kLong)
    syntax.addFlag(K_MIN_DISTANCE_FLAG, K_MIN_DISTANCE_LONG_FLAG, om.MSyntax.kLong)
    return syntax


