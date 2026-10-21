"""
Marvelous Designer Pattern Creation Script
Tailored for: SionFemaleBodyV1 (Height: 152.1 cm)
Measurements Source: trial-female-measurements.yaml

Usage in Marvelous Designer:
1. Open Marvelous Designer
2. Go to Python Console / Script Editor
3. Run or import this script
4. The 2D sewing patterns will be generated in the 2D window at exact scale!
"""

import math

try:
    import pattern_api
except ImportError:
    # Standalone test mock when running outside Marvelous Designer
    class MockPatternApi:
        @staticmethod
        def CreatePatternWithPoints(points):
            print(f"Created pattern piece with {len(points)} vertices. Bounds: X=[{min(p[0] for p in points):.1f}, {max(p[0] for p in points):.1f}], Y=[{min(p[1] for p in points):.1f}, {max(p[1] for p in points):.1f}]")
    pattern_api = MockPatternApi()

# ==============================================================================
# 1. SCALE & SPACING CONFIGURATION
# ==============================================================================
# Measurements in YAML are in centimeters (cm).
# Marvelous Designer 2D pattern window uses millimeters (mm).
# Scale factor = 10.0 converts 1 cm -> 10 mm (10.0 units in MD).
scale = 10.0

# Spacing between pattern pieces in the 2D pattern window (in mm)
spacing = 150.0

# ==============================================================================
# 2. BODY MEASUREMENTS (from trial-female-measurements.yaml)
# ==============================================================================
body_height = 152.1           # cm
bust_circ = 69.2              # cm
bust_width = 22.2             # cm
waist_circ = 48.5             # cm
waist_width = 17.1            # cm
hips_circ = 74.5              # cm
hips_width = 29.1             # cm
neck_to_waist = 24.8          # cm
waist_to_hip = 20.2           # cm
shoulder_to_wrist = 41.8      # cm
bicep_circ = 21.0             # cm
wrist_circ = 11.2             # cm

# ==============================================================================
# 3. TAILORING PARAMETERS & EASE (in cm)
# ==============================================================================
# Ease allowances for a comfortable, flattering t-shirt fit:
bust_ease = 4.0               # Garment bust circumference: 73.2 cm
waist_ease = 5.5              # Garment waist circumference: 54.0 cm
hem_ease = 5.0                # Garment hem circumference: 68.0 cm
bicep_ease = 4.0              # Sleeve bicep circumference: 25.0 cm

# Half-widths from center-line (cm):
bust_half_w = (bust_circ + bust_ease) / 4.0        # 18.3 cm
waist_half_w = (waist_circ + waist_ease) / 4.0      # 13.5 cm
hem_half_w = 17.0                                   # 17.0 cm (total hem = 34.0 cm)
shoulder_tip_w = 15.5                               # 15.5 cm (total shoulder = 31.0 cm)
neck_half_w = 6.0                                   # 6.0 cm (total neck opening = 12.0 cm)

# Vertical heights from bottom hem (y = 0) (cm):
total_length = neck_to_waist + 10.0                 # 34.8 cm total shirt length
waist_y = 10.0                                      # 10.0 cm above hem
underarm_y = waist_y + 9.0                          # 19.0 cm above hem
shoulder_tip_y = total_length - 2.5                 # 32.3 cm above hem
neck_shoulder_y = total_length                      # 34.8 cm above hem
neck_front_scoop_y = total_length - 6.8             # 28.0 cm (front scoop)
neck_back_scoop_y = total_length - 1.8              # 33.0 cm (shallow back drop)

# Sleeve parameters (cm):
sleeve_len = 14.0                                   # 14.0 cm short sleeve length
sleeve_bicep_half_w = (bicep_circ + bicep_ease) / 2.0  # 12.5 cm (25.0 cm circumference)
sleeve_cuff_half_w = 11.0                           # 11.0 cm (22.0 cm cuff opening)
sleeve_cap_h = 10.5                                 # 10.5 cm cap height

# Helper function to generate smooth Cubic Bezier points
def cubic_bezier(p0, p1, p2, p3, num_pts=10):
    """Calculates points along a cubic Bezier curve."""
    pts = []
    for i in range(num_pts + 1):
        t = i / float(num_pts)
        b0 = (1 - t)**3
        b1 = 3 * (1 - t)**2 * t
        b2 = 3 * (1 - t) * t**2
        b3 = t**3
        x = b0 * p0[0] + b1 * p1[0] + b2 * p2[0] + b3 * p3[0]
        y = b0 * p0[1] + b1 * p1[1] + b2 * p2[1] + b3 * p3[1]
        pts.append((round(x * scale, 3), round(y * scale, 3), 0))
    return pts

