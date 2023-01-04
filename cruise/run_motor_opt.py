from fe_csdl_opt.fea.fea_dolfinx import *
from fe_csdl_opt.csdl_opt.fea_model import FEAModel
from fe_csdl_opt.csdl_opt.state_model import StateModel
from fe_csdl_opt.csdl_opt.output_model import OutputModel
import numpy as np
import csdl

from csdl_om import Simulator as om_simulator
from python_csdl_backend import Simulator as py_simulator
from matplotlib import pyplot as plt

from electric_motor_mdo.high_fidelity.geometry.motor_mesh_class import MotorMesh
from electric_motor_mdo.high_fidelity.motor_model_class_hf import HFMotorClass

import time 

pi = np.pi

# ===== GEOMETRY PRE-PROCESSING =====
p = 12 # poles
shift = 15 # angular rotor shift in degrees (ccw)
# mech_angles_deg = np.arange(0,30+1,5)
mech_angles_deg = np.arange(0,10+1,3)
rotor_rotations = mech_angles_deg[:1]
instances = len(rotor_rotations)
mech_angles = (shift+rotor_rotations)*pi/180
# elec_angles = ((shift+rotor_rotations) * pi/180) * p/2
elec_angles = ((rotor_rotations) * pi/180) * p/2

coarse_test = False # changes element size of mesh

if coarse_test:
    mesh_file_dir = 'mesh_files_coarse'
    mesh_file_name = 'motor_mesh_test'
    mesh_file_path = mesh_file_dir + '/' + mesh_file_name
    if not os.path.isdir(mesh_file_dir):
        os.mkdir(mesh_file_dir)
    mm = MotorMesh(
        file_name=mesh_file_path,
        popup=False,
        rotation_angles=rotor_rotations* pi/180,
        base_angle=shift*pi/180,
        test=True
    )
else:
    mesh_file_dir = 'mesh_files'
    mesh_file_name = 'motor_mesh'
    mesh_file_path = mesh_file_dir + '/' + mesh_file_name
    if not os.path.isdir(mesh_file_dir):
        os.mkdir(mesh_file_dir)
    mm = MotorMesh(
        file_name=mesh_file_path,
        popup=False,
        rotation_angles=rotor_rotations* pi/180,
        base_angle=shift*pi/180,
    )

mm.baseline_geometry=True
# mm.test_ffd_only=True
mm.create_motor_mesh()

# exit()
m = mm.motor_mesh_object
A_z_eval_points = mm.A_z_eval_points # COORDINATES FOR FLUX LINKAGE EVALUATION
parametrization_dict = mm.ffd_param_dict
original_motor_dim = mm.original_motor_dim
unique_sp_list = sorted(set(parametrization_dict['shape_parameter_list_input']))

motor = HFMotorClass(poles=p, slots=p*3, parametrization_dict=parametrization_dict,
                mechanical_angles=mech_angles, electrical_angles=elec_angles,
                A_z_eval_points=A_z_eval_points, mesh_file_path=mesh_file_path, 
                original_motor_dim=original_motor_dim
)

design_variables = {
    'shaft_radius_dv': {'lower': -15.e-3, 'upper': 10.e-3, 'scaler': 1.0},
    'magnet_thickness_dv': {'lower': -2.e-3, 'upper': 2.e-3, 'scaler': 1.e3}, # DON'T CHANGE
    'rotor_yoke_thickness_dv': {'lower': -5.e-3, 'upper': 10.e-3, 'scaler': 1.e3},
    'rotor_magnet_gap_dv': {'lower': -0.5e-3, 'upper': 1.5e-3, 'scaler': 1.e3}, # DON'T CHANGE
    'magnet_width_dv': {'lower': -0.07*pi/6, 'upper': 0.07*pi/6, 'scaler': 1.e3}, # bounds of OM 0.03-0.04
    'air_gap_dv': {'lower': -0.5e-3, 'upper': 1.5e-3, 'scaler': 1.e3}, # -0.5 to 1.5 mm, DON'T CHANGE
    'stator_shoe_thickness_dv': {'lower': -0.5e-3, 'upper': 1.e-3, 'scaler': 1.e3},
    'winding_height_dv': {'lower': -2.5e-3, 'upper': 5.e-3, 'scaler': 1.e3},
    'stator_yoke_thickness_dv': {'lower': -5e-3, 'upper': 5e-3, 'scaler': 1.e3},
    'slot_width_dv': {'lower': -0.05*pi/18, 'upper': 0.05*pi/18, 'scaler': 1.e2}, # bounds of OM 0.008
    'motor_length': {'lower': 0.06, 'upper': 0.08, 'scaler': 1.e2},
    'current_amplitude': {'lower': 100., 'upper': 300., 'scaler': 1.e-2},
}

