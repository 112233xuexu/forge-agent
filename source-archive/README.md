# Source archive

This directory stores the prepared open-source source package as base64 zip parts because the current connector can write text files but cannot perform a native git push of a binary archive.

To reconstruct the original prepared source package after cloning this repository:

```bash
cat source-archive/forge-agent-oss-ready.zip.b64.part* | base64 -d > forge-agent-oss-ready.zip
unzip forge-agent-oss-ready.zip -d forge-agent-oss-ready
```

On PowerShell:

```powershell
Get-Content source-archive/forge-agent-oss-ready.zip.b64.part* | Set-Content forge-agent-oss-ready.zip.b64
certutil -decode forge-agent-oss-ready.zip.b64 forge-agent-oss-ready.zip
Expand-Archive forge-agent-oss-ready.zip forge-agent-oss-ready
```

The visible repository files provide the public project landing page. The archive parts preserve the full prepared RC10 source tree for follow-up development.