def pt(x, y):
    """Converts (x, y) in cm to scaled (x, y, 0) in MD units."""
    return (round(x * scale, 3), round(y * scale, 3), 0)


# ==============================================================================
# PIECE 1: FRONT PANEL (T-Shirt Front)
# ==============================================================================
# Centered at cx_front
cx_front = bust_half_w + 5.0

front_pts = [
    # 1. Bottom Hem (left to right)
    pt(cx_front - hem_half_w, 0.0),
    pt(cx_front + hem_half_w, 0.0),
    
    # 2. Right Side Seam (hem -> waist -> underarm)
    pt(cx_front + waist_half_w, waist_y),
    pt(cx_front + bust_half_w, underarm_y),
]

# 3. Right Armhole Curve (underarm -> shoulder tip)
p_arm_start = (cx_front + bust_half_w, underarm_y)
p_arm_cp1   = (cx_front + 13.5, 19.5)
p_arm_cp2   = (cx_front + 14.0, 26.0)
p_arm_end   = (cx_front + shoulder_tip_w, shoulder_tip_y)
front_pts += cubic_bezier(p_arm_start, p_arm_cp1, p_arm_cp2, p_arm_end, 8)[1:]

# 4. Right Shoulder Seam (shoulder tip -> neck)
front_pts.append(pt(cx_front + neck_half_w, neck_shoulder_y))

# 5. Front Neckline Scoop (right neck -> center scoop -> left neck)
p_neck_r = (cx_front + neck_half_w, neck_shoulder_y)
p_neck_rcp = (cx_front + 3.5, neck_front_scoop_y)
p_neck_lcp = (cx_front - 3.5, neck_front_scoop_y)
p_neck_l = (cx_front - neck_half_w, neck_shoulder_y)
front_pts += cubic_bezier(p_neck_r, p_neck_rcp, p_neck_lcp, p_neck_l, 12)[1:]

# 6. Left Shoulder Seam (neck -> shoulder tip)
front_pts.append(pt(cx_front - shoulder_tip_w, shoulder_tip_y))

# 7. Left Armhole Curve (shoulder tip -> underarm)
p_l_arm_start = (cx_front - shoulder_tip_w, shoulder_tip_y)
p_l_arm_cp1   = (cx_front - 14.0, 26.0)
p_l_arm_cp2   = (cx_front - 13.5, 19.5)
p_l_arm_end   = (cx_front - bust_half_w, underarm_y)
front_pts += cubic_bezier(p_l_arm_start, p_l_arm_cp1, p_l_arm_cp2, p_l_arm_end, 8)[1:]

# 8. Left Side Seam (underarm -> waist)
front_pts.append(pt(cx_front - waist_half_w, waist_y))

# Create Front Pattern in Marvelous Designer
pattern_api.CreatePatternWithPoints(front_pts)


# ==============================================================================
# PIECE 2: BACK PANEL (T-Shirt Back)
# ==============================================================================
# Offset to the right of Front Panel
front_width_total = 2.0 * bust_half_w * scale
cx_back = (cx_front * scale + front_width_total / 2.0 + spacing) / scale + bust_half_w

back_pts = [
    # 1. Bottom Hem
    pt(cx_back - hem_half_w, 0.0),
    pt(cx_back + hem_half_w, 0.0),
    
    # 2. Right Side Seam
    pt(cx_back + waist_half_w, waist_y),
    pt(cx_back + bust_half_w, underarm_y),
]

# 3. Right Armhole Curve (Back has slightly flatter curve across shoulder blades)
p_b_arm_start = (cx_back + bust_half_w, underarm_y)
p_b_arm_cp1   = (cx_back + 14.5, 19.8)
p_b_arm_cp2   = (cx_back + 14.8, 26.5)
p_b_arm_end   = (cx_back + shoulder_tip_w, shoulder_tip_y)
back_pts += cubic_bezier(p_b_arm_start, p_b_arm_cp1, p_b_arm_cp2, p_b_arm_end, 8)[1:]

# 4. Right Shoulder Seam
back_pts.append(pt(cx_back + neck_half_w, neck_shoulder_y))

