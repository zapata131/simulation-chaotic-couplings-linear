import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

def get_parameters():
    """
    Returns the parameters for the Rossler R5 system and the network.
    Matches param_Ross.m and Simulink block values.
    """
    params = {
        # Rossler Parameters
        'a': 0.1,
        'b': 4.0,
        'd': 2.0,
        'e': 0.1,
        
        # Network Parameters
        'K': 1.0,           # Coupling Constant
        'ofs': 1.0,         # Offset for chaotic signals
        'amp': 0.2,         # Amplitude multiplier
        'w1': 1.0,          # Frequency parameters (implied from MATLAB code, though Simulink uses hardcoded -5)
        'w2': 1.0, 
        
        # Simulation Parameters
        't_start': 0.0,
        't_end': 30.0,      # Matches Simulink StopTime
        'max_step': 0.01,   # To ensure smooth plots
    }
    return params

def rossler_r5_deriv(t, u, p):
    """
    Computes the derivative of the Generalized Rossler R5 system.
    u: State vector [x1, x2, x3, x4, x5]
    """
    x1, x2, x3, x4, x5 = u
    
    # Equations derived from Simulink RosslerR5 subsystem:
    # dx1 = a*x1 - x2
    # dx2 = x1 - x3
    # dx3 = x2 - x4
    # dx4 = x3 - x5
    # dx5 = e + b*x5*(x4 - d)
    
    dx1 = p['a'] * x1 - x2
    dx2 = x1 - x3
    dx3 = x2 - x4
    dx4 = x3 - x5
    dx5 = p['e'] + p['b'] * x5 * (x4 - p['d'])
    
    return [dx1, dx2, dx3, dx4, dx5]

