import numpy as np
import os

pi = np.pi

# region input parameters
p = 12 # poles
shift = 15 # angular rotor shift in degrees (ccw)
mech_angles_deg = np.arange(0,10+1,3)
rotor_rotations = mech_angles_deg[:1]
instances = len(rotor_rotations)
mech_angles = (shift+rotor_rotations)*pi/180
# elec_angles = ((shift+rotor_rotations) * pi/180) * p/2
elec_angles = ((rotor_rotations) * pi/180) * p/2
# endregion

mesh_file_dir = 'grid_indep'
if not os.path.isdir(mesh_file_dir):
    os.mkdir(mesh_file_dir)
mesh_file_base = 'motor_mesh'
mesh_file_base_dir = mesh_file_dir + '/' + mesh_file_base

# region mesh size list
l1_list = [6.e-3, 1.e-2]
l2_list = [3.e-3, 1.e-2]
l3_list = [1.5e-3, 5.e-3]
l4_list = [5.e-4, 1.e-3]
# endregion
