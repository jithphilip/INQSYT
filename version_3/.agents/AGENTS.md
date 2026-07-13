# Git Automation Rules

When creating or modifying project files in the `version_3` directory:
1. Automatically stage and commit new/modified files.
2. Automatically push commits to the remote repository using the configured credentials.
3. If the built-in GitHub MCP server experiences 401 Bad credentials, fallback to using the Git CLI with HTTPS URL token authentication (`https://<user>:<token>@github.com/jithphilip/INQSYT.git`) using the active token retrieved from the Windows Credential Manager. This ensures non-interactive background pushes succeed.
