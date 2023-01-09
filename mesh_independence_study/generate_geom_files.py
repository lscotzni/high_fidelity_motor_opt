import numpy as np
import os  
from electric_motor_mdo.high_fidelity.geometry.motor_mesh_class import MotorMesh
from input_parameters import *

angles = rotor_rotations

for a, l1 in enumerate(l1_list):
    for b, l2 in enumerate(l2_list):
        for c, l3 in enumerate(l3_list):
            for d, l4 in enumerate(l4_list):
                file_name = mesh_file_base_dir + '_{}'.format(a) + \
                '_{}'.format(b) + '_{}'.format(c) + '_{}'.format(d)

                mm = MotorMesh(
                    file_name=file_name,
                    popup=False,
                    rotation_angles=angles*pi/180,
                    base_angle=shift*pi/180
                )
                mm.l1 = l1
                mm.l2 = l2
                mm.l3 = l3
                mm.l4 = l4

                mm.baseline_geometry=True
                mm.create_motor_mesh()