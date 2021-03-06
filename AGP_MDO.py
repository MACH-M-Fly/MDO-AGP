'''
Aircraft Geometry and Performance Optimzer (AGPO)

Multi-disciplinary Optimization (MDO) program developed for M-Fly that does low-fidelity aerostructural
as well as geometric shape optimization for wing

'''


# Imported from OpenMDAO Library
from __future__ import print_function
from openmdao.api import ExecComp, Component, Group, Problem, IndepVarComp, ScipyOptimizer#, ScipyGMRES
from openmdao.recorders.csv_recorder import CsvRecorder
from openmdao.drivers.pyoptsparse_driver import pyOptSparseDriver
# Imported from Python standard
import sys
import os
import time
import math
import numpy


# Modules
from aero_AVL import aero_AVL
from aero_MTOW import aero_MTOW
from struct_weight import struct_weight
import settings


class AGP_MDO(Group):

	def __init__(self):
		# add parameter
		super(AGP_MDO,self).__init__()

		#=====================================
		# AC Config Library setup
		#=====================================
		
		settings.init('tube-wing-test.txt')

		
		#=====================================
		# Design variables
		#=====================================
		# self.add('b_w', IndepVarComp('b_w', 5.0), promotes=['*']) # Wing Span 
		# self.add('chord_w', IndepVarComp('chord_w',2.0), promotes=['*'])
		# self.add('taper', IndepVarComp('taper', [1.0, 1.0, 1.0, 1.0]), promotes=['*']) # taper ratio
		
		# ----Wing Design Variables-----------
		for i in range(settings.WING):
			if settings.W['W'+str(i+1)][6]:
				key_start = 'wing_' + str(i+1) + '_'
				self.add(key_start+'chord', IndepVarComp(key_start+'chord', settings.W['W' + str(i+1)][2]), promotes=['*'])
				self.add(key_start+'b', IndepVarComp(key_start+'b', settings.W['W' + str(i+1)][3]), promotes=['*'])
				for j in range(settings.W['W' + str(i+1)][4]):
					self.add(key_start+'taper_'+str(j+1), IndepVarComp(key_start+'taper_'+str(j+1), 1.0), promotes=['*'])
					self.add(key_start+'angle_'+str(j+1), IndepVarComp(key_start+'angle_'+str(j+1), 0.0), promotes=['*'])
					#self.add(key_start+'dihedral_'+str(j+1), IndepVarComp(key_start+'dihedral_'+str(j+1), 0.0), promotes=['*'])
					self.add(key_start+'x_offset_'+str(j+1), IndepVarComp(key_start+'x_offset_'+str(j+1), settings.AC_0.wing['wing_' + str(i+1)]['X_offset'][j]), promotes=['*'])

		# ----H tail Design Variables---------
		for i in range(settings.H_TAIL):
			if settings.H['H'+str(i+1)][6]:
				key_start = 'h_tail_' + str(i+1) + '_'
				self.add(key_start+'chord', IndepVarComp(key_start+'chord', settings.H['H' + str(i+1)][2]), promotes=['*'])
				self.add(key_start+'b', IndepVarComp(key_start+'b', settings.H['H' + str(i+1)][3]), promotes=['*'])
				for j in range(settings.H['H' + str(i+1)][4]):
					self.add(key_start+'taper_'+str(j+1), IndepVarComp(key_start+'taper_'+str(j+1), 1.0), promotes=['*'])
					self.add(key_start+'angle_'+str(j+1), IndepVarComp(key_start+'angle_'+str(j+1), 0.0), promotes=['*'])
					#self.add(key_start+'dihedral_'+str(j+1), IndepVarComp(key_start+'dihedral_'+str(j+1), 0.0), promotes=['*'])
					self.add(key_start+'x_offset_'+str(j+1), IndepVarComp(key_start+'x_offset_'+str(j+1), settings.AC_0.h_tail['h_tail_' + str(i+1)]['X_offset'][j]), promotes=['*'])

		# ----V tail Design Variables---------
		for i in range(settings.V_TAIL):
			if settings.V['V'+str(i+1)][7]:
				key_start = 'v_tail_' + str(i+1) + '_'
				self.add(key_start+'chord', IndepVarComp(key_start+'chord', settings.V['V' + str(i+1)][2]), promotes=['*'])
				self.add(key_start+'b', IndepVarComp(key_start+'b', settings.V['V' + str(i+1)][3]), promotes=['*'])
				for j in range(settings.V['V' + str(i+1)][4]):
					self.add(key_start+'taper_'+str(j+1), IndepVarComp(key_start+'taper_'+str(j+1), 1.0), promotes=['*'])
					self.add(key_start+'angle_'+str(j+1), IndepVarComp(key_start+'angle_'+str(j+1), 0.0), promotes=['*'])
					#self.add(key_start+'dihedral_'+str(j+1), IndepVarComp(key_start+'dihedral_'+str(j+1), 0.0), promotes=['*'])
					self.add(key_start+'x_offset_'+str(j+1), IndepVarComp(key_start+'x_offset_'+str(j+1), settings.AC_0.v_tail['v_tail_' + str(i+1)]['X_offset'][j]), promotes=['*'])
					self.add(key_start+'y_offset_'+str(j+1), IndepVarComp(key_start+'y_offset_'+str(j+1), settings.AC_0.v_tail['v_tail_' + str(i+1)]['Y_offset'][j]), promotes=['*'])

		# ---- Boom Design variables----------
		for i in range(settings.BOOM):
			key_start = 'boom_'+str(i+1) + '_'
			self.add(key_start+'length', IndepVarComp(key_start+'length', settings.B['B'+str(i+1)]), promotes=['*'])	

		
		#====================================
		# Add Components
		#====================================
		self.add('aero_AVL', aero_AVL())
		self.add('aero_MTOW', aero_MTOW(), promotes = ['PAYLOAD'])
		# self.add('aero_CFD', aero_CFD());
		# self.add('struct_FEA', struct_FEA());
		# self.add('struct_LF', struct_LF());
		# self.add('geometry', geometry());
		# self.add('stability', stability());
		# self.add('sim_score', sim_score());
		# self.add('propulsion', propulsion());
		self.add('struct_weight', struct_weight())

		#====================================
		# Add Connections
		#====================================
		# (unknown, parameter)

		#----Design variables----------------
		# self.connect('taper', ['aero_AVL.taper', 'struct_weight.taper'])
		# self.connect('b_w', ['aero_AVL.b_w', 'struct_weight.b_w'])
		# self.connect('chord_w', ['aero_AVL.chord_w', 'struct_weight.chord_w'])
		for i in range(settings.WING):
			if settings.W['W'+str(i+1)][6]:
				key_start = 'wing_' + str(i+1) + '_'
				self.connect(key_start+'chord', 'aero_AVL.'+key_start+'chord')
				self.connect(key_start+'b', 'aero_AVL.'+key_start+'b')
				for j in range(settings.W['W' + str(i+1)][4]):
					self.connect(key_start+'taper_'+str(j+1), 'aero_AVL.'+key_start+'taper_'+str(j+1))
					self.connect(key_start+'angle_'+str(j+1), 'aero_AVL.'+key_start+'angle_'+str(j+1))
					#self.connect(key_start+'dihedral_'+str(j+1), 'aero_AVL.'+key_start+'dihedral_'+str(j+1))
					self.connect(key_start+'x_offset_'+str(j+1), 'aero_AVL.'+key_start+'x_offset_'+str(j+1))

		# ----H tail Design Variables---------
		for i in range(settings.H_TAIL):
			if settings.H['H'+str(i+1)][6]:
				key_start = 'h_tail_' + str(i+1) + '_'
				self.connect(key_start+'chord', 'aero_AVL.'+key_start+'chord')
				self.connect(key_start+'b', 'aero_AVL.'+key_start+'b')
				for j in range(settings.H['H' + str(i+1)][4]):
					self.connect(key_start+'taper_'+str(j+1), 'aero_AVL.'+key_start+'taper_'+str(j+1))
					self.connect(key_start+'angle_'+str(j+1), 'aero_AVL.'+key_start+'angle_'+str(j+1))
					#self.connect(key_start+'dihedral_'+str(j+1), 'aero_AVL.'+key_start+'dihedral_'+str(j+1))
					self.connect(key_start+'x_offset_'+str(j+1), 'aero_AVL.'+key_start+'x_offset_'+str(j+1))

		# ----V tail Design Variables---------
		for i in range(settings.V_TAIL):
			if settings.V['V'+str(i+1)][7]:
				key_start = 'v_tail_' + str(i+1) + '_'
				self.connect(key_start+'chord', 'aero_AVL.'+key_start+'chord')
				self.connect(key_start+'b', 'aero_AVL.'+key_start+'b')
				for j in range(settings.V['V' + str(i+1)][4]):
					self.connect(key_start+'taper_'+str(j+1), 'aero_AVL.'+key_start+'taper_'+str(j+1))
					self.connect(key_start+'angle_'+str(j+1), 'aero_AVL.'+key_start+'angle_'+str(j+1))
					#self.connect(key_start+'dihedral_'+str(j+1), 'aero_AVL.'+key_start+'dihedral_'+str(j+1))
					self.connect(key_start+'x_offset_'+str(j+1), 'aero_AVL.'+key_start+'x_offset_'+str(j+1))
					self.connect(key_start+'y_offset_'+str(j+1), 'aero_AVL.'+key_start+'y_offset_'+str(j+1))
		# ---- Boom Design variables----------
		for i in range(settings.BOOM):
			key_start = 'boom_'+str(i+1) + '_'
			self.connect(key_start+'length', 'aero_AVL.'+key_start+'length')	



		# aero_AVL
		self.connect('aero_AVL.CL', 'aero_MTOW.CL')
		self.connect('aero_AVL.CD', 'aero_MTOW.CD')
		self.connect('aero_AVL.Sref', 'aero_MTOW.Sref')

		# aero_MTOW
		self.connect('struct_weight.EW', 'aero_MTOW.EW')

		
		#====================================
		# Add Objective
		#====================================
		self.add('obj_comp', ExecComp('obj = PAYLOAD'), promotes=['*'] )
		# self.nl_solver = Newton()
		# self.nl_solver.options['alpha'] = 10000000.0
		# self.nl_solver.iprint = 1

		#self.ln_solver = ScipyGMRES()

		#===================================
		# Add constraints
		#===================================
		#self.add('1', ExecComp('taper < 1'))