def system_deriv(t, Y, p):
    """
    Computes the derivative of the entire coupled system.
    Y: State vector of size 17
       Indices 0-4: Rossler states [u1, u2, u3, u4, u5]
       Indices 5-16: Linear systems 1-6 [x1_1, x2_1, x1_2, x2_2, ..., x1_6, x2_6]
    """
    
    # Split state vector
    u_ross = Y[0:5]
    u_linear = Y[5:] # 12 states (6 systems * 2 states)
    
    # 1. Rossler Dynamics
    du_ross = rossler_r5_deriv(t, u_ross, p)
    
    # 2. Coupling Signals
    # Rossler output "Out1" in Simulink is: amp * u_ross + ofs
    # However, the Fcn blocks use raw Rossler states u(1)..u(5) directly from Mux3/Mux4?
    # Let's re-verify the Simulink wiring.
    # RosslerR5 output goes to Mux3 Port 1.
    # Mux3 inputs: RosslerR5 (5 signals) and Mux1 (6 signals).
    # So "u(1)" in Fcn is definitely raw Rossler x1.
    # "u(2)" is Rossler x2, etc.
    # The "Out1" port of RosslerR5 (amp*x+ofs) is ONLY used for SCOPE and Output, NOT for feedback to linear systems?
    # Wait, check RosslerR5 Out1 connection.
    # Line 3071: RosslerR5 SrcPort 1 -> Branch Mux3 (Port 1), Branch Mux4 (Port 1).
    # Inside RosslerR5: Out1 is connected to Add4 (amp*x+ofs).
    # The port labeled "Out1" (SID 136) is the physical outport of the subsystem.
    # BUT, does Mux3 connect to the 'Out1' port or to a tap inside?
    # In Simulink, lines connect ports. RosslerR5 has 1 Outport.
    # So Mux3 receives (amp * x + ofs).
    # THIS IS CRITICAL.
    # If Mux3 receives the SCALED output, then u(1) in Fcn is (amp*x1 + ofs).
    # Let's verify RosslerR5 internal structure again.
    # Block "Out1" (SID 136) is connected to "Add4".
    # "Add4" result is (Gain1 + Constant1).
    # So yes, the output of the Rossler block is SCALED and OFFSET.
    
    # Calculated Rossler Output Vector (for coupling usage)
    # The Simulink Mux3 receives the vector output of RosslerR5.
    u_ross_out = p['amp'] * u_ross + p['ofs']
    
    # Mux3 Composition (Odd/First States):
    # u[1]..u[5] = u_ross_out[0]..u_ross_out[4]
    # u[6]..u[11] = x1 of Linear 1..6
    # Note: Python 0-indexed vs Simulink 1-indexed.
    
    # Extract Linear Systems states
    # Linear State Vector structure in Y[5:]:
    # [x1_L1, x2_L1, x1_L2, x2_L2, ..., x1_L6, x2_L6]
    # BUT Mux1 collects all x1_Li, Mux2 collects all x2_Li.
    # The Fcn blocks use Mux3 or Mux4.
    
    # Construct "u" vector for Fcn blocks connected to Mux3 (Odd/First Inputs)
    # Indices 1-5: Rossler Out
    # Indices 6-11: x1 states of Linear 1-6
    # Let's call this vec_mux3
    x1_linears = [u_linear[2*i] for i in range(6)] # [x1_L1, x1_L2, ..., x1_L6]
    vec_mux3 = np.concatenate([u_ross_out, x1_linears])
    
    # Construct "u" vector for Fcn blocks connected to Mux4 (Even/Second Inputs)
    # Indices 1-5: Rossler Out (Mux4 port 1 also connected from Rossler Out)
    # Indices 6-11: x2 states of Linear 1-6
    x2_linears = [u_linear[2*i+1] for i in range(6)] # [x2_L1, x2_L2, ..., x2_L6]
    vec_mux4 = np.concatenate([u_ross_out, x2_linears])
    
    # Helper to clean up Fcn expressions (convert 1-based index to 0-based value)
    def u_odd(i): return vec_mux3[i-1]
    def u_even(i): return vec_mux4[i-1]
    
    # Connection Timer (Step Function)
    # Time 15 (Wait, Simulink Step block Time "1" or "15"?)
    # Root Step block (SID 43 inside Rossler? No, SID 29 in Root?)
    # Let's check Root Step block.
    # Line 788: Time "1". Before "0", After "1".
    # So connection starts at t=1.
    step_val = 1.0 if t >= 1.0 else 0.0
    
    K = p['K']
    
    # Compute Coupling Functions (fcn1..fcn12)
    # fcn1 (L1, input 1): -(u(1)*u(6))+(u(1)*u(8)) using Mux3 (Odd)
    c1 = -(u_odd(1)*u_odd(6)) + (u_odd(1)*u_odd(8))
    
    # fcn2 (L1, input 2): -(u(1)*u(6))+(u(1)*u(8)) using Mux4 (Even)
    # Note: Expression is SAME as fcn1, but uses Mux4 vector.
    # So u(1)=Rossler1, u(6)=x2_L1, u(8)=x2_L3
    c2 = -(u_even(1)*u_even(6)) + (u_even(1)*u_even(8))
    
    # fcn3 (L2, input 1): (u(2)*u(8))-(u(2)*u(7)) using Mux3
    c3 = (u_odd(2)*u_odd(8)) - (u_odd(2)*u_odd(7))
    
    # fcn4 (L2, input 2): (u(2)*u(8))-(u(2)*u(7)) using Mux4
    c4 = (u_even(2)*u_even(8)) - (u_even(2)*u_even(7))
    
    # fcn5 (L3, input 1): u(6)*u(1)+u(7)*u(2)+u(9)*u(3)-((u(1)+u(2)+u(3))*u(8)) using Mux3
    c5 = u_odd(6)*u_odd(1) + u_odd(7)*u_odd(2) + u_odd(9)*u_odd(3) - ((u_odd(1)+u_odd(2)+u_odd(3))*u_odd(8))
    
    # fcn6 (L3, input 2): same expr using Mux4
    c6 = u_even(6)*u_even(1) + u_even(7)*u_even(2) + u_even(9)*u_even(3) - ((u_even(1)+u_even(2)+u_even(3))*u_even(8))
    
    # fcn7 (L4, input 1): u(8)*u(3)+u(10)*u(4)+u(11)*u(5)-((u(3)+u(4)+u(5))*u(9)) using Mux3
    c7 = u_odd(8)*u_odd(3) + u_odd(10)*u_odd(4) + u_odd(11)*u_odd(5) - ((u_odd(3)+u_odd(4)+u_odd(5))*u_odd(9))
    
    # fcn8 (L4, input 2): same expr using Mux4
    c8 = u_even(8)*u_even(3) + u_even(10)*u_even(4) + u_even(11)*u_even(5) - ((u_even(3)+u_even(4)+u_even(5))*u_even(9))
    
    # fcn9 (L5, input 1): u(9)*u(4)-u(4)*u(10) using Mux3
    c9 = u_odd(9)*u_odd(4) - u_odd(4)*u_odd(10)
    
    # fcn10 (L5, input 2): same expr using Mux4
    c10 = u_even(9)*u_even(4) - u_even(4)*u_even(10)
    
    # fcn12 (L6, input 1): u(5)*u(9)-u(5)*u(11) using Mux3
    # Note: fcn11/12 swap logic handled here by manual assignment
    # System 6 input 1 uses fcn12
    c12 = u_odd(5)*u_odd(9) - u_odd(5)*u_odd(11)
    
    # fcn11 (L6, input 2): u(5)*u(9)-u(5)*u(11) using Mux4
    # System 6 input 2 uses fcn11
    c11 = u_even(5)*u_even(9) - u_even(5)*u_even(11)
    
    # Apply Step and Gain (K)
    # Inputs to subsystems are: Step * K * c_i
    # Note: Product block inputs are Step and (Gain output). Gain is K*fcn.
    # So final input = Step * K * fcn_output
    
    inputs_L1 = [step_val * K * c1, step_val * K * c2]
    inputs_L2 = [step_val * K * c3, step_val * K * c4]
    inputs_L3 = [step_val * K * c5, step_val * K * c6]
    inputs_L4 = [step_val * K * c7, step_val * K * c8]
    inputs_L5 = [step_val * K * c9, step_val * K * c10]
    inputs_L6 = [step_val * K * c12, step_val * K * c11] # Note c12 then c11
    
    all_inputs = [inputs_L1, inputs_L2, inputs_L3, inputs_L4, inputs_L5, inputs_L6]
    
    # 3. Linear Dynamics
    du_linear = []
    
    for i in range(6):
        # State variables for system i
        x1_i = u_linear[2*i]
        x2_i = u_linear[2*i+1]
        
        inp1, inp2 = all_inputs[i]
        
        # Differential equations from Linear Subsystem:
        # dx1 = x2 + inp1
        # dx2 = -5*x1 + inp2
        
        dx1_i = x2_i + inp1
        dx2_i = -5.0 * x1_i + inp2
        
        du_linear.extend([dx1_i, dx2_i])
        
    return np.concatenate([du_ross, du_linear])

