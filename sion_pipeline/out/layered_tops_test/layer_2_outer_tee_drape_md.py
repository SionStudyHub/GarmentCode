import sys
import traceback
import json
import pattern_api
import utility_api
import export_api
import import_api
import fabric_api
import ApiTypes

def run():
    print("=== 1. Loading Sion Female Avatar ===")
    avatar_path = '/Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_avatars/sion-female-apose.obj'
    ok = import_api.ImportFile(avatar_path)
    print(f"Loaded avatar: {ok}")
    arr_list = pattern_api.GetArrangementList()
    print(f"Available arrangement points: {len(arr_list) if arr_list else 0}")

    panel_ids = {}
    panel_arr_targets = {}

    # === 2. Create Pattern Pieces ===
    # Panel: left_ftorso -> Body_Front_Center_1
    left_ftorso_pts = [
        (0.0, 797.5168, 0),
        (233.4629, 797.5168, 0),
        (222.7116, 1109.6904, 0),
        (215.1358, 1108.1496, 0),
        (207.4734, 1107.1268, 0),
        (199.754, 1106.7317, 0),
        (192.0335, 1107.0862, 0),
        (184.4033, 1108.3081, 0),
        (176.9886, 1110.4813, 0),
        (169.9292, 1113.6213, 0),
        (163.3423, 1117.6608, 0),
        (157.2915, 1122.4679, 0),
        (151.7805, 1127.8871, 0),
        (146.7694, 1133.7729, 0),
        (142.1967, 1140.0063, 0),
        (137.9963, 1146.4969, 0),
        (134.1055, 1153.1781, 0),
        (130.4694, 1160.0015, 0),
        (127.0409, 1166.9317, 0),
        (123.7802, 1173.9425, 0),
        (120.6542, 1181.0144, 0),
        (117.6349, 1188.1326, 0),
        (114.6988, 1195.2856, 0),
        (111.8259, 1202.4641, 0),
        (108.9993, 1209.661, 0),
        (106.2042, 1216.8703, 0),
        (103.4282, 1224.0869, 0),
        (101.1931, 1229.9159, 0),
        (98.9582, 1235.745, 0),
        (96.7189, 1241.5724, 0),
        (94.4709, 1247.3964, 0),
        (58.202, 1266.4784, 0),
        (63.64, 1260.8801, 0),
        (68.5416, 1254.8067, 0),
        (72.8657, 1248.3095, 0),
        (76.5758, 1241.443, 0),
        (79.6406, 1234.2653, 0),
        (82.0342, 1226.8368, 0),
        (83.7366, 1219.2201, 0),
        (84.7333, 1211.4793, 0),
        (85.016, 1203.6798, 0),
        (84.5823, 1195.8872, 0),
        (83.4358, 1188.1672, 0),
        (81.5862, 1180.5849, 0),
        (79.0491, 1173.2041, 0),
        (75.8459, 1166.0871, 0),
        (72.0035, 1159.2938, 0),
        (67.5544, 1152.8815, 0),
        (62.536, 1146.9042, 0),
        (56.9906, 1141.4123, 0),
        (50.965, 1136.452, 0),
        (44.5099, 1132.0652, 0),
        (37.6797, 1128.2888, 0),
        (30.532, 1125.1547, 0),
        (23.127, 1122.6892, 0),
        (15.5271, 1120.9131, 0),
        (7.7964, 1119.8415, 0),
        (0.0, 1119.4833, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(left_ftorso_pts)
    if pid is not None:
        panel_ids['left_ftorso'] = pid
        panel_arr_targets['left_ftorso'] = 'Body_Front_Center_1'
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'left_ftorso')
        except Exception:
            pass
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 58, "MD boundary segment mismatch: left_ftorso"
        print(f"Created pattern left_ftorso -> ID {pid} (target=Body_Front_Center_1)")

    # Panel: left_sleeve_b -> Arm_Back_1_L
    left_sleeve_b_pts = [
        (1400.0, 1106.2578, 0),
        (1503.9999, 1106.2578, 0),
        (1526.8291, 1198.879, 0),
        (1521.8849, 1205.0226, 0),
        (1517.5554, 1211.6152, 0),
        (1513.7483, 1218.5237, 0),
        (1510.357, 1225.6464, 0),
        (1507.2747, 1232.9086, 0),
        (1504.4009, 1240.256, 0),
        (1501.6415, 1247.6474, 0),
        (1498.9076, 1255.0482, 0),
        (1496.1133, 1262.4264, 0),
        (1493.1728, 1269.7473, 0),
        (1489.9988, 1276.9698, 0),
        (1486.5022, 1284.0413, 0),
        (1482.5936, 1290.8931, 0),
        (1478.1901, 1297.4369, 0),
        (1473.2256, 1303.5649, 0),
        (1467.666, 1309.1576, 0),
        (1461.5229, 1314.1014, 0),
        (1454.8556, 1318.3116, 0),
        (1447.7594, 1321.7509, 0),
        (1440.3426, 1324.4316, 0),
        (1432.7062, 1326.4045, 0),
        (1424.9326, 1327.7411, 0),
        (1418.6914, 1328.0599, 0),
        (1412.4421, 1328.053, 0),
        (1406.2036, 1327.689, 0),
        (1400.0, 1326.9378, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(left_sleeve_b_pts)
    if pid is not None:
        panel_ids['left_sleeve_b'] = pid
        panel_arr_targets['left_sleeve_b'] = 'Arm_Back_1_L'
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'left_sleeve_b')
        except Exception:
            pass
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 29, "MD boundary segment mismatch: left_sleeve_b"
        print(f"Created pattern left_sleeve_b -> ID {pid} (target=Arm_Back_1_L)")

    # Panel: left_sleeve_f -> Arm_Front_1_L
    left_sleeve_f_pts = [
        (1150.0, 1106.2578, 0),
        (1150.0, 1326.9378, 0),
        (1142.4172, 1325.433, 0),
        (1134.9987, 1323.2594, 0),
        (1127.8146, 1320.4054, 0),
        (1120.9305, 1316.8889, 0),
        (1114.397, 1312.7569, 0),
        (1108.2426, 1308.0781, 0),
        (1102.4719, 1302.933, 0),
        (1097.0681, 1297.4032, 0),
        (1091.9988, 1291.5647, 0),
        (1087.2221, 1285.4841, 0),
        (1082.6907, 1279.2183, 0),
        (1078.3554, 1272.815, 0),
        (1074.1666, 1266.3148, 0),
        (1070.075, 1259.7529, 0),
        (1066.0313, 1253.1613, 0),
        (1061.986, 1246.5707, 0),
        (1057.8888, 1240.0123, 0),
        (1053.6873, 1233.5203, 0),
        (1049.3271, 1227.134, 0),
        (1044.7514, 1220.9006, 0),
        (1039.9016, 1214.8783, 0),
        (1034.7203, 1209.1395, 0),
        (1029.1558, 1203.7721, 0),
        (1023.1709, 1198.879, 0),
        (1046.0001, 1106.2578, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(left_sleeve_f_pts)
    if pid is not None:
        panel_ids['left_sleeve_f'] = pid
        panel_arr_targets['left_sleeve_f'] = 'Arm_Front_1_L'
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'left_sleeve_f')
        except Exception:
            pass
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 27, "MD boundary segment mismatch: left_sleeve_f"
        print(f"Created pattern left_sleeve_f -> ID {pid} (target=Arm_Front_1_L)")

    # Panel: left_btorso -> Body_Back_Center_1
    left_btorso_pts = [
        (600.0, 800.6389, 0),
        (600.0, 1191.0675, 0),
        (592.1707, 1191.5791, 0),
        (584.4746, 1193.1051, 0),
        (577.0425, 1195.6197, 0),
        (570.0009, 1199.08, 0),
        (563.4693, 1203.4272, 0),
        (557.559, 1208.5873, 0),
        (552.3705, 1214.4727, 0),
        (547.9919, 1220.9832, 0),
        (544.4978, 1228.0082, 0),
        (541.9475, 1235.4281, 0),
        (540.3844, 1243.1168, 0),
        (539.8351, 1250.9435, 0),
        (540.309, 1258.7751, 0),
        (541.798, 1266.4784, 0),
        (504.1263, 1246.6584, 0),
        (503.3648, 1238.8054, 0),
        (502.6165, 1230.9512, 0),
        (501.8671, 1223.097, 0),
        (501.1, 1215.2446, 0),
        (500.295, 1207.3959, 0),
        (499.4284, 1199.5538, 0),
        (498.471, 1191.7224, 0),
        (497.3869, 1183.9075, 0),
        (496.1315, 1176.1184, 0),
        (494.6488, 1168.3695, 0),
        (492.8674, 1160.6841, 0),
        (490.697, 1153.0998, 0),
        (488.025, 1145.6782, 0),
        (484.7175, 1138.5187, 0),
        (480.634, 1131.7738, 0),
        (475.6657, 1125.6542, 0),
        (469.7971, 1120.3942, 0),
        (463.1437, 1116.17, 0),
        (455.9153, 1113.0252, 0),
        (448.3292, 1110.875, 0),
        (440.5514, 1109.5695, 0),
        (432.6877, 1108.9524, 0),
        (425.2442, 800.6389, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(left_btorso_pts)
    if pid is not None:
        panel_ids['left_btorso'] = pid
        panel_arr_targets['left_btorso'] = 'Body_Back_Center_1'
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'left_btorso')
        except Exception:
            pass
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 40, "MD boundary segment mismatch: left_btorso"
        print(f"Created pattern left_btorso -> ID {pid} (target=Body_Back_Center_1)")

    # Panel: right_sleeve_b -> Arm_Back_1_R
    right_sleeve_b_pts = [
        (-800.0, 1106.2578, 0),
        (-800.0, 1326.9378, 0),
        (-806.2036, 1327.689, 0),
        (-812.4421, 1328.053, 0),
        (-818.6914, 1328.0599, 0),
        (-824.9326, 1327.7411, 0),
        (-832.7062, 1326.4045, 0),
        (-840.3426, 1324.4316, 0),
        (-847.7594, 1321.7509, 0),
        (-854.8556, 1318.3116, 0),
        (-861.5229, 1314.1014, 0),
        (-867.666, 1309.1576, 0),
        (-873.2256, 1303.5649, 0),
        (-878.1901, 1297.4369, 0),
        (-882.5936, 1290.8931, 0),
        (-886.5022, 1284.0413, 0),
        (-889.9988, 1276.9698, 0),
        (-893.1728, 1269.7473, 0),
        (-896.1133, 1262.4264, 0),
        (-898.9076, 1255.0482, 0),
        (-901.6415, 1247.6474, 0),
        (-904.4009, 1240.256, 0),
        (-907.2747, 1232.9086, 0),
        (-910.357, 1225.6464, 0),
        (-913.7483, 1218.5237, 0),
        (-917.5554, 1211.6152, 0),
        (-921.8849, 1205.0226, 0),
        (-926.8291, 1198.879, 0),
        (-903.9999, 1106.2578, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(right_sleeve_b_pts)
    if pid is not None:
        panel_ids['right_sleeve_b'] = pid
        panel_arr_targets['right_sleeve_b'] = 'Arm_Back_1_R'
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'right_sleeve_b')
        except Exception:
            pass
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 29, "MD boundary segment mismatch: right_sleeve_b"
        print(f"Created pattern right_sleeve_b -> ID {pid} (target=Arm_Back_1_R)")

    # Panel: right_sleeve_f -> Arm_Front_1_R
    right_sleeve_f_pts = [
        (-550.0, 1106.2578, 0),
        (-446.0001, 1106.2578, 0),
        (-423.1709, 1198.879, 0),
        (-429.1558, 1203.7721, 0),
        (-434.7203, 1209.1395, 0),
        (-439.9016, 1214.8783, 0),
        (-444.7514, 1220.9006, 0),
        (-449.3271, 1227.134, 0),
        (-453.6873, 1233.5203, 0),
        (-457.8888, 1240.0123, 0),
        (-461.986, 1246.5707, 0),
        (-466.0313, 1253.1613, 0),
        (-470.075, 1259.7529, 0),
        (-474.1666, 1266.3148, 0),
        (-478.3554, 1272.815, 0),
        (-482.6907, 1279.2183, 0),
        (-487.2221, 1285.4841, 0),
        (-491.9988, 1291.5647, 0),
        (-497.0681, 1297.4032, 0),
        (-502.4719, 1302.933, 0),
        (-508.2426, 1308.0781, 0),
        (-514.397, 1312.7569, 0),
        (-520.9305, 1316.8889, 0),
        (-527.8146, 1320.4054, 0),
        (-534.9987, 1323.2594, 0),
        (-542.4172, 1325.433, 0),
        (-550.0, 1326.9378, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(right_sleeve_f_pts)
    if pid is not None:
        panel_ids['right_sleeve_f'] = pid
        panel_arr_targets['right_sleeve_f'] = 'Arm_Front_1_R'
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'right_sleeve_f')
        except Exception:
            pass
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 27, "MD boundary segment mismatch: right_sleeve_f"
        print(f"Created pattern right_sleeve_f -> ID {pid} (target=Arm_Front_1_R)")

    # Panel: right_ftorso -> Body_Front_Center_1
    right_ftorso_pts = [
        (0.0, 797.5168, 0),
        (-0.0, 1119.4833, 0),
        (-7.7964, 1119.8415, 0),
        (-15.5271, 1120.9131, 0),
        (-23.127, 1122.6892, 0),
        (-30.532, 1125.1547, 0),
        (-37.6797, 1128.2888, 0),
        (-44.5099, 1132.0652, 0),
        (-50.965, 1136.452, 0),
        (-56.9906, 1141.4123, 0),
        (-62.536, 1146.9042, 0),
        (-67.5544, 1152.8815, 0),
        (-72.0035, 1159.2938, 0),
        (-75.8459, 1166.0871, 0),
        (-79.0491, 1173.2041, 0),
        (-81.5862, 1180.5849, 0),
        (-83.4358, 1188.1672, 0),
        (-84.5823, 1195.8872, 0),
        (-85.016, 1203.6798, 0),
        (-84.7333, 1211.4793, 0),
        (-83.7366, 1219.2201, 0),
        (-82.0342, 1226.8368, 0),
        (-79.6406, 1234.2653, 0),
        (-76.5758, 1241.443, 0),
        (-72.8657, 1248.3095, 0),
        (-68.5416, 1254.8067, 0),
        (-63.64, 1260.8801, 0),
        (-58.202, 1266.4784, 0),
        (-94.4709, 1247.3964, 0),
        (-96.7189, 1241.5724, 0),
        (-98.9582, 1235.745, 0),
        (-101.1931, 1229.9159, 0),
        (-103.4282, 1224.0869, 0),
        (-106.2042, 1216.8703, 0),
        (-108.9993, 1209.661, 0),
        (-111.8259, 1202.4641, 0),
        (-114.6988, 1195.2856, 0),
        (-117.6349, 1188.1326, 0),
        (-120.6542, 1181.0144, 0),
        (-123.7802, 1173.9425, 0),
        (-127.0409, 1166.9317, 0),
        (-130.4694, 1160.0015, 0),
        (-134.1055, 1153.1781, 0),
        (-137.9963, 1146.4969, 0),
        (-142.1967, 1140.0063, 0),
        (-146.7694, 1133.7729, 0),
        (-151.7805, 1127.8871, 0),
        (-157.2915, 1122.4679, 0),
        (-163.3423, 1117.6608, 0),
        (-169.9292, 1113.6213, 0),
        (-176.9886, 1110.4813, 0),
        (-184.4033, 1108.3081, 0),
        (-192.0335, 1107.0862, 0),
        (-199.754, 1106.7317, 0),
        (-207.4734, 1107.1268, 0),
        (-215.1358, 1108.1496, 0),
        (-222.7116, 1109.6904, 0),
        (-233.4629, 797.5168, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(right_ftorso_pts)
    if pid is not None:
        panel_ids['right_ftorso'] = pid
        panel_arr_targets['right_ftorso'] = 'Body_Front_Center_1'
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'right_ftorso')
        except Exception:
            pass
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 58, "MD boundary segment mismatch: right_ftorso"
        print(f"Created pattern right_ftorso -> ID {pid} (target=Body_Front_Center_1)")

    # Panel: right_btorso -> Body_Back_Center_1
    right_btorso_pts = [
        (600.0, 800.6389, 0),
        (774.7558, 800.6389, 0),
        (767.3123, 1108.9524, 0),
        (759.4486, 1109.5695, 0),
        (751.6708, 1110.875, 0),
        (744.0847, 1113.0252, 0),
        (736.8563, 1116.17, 0),
        (730.2029, 1120.3942, 0),
        (724.3343, 1125.6542, 0),
        (719.366, 1131.7738, 0),
        (715.2825, 1138.5187, 0),
        (711.975, 1145.6782, 0),
        (709.303, 1153.0998, 0),
        (707.1326, 1160.6841, 0),
        (705.3512, 1168.3695, 0),
        (703.8685, 1176.1184, 0),
        (702.6131, 1183.9075, 0),
        (701.529, 1191.7224, 0),
        (700.5716, 1199.5538, 0),
        (699.705, 1207.3959, 0),
        (698.9, 1215.2446, 0),
        (698.1329, 1223.097, 0),
        (697.3835, 1230.9512, 0),
        (696.6352, 1238.8054, 0),
        (695.8737, 1246.6584, 0),
        (658.202, 1266.4784, 0),
        (659.691, 1258.7751, 0),
        (660.1649, 1250.9435, 0),
        (659.6156, 1243.1168, 0),
        (658.0525, 1235.4281, 0),
        (655.5022, 1228.0082, 0),
        (652.0081, 1220.9832, 0),
        (647.6295, 1214.4727, 0),
        (642.441, 1208.5873, 0),
        (636.5307, 1203.4272, 0),
        (629.9991, 1199.08, 0),
        (622.9575, 1195.6197, 0),
        (615.5254, 1193.1051, 0),
        (607.8293, 1191.5791, 0),
        (600.0, 1191.0675, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(right_btorso_pts)
    if pid is not None:
        panel_ids['right_btorso'] = pid
        panel_arr_targets['right_btorso'] = 'Body_Back_Center_1'
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'right_btorso')
        except Exception:
            pass
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 40, "MD boundary segment mismatch: right_btorso"
        print(f"Created pattern right_btorso -> ID {pid} (target=Body_Back_Center_1)")

    # === 3. Apply Sewing Stitches ===
    print("\n--- Sewing Seams ---")
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 0, int(panel_ids['left_sleeve_b']), 28, True, False), "Sewing failed: left_sleeve_f/0 to left_sleeve_b/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 25, int(panel_ids['left_sleeve_b']), 1, True, False), "Sewing failed: left_sleeve_f/2 to left_sleeve_b/1"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 1, int(panel_ids['left_ftorso']), 25, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 2, int(panel_ids['left_ftorso']), 24, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 3, int(panel_ids['left_ftorso']), 23, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 4, int(panel_ids['left_ftorso']), 22, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 5, int(panel_ids['left_ftorso']), 21, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 6, int(panel_ids['left_ftorso']), 20, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 7, int(panel_ids['left_ftorso']), 19, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 8, int(panel_ids['left_ftorso']), 18, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 9, int(panel_ids['left_ftorso']), 17, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 10, int(panel_ids['left_ftorso']), 16, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 11, int(panel_ids['left_ftorso']), 15, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 12, int(panel_ids['left_ftorso']), 14, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 13, int(panel_ids['left_ftorso']), 13, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 14, int(panel_ids['left_ftorso']), 12, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 15, int(panel_ids['left_ftorso']), 11, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 16, int(panel_ids['left_ftorso']), 10, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 17, int(panel_ids['left_ftorso']), 9, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 18, int(panel_ids['left_ftorso']), 8, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 19, int(panel_ids['left_ftorso']), 7, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 20, int(panel_ids['left_ftorso']), 6, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 21, int(panel_ids['left_ftorso']), 5, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 22, int(panel_ids['left_ftorso']), 4, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 23, int(panel_ids['left_ftorso']), 3, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 24, int(panel_ids['left_ftorso']), 2, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 24, int(panel_ids['left_ftorso']), 29, True, False), "Sewing failed: left_sleeve_b/3 to left_ftorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 25, int(panel_ids['left_ftorso']), 28, True, False), "Sewing failed: left_sleeve_b/3 to left_ftorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 26, int(panel_ids['left_ftorso']), 27, True, False), "Sewing failed: left_sleeve_b/3 to left_ftorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 27, int(panel_ids['left_ftorso']), 26, True, False), "Sewing failed: left_sleeve_b/3 to left_ftorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 2, int(panel_ids['left_btorso']), 37, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 3, int(panel_ids['left_btorso']), 36, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 4, int(panel_ids['left_btorso']), 35, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 5, int(panel_ids['left_btorso']), 34, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 6, int(panel_ids['left_btorso']), 33, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 7, int(panel_ids['left_btorso']), 32, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 8, int(panel_ids['left_btorso']), 31, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 9, int(panel_ids['left_btorso']), 30, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 10, int(panel_ids['left_btorso']), 29, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 11, int(panel_ids['left_btorso']), 28, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 12, int(panel_ids['left_btorso']), 27, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 13, int(panel_ids['left_btorso']), 26, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 14, int(panel_ids['left_btorso']), 25, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 15, int(panel_ids['left_btorso']), 24, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 16, int(panel_ids['left_btorso']), 23, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 17, int(panel_ids['left_btorso']), 22, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 18, int(panel_ids['left_btorso']), 21, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 19, int(panel_ids['left_btorso']), 20, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 20, int(panel_ids['left_btorso']), 19, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 21, int(panel_ids['left_btorso']), 18, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 22, int(panel_ids['left_btorso']), 17, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 23, int(panel_ids['left_btorso']), 16, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_ftorso']), 30, int(panel_ids['left_btorso']), 15, True, False), "Sewing failed: left_ftorso/4 to left_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_ftorso']), 1, int(panel_ids['left_btorso']), 38, True, False), "Sewing failed: left_ftorso/1 to left_btorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 26, int(panel_ids['right_sleeve_b']), 0, True, False), "Sewing failed: right_sleeve_f/3 to right_sleeve_b/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 1, int(panel_ids['right_sleeve_b']), 27, True, False), "Sewing failed: right_sleeve_f/1 to right_sleeve_b/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 2, int(panel_ids['right_ftorso']), 55, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 3, int(panel_ids['right_ftorso']), 54, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 4, int(panel_ids['right_ftorso']), 53, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 5, int(panel_ids['right_ftorso']), 52, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 6, int(panel_ids['right_ftorso']), 51, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 7, int(panel_ids['right_ftorso']), 50, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 8, int(panel_ids['right_ftorso']), 49, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 9, int(panel_ids['right_ftorso']), 48, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 10, int(panel_ids['right_ftorso']), 47, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 11, int(panel_ids['right_ftorso']), 46, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 12, int(panel_ids['right_ftorso']), 45, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 13, int(panel_ids['right_ftorso']), 44, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 14, int(panel_ids['right_ftorso']), 43, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 15, int(panel_ids['right_ftorso']), 42, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 16, int(panel_ids['right_ftorso']), 41, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 17, int(panel_ids['right_ftorso']), 40, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 18, int(panel_ids['right_ftorso']), 39, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 19, int(panel_ids['right_ftorso']), 38, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 20, int(panel_ids['right_ftorso']), 37, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 21, int(panel_ids['right_ftorso']), 36, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 22, int(panel_ids['right_ftorso']), 35, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 23, int(panel_ids['right_ftorso']), 34, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 24, int(panel_ids['right_ftorso']), 33, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 25, int(panel_ids['right_ftorso']), 32, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 1, int(panel_ids['right_ftorso']), 31, True, False), "Sewing failed: right_sleeve_b/1 to right_ftorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 2, int(panel_ids['right_ftorso']), 30, True, False), "Sewing failed: right_sleeve_b/1 to right_ftorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 3, int(panel_ids['right_ftorso']), 29, True, False), "Sewing failed: right_sleeve_b/1 to right_ftorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 4, int(panel_ids['right_ftorso']), 28, True, False), "Sewing failed: right_sleeve_b/1 to right_ftorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 5, int(panel_ids['right_btorso']), 23, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 6, int(panel_ids['right_btorso']), 22, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 7, int(panel_ids['right_btorso']), 21, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 8, int(panel_ids['right_btorso']), 20, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 9, int(panel_ids['right_btorso']), 19, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 10, int(panel_ids['right_btorso']), 18, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 11, int(panel_ids['right_btorso']), 17, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 12, int(panel_ids['right_btorso']), 16, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 13, int(panel_ids['right_btorso']), 15, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 14, int(panel_ids['right_btorso']), 14, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 15, int(panel_ids['right_btorso']), 13, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 16, int(panel_ids['right_btorso']), 12, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 17, int(panel_ids['right_btorso']), 11, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 18, int(panel_ids['right_btorso']), 10, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 19, int(panel_ids['right_btorso']), 9, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 20, int(panel_ids['right_btorso']), 8, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 21, int(panel_ids['right_btorso']), 7, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 22, int(panel_ids['right_btorso']), 6, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 23, int(panel_ids['right_btorso']), 5, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 24, int(panel_ids['right_btorso']), 4, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 25, int(panel_ids['right_btorso']), 3, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 26, int(panel_ids['right_btorso']), 2, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_ftorso']), 27, int(panel_ids['right_btorso']), 24, True, False), "Sewing failed: right_ftorso/2 to right_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_ftorso']), 56, int(panel_ids['right_btorso']), 1, True, False), "Sewing failed: right_ftorso/5 to right_btorso/1"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_ftorso']), 0, int(panel_ids['left_ftorso']), 57, True, False), "Sewing failed: right_ftorso/0 to left_ftorso/6"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_btorso']), 39, int(panel_ids['left_btorso']), 0, True, False), "Sewing failed: right_btorso/5 to left_btorso/0"

    # === 4. Native 3D Arrangement ===
    print("\n--- Arranging 3D Panels Around Avatar ---")
    for key, pid in panel_ids.items():
        target_name = panel_arr_targets.get(key)
        if target_name and arr_list:
            matched_id = None
            for item in arr_list:
                if item.get("ArrangementName", "").strip().lower() == target_name.lower():
                    matched_id = int(item["ArrangementIndex"])
                    break
            if matched_id is not None:
                pattern_api.SetArrangement(pid, matched_id)
                # Native points center each pattern independently; place halves on their own side.
                if "ftorso" in key:
                    pattern_api.SetArrangementPosition(pid, 35 if "left" in key else 65, 55, 50)
                elif "btorso" in key:
                    pattern_api.SetArrangementPosition(pid, 15 if "left" in key else 85, 55, 50)
                elif "sleeve" in key:
                    ap = pattern_api.GetArrangementOfPattern(pid)
                    pattern_api.SetArrangementPosition(pid, int(ap["ArrangementOffsetX"]), 95, 50)
                print(f"Arranged {key} -> {target_name} (idx {matched_id})")

    print("\nResetting cloth arrangement in 3D...")
    utility_api.ResetClothArrangement()

    opt_initial = ApiTypes.ImportExportOption()
    opt_initial.bExportGarment = True
    opt_initial.bExportAvatar = False
    export_api.ExportOBJ('/Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/out/layered_tops_test/layer_2_outer_tee_draped_arranged.obj', opt_initial)
    # === 5. Simulate Cloth Drape (240 steps) ===
    print("\n--- Simulating Physical Drape (240 steps) ---")
    utility_api.Simulate(240)
    print("Simulation completed!")

    # === 6. Export Garment Mesh (Non-Interactive) ===
    print("\n--- Exporting OBJ & ZPRJ ---")
    opt = ApiTypes.ImportExportOption()
    opt.bExportGarment = True
    opt.bExportAvatar = False
    export_api.ExportOBJ('/Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/out/layered_tops_test/layer_2_outer_tee_draped.obj', opt)
    export_api.ExportZPrj('/Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/out/layered_tops_test/layer_2_outer_tee_draped.zprj', False)
    print("Finished headless drape export!")

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)