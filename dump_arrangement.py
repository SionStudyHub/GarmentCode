import pattern_api

dump_file = "/Users/vaz/Desktop/antigravity_apps/GarmentCode/arr_dump.txt"

with open(dump_file, "w") as f:
    f.write("=== Native Arrangement Points on Avatar ===\n")
    try:
        arr_list = pattern_api.GetArrangementList()
        if arr_list:
            for p in arr_list:
                f.write(f"{p}\n")
        else:
            f.write("No arrangement points found.\n")
    except Exception as e:
        f.write(f"GetArrangementList error: {e}\n")
    
    f.write("\n=== Current Pattern Arrangements ===\n")
    for i in range(10):
        try:
            res = pattern_api.GetArrangementOfPattern(i)
            f.write(f"Pattern {i}: {res}\n")
        except Exception as err:
            f.write(f"Pattern {i}: error: {err}\n")

print(f"Dumped arrangement data to {dump_file}")
