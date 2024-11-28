# [[file:../../../journal.org::*\[2023-12-16 sam. 16:41\] Exec time module][[2023-12-16 sam. 16:41] Exec time module:1]]
import time

def exec_time (func, *args, **kwargs):
    print("\n====================================================")
    start_time = time.time()
    str_time = time.strftime("%H:%M:%S, %Y-%m-%d")
    f_name = func.__qualname__
    print (f"{f_name} started at:\t{str_time}\n")

    output = func(*args, **kwargs)
    if output:
        o_type = type(output)
        print(f"Function returned a type {o_type} output.")
    else:
        print("Function returned None.")

    elapsed_time = time.time() - start_time
    print(f"\nElapsed time:\t{elapsed_time}")
    print("====================================================\n")
    return output
# [2023-12-16 sam. 16:41] Exec time module:1 ends here