for key in design_variables.keys():
    print(key)
    motor.add_input(key)
# motor.add_input('shaft_radius_dv')
# motor.add_input('magnet_thickness_dv')
# motor.add_input('rotor_yoke_thickness_dv')
# motor.add_input('rotor_magnet_gap_dv')
# motor.add_input('magnet_width_dv')
# motor.add_input('air_gap_dv')
# motor.add_input('stator_shoe_thickness_dv')
# motor.add_input('winding_height_dv')
# motor.add_input('stator_yoke_thickness_dv')
# motor.add_input('slot_width_dv')

# motor.add_input('motor_length')
# motor.add_input('current_amplitude')
motor.add_dv_dictionary(design_variables)
motor_model = motor.create_motor_model()

# motor_model.add_objective('efficiency', scaler=-1.)
motor_model.add_objective('total_mass', scaler=1e-3)
# for dv in design_variables.keys():
#     motor_model.add_design_variable(
#         dv,
#         lower=design_variables[dv]['lower'],
#         upper=design_variables[dv]['upper'],
#         scaler=design_variables[dv]['scaler'],
#     )


current_amp = 100.
sim =  py_simulator(motor_model, display_scripts=False)
# sim =  om_simulator(motor_model)
# sim['magnet_pos_delta_dv'] = -0.0002

# sim['shaft_radius_dv'] = -0.001 
# sim['air_gap_dv'] = 0.001
# sim['magnet_width_dv'] = 0.01
sim['current_amplitude'] = current_amp
sim['motor_length'] = 0.07
sim['rpm'] = 882.449599 * 4.
sim['output_torque_from_rotor'] = 1792.64 / 4

# sim.run()
# exit()

from modopt.csdl_library import CSDLProblem
from modopt.snopt_library import SNOPT
from modopt.scipy_library import SLSQP
from motor_dash_paper import MotorDashboard

dashboard = MotorDashboard(instances=instances)
sim.add_recorder(dashboard.get_recorder())

prob = CSDLProblem(
    problem_name='cruise',
    simulator=sim,
)

optimizer = SNOPT(
    prob, 
    Major_iterations = 100,
    Major_optimality=1e-6, 
    Major_feasibility=1e-6,
    append2file=True,
)

# optimizer = SLSQP(prob, maxiter=20, ftol=1e-8)

# Solve your optimization problem
opt_start = time.time()
optimizer.solve()
opt_end = time.time()
print('Time for optimization to finish (seconds):', opt_end - opt_start)

# Print results of optimization
optimizer.print_results()

# region: asdf

# endregion

if False:
    fea_list = motor.fea_list
    fea = fea_list[0][1]
    V = fea.state_function_space

    import pyvista
    from dolfinx.plot import create_vtk_mesh

    plotter = pyvista.Plotter()
    Az_grid = pyvista.UnstructuredGrid(*create_vtk_mesh(V))
    Az_grid.point_data["A_z"] = sim['instance_model_1.A_z']
    Az_grid.set_active_scalars("A_z")
    actor = plotter.add_mesh(Az_grid, show_edges=True)
    # if not pyvista.OFF_SCREEN:
    #     plotter.show()

    # mesh = motor.mesh_list[0]

    # from dolfinx import io
    # with io.VTKFile(mesh.comm, "output.pvd", "w") as vtk:
    #     vtk.write([uh._cpp_object])
    # with io.XDMFFile(mesh.comm, "output.xdmf", "w") as xdmf:
    #     xdmf.write_mesh(mesh)
    #     xdmf.write_function(uh)
    # vtkfile_A_z = File('solutions/'+file_name+'/Magnetic_Vector_Potential_{}_{}.pvd'.format(current_amp,i+1))
    # vtkfile_B = File('solutions/'+file_name+'/Magnetic_Flux_Density_{}_{}.pvd'.format(current_amp,i+1))
    # vtkfile_A_z << fea_list[i].A_z
    # vtkfile_B << fea_list[i].B
    # sim.check_partials()