# Main routine
if __name__ == "__main__":

	# Initialize the problem
	top = Problem()
	
	top.root = AGP_MDO()
	top.driver = pyOptSparseDriver()
	top.driver.options['optimizer'] = 'ALPSO'
	#top.root.fd_options['force_fd'] = True	

	# Design variables
	# top.driver.add_desvar('taper', lower=[0.01, 0.01, 0.01], upper=[1.0, 1.0, 1.0])
	# top.driver.add_desvar('b_w', lower=2.0, upper=10.0 ) # Feet
	# top.driver.add_desvar('chord_w', lower=0.5, upper=4.0)


	# ----Wing Design Variables-----------
	for i in range(settings.WING):
		if settings.W['W'+str(i+1)][6]:
			key_start = 'wing_' + str(i+1) + '_'
			key_start_2 = 'W'+str(i+1) + 'c'
			top.driver.add_desvar(key_start+'chord', lower = settings.W[key_start_2]['WING'+str(i+1)+'_CHORD_MIN'], upper = settings.W[key_start_2]['WING'+str(i+1)+'_CHORD_MAX'])
			top.driver.add_desvar(key_start+'b' , lower = settings.W[key_start_2]['WING'+str(i+1)+'_WINGSPAN_MIN'], upper = settings.W[key_start_2]['WING'+str(i+1)+'_WINGSPAN_MAX'])
			for j in range(settings.W['W' + str(i+1)][4]):
				top.driver.add_desvar(key_start+'taper_'+str(j+1), lower = settings.W[key_start_2]['WING'+str(i+1)+'_TAPER_MIN'], upper = settings.W[key_start_2]['WING'+str(i+1)+'_TAPER_MAX'])
				top.driver.add_desvar(key_start+'angle_'+str(j+1), lower = settings.W[key_start_2]['WING'+str(i+1)+'_ANGLE_MIN'], upper = settings.W[key_start_2]['WING'+str(i+1)+'_ANGLE_MAX'])
				#top.driver.add_desvar(key_start+'dihedral_'+str(j+1), lower = settings.W[key_start_2]['WING'+str(i+1)+'_DIHEDRAL_MIN'], upper = settings.W[key_start_2]['WING'+str(i+1)+'_DIHEDRAL_MAX'])
				top.driver.add_desvar(key_start+'x_offset_'+str(j+1),  lower = settings.W[key_start_2]['WING'+str(i+1)+'_X_OFFSET_MIN'], upper = settings.W[key_start_2]['WING'+str(i+1)+'_X_OFFSET_MAX'])

	# ----H tail Design Variables---------
	for i in range(settings.H_TAIL):
		if settings.H['H'+str(i+1)][6]:
			key_start = 'h_tail_' + str(i+1) + '_'
			key_start_2 = 'H'+str(i+1) + 'c'
			top.driver.add_desvar(key_start+'chord', lower = settings.H[key_start_2]['H_TAIL'+str(i+1)+'_CHORD_MIN'], upper = settings.H[key_start_2]['H_TAIL'+str(i+1)+'_CHORD_MAX'])
			top.driver.add_desvar(key_start+'b' , lower = settings.H[key_start_2]['H_TAIL'+str(i+1)+'_WINGSPAN_MIN'], upper = settings.H[key_start_2]['H_TAIL'+str(i+1)+'_WINGSPAN_MAX'])
			for j in range(settings.H['H' + str(i+1)][4]):
				top.driver.add_desvar(key_start+'taper_'+str(j+1), lower = settings.H[key_start_2]['H_TAIL'+str(i+1)+'_TAPER_MIN'], upper = settings.H[key_start_2]['H_TAIL'+str(i+1)+'_TAPER_MAX'])
				top.driver.add_desvar(key_start+'angle_'+str(j+1), lower = settings.H[key_start_2]['H_TAIL'+str(i+1)+'_ANGLE_MIN'], upper = settings.H[key_start_2]['H_TAIL'+str(i+1)+'_ANGLE_MAX'])
				#top.driver.add_desvar(key_start+'dihedral_'+str(j+1), lower = settings.H[key_start_2]['H_TAIL'+str(i+1)+'_DIHEDRAL_MIN'], upper = settings.H[key_start_2]['H_TAIL'+str(i+1)+'_DIHEDRAL_MAX'])
				top.driver.add_desvar(key_start+'x_offset_'+str(j+1),  lower = settings.H[key_start_2]['H_TAIL'+str(i+1)+'_X_OFFSET_MIN'], upper = settings.H[key_start_2]['H_TAIL'+str(i+1)+'_X_OFFSET_MAX'])

	# ----V tail Design Variables---------
	for i in range(settings.V_TAIL):
		if settings.V['V'+str(i+1)][7]:
			key_start = 'v_tail_' + str(i+1) + '_'
			key_start_2 = 'V'+str(i+1) + 'c'
			top.driver.add_desvar(key_start+'chord', lower = settings.V[key_start_2]['V_TAIL'+str(i+1)+'_CHORD_MIN'], upper = settings.V[key_start_2]['V_TAIL'+str(i+1)+'_CHORD_MAX'])
			top.driver.add_desvar(key_start+'b' , lower = settings.V[key_start_2]['V_TAIL'+str(i+1)+'_WINGSPAN_MIN'], upper = settings.V[key_start_2]['V_TAIL'+str(i+1)+'_WINGSPAN_MAX'])
			for j in range(settings.V['V' + str(i+1)][4]):
				top.driver.add_desvar(key_start+'taper_'+str(j+1), lower = settings.V[key_start_2]['V_TAIL'+str(i+1)+'_TAPER_MIN'], upper = settings.V[key_start_2]['V_TAIL'+str(i+1)+'_TAPER_MAX'])
				top.driver.add_desvar(key_start+'angle_'+str(j+1), lower = settings.V[key_start_2]['V_TAIL'+str(i+1)+'_ANGLE_MIN'], upper = settings.V[key_start_2]['V_TAIL'+str(i+1)+'_ANGLE_MAX'])
				#top.driver.add_desvar(key_start+'dihedral_'+str(j+1), lower = settings.V[key_start_2]['V_TAIL'+str(i+1)+'_DIHEDRAL_MIN'], upper = settings.V[key_start_2]['V_TAIL'+str(i+1)+'_DIHEDRAL_MAX'])
				top.driver.add_desvar(key_start+'x_offset_'+str(j+1),  lower = settings.V[key_start_2]['V_TAIL'+str(i+1)+'_X_OFFSET_MIN'], upper = settings.V[key_start_2]['V_TAIL'+str(i+1)+'_X_OFFSET_MAX'])
				top.driver.add_desvar(key_start+'y_offset_'+str(j+1),  lower = settings.V[key_start_2]['V_TAIL'+str(i+1)+'_Y_OFFSET_MIN'], upper = settings.V[key_start_2]['V_TAIL'+str(i+1)+'_Y_OFFSET_MAX'])
	# # ---- Boom Design variables----------
	# for i in range(settings.BOOM):
	# 	key_start = 'boom_'+str(i+1) + '_'
	# 	self.add_desvar(key_start+'length', IndepVarComp(key_start+'length', B['B'+str(i+1)]), promotes['*'])	

	
	# Objective
	top.driver.add_objective('obj')

	# Add constraints

	# Add Recorder
	#recorder = CsvRecorder('AGP_CG')
	#recorder.options['record_params'] = True
	#recorder.options['record_metadata'] = False
	#top.driver.add_recorder(recorder)


	# Setup
	top.setup()
	time_start = time.time()

	# Initial values (either set default in each individual libraries or set them here)


	# Run 
	top.run()

	top.cleanup()

	print('\n')
	print("Optimization Time: " + str((time.time()-time_start)/3600) + "hours")
	print('\n')
	print('Wingspan: %f, Chord: %f, Taper: %f\n' % (top['b_w'], top['chord_w'], top['taper']))





