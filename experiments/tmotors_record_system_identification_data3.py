import numpy as np

from double_pendulum.controller.pid.trajectory_pid_controller import TrajPIDController
from double_pendulum.controller.combined_controller import CombinedController
from double_pendulum.experiments.hardware_control_loop_tmotors import run_experiment


torque_limit = [8.0, 8.0]

# trajectory
dt = 0.002
t_final = 10.0
t1_final = 5.0
N = int(t1_final / dt)
T_des = np.linspace(0, t1_final, N+1)
p1_des = np.linspace(0, -np.pi/2, N+1)
p2_des = np.linspace(0, -np.pi/2, N+1)
v1_des = np.diff(p1_des, append=p1_des[-1]) / dt
v2_des = np.diff(p2_des, append=p2_des[-1]) / dt
X_des = np.array([p1_des, p2_des, v1_des, v2_des]).T

# controller parameters
Kp = 200.
Ki = 0.
Kd = 2.


def condition1(t, x):
    return False


def condition2(t, x):
    return t > 5.0


# controller
controller1 = TrajPIDController(T=T_des,
                                X=X_des,
                                read_with="numpy",
                                use_feed_forward_torque=False,
                                torque_limit=torque_limit,
                                num_break=40)
controller1.set_parameters(Kp=Kp, Ki=Ki, Kd=Kd)
controller1.init()

controller2 = TrajPIDController(T=T_des,
                                X=X_des,
                                read_with="numpy",
                                use_feed_forward_torque=False,
                                torque_limit=torque_limit,
                                num_break=40)
controller2.set_parameters(Kp=0., Ki=0., Kd=0.)
controller2.init()

controller = CombinedController(
        controller1=controller1,
        controller2=controller2,
        condition1=condition1,
        condition2=condition2)

# experiment
run_experiment(controller=controller,
               dt=dt,
               t_final=t_final,
               can_port="can0",
               motor_ids=[8, 9],
               tau_limit=torque_limit,
               friction_compensation=False,
               friction_terms=None,
               velocity_filter="lowpass",
               filter_args={"alpha": 0.2,
                            "kernel_size": 5,
                            "filter_size": 1},
               save_dir="data/acrobot/tmotors/sysid")
