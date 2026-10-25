# Operations: Console Commands, Settings, Recovery

Read this when something is misbehaving with the MCP server (tools missing, port collision, stale tool registry), or when you need a non-default configuration.

## Editor lifecycle (open, close, restart from the agent)

`scripts/editor.py` (Windows) lets the agent manage the editor without asking the user:

```bash
python scripts/editor.py open    --project C:/path/Game.uproject   # launch + wait until MCP answers (exit 0 = ready)
python scripts/editor.py status  --project C:/path/Game.uproject
python scripts/editor.py restart --project C:/path/Game.uproject   # e.g. after .uproject/.ini changes
python scripts/editor.py close   --project C:/path/Game.uproject   # graceful close; forced after 30 s
```

- It launches with `-ModelContextProtocolStartServer`, so no `.ini` or console step is needed.
- Readiness is a real MCP `initialize` request, not just an open port.
- Build C++ projects before `open`: an outdated module triggers a "rebuild?" dialog that blocks startup.
- After a restart the MCP client must reconnect (`/mcp` → Reconnect in Claude Code).

## Console commands

Run these from the Unreal Editor console (`~`).

| Command                                              | Use it for                                                                                               |
|------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| `ModelContextProtocol.StartServer [port]`            | Start the MCP server. Pass a port to override the default (e.g. when 8000 is in use).                    |
| `ModelContextProtocol.StopServer`                    | Stop the server. Useful if the registry is in a bad state and you want a clean restart.                  |
| `ModelContextProtocol.RefreshTools`                  | Re-register every toolset. Run this after the user enables a new toolset plugin.                         |
| `ModelContextProtocol.GenerateClientConfig <client>` | Regenerate the per-client config file. Args: `ClaudeCode`, `Cursor`, `VSCode`, `Gemini`, `Codex`, `All`. |

## Tool-search mode

`tools/list` has two modes, controlled by the `bEnableToolSearch` UPROPERTY on `UModelContextProtocolSettings` (default `true`):

- **`True`** (default): `tools/list` returns only `list_toolsets`, `describe_toolset`, `call_tool`. Toolset tools are dispatched server-side through `call_tool` and stay out of the prompt; the catalog never changes mid-session, so the prompt cache stays warm.
- **`False`**: every toolset tool is registered as a native MCP tool at startup, schemas visible upfront. Used by the hash-mapping commandlet.

Override in the same `.ini` used for `bAutoStartServer`:

```ini
[/Script/ModelContextProtocolEngine.ModelContextProtocolSettings]
bEnableToolSearch=False
```

## Troubleshooting matrix

| Symptom                                               | What to do                                                                                                                                                                                                                                                                                                          |
|-------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `unreal-mcp` not in `/mcp`, or `list_toolsets` errors | The editor isn't running, or the MCP server isn't started. Start it with `scripts/editor.py open` (see "Editor lifecycle"), or ask the user to launch the editor and run `ModelContextProtocol.StartServer` from the console (or enable `bAutoStartServer` per `setup.md`). Then check the Output Log for startup errors.                                                               |
| Editor logs "Failed to listen on port"                | Another process holds the default port. Change `ServerPortNumber` in the per-user `EditorPerProjectUserSettings.ini` (see `setup.md`), or pass `-ModelContextProtocolPort=<port>` on the next launch; restart the editor, and re-run `ModelContextProtocol.GenerateClientConfig ClaudeCode` to refresh `.mcp.json`. |
| A toolset you expect (e.g. `NiagaraTools`) is missing | Run `ModelContextProtocol.RefreshTools`. If still missing, the toolset's plugin may not be enabled in the `.uproject`. Check there.                                                                                                                                                                                 |
| Tool calls hang or return errors                      | Editor may be busy compiling, loading a level, or in PIE. Wait and retry. For long compiles, prefer `LiveCodingToolset.CompileLiveCoding`. It returns when the compile actually finishes.                                                                                                                           |
| `AIAssistantToolset.GetDockedContext` returns empty   | The Claude Code tab must be docked inside an asset editor (Blueprint, Material, etc.) to provide docked context. If undocked, that tool has nothing to report.                                                                                                                                                      |
| Warning "Asset Manager settings do not include an entry for assets of type GameFeatureData" | Appears when `AllToolsets` enables the Game Features plugin in a project that never declared that asset type. Harmless; to silence it add to `Config/DefaultGame.ini`: `[/Script/Engine.AssetManagerSettings]` + `+PrimaryAssetTypesToScan=(PrimaryAssetType="GameFeatureData",AssetBaseClass="/Script/GameFeatures.GameFeatureData",bHasBlueprintClasses=False,bIsEditorOnly=False,Directories=((Path="/Game/Unused")),SpecificAssets=,Rules=(Priority=-1,ChunkId=-1,bApplyRecursively=True,CookRule=AlwaysCook))`, then restart the editor. |
| Sequential tool calls collide                         | Tool calls execute on the game thread. Don't issue them in parallel, even when they look independent. Serialize.                                                                                                                                                                                                    |
