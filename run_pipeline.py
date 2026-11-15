import subprocess

def run_step(script_name):
    print(f"\n[PIPELINE] Running {script_name}...")
    result = subprocess.run(["python", script_name])
    if result.returncode != 0:
        print(f"[ERROR] Failed at {script_name}")
        exit(1)

if __name__ == "__main__":
    print("=== Starting Local Lakehouse CDC Pipeline ===")
    run_step("cdc_simulation.py")
    run_step("iceberg_writer.py")
    run_step("query_lakehouse.py")
    print("\n=== Pipeline Executed Successfully! ===")