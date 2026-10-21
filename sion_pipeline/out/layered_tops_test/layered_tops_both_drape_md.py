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
    panel_arr_y = {}

    # === 2. Create Pattern Pieces ===
    # Panel: l0_left_collar_back -> Neck_Back
    l0_left_collar_back_pts = [
        (750.0, 1297.1, 0),
        (757.5057, 1297.1, 0),
        (765.0114, 1297.1, 0),
        (772.5171, 1297.1, 0),
        (780.0228, 1297.1, 0),
        (787.5285, 1297.1, 0),
        (795.0342, 1297.1, 0),
        (802.5399, 1297.1, 0),
        (802.5399, 1327.1, 0),
        (750.0, 1327.1, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(l0_left_collar_back_pts)
    if pid is not None:
        panel_ids['l0_left_collar_back'] = pid
        panel_arr_targets['l0_left_collar_back'] = 'Neck_Back'
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'l0_left_collar_back')
        except Exception:
            pass
        pattern_api.SetPatternLayer(pid, 0)
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 10, "MD boundary segment mismatch: l0_left_collar_back"
        print(f"Created pattern l0_left_collar_back -> ID {pid} (target=Neck_Back)")

    # Panel: l0_left_collar_front -> Neck_Front
    l0_left_collar_front_pts = [
        (150.0, 1297.1, 0),
        (150.0, 1327.1, 0),
        (81.6061, 1327.1, 0),
        (81.6061, 1297.1, 0),
        (89.2054, 1297.1, 0),
        (96.8047, 1297.1, 0),
        (104.4041, 1297.1, 0),
        (112.0034, 1297.1, 0),
        (119.6027, 1297.1, 0),
        (127.202, 1297.1, 0),
        (134.8014, 1297.1, 0),
        (142.4007, 1297.1, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(l0_left_collar_front_pts)
    if pid is not None:
        panel_ids['l0_left_collar_front'] = pid
        panel_arr_targets['l0_left_collar_front'] = 'Neck_Front'
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'l0_left_collar_front')
        except Exception:
            pass
        pattern_api.SetPatternLayer(pid, 0)
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 12, "MD boundary segment mismatch: l0_left_collar_front"
        print(f"Created pattern l0_left_collar_front -> ID {pid} (target=Neck_Front)")

    # Panel: l0_left_ftorso -> Body_Front_Center_1
    l0_left_ftorso_pts = [
        (0.0, 733.5032, 0),
        (237.4549, 733.5032, 0),
        (211.5425, 1114.137, 0),
        (203.9387, 1112.7991, 0),
        (196.259, 1112.011, 0),
        (188.5409, 1111.8931, 0),
        (180.8535, 1112.5781, 0),
        (173.3068, 1114.1884, 0),
        (166.046, 1116.7986, 0),
        (159.2213, 1120.3981, 0),
        (152.9428, 1124.8843, 0),
        (147.2517, 1130.0976, 0),
        (142.1256, 1135.8688, 0),
        (137.5036, 1142.0525, 0),
        (133.3113, 1148.536, 0),
        (129.4756, 1155.2371, 0),
        (125.9311, 1162.097, 0),
        (122.6221, 1169.0737, 0),
        (119.5018, 1176.137, 0),
        (116.5317, 1183.2648, 0),
        (113.6794, 1190.4406, 0),
        (110.9181, 1197.652, 0),
        (108.2254, 1204.8892, 0),
        (105.5821, 1212.1447, 0),
        (102.9721, 1219.4122, 0),
        (100.3814, 1226.6866, 0),
        (97.8181, 1233.9072, 0),
        (95.2518, 1241.1267, 0),
        (92.6737, 1248.342, 0),
        (37.68, 1277.2756, 0),
        (38.4922, 1269.7322, 0),
        (37.809, 1262.176, 0),
        (35.6571, 1254.9006, 0),
        (32.12, 1248.1886, 0),
        (27.3351, 1242.3007, 0),
        (21.4884, 1237.4657, 0),
        (14.8068, 1233.8713, 0),
        (7.5501, 1231.6573, 0),
        (0.0, 1230.9096, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(l0_left_ftorso_pts)
    if pid is not None:
        panel_ids['l0_left_ftorso'] = pid
        panel_arr_targets['l0_left_ftorso'] = 'Body_Front_Center_1'
        panel_arr_y['l0_left_ftorso'] = 49
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'l0_left_ftorso')
        except Exception:
            pass
        pattern_api.SetPatternLayer(pid, 0)
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 39, "MD boundary segment mismatch: l0_left_ftorso"
        print(f"Created pattern l0_left_ftorso -> ID {pid} (target=Body_Front_Center_1)")

    # Panel: l0_left_btorso -> Body_Back_Center_1
    l0_left_btorso_pts = [
        (600.0, 734.8041, 0),
        (600.0, 1246.6514, 0),
        (592.5418, 1247.3808, 0),
        (585.3662, 1249.5415, 0),
        (578.7453, 1253.0516, 0),
        (572.9299, 1257.778, 0),
        (568.1405, 1263.5416, 0),
        (564.5586, 1270.124, 0),
        (562.32, 1277.2756, 0),
        (504.7542, 1246.9888, 0),
        (504.2413, 1239.0771, 0),
        (503.7417, 1231.1645, 0),
        (503.2394, 1223.2521, 0),
        (502.7154, 1215.3411, 0),
        (502.1472, 1207.4332, 0),
        (501.5069, 1199.5308, 0),
        (500.7607, 1191.6378, 0),
        (499.8659, 1183.7603, 0),
        (498.769, 1175.9085, 0),
        (497.4011, 1168.0996, 0),
        (495.6736, 1160.3627, 0),
        (493.4732, 1152.7476, 0),
        (490.6594, 1145.3385, 0),
        (487.0727, 1138.2733, 0),
        (482.5678, 1131.7581, 0),
        (477.0812, 1126.048, 0),
        (470.6954, 1121.3658, 0),
        (463.6231, 1117.8004, 0),
        (456.1098, 1115.2866, 0),
        (448.3516, 1113.6707, 0),
        (440.4753, 1112.7838, 0),
        (422.256, 734.8041, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(l0_left_btorso_pts)
    if pid is not None:
        panel_ids['l0_left_btorso'] = pid
        panel_arr_targets['l0_left_btorso'] = 'Body_Back_Center_1'
        panel_arr_y['l0_left_btorso'] = 49
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'l0_left_btorso')
        except Exception:
            pass
        pattern_api.SetPatternLayer(pid, 0)
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 32, "MD boundary segment mismatch: l0_left_btorso"
        print(f"Created pattern l0_left_btorso -> ID {pid} (target=Body_Back_Center_1)")

    # Panel: l0_left_sleeve_f -> Arm_Front_2_L
    l0_left_sleeve_f_pts = [
        (1150.0, 987.9703, 0),
        (1150.0, 1390.722, 0),
        (1142.4224, 1389.2551, 0),
        (1135.0141, 1387.0907, 0),
        (1127.8519, 1384.2153, 0),
        (1121.0073, 1380.6493, 0),
        (1114.5345, 1376.4455, 0),
        (1108.4617, 1371.6813, 0),
        (1102.7899, 1366.4454, 0),
        (1097.4967, 1360.8262, 0),
        (1092.5437, 1354.9046, 0),
        (1087.8825, 1348.7502, 0),
        (1083.4604, 1342.4215, 0),
        (1079.2231, 1335.9674, 0),
        (1075.1164, 1329.4293, 0),
        (1071.0864, 1322.8437, 0),
        (1067.0791, 1316.2441, 0),
        (1063.0396, 1309.6642, 0),
        (1058.9116, 1303.1396, 0),
        (1054.6361, 1296.7109, 0),
        (1050.1512, 1290.4267, 0),
        (1045.3928, 1284.3474, 0),
        (1040.2967, 1278.5489, 0),
        (1034.8042, 1273.1254, 0),
        (1028.8713, 1268.1887, 0),
        (1071.2663, 987.9703, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(l0_left_sleeve_f_pts)
    if pid is not None:
        panel_ids['l0_left_sleeve_f'] = pid
        panel_arr_targets['l0_left_sleeve_f'] = 'Arm_Front_2_L'
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'l0_left_sleeve_f')
        except Exception:
            pass
        pattern_api.SetPatternLayer(pid, 0)
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 26, "MD boundary segment mismatch: l0_left_sleeve_f"
        print(f"Created pattern l0_left_sleeve_f -> ID {pid} (target=Arm_Front_2_L)")

    # Panel: l0_left_sleeve_b -> Arm_Back_2_L
    l0_left_sleeve_b_pts = [
        (1400.0, 987.9703, 0),
        (1478.7337, 987.9703, 0),
        (1521.1287, 1268.1887, 0),
        (1516.1695, 1274.3667, 0),
        (1511.848, 1281.008, 0),
        (1508.0627, 1287.9702, 0),
        (1504.6969, 1295.1453, 0),
        (1501.6344, 1302.4555, 0),
        (1498.7658, 1309.8443, 0),
        (1495.9887, 1317.268, 0),
        (1493.206, 1324.6897, 0),
        (1490.3224, 1332.0726, 0),
        (1487.2423, 1339.3755, 0),
        (1483.8681, 1346.5467, 0),
        (1480.1011, 1353.5191, 0),
        (1475.8466, 1360.2041, 0),
        (1471.0245, 1366.491, 0),
        (1465.5865, 1372.2521, 0),
        (1459.5323, 1377.3609, 0),
        (1452.9168, 1381.7182, 0),
        (1445.8385, 1385.2754, 0),
        (1438.4141, 1388.0405, 0),
        (1430.7539, 1390.0661, 0),
        (1422.9479, 1391.4289, 0),
        (1415.2873, 1391.7433, 0),
        (1407.6237, 1391.5286, 0),
        (1400.0, 1390.722, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(l0_left_sleeve_b_pts)
    if pid is not None:
        panel_ids['l0_left_sleeve_b'] = pid
        panel_arr_targets['l0_left_sleeve_b'] = 'Arm_Back_2_L'
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'l0_left_sleeve_b')
        except Exception:
            pass
        pattern_api.SetPatternLayer(pid, 0)
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 27, "MD boundary segment mismatch: l0_left_sleeve_b"
        print(f"Created pattern l0_left_sleeve_b -> ID {pid} (target=Arm_Back_2_L)")

    # Panel: l0_right_btorso -> Body_Back_Center_1
    l0_right_btorso_pts = [
        (600.0, 734.8041, 0),
        (777.744, 734.8041, 0),
        (759.5247, 1112.7838, 0),
        (751.6484, 1113.6707, 0),
        (743.8902, 1115.2866, 0),
        (736.3769, 1117.8004, 0),
        (729.3046, 1121.3658, 0),
        (722.9188, 1126.048, 0),
        (717.4322, 1131.7581, 0),
        (712.9273, 1138.2733, 0),
        (709.3406, 1145.3385, 0),
        (706.5268, 1152.7476, 0),
        (704.3264, 1160.3627, 0),
        (702.5989, 1168.0996, 0),
        (701.231, 1175.9085, 0),
        (700.1341, 1183.7603, 0),
        (699.2393, 1191.6378, 0),
        (698.4931, 1199.5308, 0),
        (697.8528, 1207.4332, 0),
        (697.2846, 1215.3411, 0),
        (696.7606, 1223.2521, 0),
        (696.2583, 1231.1645, 0),
        (695.7587, 1239.0771, 0),
        (695.2458, 1246.9888, 0),
        (637.68, 1277.2756, 0),
        (635.4414, 1270.124, 0),
        (631.8595, 1263.5416, 0),
        (627.0701, 1257.778, 0),
        (621.2547, 1253.0516, 0),
        (614.6338, 1249.5415, 0),
        (607.4582, 1247.3808, 0),
        (600.0, 1246.6514, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(l0_right_btorso_pts)
    if pid is not None:
        panel_ids['l0_right_btorso'] = pid
        panel_arr_targets['l0_right_btorso'] = 'Body_Back_Center_1'
        panel_arr_y['l0_right_btorso'] = 49
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'l0_right_btorso')
        except Exception:
            pass
        pattern_api.SetPatternLayer(pid, 0)
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 32, "MD boundary segment mismatch: l0_right_btorso"
        print(f"Created pattern l0_right_btorso -> ID {pid} (target=Body_Back_Center_1)")

    # Panel: l0_right_sleeve_f -> Arm_Front_2_R
    l0_right_sleeve_f_pts = [
        (-550.0, 987.9703, 0),
        (-471.2663, 987.9703, 0),
        (-428.8713, 1268.1887, 0),
        (-434.8042, 1273.1254, 0),
        (-440.2967, 1278.5489, 0),
        (-445.3928, 1284.3474, 0),
        (-450.1512, 1290.4267, 0),
        (-454.6361, 1296.7109, 0),
        (-458.9116, 1303.1396, 0),
        (-463.0396, 1309.6642, 0),
        (-467.0791, 1316.2441, 0),
        (-471.0864, 1322.8437, 0),
        (-475.1164, 1329.4293, 0),
        (-479.2231, 1335.9674, 0),
        (-483.4604, 1342.4215, 0),
        (-487.8825, 1348.7502, 0),
        (-492.5437, 1354.9046, 0),
        (-497.4967, 1360.8262, 0),
        (-502.7899, 1366.4454, 0),
        (-508.4617, 1371.6813, 0),
        (-514.5345, 1376.4455, 0),
        (-521.0073, 1380.6493, 0),
        (-527.8519, 1384.2153, 0),
        (-535.0141, 1387.0907, 0),
        (-542.4224, 1389.2551, 0),
        (-550.0, 1390.722, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(l0_right_sleeve_f_pts)
    if pid is not None:
        panel_ids['l0_right_sleeve_f'] = pid
        panel_arr_targets['l0_right_sleeve_f'] = 'Arm_Front_2_R'
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'l0_right_sleeve_f')
        except Exception:
            pass
        pattern_api.SetPatternLayer(pid, 0)
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 26, "MD boundary segment mismatch: l0_right_sleeve_f"
        print(f"Created pattern l0_right_sleeve_f -> ID {pid} (target=Arm_Front_2_R)")

    # Panel: l0_right_sleeve_b -> Arm_Back_2_R
    l0_right_sleeve_b_pts = [
        (-800.0, 987.9703, 0),
        (-800.0, 1390.722, 0),
        (-807.6237, 1391.5286, 0),
        (-815.2873, 1391.7433, 0),
        (-822.9479, 1391.4289, 0),
        (-830.7539, 1390.0661, 0),
        (-838.4141, 1388.0405, 0),
        (-845.8385, 1385.2754, 0),
        (-852.9168, 1381.7182, 0),
        (-859.5323, 1377.3609, 0),
        (-865.5865, 1372.2521, 0),
        (-871.0245, 1366.491, 0),
        (-875.8466, 1360.2041, 0),
        (-880.1011, 1353.5191, 0),
        (-883.8681, 1346.5467, 0),
        (-887.2423, 1339.3755, 0),
        (-890.3224, 1332.0726, 0),
        (-893.206, 1324.6897, 0),
        (-895.9887, 1317.268, 0),
        (-898.7658, 1309.8443, 0),
        (-901.6344, 1302.4555, 0),
        (-904.6969, 1295.1453, 0),
        (-908.0627, 1287.9702, 0),
        (-911.848, 1281.008, 0),
        (-916.1695, 1274.3667, 0),
        (-921.1287, 1268.1887, 0),
        (-878.7337, 987.9703, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(l0_right_sleeve_b_pts)
    if pid is not None:
        panel_ids['l0_right_sleeve_b'] = pid
        panel_arr_targets['l0_right_sleeve_b'] = 'Arm_Back_2_R'
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'l0_right_sleeve_b')
        except Exception:
            pass
        pattern_api.SetPatternLayer(pid, 0)
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 27, "MD boundary segment mismatch: l0_right_sleeve_b"
        print(f"Created pattern l0_right_sleeve_b -> ID {pid} (target=Arm_Back_2_R)")

    # Panel: l0_right_collar_front -> Neck_Front
    l0_right_collar_front_pts = [
        (-150.0, 1297.1, 0),
        (-142.4007, 1297.1, 0),
        (-134.8014, 1297.1, 0),
        (-127.202, 1297.1, 0),
        (-119.6027, 1297.1, 0),
        (-112.0034, 1297.1, 0),
        (-104.4041, 1297.1, 0),
        (-96.8047, 1297.1, 0),
        (-89.2054, 1297.1, 0),
        (-81.6061, 1297.1, 0),
        (-81.6061, 1327.1, 0),
        (-150.0, 1327.1, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(l0_right_collar_front_pts)
    if pid is not None:
        panel_ids['l0_right_collar_front'] = pid
        panel_arr_targets['l0_right_collar_front'] = 'Neck_Front'
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'l0_right_collar_front')
        except Exception:
            pass
        pattern_api.SetPatternLayer(pid, 0)
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 12, "MD boundary segment mismatch: l0_right_collar_front"
        print(f"Created pattern l0_right_collar_front -> ID {pid} (target=Neck_Front)")

    # Panel: l0_right_collar_back -> Neck_Back
    l0_right_collar_back_pts = [
        (450.0, 1297.1, 0),
        (450.0, 1327.1, 0),
        (397.4601, 1327.1, 0),
        (397.4601, 1297.1, 0),
        (404.9658, 1297.1, 0),
        (412.4715, 1297.1, 0),
        (419.9772, 1297.1, 0),
        (427.4829, 1297.1, 0),
        (434.9886, 1297.1, 0),
        (442.4943, 1297.1, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(l0_right_collar_back_pts)
    if pid is not None:
        panel_ids['l0_right_collar_back'] = pid
        panel_arr_targets['l0_right_collar_back'] = 'Neck_Back'
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'l0_right_collar_back')
        except Exception:
            pass
        pattern_api.SetPatternLayer(pid, 0)
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 10, "MD boundary segment mismatch: l0_right_collar_back"
        print(f"Created pattern l0_right_collar_back -> ID {pid} (target=Neck_Back)")

    # Panel: l0_right_ftorso -> Body_Front_Center_1
    l0_right_ftorso_pts = [
        (0.0, 733.5032, 0),
        (0.0, 1230.9096, 0),
        (-7.5501, 1231.6573, 0),
        (-14.8068, 1233.8713, 0),
        (-21.4884, 1237.4657, 0),
        (-27.3351, 1242.3007, 0),
        (-32.12, 1248.1886, 0),
        (-35.6571, 1254.9006, 0),
        (-37.809, 1262.176, 0),
        (-38.4922, 1269.7322, 0),
        (-37.68, 1277.2756, 0),
        (-92.6737, 1248.342, 0),
        (-95.2518, 1241.1267, 0),
        (-97.8181, 1233.9072, 0),
        (-100.3814, 1226.6866, 0),
        (-102.9721, 1219.4122, 0),
        (-105.5821, 1212.1447, 0),
        (-108.2254, 1204.8892, 0),
        (-110.9181, 1197.652, 0),
        (-113.6794, 1190.4406, 0),
        (-116.5317, 1183.2648, 0),
        (-119.5018, 1176.137, 0),
        (-122.6221, 1169.0737, 0),
        (-125.9311, 1162.097, 0),
        (-129.4756, 1155.2371, 0),
        (-133.3113, 1148.536, 0),
        (-137.5036, 1142.0525, 0),
        (-142.1256, 1135.8688, 0),
        (-147.2517, 1130.0976, 0),
        (-152.9428, 1124.8843, 0),
        (-159.2213, 1120.3981, 0),
        (-166.046, 1116.7986, 0),
        (-173.3068, 1114.1884, 0),
        (-180.8535, 1112.5781, 0),
        (-188.5409, 1111.8931, 0),
        (-196.259, 1112.011, 0),
        (-203.9387, 1112.7991, 0),
        (-211.5425, 1114.137, 0),
        (-237.4549, 733.5032, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(l0_right_ftorso_pts)
    if pid is not None:
        panel_ids['l0_right_ftorso'] = pid
        panel_arr_targets['l0_right_ftorso'] = 'Body_Front_Center_1'
        panel_arr_y['l0_right_ftorso'] = 49
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'l0_right_ftorso')
        except Exception:
            pass
        pattern_api.SetPatternLayer(pid, 0)
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 39, "MD boundary segment mismatch: l0_right_ftorso"
        print(f"Created pattern l0_right_ftorso -> ID {pid} (target=Body_Front_Center_1)")

    # Panel: l1_left_ftorso -> Body_Front_Center_1
    l1_left_ftorso_pts = [
        (0.0, 2297.5168, 0),
        (233.4629, 2297.5168, 0),
        (222.7116, 2609.6904, 0),
        (215.1358, 2608.1496, 0),
        (207.4734, 2607.1268, 0),
        (199.754, 2606.7317, 0),
        (192.0335, 2607.0862, 0),
        (184.4033, 2608.3081, 0),
        (176.9886, 2610.4813, 0),
        (169.9292, 2613.6213, 0),
        (163.3423, 2617.6608, 0),
        (157.2915, 2622.4679, 0),
        (151.7805, 2627.8871, 0),
        (146.7694, 2633.7729, 0),
        (142.1967, 2640.0063, 0),
        (137.9963, 2646.4969, 0),
        (134.1055, 2653.1781, 0),
        (130.4694, 2660.0015, 0),
        (127.0409, 2666.9317, 0),
        (123.7802, 2673.9425, 0),
        (120.6542, 2681.0144, 0),
        (117.6349, 2688.1326, 0),
        (114.6988, 2695.2856, 0),
        (111.8259, 2702.4641, 0),
        (108.9993, 2709.661, 0),
        (106.2042, 2716.8703, 0),
        (103.4282, 2724.0869, 0),
        (101.1931, 2729.9159, 0),
        (98.9582, 2735.745, 0),
        (96.7189, 2741.5724, 0),
        (94.4709, 2747.3964, 0),
        (58.202, 2766.4784, 0),
        (58.6577, 2758.8464, 0),
        (58.1168, 2751.2198, 0),
        (56.5886, 2743.7284, 0),
        (54.099, 2736.4995, 0),
        (50.6903, 2729.6557, 0),
        (46.4204, 2723.3134, 0),
        (41.3619, 2717.5803, 0),
        (35.6007, 2712.5539, 0),
        (29.2347, 2708.3195, 0),
        (22.372, 2704.9491, 0),
        (15.1292, 2702.4999, 0),
        (7.6294, 2701.0135, 0),
        (0.0, 2700.5153, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(l1_left_ftorso_pts)
    if pid is not None:
        panel_ids['l1_left_ftorso'] = pid
        panel_arr_targets['l1_left_ftorso'] = 'Body_Front_Center_1'
        panel_arr_y['l1_left_ftorso'] = 55
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'l1_left_ftorso')
        except Exception:
            pass
        pattern_api.SetPatternLayer(pid, 1)
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 45, "MD boundary segment mismatch: l1_left_ftorso"
        print(f"Created pattern l1_left_ftorso -> ID {pid} (target=Body_Front_Center_1)")

    # Panel: l1_left_sleeve_b -> Arm_Back_1_L
    l1_left_sleeve_b_pts = [
        (1400.0, 2606.2578, 0),
        (1503.9999, 2606.2578, 0),
        (1526.8291, 2698.879, 0),
        (1521.8849, 2705.0226, 0),
        (1517.5554, 2711.6152, 0),
        (1513.7483, 2718.5237, 0),
        (1510.357, 2725.6464, 0),
        (1507.2747, 2732.9086, 0),
        (1504.4009, 2740.256, 0),
        (1501.6415, 2747.6474, 0),
        (1498.9076, 2755.0482, 0),
        (1496.1133, 2762.4264, 0),
        (1493.1728, 2769.7473, 0),
        (1489.9988, 2776.9698, 0),
        (1486.5022, 2784.0413, 0),
        (1482.5936, 2790.8931, 0),
        (1478.1901, 2797.4369, 0),
        (1473.2256, 2803.5649, 0),
        (1467.666, 2809.1576, 0),
        (1461.5229, 2814.1014, 0),
        (1454.8556, 2818.3116, 0),
        (1447.7594, 2821.7509, 0),
        (1440.3426, 2824.4316, 0),
        (1432.7062, 2826.4045, 0),
        (1424.9326, 2827.7411, 0),
        (1418.6914, 2828.0599, 0),
        (1412.4421, 2828.053, 0),
        (1406.2036, 2827.689, 0),
        (1400.0, 2826.9378, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(l1_left_sleeve_b_pts)
    if pid is not None:
        panel_ids['l1_left_sleeve_b'] = pid
        panel_arr_targets['l1_left_sleeve_b'] = 'Arm_Back_1_L'
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'l1_left_sleeve_b')
        except Exception:
            pass
        pattern_api.SetPatternLayer(pid, 1)
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 29, "MD boundary segment mismatch: l1_left_sleeve_b"
        print(f"Created pattern l1_left_sleeve_b -> ID {pid} (target=Arm_Back_1_L)")

    # Panel: l1_left_sleeve_f -> Arm_Front_1_L
    l1_left_sleeve_f_pts = [
        (1150.0, 2606.2578, 0),
        (1150.0, 2826.9378, 0),
        (1142.4172, 2825.433, 0),
        (1134.9987, 2823.2594, 0),
        (1127.8146, 2820.4054, 0),
        (1120.9305, 2816.8889, 0),
        (1114.397, 2812.7569, 0),
        (1108.2426, 2808.0781, 0),
        (1102.4719, 2802.933, 0),
        (1097.0681, 2797.4032, 0),
        (1091.9988, 2791.5647, 0),
        (1087.2221, 2785.4841, 0),
        (1082.6907, 2779.2183, 0),
        (1078.3554, 2772.815, 0),
        (1074.1666, 2766.3148, 0),
        (1070.075, 2759.7529, 0),
        (1066.0313, 2753.1613, 0),
        (1061.986, 2746.5707, 0),
        (1057.8888, 2740.0123, 0),
        (1053.6873, 2733.5203, 0),
        (1049.3271, 2727.134, 0),
        (1044.7514, 2720.9006, 0),
        (1039.9016, 2714.8783, 0),
        (1034.7203, 2709.1395, 0),
        (1029.1558, 2703.7721, 0),
        (1023.1709, 2698.879, 0),
        (1046.0001, 2606.2578, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(l1_left_sleeve_f_pts)
    if pid is not None:
        panel_ids['l1_left_sleeve_f'] = pid
        panel_arr_targets['l1_left_sleeve_f'] = 'Arm_Front_1_L'
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'l1_left_sleeve_f')
        except Exception:
            pass
        pattern_api.SetPatternLayer(pid, 1)
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 27, "MD boundary segment mismatch: l1_left_sleeve_f"
        print(f"Created pattern l1_left_sleeve_f -> ID {pid} (target=Arm_Front_1_L)")

    # Panel: l1_left_btorso -> Body_Back_Center_1
    l1_left_btorso_pts = [
        (600.0, 2300.6389, 0),
        (600.0, 2720.0075, 0),
        (592.7067, 2720.4548, 0),
        (585.5227, 2721.79, 0),
        (578.5558, 2723.9931, 0),
        (571.9102, 2727.031, 0),
        (565.6858, 2730.8583, 0),
        (559.9756, 2735.4175, 0),
        (554.8654, 2740.6403, 0),
        (550.4317, 2746.4485, 0),
        (546.7411, 2752.7549, 0),
        (543.8487, 2759.4651, 0),
        (541.798, 2766.4784, 0),
        (504.1263, 2746.6584, 0),
        (503.3648, 2738.8054, 0),
        (502.6165, 2730.9512, 0),
        (501.8671, 2723.097, 0),
        (501.1, 2715.2446, 0),
        (500.295, 2707.3959, 0),
        (499.4284, 2699.5538, 0),
        (498.471, 2691.7224, 0),
        (497.3869, 2683.9075, 0),
        (496.1315, 2676.1184, 0),
        (494.6488, 2668.3695, 0),
        (492.8674, 2660.6841, 0),
        (490.697, 2653.0998, 0),
        (488.025, 2645.6782, 0),
        (484.7175, 2638.5187, 0),
        (480.634, 2631.7738, 0),
        (475.6657, 2625.6542, 0),
        (469.7971, 2620.3942, 0),
        (463.1437, 2616.17, 0),
        (455.9153, 2613.0252, 0),
        (448.3292, 2610.875, 0),
        (440.5514, 2609.5695, 0),
        (432.6877, 2608.9524, 0),
        (425.2442, 2300.6389, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(l1_left_btorso_pts)
    if pid is not None:
        panel_ids['l1_left_btorso'] = pid
        panel_arr_targets['l1_left_btorso'] = 'Body_Back_Center_1'
        panel_arr_y['l1_left_btorso'] = 55
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'l1_left_btorso')
        except Exception:
            pass
        pattern_api.SetPatternLayer(pid, 1)
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 37, "MD boundary segment mismatch: l1_left_btorso"
        print(f"Created pattern l1_left_btorso -> ID {pid} (target=Body_Back_Center_1)")

    # Panel: l1_right_btorso -> Body_Back_Center_1
    l1_right_btorso_pts = [
        (600.0, 2300.6389, 0),
        (774.7558, 2300.6389, 0),
        (767.3123, 2608.9524, 0),
        (759.4486, 2609.5695, 0),
        (751.6708, 2610.875, 0),
        (744.0847, 2613.0252, 0),
        (736.8563, 2616.17, 0),
        (730.2029, 2620.3942, 0),
        (724.3343, 2625.6542, 0),
        (719.366, 2631.7738, 0),
        (715.2825, 2638.5187, 0),
        (711.975, 2645.6782, 0),
        (709.303, 2653.0998, 0),
        (707.1326, 2660.6841, 0),
        (705.3512, 2668.3695, 0),
        (703.8685, 2676.1184, 0),
        (702.6131, 2683.9075, 0),
        (701.529, 2691.7224, 0),
        (700.5716, 2699.5538, 0),
        (699.705, 2707.3959, 0),
        (698.9, 2715.2446, 0),
        (698.1329, 2723.097, 0),
        (697.3835, 2730.9512, 0),
        (696.6352, 2738.8054, 0),
        (695.8737, 2746.6584, 0),
        (658.202, 2766.4784, 0),
        (656.1513, 2759.4651, 0),
        (653.2589, 2752.7549, 0),
        (649.5683, 2746.4485, 0),
        (645.1346, 2740.6403, 0),
        (640.0244, 2735.4175, 0),
        (634.3142, 2730.8583, 0),
        (628.0898, 2727.031, 0),
        (621.4442, 2723.9931, 0),
        (614.4773, 2721.79, 0),
        (607.2933, 2720.4548, 0),
        (600.0, 2720.0075, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(l1_right_btorso_pts)
    if pid is not None:
        panel_ids['l1_right_btorso'] = pid
        panel_arr_targets['l1_right_btorso'] = 'Body_Back_Center_1'
        panel_arr_y['l1_right_btorso'] = 55
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'l1_right_btorso')
        except Exception:
            pass
        pattern_api.SetPatternLayer(pid, 1)
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 37, "MD boundary segment mismatch: l1_right_btorso"
        print(f"Created pattern l1_right_btorso -> ID {pid} (target=Body_Back_Center_1)")

    # Panel: l1_right_sleeve_b -> Arm_Back_1_R
    l1_right_sleeve_b_pts = [
        (-800.0, 2606.2578, 0),
        (-800.0, 2826.9378, 0),
        (-806.2036, 2827.689, 0),
        (-812.4421, 2828.053, 0),
        (-818.6914, 2828.0599, 0),
        (-824.9326, 2827.7411, 0),
        (-832.7062, 2826.4045, 0),
        (-840.3426, 2824.4316, 0),
        (-847.7594, 2821.7509, 0),
        (-854.8556, 2818.3116, 0),
        (-861.5229, 2814.1014, 0),
        (-867.666, 2809.1576, 0),
        (-873.2256, 2803.5649, 0),
        (-878.1901, 2797.4369, 0),
        (-882.5936, 2790.8931, 0),
        (-886.5022, 2784.0413, 0),
        (-889.9988, 2776.9698, 0),
        (-893.1728, 2769.7473, 0),
        (-896.1133, 2762.4264, 0),
        (-898.9076, 2755.0482, 0),
        (-901.6415, 2747.6474, 0),
        (-904.4009, 2740.256, 0),
        (-907.2747, 2732.9086, 0),
        (-910.357, 2725.6464, 0),
        (-913.7483, 2718.5237, 0),
        (-917.5554, 2711.6152, 0),
        (-921.8849, 2705.0226, 0),
        (-926.8291, 2698.879, 0),
        (-903.9999, 2606.2578, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(l1_right_sleeve_b_pts)
    if pid is not None:
        panel_ids['l1_right_sleeve_b'] = pid
        panel_arr_targets['l1_right_sleeve_b'] = 'Arm_Back_1_R'
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'l1_right_sleeve_b')
        except Exception:
            pass
        pattern_api.SetPatternLayer(pid, 1)
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 29, "MD boundary segment mismatch: l1_right_sleeve_b"
        print(f"Created pattern l1_right_sleeve_b -> ID {pid} (target=Arm_Back_1_R)")

    # Panel: l1_right_sleeve_f -> Arm_Front_1_R
    l1_right_sleeve_f_pts = [
        (-550.0, 2606.2578, 0),
        (-446.0001, 2606.2578, 0),
        (-423.1709, 2698.879, 0),
        (-429.1558, 2703.7721, 0),
        (-434.7203, 2709.1395, 0),
        (-439.9016, 2714.8783, 0),
        (-444.7514, 2720.9006, 0),
        (-449.3271, 2727.134, 0),
        (-453.6873, 2733.5203, 0),
        (-457.8888, 2740.0123, 0),
        (-461.986, 2746.5707, 0),
        (-466.0313, 2753.1613, 0),
        (-470.075, 2759.7529, 0),
        (-474.1666, 2766.3148, 0),
        (-478.3554, 2772.815, 0),
        (-482.6907, 2779.2183, 0),
        (-487.2221, 2785.4841, 0),
        (-491.9988, 2791.5647, 0),
        (-497.0681, 2797.4032, 0),
        (-502.4719, 2802.933, 0),
        (-508.2426, 2808.0781, 0),
        (-514.397, 2812.7569, 0),
        (-520.9305, 2816.8889, 0),
        (-527.8146, 2820.4054, 0),
        (-534.9987, 2823.2594, 0),
        (-542.4172, 2825.433, 0),
        (-550.0, 2826.9378, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(l1_right_sleeve_f_pts)
    if pid is not None:
        panel_ids['l1_right_sleeve_f'] = pid
        panel_arr_targets['l1_right_sleeve_f'] = 'Arm_Front_1_R'
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'l1_right_sleeve_f')
        except Exception:
            pass
        pattern_api.SetPatternLayer(pid, 1)
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 27, "MD boundary segment mismatch: l1_right_sleeve_f"
        print(f"Created pattern l1_right_sleeve_f -> ID {pid} (target=Arm_Front_1_R)")

    # Panel: l1_right_ftorso -> Body_Front_Center_1
    l1_right_ftorso_pts = [
        (0.0, 2297.5168, 0),
        (0.0, 2700.5153, 0),
        (-7.6294, 2701.0135, 0),
        (-15.1292, 2702.4999, 0),
        (-22.372, 2704.9491, 0),
        (-29.2347, 2708.3195, 0),
        (-35.6007, 2712.5539, 0),
        (-41.3619, 2717.5803, 0),
        (-46.4204, 2723.3134, 0),
        (-50.6903, 2729.6557, 0),
        (-54.099, 2736.4995, 0),
        (-56.5886, 2743.7284, 0),
        (-58.1168, 2751.2198, 0),
        (-58.6577, 2758.8464, 0),
        (-58.202, 2766.4784, 0),
        (-94.4709, 2747.3964, 0),
        (-96.7189, 2741.5724, 0),
        (-98.9582, 2735.745, 0),
        (-101.1931, 2729.9159, 0),
        (-103.4282, 2724.0869, 0),
        (-106.2042, 2716.8703, 0),
        (-108.9993, 2709.661, 0),
        (-111.8259, 2702.4641, 0),
        (-114.6988, 2695.2856, 0),
        (-117.6349, 2688.1326, 0),
        (-120.6542, 2681.0144, 0),
        (-123.7802, 2673.9425, 0),
        (-127.0409, 2666.9317, 0),
        (-130.4694, 2660.0015, 0),
        (-134.1055, 2653.1781, 0),
        (-137.9963, 2646.4969, 0),
        (-142.1967, 2640.0063, 0),
        (-146.7694, 2633.7729, 0),
        (-151.7805, 2627.8871, 0),
        (-157.2915, 2622.4679, 0),
        (-163.3423, 2617.6608, 0),
        (-169.9292, 2613.6213, 0),
        (-176.9886, 2610.4813, 0),
        (-184.4033, 2608.3081, 0),
        (-192.0335, 2607.0862, 0),
        (-199.754, 2606.7317, 0),
        (-207.4734, 2607.1268, 0),
        (-215.1358, 2608.1496, 0),
        (-222.7116, 2609.6904, 0),
        (-233.4629, 2297.5168, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(l1_right_ftorso_pts)
    if pid is not None:
        panel_ids['l1_right_ftorso'] = pid
        panel_arr_targets['l1_right_ftorso'] = 'Body_Front_Center_1'
        panel_arr_y['l1_right_ftorso'] = 55
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'l1_right_ftorso')
        except Exception:
            pass
        pattern_api.SetPatternLayer(pid, 1)
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 45, "MD boundary segment mismatch: l1_right_ftorso"
        print(f"Created pattern l1_right_ftorso -> ID {pid} (target=Body_Front_Center_1)")

    # === 3. Apply Sewing Stitches ===
    print("\n--- Sewing Seams ---")
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_collar_front']), 0, int(panel_ids['l0_left_collar_back']), 9, True, False), "Sewing failed: l0_left_collar_front/0 to l0_left_collar_back/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_f']), 0, int(panel_ids['l0_left_sleeve_b']), 26, True, False), "Sewing failed: l0_left_sleeve_f/0 to l0_left_sleeve_b/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_f']), 24, int(panel_ids['l0_left_sleeve_b']), 1, True, False), "Sewing failed: l0_left_sleeve_f/2 to l0_left_sleeve_b/1"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_f']), 1, int(panel_ids['l0_left_ftorso']), 24, True, False), "Sewing failed: l0_left_sleeve_f/1 to l0_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_f']), 2, int(panel_ids['l0_left_ftorso']), 23, True, False), "Sewing failed: l0_left_sleeve_f/1 to l0_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_f']), 3, int(panel_ids['l0_left_ftorso']), 22, True, False), "Sewing failed: l0_left_sleeve_f/1 to l0_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_f']), 4, int(panel_ids['l0_left_ftorso']), 21, True, False), "Sewing failed: l0_left_sleeve_f/1 to l0_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_f']), 5, int(panel_ids['l0_left_ftorso']), 20, True, False), "Sewing failed: l0_left_sleeve_f/1 to l0_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_f']), 6, int(panel_ids['l0_left_ftorso']), 19, True, False), "Sewing failed: l0_left_sleeve_f/1 to l0_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_f']), 7, int(panel_ids['l0_left_ftorso']), 18, True, False), "Sewing failed: l0_left_sleeve_f/1 to l0_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_f']), 8, int(panel_ids['l0_left_ftorso']), 17, True, False), "Sewing failed: l0_left_sleeve_f/1 to l0_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_f']), 9, int(panel_ids['l0_left_ftorso']), 16, True, False), "Sewing failed: l0_left_sleeve_f/1 to l0_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_f']), 10, int(panel_ids['l0_left_ftorso']), 15, True, False), "Sewing failed: l0_left_sleeve_f/1 to l0_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_f']), 11, int(panel_ids['l0_left_ftorso']), 14, True, False), "Sewing failed: l0_left_sleeve_f/1 to l0_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_f']), 12, int(panel_ids['l0_left_ftorso']), 13, True, False), "Sewing failed: l0_left_sleeve_f/1 to l0_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_f']), 13, int(panel_ids['l0_left_ftorso']), 12, True, False), "Sewing failed: l0_left_sleeve_f/1 to l0_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_f']), 14, int(panel_ids['l0_left_ftorso']), 11, True, False), "Sewing failed: l0_left_sleeve_f/1 to l0_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_f']), 15, int(panel_ids['l0_left_ftorso']), 10, True, False), "Sewing failed: l0_left_sleeve_f/1 to l0_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_f']), 16, int(panel_ids['l0_left_ftorso']), 9, True, False), "Sewing failed: l0_left_sleeve_f/1 to l0_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_f']), 17, int(panel_ids['l0_left_ftorso']), 8, True, False), "Sewing failed: l0_left_sleeve_f/1 to l0_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_f']), 18, int(panel_ids['l0_left_ftorso']), 7, True, False), "Sewing failed: l0_left_sleeve_f/1 to l0_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_f']), 19, int(panel_ids['l0_left_ftorso']), 6, True, False), "Sewing failed: l0_left_sleeve_f/1 to l0_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_f']), 20, int(panel_ids['l0_left_ftorso']), 5, True, False), "Sewing failed: l0_left_sleeve_f/1 to l0_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_f']), 21, int(panel_ids['l0_left_ftorso']), 4, True, False), "Sewing failed: l0_left_sleeve_f/1 to l0_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_f']), 22, int(panel_ids['l0_left_ftorso']), 3, True, False), "Sewing failed: l0_left_sleeve_f/1 to l0_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_f']), 23, int(panel_ids['l0_left_ftorso']), 2, True, False), "Sewing failed: l0_left_sleeve_f/1 to l0_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_b']), 23, int(panel_ids['l0_left_ftorso']), 27, True, False), "Sewing failed: l0_left_sleeve_b/3 to l0_left_ftorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_b']), 24, int(panel_ids['l0_left_ftorso']), 26, True, False), "Sewing failed: l0_left_sleeve_b/3 to l0_left_ftorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_b']), 25, int(panel_ids['l0_left_ftorso']), 25, True, False), "Sewing failed: l0_left_sleeve_b/3 to l0_left_ftorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_b']), 2, int(panel_ids['l0_left_btorso']), 29, True, False), "Sewing failed: l0_left_sleeve_b/2 to l0_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_b']), 3, int(panel_ids['l0_left_btorso']), 28, True, False), "Sewing failed: l0_left_sleeve_b/2 to l0_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_b']), 4, int(panel_ids['l0_left_btorso']), 27, True, False), "Sewing failed: l0_left_sleeve_b/2 to l0_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_b']), 5, int(panel_ids['l0_left_btorso']), 26, True, False), "Sewing failed: l0_left_sleeve_b/2 to l0_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_b']), 6, int(panel_ids['l0_left_btorso']), 25, True, False), "Sewing failed: l0_left_sleeve_b/2 to l0_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_b']), 7, int(panel_ids['l0_left_btorso']), 24, True, False), "Sewing failed: l0_left_sleeve_b/2 to l0_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_b']), 8, int(panel_ids['l0_left_btorso']), 23, True, False), "Sewing failed: l0_left_sleeve_b/2 to l0_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_b']), 9, int(panel_ids['l0_left_btorso']), 22, True, False), "Sewing failed: l0_left_sleeve_b/2 to l0_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_b']), 10, int(panel_ids['l0_left_btorso']), 21, True, False), "Sewing failed: l0_left_sleeve_b/2 to l0_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_b']), 11, int(panel_ids['l0_left_btorso']), 20, True, False), "Sewing failed: l0_left_sleeve_b/2 to l0_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_b']), 12, int(panel_ids['l0_left_btorso']), 19, True, False), "Sewing failed: l0_left_sleeve_b/2 to l0_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_b']), 13, int(panel_ids['l0_left_btorso']), 18, True, False), "Sewing failed: l0_left_sleeve_b/2 to l0_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_b']), 14, int(panel_ids['l0_left_btorso']), 17, True, False), "Sewing failed: l0_left_sleeve_b/2 to l0_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_b']), 15, int(panel_ids['l0_left_btorso']), 16, True, False), "Sewing failed: l0_left_sleeve_b/2 to l0_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_b']), 16, int(panel_ids['l0_left_btorso']), 15, True, False), "Sewing failed: l0_left_sleeve_b/2 to l0_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_b']), 17, int(panel_ids['l0_left_btorso']), 14, True, False), "Sewing failed: l0_left_sleeve_b/2 to l0_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_b']), 18, int(panel_ids['l0_left_btorso']), 13, True, False), "Sewing failed: l0_left_sleeve_b/2 to l0_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_b']), 19, int(panel_ids['l0_left_btorso']), 12, True, False), "Sewing failed: l0_left_sleeve_b/2 to l0_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_b']), 20, int(panel_ids['l0_left_btorso']), 11, True, False), "Sewing failed: l0_left_sleeve_b/2 to l0_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_b']), 21, int(panel_ids['l0_left_btorso']), 10, True, False), "Sewing failed: l0_left_sleeve_b/2 to l0_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_sleeve_b']), 22, int(panel_ids['l0_left_btorso']), 9, True, False), "Sewing failed: l0_left_sleeve_b/2 to l0_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_ftorso']), 29, int(panel_ids['l0_left_collar_front']), 11, True, False), "Sewing failed: l0_left_ftorso/5 to l0_left_collar_front/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_ftorso']), 30, int(panel_ids['l0_left_collar_front']), 10, True, False), "Sewing failed: l0_left_ftorso/5 to l0_left_collar_front/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_ftorso']), 31, int(panel_ids['l0_left_collar_front']), 9, True, False), "Sewing failed: l0_left_ftorso/5 to l0_left_collar_front/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_ftorso']), 32, int(panel_ids['l0_left_collar_front']), 8, True, False), "Sewing failed: l0_left_ftorso/5 to l0_left_collar_front/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_ftorso']), 33, int(panel_ids['l0_left_collar_front']), 7, True, False), "Sewing failed: l0_left_ftorso/5 to l0_left_collar_front/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_ftorso']), 34, int(panel_ids['l0_left_collar_front']), 6, True, False), "Sewing failed: l0_left_ftorso/5 to l0_left_collar_front/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_ftorso']), 35, int(panel_ids['l0_left_collar_front']), 5, True, False), "Sewing failed: l0_left_ftorso/5 to l0_left_collar_front/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_ftorso']), 36, int(panel_ids['l0_left_collar_front']), 4, True, False), "Sewing failed: l0_left_ftorso/5 to l0_left_collar_front/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_ftorso']), 37, int(panel_ids['l0_left_collar_front']), 3, True, False), "Sewing failed: l0_left_ftorso/5 to l0_left_collar_front/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_btorso']), 1, int(panel_ids['l0_left_collar_back']), 6, True, False), "Sewing failed: l0_left_btorso/1 to l0_left_collar_back/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_btorso']), 2, int(panel_ids['l0_left_collar_back']), 5, True, False), "Sewing failed: l0_left_btorso/1 to l0_left_collar_back/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_btorso']), 3, int(panel_ids['l0_left_collar_back']), 4, True, False), "Sewing failed: l0_left_btorso/1 to l0_left_collar_back/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_btorso']), 4, int(panel_ids['l0_left_collar_back']), 3, True, False), "Sewing failed: l0_left_btorso/1 to l0_left_collar_back/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_btorso']), 5, int(panel_ids['l0_left_collar_back']), 2, True, False), "Sewing failed: l0_left_btorso/1 to l0_left_collar_back/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_btorso']), 6, int(panel_ids['l0_left_collar_back']), 1, True, False), "Sewing failed: l0_left_btorso/1 to l0_left_collar_back/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_btorso']), 7, int(panel_ids['l0_left_collar_back']), 0, True, False), "Sewing failed: l0_left_btorso/1 to l0_left_collar_back/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_ftorso']), 28, int(panel_ids['l0_left_btorso']), 8, True, False), "Sewing failed: l0_left_ftorso/4 to l0_left_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_left_ftorso']), 1, int(panel_ids['l0_left_btorso']), 30, True, False), "Sewing failed: l0_left_ftorso/1 to l0_left_btorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_f']), 25, int(panel_ids['l0_right_sleeve_b']), 0, True, False), "Sewing failed: l0_right_sleeve_f/3 to l0_right_sleeve_b/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_f']), 1, int(panel_ids['l0_right_sleeve_b']), 25, True, False), "Sewing failed: l0_right_sleeve_f/1 to l0_right_sleeve_b/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_collar_front']), 11, int(panel_ids['l0_right_collar_back']), 0, True, False), "Sewing failed: l0_right_collar_front/3 to l0_right_collar_back/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_f']), 2, int(panel_ids['l0_right_ftorso']), 36, True, False), "Sewing failed: l0_right_sleeve_f/2 to l0_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_f']), 3, int(panel_ids['l0_right_ftorso']), 35, True, False), "Sewing failed: l0_right_sleeve_f/2 to l0_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_f']), 4, int(panel_ids['l0_right_ftorso']), 34, True, False), "Sewing failed: l0_right_sleeve_f/2 to l0_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_f']), 5, int(panel_ids['l0_right_ftorso']), 33, True, False), "Sewing failed: l0_right_sleeve_f/2 to l0_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_f']), 6, int(panel_ids['l0_right_ftorso']), 32, True, False), "Sewing failed: l0_right_sleeve_f/2 to l0_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_f']), 7, int(panel_ids['l0_right_ftorso']), 31, True, False), "Sewing failed: l0_right_sleeve_f/2 to l0_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_f']), 8, int(panel_ids['l0_right_ftorso']), 30, True, False), "Sewing failed: l0_right_sleeve_f/2 to l0_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_f']), 9, int(panel_ids['l0_right_ftorso']), 29, True, False), "Sewing failed: l0_right_sleeve_f/2 to l0_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_f']), 10, int(panel_ids['l0_right_ftorso']), 28, True, False), "Sewing failed: l0_right_sleeve_f/2 to l0_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_f']), 11, int(panel_ids['l0_right_ftorso']), 27, True, False), "Sewing failed: l0_right_sleeve_f/2 to l0_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_f']), 12, int(panel_ids['l0_right_ftorso']), 26, True, False), "Sewing failed: l0_right_sleeve_f/2 to l0_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_f']), 13, int(panel_ids['l0_right_ftorso']), 25, True, False), "Sewing failed: l0_right_sleeve_f/2 to l0_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_f']), 14, int(panel_ids['l0_right_ftorso']), 24, True, False), "Sewing failed: l0_right_sleeve_f/2 to l0_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_f']), 15, int(panel_ids['l0_right_ftorso']), 23, True, False), "Sewing failed: l0_right_sleeve_f/2 to l0_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_f']), 16, int(panel_ids['l0_right_ftorso']), 22, True, False), "Sewing failed: l0_right_sleeve_f/2 to l0_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_f']), 17, int(panel_ids['l0_right_ftorso']), 21, True, False), "Sewing failed: l0_right_sleeve_f/2 to l0_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_f']), 18, int(panel_ids['l0_right_ftorso']), 20, True, False), "Sewing failed: l0_right_sleeve_f/2 to l0_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_f']), 19, int(panel_ids['l0_right_ftorso']), 19, True, False), "Sewing failed: l0_right_sleeve_f/2 to l0_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_f']), 20, int(panel_ids['l0_right_ftorso']), 18, True, False), "Sewing failed: l0_right_sleeve_f/2 to l0_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_f']), 21, int(panel_ids['l0_right_ftorso']), 17, True, False), "Sewing failed: l0_right_sleeve_f/2 to l0_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_f']), 22, int(panel_ids['l0_right_ftorso']), 16, True, False), "Sewing failed: l0_right_sleeve_f/2 to l0_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_f']), 23, int(panel_ids['l0_right_ftorso']), 15, True, False), "Sewing failed: l0_right_sleeve_f/2 to l0_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_f']), 24, int(panel_ids['l0_right_ftorso']), 14, True, False), "Sewing failed: l0_right_sleeve_f/2 to l0_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_b']), 1, int(panel_ids['l0_right_ftorso']), 13, True, False), "Sewing failed: l0_right_sleeve_b/1 to l0_right_ftorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_b']), 2, int(panel_ids['l0_right_ftorso']), 12, True, False), "Sewing failed: l0_right_sleeve_b/1 to l0_right_ftorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_b']), 3, int(panel_ids['l0_right_ftorso']), 11, True, False), "Sewing failed: l0_right_sleeve_b/1 to l0_right_ftorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_b']), 4, int(panel_ids['l0_right_btorso']), 22, True, False), "Sewing failed: l0_right_sleeve_b/2 to l0_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_b']), 5, int(panel_ids['l0_right_btorso']), 21, True, False), "Sewing failed: l0_right_sleeve_b/2 to l0_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_b']), 6, int(panel_ids['l0_right_btorso']), 20, True, False), "Sewing failed: l0_right_sleeve_b/2 to l0_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_b']), 7, int(panel_ids['l0_right_btorso']), 19, True, False), "Sewing failed: l0_right_sleeve_b/2 to l0_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_b']), 8, int(panel_ids['l0_right_btorso']), 18, True, False), "Sewing failed: l0_right_sleeve_b/2 to l0_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_b']), 9, int(panel_ids['l0_right_btorso']), 17, True, False), "Sewing failed: l0_right_sleeve_b/2 to l0_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_b']), 10, int(panel_ids['l0_right_btorso']), 16, True, False), "Sewing failed: l0_right_sleeve_b/2 to l0_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_b']), 11, int(panel_ids['l0_right_btorso']), 15, True, False), "Sewing failed: l0_right_sleeve_b/2 to l0_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_b']), 12, int(panel_ids['l0_right_btorso']), 14, True, False), "Sewing failed: l0_right_sleeve_b/2 to l0_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_b']), 13, int(panel_ids['l0_right_btorso']), 13, True, False), "Sewing failed: l0_right_sleeve_b/2 to l0_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_b']), 14, int(panel_ids['l0_right_btorso']), 12, True, False), "Sewing failed: l0_right_sleeve_b/2 to l0_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_b']), 15, int(panel_ids['l0_right_btorso']), 11, True, False), "Sewing failed: l0_right_sleeve_b/2 to l0_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_b']), 16, int(panel_ids['l0_right_btorso']), 10, True, False), "Sewing failed: l0_right_sleeve_b/2 to l0_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_b']), 17, int(panel_ids['l0_right_btorso']), 9, True, False), "Sewing failed: l0_right_sleeve_b/2 to l0_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_b']), 18, int(panel_ids['l0_right_btorso']), 8, True, False), "Sewing failed: l0_right_sleeve_b/2 to l0_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_b']), 19, int(panel_ids['l0_right_btorso']), 7, True, False), "Sewing failed: l0_right_sleeve_b/2 to l0_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_b']), 20, int(panel_ids['l0_right_btorso']), 6, True, False), "Sewing failed: l0_right_sleeve_b/2 to l0_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_b']), 21, int(panel_ids['l0_right_btorso']), 5, True, False), "Sewing failed: l0_right_sleeve_b/2 to l0_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_b']), 22, int(panel_ids['l0_right_btorso']), 4, True, False), "Sewing failed: l0_right_sleeve_b/2 to l0_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_b']), 23, int(panel_ids['l0_right_btorso']), 3, True, False), "Sewing failed: l0_right_sleeve_b/2 to l0_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_sleeve_b']), 24, int(panel_ids['l0_right_btorso']), 2, True, False), "Sewing failed: l0_right_sleeve_b/2 to l0_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_ftorso']), 1, int(panel_ids['l0_right_collar_front']), 8, True, False), "Sewing failed: l0_right_ftorso/1 to l0_right_collar_front/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_ftorso']), 2, int(panel_ids['l0_right_collar_front']), 7, True, False), "Sewing failed: l0_right_ftorso/1 to l0_right_collar_front/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_ftorso']), 3, int(panel_ids['l0_right_collar_front']), 6, True, False), "Sewing failed: l0_right_ftorso/1 to l0_right_collar_front/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_ftorso']), 4, int(panel_ids['l0_right_collar_front']), 5, True, False), "Sewing failed: l0_right_ftorso/1 to l0_right_collar_front/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_ftorso']), 5, int(panel_ids['l0_right_collar_front']), 4, True, False), "Sewing failed: l0_right_ftorso/1 to l0_right_collar_front/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_ftorso']), 6, int(panel_ids['l0_right_collar_front']), 3, True, False), "Sewing failed: l0_right_ftorso/1 to l0_right_collar_front/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_ftorso']), 7, int(panel_ids['l0_right_collar_front']), 2, True, False), "Sewing failed: l0_right_ftorso/1 to l0_right_collar_front/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_ftorso']), 8, int(panel_ids['l0_right_collar_front']), 1, True, False), "Sewing failed: l0_right_ftorso/1 to l0_right_collar_front/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_ftorso']), 9, int(panel_ids['l0_right_collar_front']), 0, True, False), "Sewing failed: l0_right_ftorso/1 to l0_right_collar_front/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_btorso']), 24, int(panel_ids['l0_right_collar_back']), 9, True, False), "Sewing failed: l0_right_btorso/4 to l0_right_collar_back/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_btorso']), 25, int(panel_ids['l0_right_collar_back']), 8, True, False), "Sewing failed: l0_right_btorso/4 to l0_right_collar_back/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_btorso']), 26, int(panel_ids['l0_right_collar_back']), 7, True, False), "Sewing failed: l0_right_btorso/4 to l0_right_collar_back/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_btorso']), 27, int(panel_ids['l0_right_collar_back']), 6, True, False), "Sewing failed: l0_right_btorso/4 to l0_right_collar_back/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_btorso']), 28, int(panel_ids['l0_right_collar_back']), 5, True, False), "Sewing failed: l0_right_btorso/4 to l0_right_collar_back/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_btorso']), 29, int(panel_ids['l0_right_collar_back']), 4, True, False), "Sewing failed: l0_right_btorso/4 to l0_right_collar_back/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_btorso']), 30, int(panel_ids['l0_right_collar_back']), 3, True, False), "Sewing failed: l0_right_btorso/4 to l0_right_collar_back/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_ftorso']), 10, int(panel_ids['l0_right_btorso']), 23, True, False), "Sewing failed: l0_right_ftorso/2 to l0_right_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_ftorso']), 37, int(panel_ids['l0_right_btorso']), 1, True, False), "Sewing failed: l0_right_ftorso/5 to l0_right_btorso/1"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_ftorso']), 0, int(panel_ids['l0_left_ftorso']), 38, True, False), "Sewing failed: l0_right_ftorso/0 to l0_left_ftorso/6"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_collar_front']), 9, int(panel_ids['l0_left_collar_front']), 2, True, False), "Sewing failed: l0_right_collar_front/1 to l0_left_collar_front/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_btorso']), 31, int(panel_ids['l0_left_btorso']), 0, True, False), "Sewing failed: l0_right_btorso/5 to l0_left_btorso/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l0_right_collar_back']), 2, int(panel_ids['l0_left_collar_back']), 7, True, False), "Sewing failed: l0_right_collar_back/2 to l0_left_collar_back/1"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_f']), 0, int(panel_ids['l1_left_sleeve_b']), 28, True, False), "Sewing failed: l1_left_sleeve_f/0 to l1_left_sleeve_b/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_f']), 25, int(panel_ids['l1_left_sleeve_b']), 1, True, False), "Sewing failed: l1_left_sleeve_f/2 to l1_left_sleeve_b/1"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_f']), 1, int(panel_ids['l1_left_ftorso']), 25, True, False), "Sewing failed: l1_left_sleeve_f/1 to l1_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_f']), 2, int(panel_ids['l1_left_ftorso']), 24, True, False), "Sewing failed: l1_left_sleeve_f/1 to l1_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_f']), 3, int(panel_ids['l1_left_ftorso']), 23, True, False), "Sewing failed: l1_left_sleeve_f/1 to l1_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_f']), 4, int(panel_ids['l1_left_ftorso']), 22, True, False), "Sewing failed: l1_left_sleeve_f/1 to l1_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_f']), 5, int(panel_ids['l1_left_ftorso']), 21, True, False), "Sewing failed: l1_left_sleeve_f/1 to l1_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_f']), 6, int(panel_ids['l1_left_ftorso']), 20, True, False), "Sewing failed: l1_left_sleeve_f/1 to l1_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_f']), 7, int(panel_ids['l1_left_ftorso']), 19, True, False), "Sewing failed: l1_left_sleeve_f/1 to l1_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_f']), 8, int(panel_ids['l1_left_ftorso']), 18, True, False), "Sewing failed: l1_left_sleeve_f/1 to l1_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_f']), 9, int(panel_ids['l1_left_ftorso']), 17, True, False), "Sewing failed: l1_left_sleeve_f/1 to l1_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_f']), 10, int(panel_ids['l1_left_ftorso']), 16, True, False), "Sewing failed: l1_left_sleeve_f/1 to l1_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_f']), 11, int(panel_ids['l1_left_ftorso']), 15, True, False), "Sewing failed: l1_left_sleeve_f/1 to l1_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_f']), 12, int(panel_ids['l1_left_ftorso']), 14, True, False), "Sewing failed: l1_left_sleeve_f/1 to l1_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_f']), 13, int(panel_ids['l1_left_ftorso']), 13, True, False), "Sewing failed: l1_left_sleeve_f/1 to l1_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_f']), 14, int(panel_ids['l1_left_ftorso']), 12, True, False), "Sewing failed: l1_left_sleeve_f/1 to l1_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_f']), 15, int(panel_ids['l1_left_ftorso']), 11, True, False), "Sewing failed: l1_left_sleeve_f/1 to l1_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_f']), 16, int(panel_ids['l1_left_ftorso']), 10, True, False), "Sewing failed: l1_left_sleeve_f/1 to l1_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_f']), 17, int(panel_ids['l1_left_ftorso']), 9, True, False), "Sewing failed: l1_left_sleeve_f/1 to l1_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_f']), 18, int(panel_ids['l1_left_ftorso']), 8, True, False), "Sewing failed: l1_left_sleeve_f/1 to l1_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_f']), 19, int(panel_ids['l1_left_ftorso']), 7, True, False), "Sewing failed: l1_left_sleeve_f/1 to l1_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_f']), 20, int(panel_ids['l1_left_ftorso']), 6, True, False), "Sewing failed: l1_left_sleeve_f/1 to l1_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_f']), 21, int(panel_ids['l1_left_ftorso']), 5, True, False), "Sewing failed: l1_left_sleeve_f/1 to l1_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_f']), 22, int(panel_ids['l1_left_ftorso']), 4, True, False), "Sewing failed: l1_left_sleeve_f/1 to l1_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_f']), 23, int(panel_ids['l1_left_ftorso']), 3, True, False), "Sewing failed: l1_left_sleeve_f/1 to l1_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_f']), 24, int(panel_ids['l1_left_ftorso']), 2, True, False), "Sewing failed: l1_left_sleeve_f/1 to l1_left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_b']), 24, int(panel_ids['l1_left_ftorso']), 29, True, False), "Sewing failed: l1_left_sleeve_b/3 to l1_left_ftorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_b']), 25, int(panel_ids['l1_left_ftorso']), 28, True, False), "Sewing failed: l1_left_sleeve_b/3 to l1_left_ftorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_b']), 26, int(panel_ids['l1_left_ftorso']), 27, True, False), "Sewing failed: l1_left_sleeve_b/3 to l1_left_ftorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_b']), 27, int(panel_ids['l1_left_ftorso']), 26, True, False), "Sewing failed: l1_left_sleeve_b/3 to l1_left_ftorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_b']), 2, int(panel_ids['l1_left_btorso']), 34, True, False), "Sewing failed: l1_left_sleeve_b/2 to l1_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_b']), 3, int(panel_ids['l1_left_btorso']), 33, True, False), "Sewing failed: l1_left_sleeve_b/2 to l1_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_b']), 4, int(panel_ids['l1_left_btorso']), 32, True, False), "Sewing failed: l1_left_sleeve_b/2 to l1_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_b']), 5, int(panel_ids['l1_left_btorso']), 31, True, False), "Sewing failed: l1_left_sleeve_b/2 to l1_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_b']), 6, int(panel_ids['l1_left_btorso']), 30, True, False), "Sewing failed: l1_left_sleeve_b/2 to l1_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_b']), 7, int(panel_ids['l1_left_btorso']), 29, True, False), "Sewing failed: l1_left_sleeve_b/2 to l1_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_b']), 8, int(panel_ids['l1_left_btorso']), 28, True, False), "Sewing failed: l1_left_sleeve_b/2 to l1_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_b']), 9, int(panel_ids['l1_left_btorso']), 27, True, False), "Sewing failed: l1_left_sleeve_b/2 to l1_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_b']), 10, int(panel_ids['l1_left_btorso']), 26, True, False), "Sewing failed: l1_left_sleeve_b/2 to l1_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_b']), 11, int(panel_ids['l1_left_btorso']), 25, True, False), "Sewing failed: l1_left_sleeve_b/2 to l1_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_b']), 12, int(panel_ids['l1_left_btorso']), 24, True, False), "Sewing failed: l1_left_sleeve_b/2 to l1_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_b']), 13, int(panel_ids['l1_left_btorso']), 23, True, False), "Sewing failed: l1_left_sleeve_b/2 to l1_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_b']), 14, int(panel_ids['l1_left_btorso']), 22, True, False), "Sewing failed: l1_left_sleeve_b/2 to l1_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_b']), 15, int(panel_ids['l1_left_btorso']), 21, True, False), "Sewing failed: l1_left_sleeve_b/2 to l1_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_b']), 16, int(panel_ids['l1_left_btorso']), 20, True, False), "Sewing failed: l1_left_sleeve_b/2 to l1_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_b']), 17, int(panel_ids['l1_left_btorso']), 19, True, False), "Sewing failed: l1_left_sleeve_b/2 to l1_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_b']), 18, int(panel_ids['l1_left_btorso']), 18, True, False), "Sewing failed: l1_left_sleeve_b/2 to l1_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_b']), 19, int(panel_ids['l1_left_btorso']), 17, True, False), "Sewing failed: l1_left_sleeve_b/2 to l1_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_b']), 20, int(panel_ids['l1_left_btorso']), 16, True, False), "Sewing failed: l1_left_sleeve_b/2 to l1_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_b']), 21, int(panel_ids['l1_left_btorso']), 15, True, False), "Sewing failed: l1_left_sleeve_b/2 to l1_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_b']), 22, int(panel_ids['l1_left_btorso']), 14, True, False), "Sewing failed: l1_left_sleeve_b/2 to l1_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_sleeve_b']), 23, int(panel_ids['l1_left_btorso']), 13, True, False), "Sewing failed: l1_left_sleeve_b/2 to l1_left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_ftorso']), 30, int(panel_ids['l1_left_btorso']), 12, True, False), "Sewing failed: l1_left_ftorso/4 to l1_left_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_left_ftorso']), 1, int(panel_ids['l1_left_btorso']), 35, True, False), "Sewing failed: l1_left_ftorso/1 to l1_left_btorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_f']), 26, int(panel_ids['l1_right_sleeve_b']), 0, True, False), "Sewing failed: l1_right_sleeve_f/3 to l1_right_sleeve_b/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_f']), 1, int(panel_ids['l1_right_sleeve_b']), 27, True, False), "Sewing failed: l1_right_sleeve_f/1 to l1_right_sleeve_b/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_f']), 2, int(panel_ids['l1_right_ftorso']), 42, True, False), "Sewing failed: l1_right_sleeve_f/2 to l1_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_f']), 3, int(panel_ids['l1_right_ftorso']), 41, True, False), "Sewing failed: l1_right_sleeve_f/2 to l1_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_f']), 4, int(panel_ids['l1_right_ftorso']), 40, True, False), "Sewing failed: l1_right_sleeve_f/2 to l1_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_f']), 5, int(panel_ids['l1_right_ftorso']), 39, True, False), "Sewing failed: l1_right_sleeve_f/2 to l1_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_f']), 6, int(panel_ids['l1_right_ftorso']), 38, True, False), "Sewing failed: l1_right_sleeve_f/2 to l1_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_f']), 7, int(panel_ids['l1_right_ftorso']), 37, True, False), "Sewing failed: l1_right_sleeve_f/2 to l1_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_f']), 8, int(panel_ids['l1_right_ftorso']), 36, True, False), "Sewing failed: l1_right_sleeve_f/2 to l1_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_f']), 9, int(panel_ids['l1_right_ftorso']), 35, True, False), "Sewing failed: l1_right_sleeve_f/2 to l1_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_f']), 10, int(panel_ids['l1_right_ftorso']), 34, True, False), "Sewing failed: l1_right_sleeve_f/2 to l1_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_f']), 11, int(panel_ids['l1_right_ftorso']), 33, True, False), "Sewing failed: l1_right_sleeve_f/2 to l1_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_f']), 12, int(panel_ids['l1_right_ftorso']), 32, True, False), "Sewing failed: l1_right_sleeve_f/2 to l1_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_f']), 13, int(panel_ids['l1_right_ftorso']), 31, True, False), "Sewing failed: l1_right_sleeve_f/2 to l1_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_f']), 14, int(panel_ids['l1_right_ftorso']), 30, True, False), "Sewing failed: l1_right_sleeve_f/2 to l1_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_f']), 15, int(panel_ids['l1_right_ftorso']), 29, True, False), "Sewing failed: l1_right_sleeve_f/2 to l1_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_f']), 16, int(panel_ids['l1_right_ftorso']), 28, True, False), "Sewing failed: l1_right_sleeve_f/2 to l1_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_f']), 17, int(panel_ids['l1_right_ftorso']), 27, True, False), "Sewing failed: l1_right_sleeve_f/2 to l1_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_f']), 18, int(panel_ids['l1_right_ftorso']), 26, True, False), "Sewing failed: l1_right_sleeve_f/2 to l1_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_f']), 19, int(panel_ids['l1_right_ftorso']), 25, True, False), "Sewing failed: l1_right_sleeve_f/2 to l1_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_f']), 20, int(panel_ids['l1_right_ftorso']), 24, True, False), "Sewing failed: l1_right_sleeve_f/2 to l1_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_f']), 21, int(panel_ids['l1_right_ftorso']), 23, True, False), "Sewing failed: l1_right_sleeve_f/2 to l1_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_f']), 22, int(panel_ids['l1_right_ftorso']), 22, True, False), "Sewing failed: l1_right_sleeve_f/2 to l1_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_f']), 23, int(panel_ids['l1_right_ftorso']), 21, True, False), "Sewing failed: l1_right_sleeve_f/2 to l1_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_f']), 24, int(panel_ids['l1_right_ftorso']), 20, True, False), "Sewing failed: l1_right_sleeve_f/2 to l1_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_f']), 25, int(panel_ids['l1_right_ftorso']), 19, True, False), "Sewing failed: l1_right_sleeve_f/2 to l1_right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_b']), 1, int(panel_ids['l1_right_ftorso']), 18, True, False), "Sewing failed: l1_right_sleeve_b/1 to l1_right_ftorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_b']), 2, int(panel_ids['l1_right_ftorso']), 17, True, False), "Sewing failed: l1_right_sleeve_b/1 to l1_right_ftorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_b']), 3, int(panel_ids['l1_right_ftorso']), 16, True, False), "Sewing failed: l1_right_sleeve_b/1 to l1_right_ftorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_b']), 4, int(panel_ids['l1_right_ftorso']), 15, True, False), "Sewing failed: l1_right_sleeve_b/1 to l1_right_ftorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_b']), 5, int(panel_ids['l1_right_btorso']), 23, True, False), "Sewing failed: l1_right_sleeve_b/2 to l1_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_b']), 6, int(panel_ids['l1_right_btorso']), 22, True, False), "Sewing failed: l1_right_sleeve_b/2 to l1_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_b']), 7, int(panel_ids['l1_right_btorso']), 21, True, False), "Sewing failed: l1_right_sleeve_b/2 to l1_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_b']), 8, int(panel_ids['l1_right_btorso']), 20, True, False), "Sewing failed: l1_right_sleeve_b/2 to l1_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_b']), 9, int(panel_ids['l1_right_btorso']), 19, True, False), "Sewing failed: l1_right_sleeve_b/2 to l1_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_b']), 10, int(panel_ids['l1_right_btorso']), 18, True, False), "Sewing failed: l1_right_sleeve_b/2 to l1_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_b']), 11, int(panel_ids['l1_right_btorso']), 17, True, False), "Sewing failed: l1_right_sleeve_b/2 to l1_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_b']), 12, int(panel_ids['l1_right_btorso']), 16, True, False), "Sewing failed: l1_right_sleeve_b/2 to l1_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_b']), 13, int(panel_ids['l1_right_btorso']), 15, True, False), "Sewing failed: l1_right_sleeve_b/2 to l1_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_b']), 14, int(panel_ids['l1_right_btorso']), 14, True, False), "Sewing failed: l1_right_sleeve_b/2 to l1_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_b']), 15, int(panel_ids['l1_right_btorso']), 13, True, False), "Sewing failed: l1_right_sleeve_b/2 to l1_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_b']), 16, int(panel_ids['l1_right_btorso']), 12, True, False), "Sewing failed: l1_right_sleeve_b/2 to l1_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_b']), 17, int(panel_ids['l1_right_btorso']), 11, True, False), "Sewing failed: l1_right_sleeve_b/2 to l1_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_b']), 18, int(panel_ids['l1_right_btorso']), 10, True, False), "Sewing failed: l1_right_sleeve_b/2 to l1_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_b']), 19, int(panel_ids['l1_right_btorso']), 9, True, False), "Sewing failed: l1_right_sleeve_b/2 to l1_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_b']), 20, int(panel_ids['l1_right_btorso']), 8, True, False), "Sewing failed: l1_right_sleeve_b/2 to l1_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_b']), 21, int(panel_ids['l1_right_btorso']), 7, True, False), "Sewing failed: l1_right_sleeve_b/2 to l1_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_b']), 22, int(panel_ids['l1_right_btorso']), 6, True, False), "Sewing failed: l1_right_sleeve_b/2 to l1_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_b']), 23, int(panel_ids['l1_right_btorso']), 5, True, False), "Sewing failed: l1_right_sleeve_b/2 to l1_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_b']), 24, int(panel_ids['l1_right_btorso']), 4, True, False), "Sewing failed: l1_right_sleeve_b/2 to l1_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_b']), 25, int(panel_ids['l1_right_btorso']), 3, True, False), "Sewing failed: l1_right_sleeve_b/2 to l1_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_sleeve_b']), 26, int(panel_ids['l1_right_btorso']), 2, True, False), "Sewing failed: l1_right_sleeve_b/2 to l1_right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_ftorso']), 14, int(panel_ids['l1_right_btorso']), 24, True, False), "Sewing failed: l1_right_ftorso/2 to l1_right_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_ftorso']), 43, int(panel_ids['l1_right_btorso']), 1, True, False), "Sewing failed: l1_right_ftorso/5 to l1_right_btorso/1"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_ftorso']), 0, int(panel_ids['l1_left_ftorso']), 44, True, False), "Sewing failed: l1_right_ftorso/0 to l1_left_ftorso/6"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['l1_right_btorso']), 36, int(panel_ids['l1_left_btorso']), 0, True, False), "Sewing failed: l1_right_btorso/5 to l1_left_btorso/0"

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
                radial = 52 if key.startswith("l1_") else 50
                # Native points center each pattern independently; place halves on their own side.
                if "ftorso" in key:
                    pattern_api.SetArrangementPosition(pid, 35 if "left" in key else 65, panel_arr_y[key], radial)
                elif "btorso" in key:
                    pattern_api.SetArrangementPosition(pid, 15 if "left" in key else 85, panel_arr_y[key], radial)
                elif "sleeve" in key:
                    ap = pattern_api.GetArrangementOfPattern(pid)
                    arm_y = 95 if "_1_" in target_name else 50
                    pattern_api.SetArrangementPosition(pid, int(ap["ArrangementOffsetX"]), arm_y, radial)
                elif "collar_front" in key:
                    pattern_api.SetArrangementPosition(pid, 87 if "left" in key else 13, 50, radial)
                elif "collar_back" in key:
                    pattern_api.SetArrangementPosition(pid, 62 if "left" in key else 38, 50, radial)
                print(f"Arranged {key} -> {target_name} (idx {matched_id})")

    print("\nResetting cloth arrangement in 3D...")
    utility_api.ResetClothArrangement()

    opt_initial = ApiTypes.ImportExportOption()
    opt_initial.bExportGarment = True
    opt_initial.bExportAvatar = False
    export_api.ExportOBJ('/Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/out/layered_tops_test/layered_tops_both_draped_arranged.obj', opt_initial)
    # === 5. Simulate Cloth Drape (360 steps) ===
    print("\n--- Simulating Physical Drape (360 steps) ---")
    utility_api.SetSimulationLayerBasedCollisionDetection(True)
    utility_api.Simulate(251)
    # Reset all patterns to Layer 0 for natural contact settling
    for pid in panel_ids.values():
        pattern_api.SetPatternLayer(pid, 0)
    utility_api.Simulate(109)
    print("Simulation completed!")

    # === 6. Export Garment Mesh (Non-Interactive) ===
    print("\n--- Exporting OBJ & ZPRJ ---")
    opt = ApiTypes.ImportExportOption()
    opt.bExportGarment = True
    opt.bExportAvatar = False
    export_api.ExportOBJ('/Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/out/layered_tops_test/layered_tops_both_draped.obj', opt)
    export_api.ExportZPrj('/Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/out/layered_tops_test/layered_tops_both_draped.zprj', False)
    print("Finished headless drape export!")

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)