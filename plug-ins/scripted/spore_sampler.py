import sys
import time
import math
import random

import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaRender as omr
import maya.OpenMayaMPx as ompx

import instance_data
import node_utils
import mesh_utils
import render_utils
import brush_state
import logging_util
#  reload(instance_data)
#  reload(render_utils)


K_SAMPLET_TYPE_FLAG = '-t'
K_SAMPLE_TYPE_LONG_FLAG = '-type'
K_NUM_SAMPLES_FLAG = '-n'
K_NUM_SAMPLES_LONG_FLAG = '-numberOfSamples'
K_CELL_SIZE_FLAG = '-c'
K_CELL_SIZE_LONG_FLAG = '-cellSize'
K_MIN_DISTANCE_FLAG = '-r'
K_MIN_DISTANCE_LONG_FLAG = '-minimumRadius'

class Points(object):
    """ conatainer for sampled points.
    holds position, normal, polyid and uv coords """

    def __init__(self):

        self.position = om.MPointArray()
        self.normal = om.MVectorArray()
        self.poly_id = om.MIntArray()
        self.u_coord = [] # om.MDoubleArray()
        self.v_coord = [] # om.MDoubleArray()

    def set_length(self, length):
        """ set length for the point container """

        self.position.setLength(length)
        self.normal.setLength(length)
        self.poly_id.setLength(length)
        self.u_coord = [None] * length
        self.v_coord = [None] * length

    def set(self, index, position, normal, poly_id, u_coord=None, v_coord=None):
        """ set data for the given index """

        self.position.set(position, index)
        self.normal.set(normal, index)
        self.poly_id.set(poly_id, index)
        if u_coord:
            self.u_coord[index] = u_coord
        if v_coord:
            self.v_coord[index] = v_coord

    def remove(self, index):
        self.position.remove(index)
        self.normal.remove(index)
        self.poly_id.remove(index)
        self.u_coord.pop(index)
        self.v_coord.pop(index)

    def __iter__(self):
        """ iterate overer the sampled points """

        for i in xrange(self.position.length()):
            yield ((self.position[i].x, # position
                    self.position[i].y,
                    self.position[i].z),
                   (self.normal[i].x, # normal
                    self.normal[i].y,
                    self.normal[i].z),
                   self.poly_id[i], # poly id
                   self.u_coord[i], # u coord
                   self.v_coord[i]) # v coord

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

        self.logger = logging_util.SporeLogger(__name__)

        # emit attributes
        self.node_name = None
        self.mode = None
        self.use_tex = None
        self.num_samples = None
        self.cell_size = None
        self.min_radius = None
        self.min_radius_2d = None
        self.align_modes = None
        self.align_id = None
        self.strength = None
        self.min_rot = None
        self.max_rot = None
        self.uni_scale = None
        self.min_scale = None
        self.max_scale = None
        self.min_offset = None
        self.max_offset = None
        self.min_altitude = None
        self.max_altitude = None
        self.min_altitude_fuzz = None
        self.max_altitude_fuzz = None
        self.min_slope = None
        self.max_slope = None
        self.slope_fuzz = None
        self.ids = None

    def doIt(self, args):

        self.parse_args(args)
        self.get_settings()

        # check if we can find a geo cache on the node we operate on
        # else build a new one
        obj_handle = om.MObjectHandle(self.target)
        if hasattr(sys, '_global_spore_tracking_dir'):
            if sys._global_spore_tracking_dir.has_key(obj_handle.hashCode()):
                spore_locator = sys._global_spore_tracking_dir[obj_handle.hashCode()]
                self.geo_cache = spore_locator.geo_cache
                self.instance_data = spore_locator._state
            else:
                raise RuntimeError('Could not link to spore node')
        else:
            raise RuntimeError('There is no sporeNode in the scene')

        self.initialize_sampling()
        self.initialize_filtering()

        self.redoIt()

    def redoIt(self):

        self.append_points()

        #  ompx.MPxCommand.clearResult()
        #  ompx.MPxCommand.setResult(['foo', 'bar', 1, 2,])

    def undoIt(self):
        visibility = om.MIntArray()
        for i in range(*self.undo_range):
            self.instance_data.visibility.set(0, i)
            #  visibility.append(0)

        self.instance_data.clean_up()
        self.instance_data.set_state()



    def isUndoable(self):
        return True

    def initialize_sampling(self):
        self.point_data = Points()

        # choose sample operation
        if self.mode == 0: #'random':
            self.random_sampling(self.num_samples)

        elif self.mode == 1: #'jitter':
            self.random_sampling(self.num_samples)
            grid_partition = self.voxelize(self.cell_size)
            valid_points = self.grid_sampling(grid_partition)

        elif self.mode == 2: #'poisson3d':
            self.random_sampling(self.num_samples)
            self.cell_size = self.min_radius / math.sqrt(3)
            grid_partition = self.voxelize(self.cell_size)
            valid_points = self.disk_sampling_3d(self.min_radius, grid_partition, self.cell_size)

        elif self.mode == 3: #'poisson2d':
            self.geo_cache.create_uv_lookup()
            self.disk_sampling_2d(self.min_radius_2d)

        # get sampled points from disk or grid sampling
        if self.mode == 1 or self.mode == 2:
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

    def initialize_filtering(self):
        # texture filter
        if self.use_tex:
            try:
                texture = cmds.listConnections('{}.emitTexture'.format(self.node_name))[0]
            except RuntimeError:
                texture = None

            self.evaluate_uvs()
            self.texture_filter(texture, 0) # TODO - Filter size

        # altitude filter
        if self.min_altitude != 0 or self.max_altitude != 1:
            self.altitude_filter(self.min_altitude, self.max_altitude, self.min_altitude_fuzz, self.max_altitude_fuzz)

        # slope filter
        if self.min_slope != 0 or self.max_slope != 180:
            self.slope_filter(self.min_slope, self.max_slope, self.slope_fuzz)

    def append_points(self):

        # get final rotation, scale and position values
        # append the sampled points to the instance data object
        old_len = len(self.instance_data)
        self.instance_data.set_length(old_len + len(self.point_data))
        for i, (position, normal, poly_id, u_coord, v_coord) in enumerate(self.point_data):
            position = om.MPoint(position[0], position[1], position[2])
            normal = om.MVector(normal[0], normal[1], normal[2])
            direction = self.get_alignment(self.align_modes[self.align_id], normal)
            rotation = self.get_rotation(direction, self.strength, self.min_rot, self.max_rot)
            scale = self.get_scale(self.min_scale, self.max_scale, self.uni_scale)
            position = self.get_offset(position, self.min_offset, self.max_offset, normal)
            tangent = mesh_utils.get_tangent(normal)
            instance_id = random.choice(self.ids)
            index = old_len + i

            if not u_coord:
                u_coord = 0
            if not v_coord:
                v_coord = 0

            # set points
            self.instance_data.set_point(index,
                                    om.MVector(position),
                                    scale,
                                    rotation,
                                    instance_id,
                                    1,
                                    normal,
                                    tangent,
                                    u_coord,
                                    v_coord,
                                    poly_id,
                                    om.MVector(0, 0, 0))

        self.instance_data.set_state()

        self.undo_range = (old_len, len(self.instance_data))

        #  t_result = time.time() - t1
        #  self.logger.debug('Sampling {} points in self.mode {} took {}s.'.format(i+1, self.mode, t_result))


    def get_settings(self):
        """ get emit attributes from node """

        # get sample settings from the spore node
        # shouldn use maya commands here but i was lazy
        self.node_name = om.MFnDependencyNode(self.target).name()
        self.mode = cmds.getAttr('{}.emitType'.format(self.node_name))
        self.use_tex = cmds.getAttr('{}.emitFromTexture'.format(self.node_name))
        self.num_samples = cmds.getAttr('{}.numSamples'.format(self.node_name))
        self.cell_size = cmds.getAttr('{}.cellSize'.format(self.node_name))
        self.min_radius = cmds.getAttr('{}.minRadius'.format(self.node_name))
        self.min_radius_2d = cmds.getAttr('{}.minRadius2d'.format(self.node_name))
        self.align_modes = ['normal', 'world', 'object', 'stroke']
        self.align_id = cmds.getAttr('{}.alignTo'.format(self.node_name))
        self.strength = cmds.getAttr('{}.strength'.format(self.node_name))
        self.min_rot = cmds.getAttr('{}.minRotation'.format(self.node_name))[0]
        self.max_rot = cmds.getAttr('{}.maxRotation'.format(self.node_name))[0]
        self.uni_scale = cmds.getAttr('{}.uniformScale'.format(self.node_name))
        self.min_scale = cmds.getAttr('{}.minScale'.format(self.node_name))[0]
        self.max_scale = cmds.getAttr('{}.maxScale'.format(self.node_name))[0]
        self.min_offset = cmds.getAttr('{}.minOffset'.format(self.node_name))
        self.max_offset = cmds.getAttr('{}.maxOffset'.format(self.node_name))
        self.min_altitude = cmds.getAttr('{}.minAltitude'.format(self.node_name))
        self.max_altitude = cmds.getAttr('{}.maxAltitude'.format(self.node_name))
        self.min_altitude_fuzz = cmds.getAttr('{}.minAltitudeFuzz'.format(self.node_name))
        self.max_altitude_fuzz = cmds.getAttr('{}.maxAltitudeFuzz'.format(self.node_name))
        self.min_slope = cmds.getAttr('{}.minSlope'.format(self.node_name))
        self.max_slope = cmds.getAttr('{}.maxSlope'.format(self.node_name))
        self.slope_fuzz = cmds.getAttr('{}.slopeFuzz'.format(self.node_name))
        sel = cmds.textScrollList('instanceList', q=True, si=True)
        seed = cmds.getAttr('{}.seed'.format(self.node_name))
        if sel:
            object_index = [int(s.split(' ')[0].strip('[]:')) for s in sel]
        else:
            elements = cmds.textScrollList('instanceList', q=True, ai=True)
            if not elements:
                raise RuntimeError('No instance geometry selected')

            object_index = [int(e.split(' ')[0].strip('[]:')) for e in elements]
        self.ids = object_index

        # set the random seed and initialize the Points object
        self.set_seed(seed)

    def set_seed(self, seed):
        """ set the random seed for sampling. if the given seed is -1
        the system time will be used
        :param seed: the seed for the random function
        :return: """
        if seed == -1:
            random.seed(None)
        else:
            random.seed(seed)

    """ ---------------------------------------------------------------- """
    """ random sampler """
    """ ---------------------------------------------------------------- """

    def random_sampling(self, num_points):
        """ sample a given number of points on the previously cached triangle
        mesh. note: evaluating uvs on high poly meshes may take a long time """

        if not self.geo_cache.validate_cache():
            in_mesh = node_utils.get_connected_in_mesh(self.target, False)
            self.geo_cache.cache_geometry(in_mesh)

        self.point_data.set_length(num_points)
        [self.sample_triangle(random.choice(self.geo_cache.weighted_ids), i) for i in xrange(num_points)]

    def sample_triangle(self,triangle_id, point_id):
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
    """ disk sampling 3d """
    """ ---------------------------------------------------------------- """

    def disk_sampling_3d(self, min_radius, grid_partition, cell_size):

        in_mesh = node_utils.get_connected_in_mesh(self.target, False)
        bb = om.MFnDagNode(in_mesh).boundingBox()

        # pick randomly an initial point from where we start sampling
        initial_key = random.choice(grid_partition.keys())
        init_p_ref = random.choice(grid_partition[initial_key])

        # create two list for active (not yet processed) and valid (sampled) points
        active = []
        valid_points = [None] * self.w_count * self.h_count * self.d_count

        # append the first point to both lists
        active.append(init_p_ref)
        valid_points[initial_key] = init_p_ref

        while len(active) > 0:

            # pick a random point from the active points list
            p_active_index = int(len(active) * random.random())
            p_active = active[p_active_index]
            # TODO - get each active point only once?

            # normalize the point and get it's x,y,z index in the grid
            p_normalized = self.point_data.position[p_active] - bb.min()
            p_grid_x = int(p_normalized.x / cell_size)
            p_grid_y = int(p_normalized.y / cell_size)
            p_grid_z = int(p_normalized.z / cell_size)

            # assume no point will be found
            found = False

            # try k times to find a new sample
            k = 30
            for i in xrange(k):

                # get neighboring cell
                new_p_x, new_p_y, new_p_z = self.get_valid_neighbouring_cell(p_grid_x, p_grid_y, p_grid_z)

                # get liear index from x,y,z position.
                key = new_p_x + new_p_y * self.w_count + new_p_z * self.w_count * self.h_count

                # check if key is valid and if there isnt already a valid point...
                if grid_partition.has_key(key)\
                and not valid_points[key]:

                    # get a random point from the list associated with the key
                    new_index = int(len(grid_partition[key]) * random.random())
                    point_index = grid_partition[key][new_index]
                    point = self.point_data.position[point_index]

                # ...otherwise try again
                else:
                    continue

                valid = True
                #  print 'sample at cell:', key, 'point id: ', point_index, 'at: ', new_p_x, new_p_y, new_p_z, round(point.x,3), round(point.y,3), round(point.z,3)
                # check against all nearby cells if the sample is valid
                for x in xrange(new_p_x - 1, new_p_x + 2):
                    for y in xrange(new_p_y - 1, new_p_y + 2):
                        for z in xrange(new_p_z - 1, new_p_z + 2):

                            # ignore invalid cells
                            if x < 0 or y < 0 or z < 0:
                                continue
                            elif x > self.w_count - 1 or y > self.h_count - 1 or z > self.d_count -1:
                                continue

                            # get the index for the current cell
                            index = x + y * self.w_count + z * self.w_count * self.h_count

                            # check if there is already a valid point in the cell
                            if index >= 0 and index <= len(valid_points) - 1:
                                if valid_points[index]:
                                    neighbor = self.point_data.position[valid_points[index]]

                                else:
                                    continue
                            else:
                                raise RuntimeError
                                continue

                            # check distance to the next neighbour
                            # if it conflicts tag the point invalid and break
                            # out of the loop
                            distance = point.distanceTo(neighbor)# + min_radius / 10
                            if distance < min_radius: # - (min_radius / 10) :
                                valid = False
                                break

                        if valid is False:
                            break
                    if valid is False:
                        break

                if valid:
                    found = True
                    valid_points[key] = point_index
                    active.append(point_index)

            if not found:
                active.remove(p_active)
                #  active.pop(p_active_index)

        return [i for i in valid_points if i is not None]

    def get_valid_neighbouring_cell(self, p_grid_x, p_grid_y, p_grid_z):
        """ return a neighbouring cell within the range of p-2 to p+2 where
        0 < x/y/z < h/w/d - 1. This ensures that only valid cell will be returned.
        :param p_grid_x: cell x position
        :param p_grid_y: cell y position
        :param p_grid_z: cell z posiiton
        :return: """

        if self.w_count < 5:
            new_p_x = random.randint(0, self.w_count - 1)
        elif p_grid_x <= 2:
            new_p_x = random.randint(0, p_grid_x + 2)
        elif p_grid_x >= self.w_count - 2:
            new_p_x = random.randint(p_grid_x - 2, self.w_count - 1)
        else:
            new_p_x = random.randint(p_grid_x - 2, p_grid_x + 2)

        if self.h_count < 5:
            new_p_y = random.randint(0, self.h_count - 1)
        elif p_grid_y <= 2:
            new_p_y = random.randint(0, p_grid_y + 2)
        elif p_grid_y >= self.h_count - 2:
            new_p_y = random.randint(p_grid_y - 2, self.h_count - 1)
        else:
            new_p_y = random.randint(p_grid_y - 2, p_grid_y + 2)

        if self.d_count < 5:
            new_p_z = random.randint(0, self.d_count - 1)
        elif p_grid_z <= 2:
            new_p_z = random.randint(0, p_grid_z + 2)
        elif p_grid_z >= self.d_count - 2:
            new_p_z = random.randint(p_grid_z - 2, self.d_count - 1)
        else:
            new_p_z = random.randint(p_grid_z - 2, p_grid_z + 2)

        if new_p_x < 0 or new_p_y < 0 or new_p_z < 0:
            raise RuntimeError
        elif new_p_x > self.w_count - 1 or new_p_y > self.h_count - 1 or new_p_z > self.w_count - 1:
            raise RuntimeError

        return new_p_x, new_p_y, new_p_z

    """ ---------------------------------------------------------------- """
    """ disk sampling 2d """
    """ ---------------------------------------------------------------- """

    def disk_sampling_2d(self, radius, u=1, v=1):
        """ sample poisson disk samples in uv space
        note: the given radius must be between 0 and 1 """
        #  def poisson(radius, k, w, h, n):

        # TODO - make uv sample space editable for user

        grid = []
        active = []
        ordered = []

        cellsize = radius / math.sqrt(2)

        col = int(u / cellsize)
        row = int(v / cellsize)

        grid = [None] * col * row

        x = random.random() * u  # random.uniform( 0, w )
        y = random.random() * v  # random.uniform( 0, h )
        pos = (x, y)

        current_col = int(x / cellsize)
        current_row = int(y / cellsize)

        grid[current_col + current_row * col] = pos
        active.append(pos)
        ordered.append(pos)

        while len(active) > 0:

            rand_index = int(len(active) - 1)
            active_pos = active[rand_index]
            found = False

            k = 30
            for each in xrange(k):

                # find a new point withhin a the range of radius - 2r
                rand_distance = random.uniform(radius, 2 * radius)
                theta = 360 * random.random()
                offset_x = math.cos(theta) * rand_distance
                offset_y = math.sin(theta) * rand_distance

                # get the absolut position of the new pos
                new_x = active_pos[0] + offset_x
                new_y = active_pos[1] + offset_y
                new_pos = (new_x, new_y)

                # get the new col & row position of the point
                active_col = int(new_x / cellsize)
                active_row = int(new_y / cellsize)

                if active_col > 0 \
                and active_row > 0 \
                and active_col < col \
                and active_row < row \
                and not grid[active_col + active_row * col]:

                    valid = True
                    for j in xrange(-1, 2):
                        for f in xrange(-1, 2):
                            index = (active_col + j) + (active_row + f) * col
                            try:
                                neighbor = grid[index]
                            except IndexError:
                                continue
                            if neighbor:
                                distance = math.sqrt((neighbor[0] - new_pos[0]) ** 2 + (neighbor[1] - new_pos[1]) ** 2)
                                if (distance < radius):
                                    valid = False

                    if valid:
                        found = True
                        grid[active_col + active_row * col] = new_pos
                        active.append(new_pos)
                        ordered.append(new_pos)

                        # TODO

            if not found:
                active.pop(rand_index)

        self.point_data.set_length(len(ordered))

        util = om.MScriptUtil()
        in_mesh = node_utils.get_connected_in_mesh(self.target, False)
        mesh_fn = om.MFnMesh(in_mesh)

        for i, (u_coord, v_coord) in enumerate(ordered):

            face_ids = self.geo_cache.get_close_face_ids(u_coord, 1 - v_coord)

            position = om.MPoint()
            normal = om.MVector()
            for face_id in face_ids:
                util.createFromList([u_coord, 1 - v_coord], 2)
                ptr = util.asFloat2Ptr()

                try:
                    mesh_fn.getPointAtUV(face_id, position, ptr, om.MSpace.kWorld)
                    mesh_fn.getClosestNormal(position, normal)
                    self.point_data.set(i, position, normal, 1, u_coord, 1 - v_coord)
                except:
                    continue



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

    def evaluate_uvs(self):
        """ evaluate uv coords for all points in point data.
        note: this may take a long time for large meshes """

        in_mesh = node_utils.get_connected_in_mesh(self.target, False)

        for i, (position, normal, poly_id, u_coord, v_coord) in enumerate(self.point_data):
            if not u_coord and not v_coord:

                pos = om.MPoint(position[0], position[1], position[2])
                u_coord, v_coord = mesh_utils.get_uv_at_point(in_mesh, pos)

                self.point_data.u_coord[i] = u_coord
                self.point_data.v_coord[i] = v_coord

    """ ---------------------------------------------------------------- """
    """ filtering """
    """ ---------------------------------------------------------------- """

    def texture_filter(self, node, filter_size):
        """ filter points based on the input texture attribute """

        if not node:
            raise RuntimeError('No input shading node given')

        color, alpha = render_utils.sample_shading_node(node, self.point_data)
        invalid_ids = []
        gamma = 2.2
        for i, val in enumerate(color):
            val = val[0]
            if val < 0 or val > 1:
                val = max(min(1, val), 0)

            if val ** (1/gamma) > random.random():
                invalid_ids.append(i)

        invalid_ids = sorted(invalid_ids, reverse=True)
        [self.point_data.remove(index) for index in invalid_ids]

    def altitude_filter(self, min_altitude, max_altitude, min_fuzziness, max_fuzziness):
        """ filter points based on y position relative to bounding box """

        in_mesh = node_utils.get_connected_in_mesh(self.target, False)
        dag_fn = om.MFnDagNode(in_mesh)

        bb = dag_fn.boundingBox()
        bb_y_min = bb.min().y
        height = bb.height()

        invalid_ids = []
        for i, (position, _, _, _, _) in enumerate(self.point_data):
            y_normalized = position[1] - bb_y_min
            pos_rel = y_normalized / height

            if pos_rel < min_altitude:
                if pos_rel < min_altitude - min_fuzziness:
                    invalid_ids.append(i)

                elif min_altitude - pos_rel > random.uniform(0, min_fuzziness):
                    invalid_ids.append(i)

            elif pos_rel > max_altitude:
                if pos_rel > max_altitude + max_fuzziness:
                    invalid_ids.append(i)

                elif abs(max_altitude - pos_rel) > random.uniform(0, max_fuzziness):
                    invalid_ids.append(i)

        invalid_ids = sorted(invalid_ids, reverse=True)
        [self.point_data.remove(index) for index in invalid_ids]

    def slope_filter(self, min_slope, max_slope, fuzz):

        world = om.MVector(0, 1, 0)

        invalid_ids = []
        for i, (_, normal, _, _, _) in enumerate(self.point_data):
            normal = om.MVector(normal[0], normal[1], normal[2])
            angle = math.degrees(normal.angle(world)) + 45 * random.uniform(-fuzz, fuzz)

            if angle < min_slope or angle > max_slope:
                invalid_ids.append(i)

        invalid_ids = sorted(invalid_ids, reverse=True)
        [self.point_data.remove(index) for index in invalid_ids]


        pass






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
                    3: 'poisson2d'}

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