# 5. Back Neckline (shallow ergonomic drop)
p_b_neck_r   = (cx_back + neck_half_w, neck_shoulder_y)
p_b_neck_rcp = (cx_back + 3.0, neck_back_scoop_y)
p_b_neck_lcp = (cx_back - 3.0, neck_back_scoop_y)
p_b_neck_l   = (cx_back - neck_half_w, neck_shoulder_y)
back_pts += cubic_bezier(p_b_neck_r, p_b_neck_rcp, p_b_neck_lcp, p_b_neck_l, 10)[1:]

# 6. Left Shoulder Seam
back_pts.append(pt(cx_back - shoulder_tip_w, shoulder_tip_y))

# 7. Left Armhole Curve
p_b_l_arm_start = (cx_back - shoulder_tip_w, shoulder_tip_y)
p_b_l_arm_cp1   = (cx_back - 14.8, 26.5)
p_b_l_arm_cp2   = (cx_back - 14.5, 19.8)
p_b_l_arm_end   = (cx_back - bust_half_w, underarm_y)
back_pts += cubic_bezier(p_b_l_arm_start, p_b_l_arm_cp1, p_b_l_arm_cp2, p_b_l_arm_end, 8)[1:]

# 8. Left Side Seam
back_pts.append(pt(cx_back - waist_half_w, waist_y))

# Create Back Pattern in Marvelous Designer
pattern_api.CreatePatternWithPoints(back_pts)


# ==============================================================================
# PIECE 3 & 4: SLEEVES (Left & Right Short Sleeves)
# ==============================================================================
back_width_total = 2.0 * bust_half_w * scale
sleeve_width_total = 2.0 * sleeve_bicep_half_w * scale

# Helper to build a sleeve pattern at center coordinate sx
def build_sleeve_points(sx):
    pts = []
    
    # 1. Left underarm point to Crown top (Left half of sleeve cap curve)
    s_left_underarm = (sx - sleeve_bicep_half_w, sleeve_len)
    s_left_cp1      = (sx - sleeve_bicep_half_w + 4.0, sleeve_len + 1.5)
    s_left_cp2      = (sx - 4.5, sleeve_len + sleeve_cap_h - 1.0)
    s_crown         = (sx, sleeve_len + sleeve_cap_h)
    pts += cubic_bezier(s_left_underarm, s_left_cp1, s_left_cp2, s_crown, 10)
    
    # 2. Crown top to Right underarm point (Right half of sleeve cap curve)
    s_right_cp1       = (sx + 4.5, sleeve_len + sleeve_cap_h - 1.0)
    s_right_cp2       = (sx + sleeve_bicep_half_w - 4.0, sleeve_len + 1.5)
    s_right_underarm  = (sx + sleeve_bicep_half_w, sleeve_len)
    pts += cubic_bezier(s_crown, s_right_cp1, s_right_cp2, s_right_underarm, 10)[1:]
    
    # 3. Right Underarm Seam (down to cuff)
    pts.append(pt(sx + sleeve_cuff_half_w, 0.0))
    
    # 4. Bottom Cuff Hem (across to left cuff)
    pts.append(pt(sx - sleeve_cuff_half_w, 0.0))
    
    # Note: Loop closes automatically back to left underarm
    return pts

# Left Sleeve
sx_left = (cx_back * scale + back_width_total / 2.0 + spacing) / scale + sleeve_bicep_half_w
left_sleeve_pts = build_sleeve_points(sx_left)
pattern_api.CreatePatternWithPoints(left_sleeve_pts)

# Right Sleeve
sx_right = (sx_left * scale + sleeve_width_total / 2.0 + spacing) / scale + sleeve_bicep_half_w
right_sleeve_pts = build_sleeve_points(sx_right)
pattern_api.CreatePatternWithPoints(right_sleeve_pts)


# ==============================================================================
# PIECE 5: NECKBAND COLLAR (Rib-Knit Collar Band)
# ==============================================================================
# Placed directly below the Front and Back panels
neckband_len = 34.0   # cm (matches neckline perimeter with ~90% rib stretch)
neckband_width = 2.5  # cm (25 mm height)
neckband_x = cx_front - hem_half_w
neckband_y = - (neckband_width + 10.0)

neckband_pts = [
    pt(neckband_x, neckband_y),
    pt(neckband_x + neckband_len, neckband_y),
    pt(neckband_x + neckband_len, neckband_y + neckband_width),
    pt(neckband_x, neckband_y + neckband_width)
]
pattern_api.CreatePatternWithPoints(neckband_pts)

print("All 5 tailored shirt pattern pieces created successfully in Marvelous Designer!")
