"""Open, close, restart or check an Unreal Editor with its MCP server, so an agent can manage the editor itself.

Usage:
    python editor.py open    --project C:/path/Game.uproject [--engine "C:/Program Files/Epic Games/UE_5.8"] [--port 8000]
    python editor.py close   --project ...
    python editor.py restart --project ...
    python editor.py status  --project ...

- open: launches UnrealEditor.exe with -ModelContextProtocolStartServer and blocks until the server answers an
  MCP `initialize` (default timeout 15 min; first launches compile shaders). Exit code 0 = server ready.
- close: asks the editor to close (WM_CLOSE); force-kills only after 30 s (unsaved changes are then lost).
- C++ projects must be built first (otherwise the editor shows a "rebuild modules?" dialog and never gets ready).
- Engine: --engine, else the UE_ROOT env var, else "C:/Program Files/Epic Games/UE_<EngineAssociation>".
Windows only (process lookup uses PowerShell/CIM).
"""
import argparse, json, os, subprocess, sys, time, urllib.request
from pathlib import Path


def editor_pids(project):
    ps = ("Get-CimInstance Win32_Process -Filter \"Name='UnrealEditor.exe'\" | "
          f"Where-Object {{ $_.CommandLine -like '*{Path(project).name}*' }} | ForEach-Object {{ $_.ProcessId }}")
    out = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True).stdout
    return [int(x) for x in out.split() if x.isdigit()]


def mcp_ready(url, timeout=3):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "editor.py", "version": "1"}}}).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Content-Type": "application/json", "Accept": "application/json, text/event-stream"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status < 500
    except Exception:
        return False


def engine_root(args):
    if args.engine:
        return Path(args.engine)
    if os.environ.get("UE_ROOT"):
        return Path(os.environ["UE_ROOT"])
    assoc = json.loads(Path(args.project).read_text(encoding="utf-8")).get("EngineAssociation", "")
    return Path(rf"C:\Program Files\Epic Games\UE_{assoc}")


def close(args):
    pids = editor_pids(args.project)
    for pid in pids:
        subprocess.run(["taskkill", "/PID", str(pid)], capture_output=True)
    t0 = time.time()
    while editor_pids(args.project) and time.time() - t0 < 30:
        time.sleep(1)
    left = editor_pids(args.project)
    for pid in left:
        subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
    print("editor closed" + (" (forced after 30 s; unsaved changes lost)" if left else "") if pids else "editor was not running")
    return 0


def open_(args, url):
    if not editor_pids(args.project):
        exe = engine_root(args) / "Engine" / "Binaries" / "Win64" / "UnrealEditor.exe"
        if not exe.exists():
            print(f"UnrealEditor.exe not found: {exe} (pass --engine or set UE_ROOT)")
            return 1
        subprocess.Popen([str(exe), str(Path(args.project).resolve()), "-ModelContextProtocolStartServer",
                          f"-ModelContextProtocolPort={args.port}", "-nosplash"],
                         creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
        print(f"editor launched; waiting for MCP at {url} ...", flush=True)
    t0 = time.time()
    while time.time() - t0 < args.timeout:
        if mcp_ready(url):
            print(f"OK  MCP ready after {time.time() - t0:.0f}s")
            return 0
        if not editor_pids(args.project):
            print("FAILED  editor exited during startup (check <Project>/Saved/Logs)")
            return 1
        time.sleep(3)
    print("FAILED  MCP did not answer before the timeout")
    return 1


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("action", choices=["open", "close", "restart", "status"])
    p.add_argument("--project", required=True)
    p.add_argument("--engine")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--timeout", type=int, default=900)
    args = p.parse_args()
    url = f"http://127.0.0.1:{args.port}/mcp"
    if args.action == "status":
        pids = editor_pids(args.project)
        print(f"editor {'running (PID ' + ', '.join(map(str, pids)) + ')' if pids else 'closed'}  "
              f"mcp {'ready' if mcp_ready(url) else 'not answering'}  {url}")
        return 0
    if args.action == "close":
        return close(args)
    if args.action == "restart":
        close(args)
    return open_(args, url)


if __name__ == "__main__":
    sys.exit(main())
