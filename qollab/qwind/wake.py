import numpy as np

def jensen_wake_deficit(x_dist, y_dist, k=0.075, Ct=0.8, D=1.0):
    """
    Calculate the velocity deficit using the Jensen wake model.
    x_dist: downstream distance (in direction of wind)
    y_dist: crosswind distance
    k: wake decay constant
    Ct: thrust coefficient
    D: rotor diameter (all distances must be in units of D if D=1)
    """
    if x_dist <= 0:
        return 0.0  # Upstream or same position, no wake
        
    r0 = D / 2.0
    # Wake radius at distance x
    rw = r0 + k * x_dist
    
    # Check if turbine is inside the wake cone
    if abs(y_dist) > rw:
        return 0.0
        
    # Velocity deficit factor
    deficit = (1.0 - np.sqrt(1.0 - Ct)) / ((1.0 + 2.0 * k * x_dist / D)**2)
    return deficit

def generate_h_J(grid_shape=(4, 3), spacing_D=5.0, wind_rose=None, P0=1.0, coords=None):
    """
    Generate linear terms h and quadratic terms J for the QUBO formulation.
    
    Uses Jensen's wake model and a wind rose to calculate expected pairwise power loss.
    grid_shape: (rows, cols)
    spacing_D: distance between adjacent cells in units of rotor diameters
    wind_rose: list of tuples (angle_degrees, probability)
    coords: optional list of (x, y) cell positions in rotor diameters (x east, y north); when given it replaces the
        regular grid (grid_shape and spacing_D are then ignored), e.g. the real turbine positions of a farm
    """
    if wind_rose is None:
        # Default wind rose: mostly from North (270 deg in math if East is 0)
        # Let's define angle mathematically: 0 is East, 90 is North, 180 is West, 270 is South
        # Wind blowing FROM 270 (South) means wind vector is towards North (90)
        # We will define angles as the direction the wind is blowing TOWARDS.
        wind_rose = [(0, 0.2), (90, 0.5), (180, 0.1), (270, 0.2)]
        
    num_cells = len(coords) if coords is not None else grid_shape[0] * grid_shape[1]
    
    if np.isscalar(P0):
        P0_array = P0 * np.ones(num_cells)
    else:
        P0_array = np.asarray(P0)
        
    h = -P0_array
    J = np.zeros((num_cells, num_cells))
    
    # Calculate coordinates for each cell
    if coords is None:
        coords = []
        for r in range(grid_shape[0]):
            for c in range(grid_shape[1]):
                # x is col, y is row
                coords.append((c * spacing_D, r * spacing_D))
            
    for i in range(num_cells):
        for j in range(num_cells):
            if i == j:
                continue
                
            xi, yi = coords[i]
            xj, yj = coords[j]
            
            dx = xj - xi
            dy = yj - yi
            
            expected_loss = 0.0
            
            # Integrate over wind rose
            for angle_deg, prob in wind_rose:
                if prob == 0:
                    continue
                    
                angle_rad = np.radians(angle_deg)
                
                # Rotate coordinates so wind is blowing along positive X axis
                # If wind is blowing towards angle_rad, the unit vector is (cos, sin)
                cos_a = np.cos(angle_rad)
                sin_a = np.sin(angle_rad)
                
                # Projection of (dx, dy) onto wind direction
                x_dist = dx * cos_a + dy * sin_a
                # Projection onto crosswind direction
                y_dist = -dx * sin_a + dy * cos_a
                
                deficit = jensen_wake_deficit(x_dist, y_dist)
                
                # Power is proportional to v^3. 
                # If v = v0(1 - deficit), then P = P0 * (1 - deficit)^3
                # Power loss = P0 - P0*(1 - deficit)^3
                if deficit > 0:
                    loss = P0_array[j] * (1.0 - (1.0 - deficit)**3)
                    expected_loss += prob * loss
                    
            # In QUBO, the x_i x_j term appears for i < j.
            # J matrix accumulates effects from i to j and j to i
            # J_ij = loss(i->j) + loss(j->i)
            if expected_loss > 0:
                if i < j:
                    J[i, j] += expected_loss
                else:
                    J[j, i] += expected_loss
                    
    return h, J
