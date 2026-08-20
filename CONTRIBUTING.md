# Contributing to Claude Code Starter Kit

## Reporting bugs

Open an issue at https://github.com/goksnair/claude-code-starter-kit/issues with:
- Your OS and Claude Code version (`claude --version`)
- Steps to reproduce
- What you expected vs what happened

## Requesting features

Open an issue tagged `enhancement`. Describe the use case, not just the feature.

## Submitting improvements

1. Fork the repo
2. Create a branch: `git checkout -b fix/your-description`
3. Make your changes — follow the existing file structure
4. Test with `bash score-starter-kit.sh` (should score 95+)
5. Open a pull request with a clear description

## What's in scope

- Bug fixes in hooks, install.sh, or commands
- Documentation improvements
- New hook ideas (open an issue first to discuss)
- Better test fixtures

## What's out of scope

- Opinionated persona-specific changes (this kit is persona-agnostic)
- Breaking changes to the hook API without a migration path

## Support

For Gumroad customers: reply to your purchase receipt for priority support.
For GitHub users: open an issue or start a Discussion.
