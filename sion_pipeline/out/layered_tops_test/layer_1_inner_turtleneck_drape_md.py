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
    # Panel: left_sleeve_f -> Arm_Front_2_L
    left_sleeve_f_pts = [
        (1150.0, 987.2278, 0),
        (1150.0, 1389.9084, 0),
        (1142.1367, 1388.4898, 0),
        (1134.4427, 1386.3357, 0),
        (1127.005, 1383.4183, 0),
        (1119.9086, 1379.7479, 0),
        (1113.2213, 1375.3758, 0),
        (1106.9808, 1370.3857, 0),
        (1101.1905, 1364.8788, 0),
        (1095.8242, 1358.9572, 0),
        (1090.8343, 1352.7144, 0),
        (1086.1616, 1346.2303, 0),
        (1081.7412, 1339.5713, 0),
        (1077.5068, 1332.7923, 0),
        (1073.3921, 1325.9398, 0),
        (1069.3311, 1319.0553, 0),
        (1065.2574, 1312.1783, 0),
        (1061.1034, 1305.3496, 0),
        (1056.7989, 1298.615, 0),
        (1052.2709, 1292.0289, 0),
        (1047.4443, 1285.6589, 0),
        (1042.2449, 1279.5901, 0),
        (1036.6065, 1273.9279, 0),
        (1030.4828, 1268.7959, 0),
        (1072.3138, 987.2278, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(left_sleeve_f_pts)
    if pid is not None:
        panel_ids['left_sleeve_f'] = pid
        panel_arr_targets['left_sleeve_f'] = 'Arm_Front_2_L'
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'left_sleeve_f')
        except Exception:
            pass
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 25, "MD boundary segment mismatch: left_sleeve_f"
        print(f"Created pattern left_sleeve_f -> ID {pid} (target=Arm_Front_2_L)")

    # Panel: left_sleeve_b -> Arm_Back_2_L
    left_sleeve_b_pts = [
        (1400.0, 987.2278, 0),
        (1477.6862, 987.2278, 0),
        (1519.5172, 1268.7959, 0),
        (1514.5953, 1274.9239, 0),
        (1510.3185, 1281.5199, 0),
        (1506.5891, 1288.4414, 0),
        (1503.2905, 1295.5791, 0),
        (1500.3042, 1302.8535, 0),
        (1497.5175, 1310.207, 0),
        (1494.8243, 1317.5954, 0),
        (1492.1231, 1324.9809, 0),
        (1489.3143, 1332.3259, 0),
        (1486.2973, 1339.5876, 0),
        (1482.9697, 1346.7119, 0),
        (1479.2284, 1353.6272, 0),
        (1474.9763, 1360.2397, 0),
        (1470.135, 1366.4326, 0),
        (1464.6633, 1372.075, 0),
        (1458.5735, 1377.0431, 0),
        (1451.9338, 1381.2482, 0),
        (1444.8516, 1384.657, 0),
        (1437.4458, 1387.2918, 0),
        (1429.8232, 1389.2146, 0),
        (1422.0679, 1390.5058, 0),
        (1414.7033, 1390.7925, 0),
        (1407.3357, 1390.6125, 0),
        (1400.0, 1389.9084, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(left_sleeve_b_pts)
    if pid is not None:
        panel_ids['left_sleeve_b'] = pid
        panel_arr_targets['left_sleeve_b'] = 'Arm_Back_2_L'
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'left_sleeve_b')
        except Exception:
            pass
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 27, "MD boundary segment mismatch: left_sleeve_b"
        print(f"Created pattern left_sleeve_b -> ID {pid} (target=Arm_Back_2_L)")

    # Panel: left_btorso -> Body_Back_Center_1
    left_btorso_pts = [
        (600.0, 755.5871, 0),
        (600.0, 1244.7221, 0),
        (592.3003, 1245.5085, 0),
        (584.9186, 1247.8355, 0),
        (578.1599, 1251.6068, 0),
        (572.3031, 1256.6667, 0),
        (567.5904, 1262.8062, 0),
        (564.2162, 1269.7717, 0),
        (562.32, 1277.2756, 0),
        (504.0789, 1246.6335, 0),
        (503.7076, 1238.7786, 0),
        (503.3494, 1230.9232, 0),
        (502.9886, 1223.0678, 0),
        (502.6063, 1215.2135, 0),
        (502.1799, 1207.3614, 0),
        (501.6821, 1199.5136, 0),
        (501.079, 1191.6732, 0),
        (500.3285, 1183.8457, 0),
        (499.3769, 1176.0401, 0),
        (498.1558, 1168.2724, 0),
        (496.577, 1160.5698, 0),
        (494.527, 1152.9798, 0),
        (491.8652, 1145.5834, 0),
        (488.4308, 1138.5147, 0),
        (484.0765, 1131.9755, 0),
        (478.7346, 1126.2177, 0),
        (472.4831, 1121.4635, 0),
        (465.5314, 1117.8051, 0),
        (458.1242, 1115.1818, 0),
        (450.4585, 1113.4447, 0),
        (442.663, 1112.4285, 0),
        (433.0752, 755.5871, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(left_btorso_pts)
    if pid is not None:
        panel_ids['left_btorso'] = pid
        panel_arr_targets['left_btorso'] = 'Body_Back_Center_1'
        panel_arr_y['left_btorso'] = 51
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'left_btorso')
        except Exception:
            pass
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 32, "MD boundary segment mismatch: left_btorso"
        print(f"Created pattern left_btorso -> ID {pid} (target=Body_Back_Center_1)")

    # Panel: left_ftorso -> Body_Front_Center_1
    left_ftorso_pts = [
        (0.0, 754.2862, 0),
        (223.0011, 754.2862, 0),
        (209.3471, 1113.1716, 0),
        (201.4592, 1111.9358, 0),
        (193.501, 1111.3042, 0),
        (185.5196, 1111.4148, 0),
        (177.6022, 1112.417, 0),
        (169.8841, 1114.4416, 0),
        (162.5367, 1117.5514, 0),
        (155.7223, 1121.7015, 0),
        (149.5399, 1126.7472, 0),
        (144.004, 1132.4969, 0),
        (139.0639, 1138.7678, 0),
        (134.638, 1145.4127, 0),
        (130.6391, 1152.3237, 0),
        (126.9871, 1159.4246, 0),
        (123.6135, 1166.6621, 0),
        (120.461, 1173.9989, 0),
        (117.4828, 1181.4082, 0),
        (114.6402, 1188.8707, 0),
        (111.9014, 1196.3719, 0),
        (109.2398, 1203.9009, 0),
        (106.6334, 1211.4492, 0),
        (104.0635, 1219.0099, 0),
        (101.514, 1226.5776, 0),
        (99.1849, 1233.5126, 0),
        (96.8524, 1240.4465, 0),
        (94.5086, 1247.3766, 0),
        (37.68, 1277.2756, 0),
        (39.0581, 1270.1404, 0),
        (39.097, 1262.8734, 0),
        (37.7954, 1255.7239, 0),
        (35.198, 1248.9368, 0),
        (31.3939, 1242.745, 0),
        (26.5133, 1237.3607, 0),
        (20.7237, 1232.9686, 0),
        (14.2236, 1229.7191, 0),
        (7.2359, 1227.7238, 0),
        (0.0, 1227.051, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(left_ftorso_pts)
    if pid is not None:
        panel_ids['left_ftorso'] = pid
        panel_arr_targets['left_ftorso'] = 'Body_Front_Center_1'
        panel_arr_y['left_ftorso'] = 51
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'left_ftorso')
        except Exception:
            pass
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 39, "MD boundary segment mismatch: left_ftorso"
        print(f"Created pattern left_ftorso -> ID {pid} (target=Body_Front_Center_1)")

    # Panel: left_collar_back -> Neck_Back
    left_collar_back_pts = [
        (750.0, 1297.1, 0),
        (757.7531, 1297.1, 0),
        (765.5063, 1297.1, 0),
        (773.2594, 1297.1, 0),
        (781.0125, 1297.1, 0),
        (788.7657, 1297.1, 0),
        (796.5188, 1297.1, 0),
        (804.2719, 1297.1, 0),
        (804.2719, 1337.1, 0),
        (750.0, 1337.1, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(left_collar_back_pts)
    if pid is not None:
        panel_ids['left_collar_back'] = pid
        panel_arr_targets['left_collar_back'] = 'Neck_Back'
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'left_collar_back')
        except Exception:
            pass
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 10, "MD boundary segment mismatch: left_collar_back"
        print(f"Created pattern left_collar_back -> ID {pid} (target=Neck_Back)")

    # Panel: left_collar_front -> Neck_Front
    left_collar_front_pts = [
        (150.0, 1297.1, 0),
        (150.0, 1337.1, 0),
        (77.2251, 1337.1, 0),
        (77.2251, 1297.1, 0),
        (84.5026, 1297.1, 0),
        (91.7801, 1297.1, 0),
        (99.0576, 1297.1, 0),
        (106.3351, 1297.1, 0),
        (113.6125, 1297.1, 0),
        (120.89, 1297.1, 0),
        (128.1675, 1297.1, 0),
        (135.445, 1297.1, 0),
        (142.7225, 1297.1, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(left_collar_front_pts)
    if pid is not None:
        panel_ids['left_collar_front'] = pid
        panel_arr_targets['left_collar_front'] = 'Neck_Front'
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'left_collar_front')
        except Exception:
            pass
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 13, "MD boundary segment mismatch: left_collar_front"
        print(f"Created pattern left_collar_front -> ID {pid} (target=Neck_Front)")

    # Panel: right_sleeve_f -> Arm_Front_2_R
    right_sleeve_f_pts = [
        (-550.0, 987.2278, 0),
        (-472.3138, 987.2278, 0),
        (-430.4828, 1268.7959, 0),
        (-436.6065, 1273.9279, 0),
        (-442.2449, 1279.5901, 0),
        (-447.4443, 1285.6589, 0),
        (-452.2709, 1292.0289, 0),
        (-456.7989, 1298.615, 0),
        (-461.1034, 1305.3496, 0),
        (-465.2574, 1312.1783, 0),
        (-469.3311, 1319.0553, 0),
        (-473.3921, 1325.9398, 0),
        (-477.5068, 1332.7923, 0),
        (-481.7412, 1339.5713, 0),
        (-486.1616, 1346.2303, 0),
        (-490.8343, 1352.7144, 0),
        (-495.8242, 1358.9572, 0),
        (-501.1905, 1364.8788, 0),
        (-506.9808, 1370.3857, 0),
        (-513.2213, 1375.3758, 0),
        (-519.9086, 1379.7479, 0),
        (-527.005, 1383.4183, 0),
        (-534.4427, 1386.3357, 0),
        (-542.1367, 1388.4898, 0),
        (-550.0, 1389.9084, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(right_sleeve_f_pts)
    if pid is not None:
        panel_ids['right_sleeve_f'] = pid
        panel_arr_targets['right_sleeve_f'] = 'Arm_Front_2_R'
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'right_sleeve_f')
        except Exception:
            pass
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 25, "MD boundary segment mismatch: right_sleeve_f"
        print(f"Created pattern right_sleeve_f -> ID {pid} (target=Arm_Front_2_R)")

    # Panel: right_sleeve_b -> Arm_Back_2_R
    right_sleeve_b_pts = [
        (-800.0, 987.2278, 0),
        (-800.0, 1389.9084, 0),
        (-807.3357, 1390.6125, 0),
        (-814.7033, 1390.7925, 0),
        (-822.0679, 1390.5058, 0),
        (-829.8232, 1389.2146, 0),
        (-837.4458, 1387.2918, 0),
        (-844.8516, 1384.657, 0),
        (-851.9338, 1381.2482, 0),
        (-858.5735, 1377.0431, 0),
        (-864.6633, 1372.075, 0),
        (-870.135, 1366.4326, 0),
        (-874.9763, 1360.2397, 0),
        (-879.2284, 1353.6272, 0),
        (-882.9697, 1346.7119, 0),
        (-886.2973, 1339.5876, 0),
        (-889.3143, 1332.3259, 0),
        (-892.1231, 1324.9809, 0),
        (-894.8243, 1317.5954, 0),
        (-897.5175, 1310.207, 0),
        (-900.3042, 1302.8535, 0),
        (-903.2905, 1295.5791, 0),
        (-906.5891, 1288.4414, 0),
        (-910.3185, 1281.5199, 0),
        (-914.5953, 1274.9239, 0),
        (-919.5172, 1268.7959, 0),
        (-877.6862, 987.2278, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(right_sleeve_b_pts)
    if pid is not None:
        panel_ids['right_sleeve_b'] = pid
        panel_arr_targets['right_sleeve_b'] = 'Arm_Back_2_R'
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'right_sleeve_b')
        except Exception:
            pass
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 27, "MD boundary segment mismatch: right_sleeve_b"
        print(f"Created pattern right_sleeve_b -> ID {pid} (target=Arm_Back_2_R)")

    # Panel: right_collar_front -> Neck_Front
    right_collar_front_pts = [
        (-150.0, 1297.1, 0),
        (-142.7225, 1297.1, 0),
        (-135.445, 1297.1, 0),
        (-128.1675, 1297.1, 0),
        (-120.89, 1297.1, 0),
        (-113.6125, 1297.1, 0),
        (-106.3351, 1297.1, 0),
        (-99.0576, 1297.1, 0),
        (-91.7801, 1297.1, 0),
        (-84.5026, 1297.1, 0),
        (-77.2251, 1297.1, 0),
        (-77.2251, 1337.1, 0),
        (-150.0, 1337.1, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(right_collar_front_pts)
    if pid is not None:
        panel_ids['right_collar_front'] = pid
        panel_arr_targets['right_collar_front'] = 'Neck_Front'
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'right_collar_front')
        except Exception:
            pass
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 13, "MD boundary segment mismatch: right_collar_front"
        print(f"Created pattern right_collar_front -> ID {pid} (target=Neck_Front)")

    # Panel: right_collar_back -> Neck_Back
    right_collar_back_pts = [
        (450.0, 1297.1, 0),
        (450.0, 1337.1, 0),
        (395.7281, 1337.1, 0),
        (395.7281, 1297.1, 0),
        (403.4812, 1297.1, 0),
        (411.2343, 1297.1, 0),
        (418.9875, 1297.1, 0),
        (426.7406, 1297.1, 0),
        (434.4937, 1297.1, 0),
        (442.2469, 1297.1, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(right_collar_back_pts)
    if pid is not None:
        panel_ids['right_collar_back'] = pid
        panel_arr_targets['right_collar_back'] = 'Neck_Back'
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'right_collar_back')
        except Exception:
            pass
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 10, "MD boundary segment mismatch: right_collar_back"
        print(f"Created pattern right_collar_back -> ID {pid} (target=Neck_Back)")

    # Panel: right_btorso -> Body_Back_Center_1
    right_btorso_pts = [
        (600.0, 755.5871, 0),
        (766.9248, 755.5871, 0),
        (757.337, 1112.4285, 0),
        (749.5415, 1113.4447, 0),
        (741.8758, 1115.1818, 0),
        (734.4686, 1117.8051, 0),
        (727.5169, 1121.4635, 0),
        (721.2654, 1126.2177, 0),
        (715.9235, 1131.9755, 0),
        (711.5692, 1138.5147, 0),
        (708.1348, 1145.5834, 0),
        (705.473, 1152.9798, 0),
        (703.423, 1160.5698, 0),
        (701.8442, 1168.2724, 0),
        (700.6231, 1176.0401, 0),
        (699.6715, 1183.8457, 0),
        (698.921, 1191.6732, 0),
        (698.3179, 1199.5136, 0),
        (697.8201, 1207.3614, 0),
        (697.3937, 1215.2135, 0),
        (697.0114, 1223.0678, 0),
        (696.6506, 1230.9232, 0),
        (696.2924, 1238.7786, 0),
        (695.9211, 1246.6335, 0),
        (637.68, 1277.2756, 0),
        (635.7838, 1269.7717, 0),
        (632.4096, 1262.8062, 0),
        (627.6969, 1256.6667, 0),
        (621.8401, 1251.6068, 0),
        (615.0814, 1247.8355, 0),
        (607.6997, 1245.5085, 0),
        (600.0, 1244.7221, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(right_btorso_pts)
    if pid is not None:
        panel_ids['right_btorso'] = pid
        panel_arr_targets['right_btorso'] = 'Body_Back_Center_1'
        panel_arr_y['right_btorso'] = 51
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'right_btorso')
        except Exception:
            pass
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 32, "MD boundary segment mismatch: right_btorso"
        print(f"Created pattern right_btorso -> ID {pid} (target=Body_Back_Center_1)")

    # Panel: right_ftorso -> Body_Front_Center_1
    right_ftorso_pts = [
        (0.0, 754.2862, 0),
        (0.0, 1227.051, 0),
        (-7.2359, 1227.7238, 0),
        (-14.2236, 1229.7191, 0),
        (-20.7237, 1232.9686, 0),
        (-26.5133, 1237.3607, 0),
        (-31.3939, 1242.745, 0),
        (-35.198, 1248.9368, 0),
        (-37.7954, 1255.7239, 0),
        (-39.097, 1262.8734, 0),
        (-39.0581, 1270.1404, 0),
        (-37.68, 1277.2756, 0),
        (-94.5086, 1247.3766, 0),
        (-96.8524, 1240.4465, 0),
        (-99.1849, 1233.5126, 0),
        (-101.514, 1226.5776, 0),
        (-104.0635, 1219.0099, 0),
        (-106.6334, 1211.4492, 0),
        (-109.2398, 1203.9009, 0),
        (-111.9014, 1196.3719, 0),
        (-114.6402, 1188.8707, 0),
        (-117.4828, 1181.4082, 0),
        (-120.461, 1173.9989, 0),
        (-123.6135, 1166.6621, 0),
        (-126.9871, 1159.4246, 0),
        (-130.6391, 1152.3237, 0),
        (-134.638, 1145.4127, 0),
        (-139.0639, 1138.7678, 0),
        (-144.004, 1132.4969, 0),
        (-149.5399, 1126.7472, 0),
        (-155.7223, 1121.7015, 0),
        (-162.5367, 1117.5514, 0),
        (-169.8841, 1114.4416, 0),
        (-177.6022, 1112.417, 0),
        (-185.5196, 1111.4148, 0),
        (-193.501, 1111.3042, 0),
        (-201.4592, 1111.9358, 0),
        (-209.3471, 1113.1716, 0),
        (-223.0011, 754.2862, 0),
    ]
    pid = pattern_api.CreatePatternWithPoints(right_ftorso_pts)
    if pid is not None:
        panel_ids['right_ftorso'] = pid
        panel_arr_targets['right_ftorso'] = 'Body_Front_Center_1'
        panel_arr_y['right_ftorso'] = 51
        try:
            if hasattr(pattern_api, "SetPatternPieceName"):
                pattern_api.SetPatternPieceName(pid, 'right_ftorso')
        except Exception:
            pass
        pattern_api.SetParticleDistanceOfPattern(pid, 8.0)
        assert json.loads(pattern_api.GetPatternLineInfo(pid))["lineCount"] == 39, "MD boundary segment mismatch: right_ftorso"
        print(f"Created pattern right_ftorso -> ID {pid} (target=Body_Front_Center_1)")

    # === 3. Apply Sewing Stitches ===
    print("\n--- Sewing Seams ---")
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 0, int(panel_ids['left_sleeve_b']), 26, True, False), "Sewing failed: left_sleeve_f/0 to left_sleeve_b/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 23, int(panel_ids['left_sleeve_b']), 1, True, False), "Sewing failed: left_sleeve_f/2 to left_sleeve_b/1"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_collar_front']), 0, int(panel_ids['left_collar_back']), 9, True, False), "Sewing failed: left_collar_front/0 to left_collar_back/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 1, int(panel_ids['left_ftorso']), 23, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 2, int(panel_ids['left_ftorso']), 22, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 3, int(panel_ids['left_ftorso']), 21, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 4, int(panel_ids['left_ftorso']), 20, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 5, int(panel_ids['left_ftorso']), 19, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 6, int(panel_ids['left_ftorso']), 18, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 7, int(panel_ids['left_ftorso']), 17, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 8, int(panel_ids['left_ftorso']), 16, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 9, int(panel_ids['left_ftorso']), 15, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 10, int(panel_ids['left_ftorso']), 14, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 11, int(panel_ids['left_ftorso']), 13, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 12, int(panel_ids['left_ftorso']), 12, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 13, int(panel_ids['left_ftorso']), 11, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 14, int(panel_ids['left_ftorso']), 10, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 15, int(panel_ids['left_ftorso']), 9, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 16, int(panel_ids['left_ftorso']), 8, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 17, int(panel_ids['left_ftorso']), 7, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 18, int(panel_ids['left_ftorso']), 6, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 19, int(panel_ids['left_ftorso']), 5, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 20, int(panel_ids['left_ftorso']), 4, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 21, int(panel_ids['left_ftorso']), 3, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_f']), 22, int(panel_ids['left_ftorso']), 2, True, False), "Sewing failed: left_sleeve_f/1 to left_ftorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 23, int(panel_ids['left_ftorso']), 26, True, False), "Sewing failed: left_sleeve_b/3 to left_ftorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 24, int(panel_ids['left_ftorso']), 25, True, False), "Sewing failed: left_sleeve_b/3 to left_ftorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 25, int(panel_ids['left_ftorso']), 24, True, False), "Sewing failed: left_sleeve_b/3 to left_ftorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 2, int(panel_ids['left_btorso']), 29, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 3, int(panel_ids['left_btorso']), 28, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 4, int(panel_ids['left_btorso']), 27, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 5, int(panel_ids['left_btorso']), 26, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 6, int(panel_ids['left_btorso']), 25, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 7, int(panel_ids['left_btorso']), 24, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 8, int(panel_ids['left_btorso']), 23, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 9, int(panel_ids['left_btorso']), 22, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 10, int(panel_ids['left_btorso']), 21, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 11, int(panel_ids['left_btorso']), 20, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 12, int(panel_ids['left_btorso']), 19, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 13, int(panel_ids['left_btorso']), 18, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 14, int(panel_ids['left_btorso']), 17, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 15, int(panel_ids['left_btorso']), 16, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 16, int(panel_ids['left_btorso']), 15, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 17, int(panel_ids['left_btorso']), 14, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 18, int(panel_ids['left_btorso']), 13, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 19, int(panel_ids['left_btorso']), 12, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 20, int(panel_ids['left_btorso']), 11, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 21, int(panel_ids['left_btorso']), 10, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_sleeve_b']), 22, int(panel_ids['left_btorso']), 9, True, False), "Sewing failed: left_sleeve_b/2 to left_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_ftorso']), 28, int(panel_ids['left_collar_front']), 12, True, False), "Sewing failed: left_ftorso/5 to left_collar_front/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_ftorso']), 29, int(panel_ids['left_collar_front']), 11, True, False), "Sewing failed: left_ftorso/5 to left_collar_front/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_ftorso']), 30, int(panel_ids['left_collar_front']), 10, True, False), "Sewing failed: left_ftorso/5 to left_collar_front/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_ftorso']), 31, int(panel_ids['left_collar_front']), 9, True, False), "Sewing failed: left_ftorso/5 to left_collar_front/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_ftorso']), 32, int(panel_ids['left_collar_front']), 8, True, False), "Sewing failed: left_ftorso/5 to left_collar_front/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_ftorso']), 33, int(panel_ids['left_collar_front']), 7, True, False), "Sewing failed: left_ftorso/5 to left_collar_front/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_ftorso']), 34, int(panel_ids['left_collar_front']), 6, True, False), "Sewing failed: left_ftorso/5 to left_collar_front/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_ftorso']), 35, int(panel_ids['left_collar_front']), 5, True, False), "Sewing failed: left_ftorso/5 to left_collar_front/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_ftorso']), 36, int(panel_ids['left_collar_front']), 4, True, False), "Sewing failed: left_ftorso/5 to left_collar_front/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_ftorso']), 37, int(panel_ids['left_collar_front']), 3, True, False), "Sewing failed: left_ftorso/5 to left_collar_front/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_btorso']), 1, int(panel_ids['left_collar_back']), 6, True, False), "Sewing failed: left_btorso/1 to left_collar_back/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_btorso']), 2, int(panel_ids['left_collar_back']), 5, True, False), "Sewing failed: left_btorso/1 to left_collar_back/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_btorso']), 3, int(panel_ids['left_collar_back']), 4, True, False), "Sewing failed: left_btorso/1 to left_collar_back/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_btorso']), 4, int(panel_ids['left_collar_back']), 3, True, False), "Sewing failed: left_btorso/1 to left_collar_back/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_btorso']), 5, int(panel_ids['left_collar_back']), 2, True, False), "Sewing failed: left_btorso/1 to left_collar_back/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_btorso']), 6, int(panel_ids['left_collar_back']), 1, True, False), "Sewing failed: left_btorso/1 to left_collar_back/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_btorso']), 7, int(panel_ids['left_collar_back']), 0, True, False), "Sewing failed: left_btorso/1 to left_collar_back/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_ftorso']), 27, int(panel_ids['left_btorso']), 8, True, False), "Sewing failed: left_ftorso/4 to left_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['left_ftorso']), 1, int(panel_ids['left_btorso']), 30, True, False), "Sewing failed: left_ftorso/1 to left_btorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 24, int(panel_ids['right_sleeve_b']), 0, True, False), "Sewing failed: right_sleeve_f/3 to right_sleeve_b/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 1, int(panel_ids['right_sleeve_b']), 25, True, False), "Sewing failed: right_sleeve_f/1 to right_sleeve_b/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_collar_front']), 12, int(panel_ids['right_collar_back']), 0, True, False), "Sewing failed: right_collar_front/3 to right_collar_back/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 2, int(panel_ids['right_ftorso']), 36, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 3, int(panel_ids['right_ftorso']), 35, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 4, int(panel_ids['right_ftorso']), 34, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 5, int(panel_ids['right_ftorso']), 33, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 6, int(panel_ids['right_ftorso']), 32, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 7, int(panel_ids['right_ftorso']), 31, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 8, int(panel_ids['right_ftorso']), 30, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 9, int(panel_ids['right_ftorso']), 29, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 10, int(panel_ids['right_ftorso']), 28, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 11, int(panel_ids['right_ftorso']), 27, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 12, int(panel_ids['right_ftorso']), 26, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 13, int(panel_ids['right_ftorso']), 25, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 14, int(panel_ids['right_ftorso']), 24, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 15, int(panel_ids['right_ftorso']), 23, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 16, int(panel_ids['right_ftorso']), 22, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 17, int(panel_ids['right_ftorso']), 21, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 18, int(panel_ids['right_ftorso']), 20, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 19, int(panel_ids['right_ftorso']), 19, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 20, int(panel_ids['right_ftorso']), 18, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 21, int(panel_ids['right_ftorso']), 17, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 22, int(panel_ids['right_ftorso']), 16, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_f']), 23, int(panel_ids['right_ftorso']), 15, True, False), "Sewing failed: right_sleeve_f/2 to right_ftorso/4"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 1, int(panel_ids['right_ftorso']), 14, True, False), "Sewing failed: right_sleeve_b/1 to right_ftorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 2, int(panel_ids['right_ftorso']), 13, True, False), "Sewing failed: right_sleeve_b/1 to right_ftorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 3, int(panel_ids['right_ftorso']), 12, True, False), "Sewing failed: right_sleeve_b/1 to right_ftorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 4, int(panel_ids['right_btorso']), 22, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 5, int(panel_ids['right_btorso']), 21, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 6, int(panel_ids['right_btorso']), 20, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 7, int(panel_ids['right_btorso']), 19, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 8, int(panel_ids['right_btorso']), 18, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 9, int(panel_ids['right_btorso']), 17, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 10, int(panel_ids['right_btorso']), 16, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 11, int(panel_ids['right_btorso']), 15, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 12, int(panel_ids['right_btorso']), 14, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 13, int(panel_ids['right_btorso']), 13, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 14, int(panel_ids['right_btorso']), 12, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 15, int(panel_ids['right_btorso']), 11, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 16, int(panel_ids['right_btorso']), 10, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 17, int(panel_ids['right_btorso']), 9, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 18, int(panel_ids['right_btorso']), 8, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 19, int(panel_ids['right_btorso']), 7, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 20, int(panel_ids['right_btorso']), 6, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 21, int(panel_ids['right_btorso']), 5, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 22, int(panel_ids['right_btorso']), 4, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 23, int(panel_ids['right_btorso']), 3, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_sleeve_b']), 24, int(panel_ids['right_btorso']), 2, True, False), "Sewing failed: right_sleeve_b/2 to right_btorso/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_ftorso']), 1, int(panel_ids['right_collar_front']), 9, True, False), "Sewing failed: right_ftorso/1 to right_collar_front/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_ftorso']), 2, int(panel_ids['right_collar_front']), 8, True, False), "Sewing failed: right_ftorso/1 to right_collar_front/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_ftorso']), 3, int(panel_ids['right_collar_front']), 7, True, False), "Sewing failed: right_ftorso/1 to right_collar_front/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_ftorso']), 4, int(panel_ids['right_collar_front']), 6, True, False), "Sewing failed: right_ftorso/1 to right_collar_front/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_ftorso']), 5, int(panel_ids['right_collar_front']), 5, True, False), "Sewing failed: right_ftorso/1 to right_collar_front/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_ftorso']), 6, int(panel_ids['right_collar_front']), 4, True, False), "Sewing failed: right_ftorso/1 to right_collar_front/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_ftorso']), 7, int(panel_ids['right_collar_front']), 3, True, False), "Sewing failed: right_ftorso/1 to right_collar_front/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_ftorso']), 8, int(panel_ids['right_collar_front']), 2, True, False), "Sewing failed: right_ftorso/1 to right_collar_front/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_ftorso']), 9, int(panel_ids['right_collar_front']), 1, True, False), "Sewing failed: right_ftorso/1 to right_collar_front/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_ftorso']), 10, int(panel_ids['right_collar_front']), 0, True, False), "Sewing failed: right_ftorso/1 to right_collar_front/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_btorso']), 24, int(panel_ids['right_collar_back']), 9, True, False), "Sewing failed: right_btorso/4 to right_collar_back/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_btorso']), 25, int(panel_ids['right_collar_back']), 8, True, False), "Sewing failed: right_btorso/4 to right_collar_back/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_btorso']), 26, int(panel_ids['right_collar_back']), 7, True, False), "Sewing failed: right_btorso/4 to right_collar_back/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_btorso']), 27, int(panel_ids['right_collar_back']), 6, True, False), "Sewing failed: right_btorso/4 to right_collar_back/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_btorso']), 28, int(panel_ids['right_collar_back']), 5, True, False), "Sewing failed: right_btorso/4 to right_collar_back/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_btorso']), 29, int(panel_ids['right_collar_back']), 4, True, False), "Sewing failed: right_btorso/4 to right_collar_back/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_btorso']), 30, int(panel_ids['right_collar_back']), 3, True, False), "Sewing failed: right_btorso/4 to right_collar_back/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_ftorso']), 11, int(panel_ids['right_btorso']), 23, True, False), "Sewing failed: right_ftorso/2 to right_btorso/3"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_ftorso']), 37, int(panel_ids['right_btorso']), 1, True, False), "Sewing failed: right_ftorso/5 to right_btorso/1"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_ftorso']), 0, int(panel_ids['left_ftorso']), 38, True, False), "Sewing failed: right_ftorso/0 to left_ftorso/6"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_collar_front']), 10, int(panel_ids['left_collar_front']), 2, True, False), "Sewing failed: right_collar_front/1 to left_collar_front/2"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_btorso']), 31, int(panel_ids['left_btorso']), 0, True, False), "Sewing failed: right_btorso/5 to left_btorso/0"
    assert pattern_api.AddSeamlinePairGroup(int(panel_ids['right_collar_back']), 2, int(panel_ids['left_collar_back']), 7, True, False), "Sewing failed: right_collar_back/2 to left_collar_back/1"

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
                    pattern_api.SetArrangementPosition(pid, 35 if "left" in key else 65, panel_arr_y[key], 50)
                elif "btorso" in key:
                    pattern_api.SetArrangementPosition(pid, 15 if "left" in key else 85, panel_arr_y[key], 50)
                elif "sleeve" in key:
                    ap = pattern_api.GetArrangementOfPattern(pid)
                    arm_y = 95 if "_1_" in target_name else 50
                    pattern_api.SetArrangementPosition(pid, int(ap["ArrangementOffsetX"]), arm_y, 50)
                elif "collar_front" in key:
                    pattern_api.SetArrangementPosition(pid, 38 if "left" in key else 62, 55, 50)
                elif "collar_back" in key:
                    pattern_api.SetArrangementPosition(pid, 13 if "left" in key else 87, 55, 50)
                print(f"Arranged {key} -> {target_name} (idx {matched_id})")

    print("\nResetting cloth arrangement in 3D...")
    utility_api.ResetClothArrangement()

    opt_initial = ApiTypes.ImportExportOption()
    opt_initial.bExportGarment = True
    opt_initial.bExportAvatar = False
    export_api.ExportOBJ('/Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/out/layered_tops_test/layer_1_inner_turtleneck_draped_arranged.obj', opt_initial)
    # === 5. Simulate Cloth Drape (240 steps) ===
    print("\n--- Simulating Physical Drape (240 steps) ---")
    utility_api.Simulate(240)
    print("Simulation completed!")

    # === 6. Export Garment Mesh (Non-Interactive) ===
    print("\n--- Exporting OBJ & ZPRJ ---")
    opt = ApiTypes.ImportExportOption()
    opt.bExportGarment = True
    opt.bExportAvatar = False
    export_api.ExportOBJ('/Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/out/layered_tops_test/layer_1_inner_turtleneck_draped.obj', opt)
    export_api.ExportZPrj('/Users/vaz/Desktop/antigravity_apps/GarmentCode/sion_pipeline/out/layered_tops_test/layer_1_inner_turtleneck_draped.zprj', False)
    print("Finished headless drape export!")

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)