def run_simulation():
    p = get_parameters()
    t_span = (p['t_start'], p['t_end'])
    t_eval = np.arange(p['t_start'], p['t_end'], p['max_step'])
    
    # Initial Conditions
    # Rossler: [0.1, 0, -1, 0, 1]
    y0_ross = [0.1, 0.0, -1.0, 0.0, 1.0]
    
    # Linear Systems: [x1, x2] pairs
    # L1: [10, 1]
    # L2: [-10, 2]
    # L3: [-8, 10]
    # L4: [-3, 10]
    # L5: [-9, 8]
    # L6: [-5, 11]
    y0_linear = [
        10.0, 1.0, 
        -10.0, 2.0, 
        -8.0, 10.0, 
        -3.0, 10.0, 
        -9.0, 8.0, 
        -5.0, 11.0
    ]
    
    y0 = np.concatenate([y0_ross, y0_linear])
    
    print("Starting simulation...")
    sol = solve_ivp(system_deriv, t_span, y0, args=(p,), t_eval=t_eval, rtol=1e-6, atol=1e-9)
    print("Simulation complete.")
    
    if not sol.success:
        print("Solver failed:", sol.message)
        return

    # Plotting
    plot_results(sol)

def plot_results(sol):
    t = sol.t
    y = sol.y
    
    # Figure 1: Rossler States / Coupling Strengths
    # In Simulink's scope, these are the scaled output of Rossler.
    # We should reconstruct them or plot the raw rossler states.
    # The MATLAB graph.m plots "ScopeData2" which are coupling strengths?
    # Actually graph.m plots:
    # subplot(5,1,1) -> data2(:,1) -> "First state of systems" aka Rossler Out 1?
    # Let's plot raw Rossler states first.
    
    plt.figure(figsize=(10, 12))
    state_names = ['x1', 'x2', 'x3', 'x4', 'x5']
    for i in range(5):
        plt.subplot(5, 1, i+1)
        plt.plot(t, y[i])
        plt.ylabel(f"Rossler {state_names[i]}")
        plt.grid(True)
    plt.xlabel("Time")
    plt.suptitle("Rossler R5 States (Coupling Signals)")
    plt.tight_layout()
    plt.savefig('rossler_states.png')
    
    # Figure 2: Linear System States
    # Plot x1 of all 6 systems
    plt.figure(figsize=(10, 8))
    
    plt.subplot(2, 1, 1)
    for i in range(6):
        idx = 5 + 2*i # Index of x1 for system i
        plt.plot(t, y[idx], label=f"Linear {i+1}")
    plt.title("First State (x1) of Linear Systems")
    plt.ylabel("x1")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    
    plt.subplot(2, 1, 2)
    for i in range(6):
        idx = 5 + 2*i + 1 # Index of x2 for system i
        plt.plot(t, y[idx], label=f"Linear {i+1}")
    plt.title("Second State (x2) of Linear Systems")
    plt.ylabel("x2")
    plt.xlabel("Time")
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('linear_systems_states.png')
    print("Graphs saved to rossler_states.png and linear_systems_states.png")

if __name__ == "__main__":
    run_simulation()
